# Socket Chat Server

A simple TCP-based chat server and client implemented in Python.  
Allows multiple clients to connect, send messages, and chat in real-time.  
Ideal for learning socket programming, networking fundamentals, and building basic chat apps.

## 📁 Repository Contents

- `server.py` — The chat server implementation, listens for incoming connections, manages client sessions, and broadcasts messages.  
- `client.py` — A command-line chat client which connects to the server, sends and receives messages.  
- `test_chat.sh` — A simple shell script to start the server and multiple client instances for testing.  
- `README.md` — This documentation file.

## 🧭 Features

- Multi-client support: Multiple clients can connect simultaneously and chat with each other.  
- Simple command interface: Clients can send messages which are broadcast to all other connected clients.  
- Easy to extend: Base code can be extended for authentication, private messaging, encryption, GUI client, etc.

## 🛠️ Getting Started

### Prerequisites
- Python 3.6+ installed  
- Network access (for local testing `localhost` is fine)  
- (Optional) GNU bash or compatible shell for `test_chat.sh`

### Running the Server
```bash
python server.py
