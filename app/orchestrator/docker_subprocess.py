# Wrapper to use Docker CLI instead of Python SDK (Windows workaround)
import subprocess
import json


class DockerSubprocessClient:
    """Use Docker CLI as fallback for Windows named pipe issues"""

    def ping(self):
        """Test Docker connection"""
        try:
            result = subprocess.run(['docker', 'info'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def containers_list(self, all=False):
        """List containers using docker ps"""
        cmd = ['docker', 'ps', '--format', '{{json .}}', '--no-trunc']
        if all:
            cmd.append('-a')

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"Docker CLI error: {result.stderr}")

        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                # Create a simple object that mimics docker SDK container
                container = type('Container', (), {
                    'id': data.get('ID', ''),
                    'name': data.get('Names', ''),
                    'status': data.get('Status', ''),
                    'image': type('Image', (), {'tags': [data.get('Image', '')]})()
                })()
                containers.append(container)
        return containers

    def containers_get(self, container_id):
        """Get a single container"""
        result = subprocess.run(
            ['docker', 'inspect', container_id],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise RuntimeError(f"Container not found: {container_id}")

        data = json.loads(result.stdout)[0]
        container = type('Container', (), {
            'id': data['Id'],
            'name': data['Name'].lstrip('/'),
            'status': data['State']['Status'],
            'image': type('Image', (), {
                'tags': data.get('Config', {}).get('Image', 'unknown').split()
            })()
        })()
        return container

    def containers_run(self, image, name=None, command=None, detach=True):
        """Start a container with optional command"""
        cmd = ['docker', 'run']
        if detach:
            cmd.append('-d')
        if name:
            cmd.extend(['--name', name])
        cmd.append(image)
        # Add command at the end if provided
        if command:
            cmd.extend(command.split())

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"Docker run failed: {result.stderr}")

        container_id = result.stdout.strip()
        return self.containers_get(container_id)

    def containers_stop(self, container_id, timeout=5):
        """Stop a container"""
        result = subprocess.run(
            ['docker', 'stop', '-t', str(timeout), container_id],
            capture_output=True,
            text=True,
            timeout=timeout+10
        )
        return result.returncode == 0

    def containers_remove(self, container_id, force=True):
        """Remove a container"""
        cmd = ['docker', 'rm']
        if force:
            cmd.append('-f')
        cmd.append(container_id)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
