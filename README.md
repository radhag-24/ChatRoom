# WebSocket Chat Room

A simple **topic-based real-time chat application** built using **FastAPI + WebSockets** on the backend and a minimal **HTML/JavaScript** client on the frontend.

Users can:
- Connect with a **username**
- **Join or create** a chat topic (room)
- **Send & receive** real-time messages instantly
- Use `/list` to view all active topics with user counts
- Messages **auto-expire** after a configurable duration (e.g., 30 seconds)

---

## 📂 Project Structure

```
ChatRoom/
│
├── main.py              # FastAPI WebSocket server
├── client_example.py    # Terminal-based chat client
└── chat.html            # Simple web-based client UI
```


Install dependencies:
```bash
pip install fastapi uvicorn websockets
```

Or using requirements file:
```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server

Activate your virtual environment:
```bash
.\venv\Scripts\activate
```

Start FastAPI WebSocket server:
```bash
uvicorn main:app --reload
```

Server will run at:
```
http://127.0.0.1:8000
```

---

## 💬 Using the Web Client

1. Go to your project folder:
   ```
   ChatRoom/
     └── chat.html
   ```
2. **Double click** `chat.html`  
   → It will open in your browser.

**OR (VS Code Option)**  
1. Open the folder in VS Code  
2. Right-click `chat.html`  
3. Select **“Open with Live Server”**

> **Note:** The WebSocket server **must be running** for the chat page to work.

---

## 🖥 Optional: Terminal Chat Client

Open two terminals and run:
```bash
python client_example.py
```

Example:
```
=== Simple WebSocket Chat Client ===
Enter your username: alice
Enter topic name: sports
You: hello!
```

---

## 📝 Commands

| Command | Description                           |
|--------|----------------------------------------|
| `/list` | Shows all active topics + user counts |
| `exit`  | Disconnects gracefully                |

---

## ✅ Example Chat Flow

**Client 1**
```
Username: bob
Topic: sports
You: hello
```

**Client 2**
```
Username: alice
Topic: sports
[RECEIVED] bob: hello
```

**Any Client**
```
/list
Active Topics:
sports (2 users)
```

## 👨‍💻 Author
Developed by 
[radhag-24](https://github.com/radhag-24) ✨
Software Developer
