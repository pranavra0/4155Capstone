from fastapi import FastAPI
import psutil
import socket

app = FastAPI(title="Node Agent")

@app.get("/health")
def health():
    return {
        "hostname": socket.gethostname(),
        "status": "ok",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent
    }
