import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def captive_portal_home():
    return {"message": "Welcome to the Captive Portal"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)