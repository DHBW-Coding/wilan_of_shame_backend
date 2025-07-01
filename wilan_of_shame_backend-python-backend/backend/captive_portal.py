from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
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

ALLOWED_PATHS = {
    "/connecttest.txt",
    "/canonical.html",
    "/generate_204",
    "/hotspot-detect.html",
}

@app.get("/{path:path}")
async def captive_portal(request: Request, path: str):
    if f"/{path}" in ALLOWED_PATHS:
        # Sende leere Antwort mit Status 204 (No Content) oder eine kleine Datei
        return PlainTextResponse("", status_code=204)
    
    # Ansonsten redirect auf Portal-Seite
    return RedirectResponse(url="http://192.168.4.1:8080")

@app.post("/login")
async def login(request: Request):
    # Get client IP
    client_ip = request.client.host

    # Use arp to get MAC address
    try:
        arp_output = subprocess.check_output(["arp", "-n", client_ip]).decode()
        mac_address = None
        for line in arp_output.splitlines():
            if client_ip in line:
                parts = line.split()
                mac_address = next((p for p in parts if ":" in p), None)
                break

        if not mac_address:
            print(f"Could not find MAC address for IP {client_ip}")
            return HTMLResponse("Login failed: MAC not found", status_code=500)

        # Allow client MAC through firewall
        subprocess.run(
            ["iptables", "-I", "FORWARD", "-m", "mac", "--mac-source", mac_address, "-j", "ACCEPT"],
            check=True
        )
        print(f"MAC {mac_address} added to whitelist")

    except subprocess.CalledProcessError as e:
        print(f"Failed to whitelist MAC: {e}")
        return HTMLResponse("Login failed", status_code=500)

    return RedirectResponse(url="http://example.com", status_code=302)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)