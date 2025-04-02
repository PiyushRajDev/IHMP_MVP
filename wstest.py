import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws/1"  # Replace '1' with doctor_id
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")

        # Wait for updates from the server
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(test_websocket())
