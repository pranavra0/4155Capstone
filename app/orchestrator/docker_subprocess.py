import subprocess
import json
import re

ALLOWED_IMAGES = [
    'python:3.11-slim', 'python:3.10-slim', 'python:3.9-slim',
    'node:20-slim', 'node:18-slim',
    'ruby:3.2-slim', 'golang:1.21-alpine', 'rust:slim',
    'ubuntu:22.04', 'debian:bookworm-slim', 'alpine:3.18',
    'nginx:alpine', 'redis:alpine', 'postgres:15-alpine',
    'openjdk:17-slim', 'maven:3.9-eclipse-temurin-17',
]

BLOCKED_PATTERNS = [
    r'--privileged', r'--net[=\s]*host', r'--network[=\s]*host', r'--pid[=\s]*host',
    r'-v\s+/', r'--volume\s+/', r':/host', r':/etc', r':/var', r':/root', r':/proc', r':/sys',
    r'rm\s+-rf\s+/', r'mkfs', r'dd\s+if=', r'chmod\s+777', r'chmod\s+\+s', r'chown',
    r'/etc/shadow', r'/etc/passwd', r'/etc/sudoers',
    r'curl.*\|.*sh', r'wget.*\|.*sh', r'curl.*\|.*bash', r'wget.*\|.*bash',
    r'nc\s+-', r'ncat', r'/dev/tcp', r'/dev/udp',
    r'python.*-c.*socket', r'python.*-c.*subprocess',
    r'base64\s+-d', r'eval\s*\(', r'\.\./', r'/\.\.',
    r'sudo', r'su\s+-', r'su\s+root',
    r'apt\s+install', r'yum\s+install', r'apk\s+add',
    r'pip\s+install', r'npm\s+install', r'gem\s+install',
    r'crontab', r'/etc/cron', r'iptables', r'nmap', r'masscan',
    r'mount\s+', r'umount\s+', r'docker\s+', r'kubectl',
    r'ssh\s+', r'scp\s+', r'rsync\s+',
    r'>\s*/etc/', r'>\s*/var/', r'>\s*/root/',
    r'&>', r'2>&1.*>', r'xargs', r'find.*-exec',
]


class SecurityError(Exception):
    pass


def validate_image(image: str) -> None:
    if image not in ALLOWED_IMAGES:
        raise SecurityError(f"Image '{image}' not allowed")


def validate_command(command: str) -> None:
    if not command:
        return
    cmd_lower = command.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, cmd_lower):
            raise SecurityError("Command contains blocked pattern")


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
        validate_image(image)
        validate_command(command)

        cmd = ['docker', 'run']
        if detach:
            cmd.append('-d')
        cmd.extend(['--memory', '256m'])
        cmd.extend(['--cpus', '0.5'])
        cmd.extend(['--network', 'none'])
        cmd.extend(['--security-opt', 'no-new-privileges'])
        cmd.extend(['--cap-drop', 'ALL'])
        if name:
            cmd.extend(['--name', name])
        cmd.append(image)
        if command:
            cmd.extend(['sh', '-c', command])

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
