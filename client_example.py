import asyncio
import json
import websockets
import sys

SERVER_URL = "ws://localhost:8000/ws"


async def listen_messages(websocket):
    """Continuously receive messages from server."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"\n[RECEIVED JSON]\n{json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"\n[RECEIVED TEXT]\n{message}")
            print("You: ", end="", flush=True)
    except websockets.ConnectionClosed:
        print("\n[SERVER CLOSED CONNECTION]")


async def user_input(websocket):
    """Non-blocking input loop."""
    loop = asyncio.get_event_loop()
    while True:
        msg = await loop.run_in_executor(None, sys.stdin.readline)
        msg = msg.strip()
        if not msg:
            continue
        if msg.lower() in {"exit", "quit"}:
            print("[INFO] Closing connection.")
            await websocket.close()
            break
        if msg.startswith("/"):
            await websocket.send(msg)
        else:
            await websocket.send(json.dumps({"message": msg}))


async def chat_client(username, topic):
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send(json.dumps({"username": username, "topic": topic}))
        print("[INFO] Connected to server.")

        await asyncio.gather(listen_messages(websocket), user_input(websocket))


if __name__ == "__main__":
    print("=== Simple WebSocket Chat Client ===")
    username = input("Enter your username: ").strip()
    topic = input("Enter topic name: ").strip()
    asyncio.run(chat_client(username, topic))
