# app/orchestrator/container_manager.py
from __future__ import annotations

import docker
from docker.errors import NotFound, APIError


class DockerUnavailable(RuntimeError):
    """Raised when the local Docker daemon cannot be reached."""


class ContainerManager:
    def __init__(self) -> None:
        self._client: docker.DockerClient | None = None

    # ---------- private helpers ----------

    def _client_or_raise(self) -> docker.DockerClient:
        if self._client is None:
            try:
                self._client = docker.from_env()
                # sanity check: proves the daemon is reachable
                self._client.ping()
            except Exception as e:  # broad by design; connection failures vary by platform
                raise DockerUnavailable(f"Docker unavailable: {e}")
        return self._client

    # ---------- public API used by FastAPI routes ----------

    def list_containers(self, all: bool = False):
        client = self._client_or_raise()
        return client.containers.list(all=all)

    def get_container(self, container_id: str):
        client = self._client_or_raise()
        return client.containers.get(container_id)

    def start_container(self, image: str, name: str | None = None):
        client = self._client_or_raise()
        # detach=True so run returns a Container object immediately
        c = client.containers.run(image=image, name=name, detach=True)
        # refresh to get status/name fields
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
        try:
            c = client.containers.get(container_id)
        except NotFound:
            raise

        # stop (ignore if it's already exited)
        try:
            c.stop(timeout=5)
        except APIError:
            # best-effort; keep going to remove
            pass

        if remove:
            try:
                c.remove(force=True)
            except NotFound:
                pass
            except APIError:
                # surface real Docker API errors to the route layer
                raise

        return {"status": "removed" if remove else "stopped", "id": container_id}
