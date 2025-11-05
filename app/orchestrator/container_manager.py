# app/orchestrator/container_manager.py
from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import platform

try:
    import docker
    from docker.errors import NotFound, APIError
    DOCKER_SDK_AVAILABLE = True
except ImportError:
    DOCKER_SDK_AVAILABLE = False
    NotFound = RuntimeError
    APIError = RuntimeError

from .docker_subprocess import DockerSubprocessClient


class DockerUnavailable(RuntimeError):
    """Raised when the local Docker daemon cannot be reached."""


class ContainerManager:
    def __init__(self, max_workers: int = 4) -> None:
        self._client = None
        self._use_subprocess = False
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    # ---------- private helpers ----------

    def _client_or_raise(self):
        if self._client is None:
            # On Windows, try subprocess method first (doesn't require TLS settings)
            if platform.system() == "Windows":
                try:
                    cli = DockerSubprocessClient()
                    if cli.ping():
                        self._client = cli
                        self._use_subprocess = True
                        print("Using Docker CLI subprocess (no TLS configuration needed)")
                        return self._client
                except Exception:
                    pass

            # Fall back to SDK if available and not Windows
            if DOCKER_SDK_AVAILABLE:
                try:
                    if platform.system() == "Windows":
                        # Try TCP first
                        try:
                            self._client = docker.DockerClient(base_url='tcp://localhost:2375')
                            self._client.ping()
                            print("Using Docker SDK via TCP")
                        except Exception:
                            # Try from_env
                            self._client = docker.from_env()
                            self._client.ping()
                            print("Using Docker SDK via from_env")
                    else:
                        self._client = docker.from_env()
                        self._client.ping()
                    self._use_subprocess = False
                    return self._client
                except Exception as e:
                    raise DockerUnavailable(f"Docker unavailable: {e}")
            else:
                raise DockerUnavailable("Docker SDK not available and subprocess method failed")
        return self._client

    # ---------- synchronous methods ----------

    def list_containers(self, all: bool = False):
        client = self._client_or_raise()
        if self._use_subprocess:
            return client.containers_list(all=all)
        else:
            return client.containers.list(all=all)

    def get_container(self, container_id: str):
        client = self._client_or_raise()
        if self._use_subprocess:
            return client.containers_get(container_id)
        else:
            return client.containers.get(container_id)

    def start_container(self, image: str, name: str | None = None):
        client = self._client_or_raise()
        if self._use_subprocess:
            c = client.containers_run(image=image, name=name, detach=True)
        else:
            c = client.containers.run(image=image, name=name, detach=True)
            try:
                c.reload()
            except Exception:
                pass

        return {
            "id": c.id,
            "name": getattr(c, "name", None),
            "image": (getattr(c.image, "tags", None) or ["<none>"])[0],
            "status": getattr(c, "status", None),
        }

    def stop_container(self, container_id: str, remove: bool = True):
        client = self._client_or_raise()

        if self._use_subprocess:
            try:
                client.containers_stop(container_id, timeout=5)
            except Exception:
                pass

            if remove:
                try:
                    client.containers_remove(container_id, force=True)
                except Exception:
                    pass
        else:
            try:
                c = client.containers.get(container_id)
            except NotFound:
                raise

            try:
                c.stop(timeout=5)
            except APIError:
                pass

            if remove:
                try:
                    c.remove(force=True)
                except NotFound:
                    pass
                except APIError:
                    raise

        return {"status": "removed" if remove else "stopped", "id": container_id}

    # ---------- async wrappers ----------

    async def list_containers_async(self, all: bool = False):
        """Async version - runs blocking call in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.list_containers,
            all
        )

    async def get_container_async(self, container_id: str):
        """Async version - runs blocking call in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self.get_container,
            container_id
        )

    async def start_container_async(self, image: str, name: str | None = None):
        """Async version - runs blocking call in thread pool"""
        loop = asyncio.get_event_loop()
        func = partial(self.start_container, image=image, name=name)
        return await loop.run_in_executor(self._executor, func)

    async def stop_container_async(self, container_id: str, remove: bool = True):
        """Async version - runs blocking call in thread pool"""
        loop = asyncio.get_event_loop()
        func = partial(self.stop_container, container_id=container_id, remove=remove)
        return await loop.run_in_executor(self._executor, func)

    # ---------- cleanup ----------

    def shutdown(self):
        """Call this on app shutdown to cleanup thread pool"""
        self._executor.shutdown(wait=True)
        if self._client:
            self._client.close()