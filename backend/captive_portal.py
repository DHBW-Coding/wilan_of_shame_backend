from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import subprocess
import uvicorn

app = FastAPI()

#@app.get("/")
#async def captive_portal_home():
    #return {"message": "Welcome to the Captive Portal"}

@app.get("/", response_class=HTMLResponse)
async def portal():
    return """
    <html>
        <head><title>Welcome</title></head>
        <body>
            <h1>Welcome to Free WiFi</h1>
            <form action="/login" method="post">
                <input type="submit" value="Accept and Continue">
            </form>
        </body>
    </html>
    """

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