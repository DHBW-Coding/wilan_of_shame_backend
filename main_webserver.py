import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from websocket_manager import ws_manager

app = FastAPI()

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