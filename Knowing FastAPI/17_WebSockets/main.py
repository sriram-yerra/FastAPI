from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
)

@app.get("/")
async def get():
    with open("static/chat.html", "r") as f:
        # Show simple HTML → HTMLResponse  
        return HTMLResponse(content=f.read(), status_code=200)

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # waiting for someone to open the chat, opce opened -> then accepted()
    await websocket.accept()
    clients.append(websocket)

    # check if client is live
    try:
        # if client is live then do this continously..!
        while True:
            data = await websocket.receive_text()

            # send message to EVERYONE
            for client in clients:
                await client.send_text(data)

    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")