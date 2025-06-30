from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import uvicorn
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = Path(BASE_DIR / "captive-p/index.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/privacy-policy.html", response_class=HTMLResponse)
def read_root():
    html_path = Path(BASE_DIR / "captive-p/privacy-policy.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/terms-of-service.html", response_class=HTMLResponse)
def read_root():
    html_path = Path(BASE_DIR / "captive-p/terms-of-service.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "frontend" / "assets" / "favicon.ico")

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