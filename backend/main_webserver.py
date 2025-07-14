from fastapi.responses import FileResponse
import uvicorn
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from websocket_manager import ws_manager
import asyncio

app = FastAPI()

# Absolute path to the frontend directory
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')

# Serve all static files in frontend directory (e.g., CSS, JS, images)
app.mount("/static", StaticFiles(directory=frontend_path, html=True), name="static")

@app.on_event("startup")
async def startup_event():
    event_queue = app.state.event_queue

    async def forward_events_from_queue():
        loop = asyncio.get_event_loop()
        while True:
            # multiprocessing.Queue ist blockierend, daher in Thread auslesen
            data = await loop.run_in_executor(None, event_queue.get)
            await ws_manager.send_to_queue(data)

    # event_queue to ws_manager-Queue
    asyncio.create_task(forward_events_from_queue())
    # ws_manager-Queue to all WebSocket-Clients
    asyncio.create_task(ws_manager.broadcast_from_queue())


# serve index.html at root explicitly
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.receive_text()  # blockiert, bis Client trennt
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)