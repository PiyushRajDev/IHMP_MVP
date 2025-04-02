from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_websocket_pubsub import PubSubEndpoint

app = FastAPI()

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],  # Add allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# WebSocket PubSub setup
pubsub = PubSubEndpoint()

@app.websocket("/ws/{doctor_id}")
async def websocket_endpoint(websocket: WebSocket, doctor_id: int):
    """
    WebSocket endpoint for real-time updates.
    Clients subscribe to topics like 'doctor_{doctor_id}'.
    """
    topic = f"doctor_{doctor_id}"
    try:
        await pubsub.register(websocket, [topic])
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        await pubsub.unregister(websocket)

# Function to notify slot changes
def notify_slot_change(doctor_id: int):
    """
    Publish a 'slots_updated' event to the topic for the given doctor.
    """
    pubsub.publish([f"doctor_{doctor_id}"], "slots_updated")
