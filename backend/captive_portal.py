from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import uvicorn
from pathlib import Path

app = FastAPI()

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = Path("../captive-p/index.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.post("/login")
async def login(request: Request):
    # Get client IP
    client_ip = request.client.host

    # Allow client IP through firewall
    try:
        subprocess.run(
            ["iptables", "-I", "FORWARD", "-s", client_ip, "-j", "ACCEPT"],
            check=True
        )
        print(f"IP {client_ip} added to whitelist")
    except subprocess.CalledProcessError as e:
        print(f"Failed to whitelist {client_ip}: {e}")
        return HTMLResponse("Login failed", status_code=500)

    return RedirectResponse(url="http://example.com", status_code=302)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)