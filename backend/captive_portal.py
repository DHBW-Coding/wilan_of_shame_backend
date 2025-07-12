import time
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import uvicorn
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
CAPTIVE_DIR = BASE_DIR / "captive-p"

app.mount("/cpstatic", StaticFiles(directory=CAPTIVE_DIR / "static"), name="cpstatic")

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = Path(CAPTIVE_DIR / "index.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/privacy-policy.html", response_class=HTMLResponse)
def read_root():
    html_path = Path(CAPTIVE_DIR / "privacy-policy.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/terms-of-service.html", response_class=HTMLResponse)
def read_root():
    html_path = Path(CAPTIVE_DIR / "terms-of-service.html")
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(CAPTIVE_DIR / "static" / "cp-assets" / "favicon.ico")

'''
1. Abfage welches gerät (z.B. Apple, etc.) sich verbinden will (über Macadresse in Verbindung mit dem Captive Portal Call siehe unten)
2. Funktionen für die Verbindung nur spezifisch für das Gerät ausführen/nur passende Abfrageantworten geben.
3. Wenn das nicht geht alles löschen und aufgeben
'''
ALLOWED_PATHS = {
    "/connecttest.txt", # Microsoft
    "/canonical.html", # Mircosoft
    "/generate_204", # Android
    "/gen_204", # Android
    "/hotspot-detect.html", # Apple
}

# Apple expects /hotspot-detect.html to return a very specific HTML page when no captive portal
def apple_hotspot_detect():
    # When no captive portal, Apple expects a page containing the phrase "Success"
    html_content = '<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>'
    return HTMLResponse(content=html_content, status_code=200)

# Apple expects /success.txt (or /connecttest.txt) to contain exactly "Success"
def apple_success_txt():
    return PlainTextResponse(content="Success")

# Microsoft expects or /connecttest.txt to contain just plain "Microsoft Connect Test"
def microsoft_connecttext_txt():
    return PlainTextResponse(content="Microsoft Connect Test", status_code=200)

# Apple expects /generate_204 to return 204 status with no content
def generate_204():
    return Response(status_code=204)

# Microsoft expects /canonical_204 to return 204 status with success
def canonical_204():
    return Response(content="success", media_type="text/plain")

whitelist = []

@app.get("/{path:path}")
async def captive_portal(request: Request, path: str):
    client_ip = request.client.host
    #mac_address = get_mac_from_arp(client_ip)  # your function to get MAC
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
    
    if mac_address in whitelist:
        # User is allowed, return expected success responses or 204
        print("Check for Captive Success or 204")
        if path in ["hotspot-detect.html"]:
            return apple_hotspot_detect()
        elif path == "canonical.html":
            return canonical_204()
        elif path == "connecttest.txt":
            return microsoft_connecttext_txt()
        elif path in ["success.txt", "connecttest.txt"]: #Wie ist das bei Microsoft mit connecttest und canonical?
            return apple_success_txt()
        elif path == "generate_204":
            return generate_204()
        else:
            # Allow normal internet access (or proxy)
            # Allow client MAC through firewall
            subprocess.run(
                ["iptables", "-I", "FORWARD", "-m", "mac", "--mac-source", mac_address, "-j", "ACCEPT"],
                check=True
            )
            # Regel vor der allgemeinen Weiterleitung einfügen (insert -I)
            subprocess.run([
                "iptables", "-t", "nat", "-I", "PREROUTING",
                "-i", "wlan0",
                "-p", "tcp", "--dport", "80",
                "-m", "mac", "--mac-source", mac_address,
                "-j", "RETURN"
            ], check=True)
            print(f"MAC {mac_address} vom Captive Portal Redirect ausgeschlossen.")
            
            print(f"MAC {mac_address} added to whitelist")
            return RedirectResponse(url="http://example.com")  # or your real internet destination
    else:
        # Not whitelisted, redirect to captive portal page
        # print("Redirected")
        return RedirectResponse(url="http://192.168.4.1")

    # if f"/{path}" in ALLOWED_PATHS:
    #     # Sende leere Antwort mit Status 204 (No Content) oder eine kleine Datei
    #     return PlainTextResponse("", status_code=204)
    
    # # Ansonsten redirect auf Portal-Seite
    # return RedirectResponse(url="http://192.168.4.1")

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

        whitelist.append(mac_address)
        print(f"MAC {mac_address} added to whitelist")
        print(whitelist)
        # Regel vor der allgemeinen Weiterleitung einfügen (insert -I)
        subprocess.run([
            "iptables", "-t", "nat", "-I", "PREROUTING",
            "-i", "wlan0",
            "-p", "tcp", "--dport", "80",
            "-m", "mac", "--mac-source", mac_address,
            "-j", "RETURN"
        ], check=True)
        print(f"MAC {mac_address} vom Captive Portal Redirect ausgeschlossen.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to whitelist MAC: {e}")
        return HTMLResponse("Login failed", status_code=500)

    return HTMLResponse("Login succceded", status_code=200)
    #return RedirectResponse(url="http://example.com", status_code=302)

# @app.middleware("http")
# async def log_request_time(request: Request, call_next):
#     start = time.time()
#     response = await call_next(request)
#     duration = time.time() - start
#     print(f"{request.method} {request.url} - {duration:.3f}s")
#     return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)