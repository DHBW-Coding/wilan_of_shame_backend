import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from websocket_manager import ws_manager

app = FastAPI()

# Absolute path to the frontend directory
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')

# Serve all static files in frontend directory (e.g., CSS, JS, images)
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

# Optional: serve index.html at root explicitly
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_to_queue(f"Echo: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(ws_manager.broadcast_from_queue())
    uvicorn.run(app, host="127.0.0.1", port=8082)