from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import logging
import time
from typing import Dict, List

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

topics: Dict[str, Dict[str, WebSocket]] = {}
messages: Dict[str, List[Dict]] = {}

MESSAGE_TTL = 30  


async def make_username_unique(topic: str, desired: str) -> str:
    """Return a username unique inside the topic by appending #n if needed."""
    users = topics.get(topic, {})
    if desired not in users:
        return desired
    suffix = 2
    while f"{desired}#{suffix}" in users:
        suffix += 1
    return f"{desired}#{suffix}"


async def expire_message(topic: str, msg_id: int, ttl: int = MESSAGE_TTL):
    """Sleep for ttl seconds and then remove message with msg_id from messages[topic]."""
    await asyncio.sleep(ttl)
    try:
        topic_msgs = messages.get(topic)
        if not topic_msgs:
            return
        messages[topic] = [m for m in topic_msgs if m.get("id") != msg_id]
        logging.info(f"Expired message {msg_id} in topic '{topic}'.")
    except Exception as e:
        logging.exception("Error expiring message: %s", e)


async def broadcast_to_topic(topic: str, payload: dict, exclude_username: str = None):
    """Send payload (dict) to all users in topic except exclude_username."""
    users = topics.get(topic, {})
    dead_users = []
    for username, ws in list(users.items()):
        if username == exclude_username:
            continue
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            logging.exception(f"Failed to send message to {username} (will be removed).")
            dead_users.append(username)
    for username in dead_users:
        await remove_user_from_topic(topic, username)


async def remove_user_from_topic(topic: str, username: str):
    """Remove a user from a topic and delete topic if empty."""
    try:
        users = topics.get(topic)
        if not users:
            return
        ws = users.pop(username, None)
        if ws:
            logging.info(f"User '{username}' removed from topic '{topic}'.")
        if not users:
            topics.pop(topic, None)
            messages.pop(topic, None)
            logging.info(f"Topic '{topic}' removed because it became empty.")
    except Exception:
        logging.exception("Error removing user from topic")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    assigned_username = None
    user_topic = None
    try:
        raw = await websocket.receive_text()
        try:
            init = json.loads(raw)
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({"error": "Invalid JSON in initial payload"}))
            await websocket.close()
            return

        username = init.get("username")
        topic = init.get("topic")
        if not username or not topic:
            await websocket.send_text(json.dumps({"error": "username and topic are required"}))
            await websocket.close()
            return

        if topic not in topics:
            topics[topic] = {}
            messages[topic] = []

        assigned_username = await make_username_unique(topic, username)
        topics[topic][assigned_username] = websocket
        user_topic = topic

        logging.info(f"User '{assigned_username}' connected to topic '{topic}'.")
        await websocket.send_text(json.dumps({
            "status": "connected",
            "username": assigned_username,
            "topic": topic,
        }))

        msg_counter = 0
        while True:
            try:
                text = await websocket.receive_text()
            except WebSocketDisconnect:
                logging.info(f"WebSocketDisconnect from {assigned_username}")
                break

            if text.strip() == "/list":
                lines = ["Active Topics:"]
                for tname, users in topics.items():
                    lines.append(f"{tname} ({len(users)} users)")
                list_output = "\n".join(lines)
                logging.info(f"Sending /list output to {assigned_username}: {list_output}")
                await websocket.send_text(list_output)
                continue

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON payload"}))
                continue

            message_text = data.get("message")
            if not message_text:
                await websocket.send_text(json.dumps({"error": "No message provided"}))
                continue

            timestamp = int(time.time())
            msg_counter += 1
            msg_id = int(f"{int(time.time())}{msg_counter}")
            msg_obj = {
                "id": msg_id,
                "username": assigned_username,
                "message": message_text,
                "timestamp": timestamp,
            }

            messages[user_topic].append(msg_obj)
            asyncio.create_task(expire_message(user_topic, msg_id, MESSAGE_TTL))

            await broadcast_to_topic(user_topic, {
                "username": assigned_username,
                "message": message_text,
                "timestamp": timestamp,
            }, exclude_username=assigned_username)

            await websocket.send_text(json.dumps({"status": "delivered", "timestamp": timestamp}))

    except Exception:
        logging.exception("Unexpected error in websocket handler")
    finally:
        if assigned_username and user_topic:
            await remove_user_from_topic(user_topic, assigned_username)
            logging.info(f"Cleaned up connection for {assigned_username} in topic {user_topic}")
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/")
async def get_root():
    return (" WebSocket chat server is running. Connect to /ws ")
