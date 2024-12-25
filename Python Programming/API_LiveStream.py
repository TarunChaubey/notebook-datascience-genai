# mv.py
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict
# import httpx
import uvicorn
import cv2
import base64

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import asyncio

app = FastAPI()

# Dummy user data for demonstration
user_data: Dict[str, WebSocket] = {}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    user_data[user_id] = websocket
    try:
        while True:
            pass
            data = await websocket.receive_text()
            # print(f"Received message from user {user_id}: {data}")
    except Exception as e:
        print(f"WebSocket connection for user {user_id} closed unexpectedly:", e)
        del user_data[user_id]

@app.get("/")
async def home():
    return {"message": "Welcome to Video Socket API"} 


@app.post("/getframe")
async def get_video_frame(source_id):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {"Video Source Not Accessible"}
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error reading video frame")
                    break 
                encoded_frame = frame.tobytes()
                await user_data[source_id].send_bytes(encoded_frame)
        except Exception as e:
            return e
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("__main__:app", port=8000, reload=True, workers=2)