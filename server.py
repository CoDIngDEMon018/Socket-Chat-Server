#!/usr/bin/env python3
"""
TCP Chat Server - Complete Implementation
Supports: Login, Broadcasting, WHO, DM, PING/PONG, Idle Timeout
"""
import socket
import threading
import sys

# Global dictionary: username -> connection socket
clients = {}
clients_lock = threading.Lock()

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 4000       # Default port
IDLE_TIMEOUT = 3600  # 1 hour (adjustable for testing)


def broadcast(message, exclude=None):
    """
    Send a message to all connected clients except the one in 'exclude'.
    """
    with clients_lock:
        disconnected = []
        for username, conn in list(clients.items()):
            if username == exclude:
                continue
            try:
                conn.sendall((message + "\n").encode())
            except Exception:
                disconnected.append(username)
        
        # Clean up disconnected clients
        for username in disconnected:
            if username in clients:
                del clients[username]


def handle_client(conn, addr):
    """
    Handle communication with a connected client.
    Protocol:
      - First message: LOGIN <username>
      - Then: MSG <text>, DM <user> <text>, WHO, PING, etc.
    """
    username = None
    buffer = ""
    
    try:
        # === LOGIN PHASE ===
        conn.settimeout(30)  # 30 second timeout for login
        login_data = conn.recv(1024)
        
        if not login_data:
            conn.close()
            return
        
        login_line = login_data.decode().strip()
        
        # Check if it's a proper LOGIN command
        if not login_line.startswith("LOGIN "):
            conn.sendall(b"ERR invalid-login\n")
            conn.close()
            return
        
        # Extract username
        parts = login_line.split(' ', 1)
        if len(parts) != 2 or not parts[1].strip():
            conn.sendall(b"ERR invalid-username\n")
            conn.close()
            return
        
        username = parts[1].strip()
        
        # Validate username (no spaces)
        if ' ' in username:
            conn.sendall(b"ERR invalid-username\n")
            conn.close()
            return
        
        # Check for duplicate username
        with clients_lock:
            if username in clients:
                conn.sendall(b"ERR username-taken\n")
                conn.close()
                return
            # Register the client
            clients[username] = conn
        
        # Send OK response
        conn.sendall(b"OK\n")
        print(f"[Server] {username} logged in from {addr}")
        
        # Notify others
        broadcast(f"INFO {username} joined", exclude=username)
        
        # === MESSAGE LOOP ===
        conn.settimeout(IDLE_TIMEOUT)  # Set idle timeout
        
        while True:
            data = conn.recv(1024)
            
            if not data:
                break  # Client disconnected
            
            buffer += data.decode()
            
            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                
                if not line:
                    continue
                
                # Parse command
                parts = line.split(' ', 1)
                cmd = parts[0].upper()
                
                # === WHO command: list all users ===
                if cmd == "WHO":
                    with clients_lock:
                        for user in clients:
                            try:
                                conn.sendall(f"USER {user}\n".encode())
                            except Exception:
                                pass
                
                # === DM command: private message ===
                elif cmd == "DM":
                    if len(parts) < 2:
                        conn.sendall(b"ERR invalid-dm-format\n")
                        continue
                    
                    dm_parts = parts[1].split(' ', 1)
                    if len(dm_parts) < 2:
                        conn.sendall(b"ERR invalid-dm-format\n")
                        continue
                    
                    target_user = dm_parts[0]
                    dm_text = dm_parts[1]
                    
                    with clients_lock:
                        if target_user in clients:
                            try:
                                clients[target_user].sendall(f"DM {username} {dm_text}\n".encode())
                                # Echo back to sender
                                conn.sendall(f"DM {target_user} {dm_text}\n".encode())
                                print(f"[Server] DM from {username} to {target_user}: {dm_text}")
                            except Exception:
                                conn.sendall(b"ERR send-failed\n")
                        else:
                            conn.sendall(f"ERR user-not-found {target_user}\n".encode())
                
                # === PING/PONG heartbeat ===
                elif cmd == "PING":
                    try:
                        conn.sendall(b"PONG\n")
                    except Exception:
                        pass
                
                # === MSG command: broadcast message ===
                elif cmd == "MSG":
                    if len(parts) < 2:
                        continue  # Ignore empty messages
                    
                    message_text = parts[1]
                    broadcast(f"MSG {username} {message_text}")
                    print(f"[Server] {username}: {message_text}")
                
                # === Unknown command ===
                else:
                    conn.sendall(b"ERR unknown-command\n")
    
    except socket.timeout:
        # Idle timeout occurred
        print(f"[Server] {username or addr} timed out due to inactivity")
        try:
            conn.sendall(b"INFO You have been disconnected due to inactivity\n")
        except:
            pass
        
        if username:
            with clients_lock:
                if username in clients:
                    del clients[username]
            broadcast(f"INFO {username} disconnected")
    
    except Exception as e:
        print(f"[Server] Error with {username or addr}: {e}")
    
    finally:
        # === CLEANUP ===
        if username:
            print(f"[Server] {username} disconnected")
            with clients_lock:
                if username in clients:
                    del clients[username]
            broadcast(f"INFO {username} disconnected")
        
        try:
            conn.close()
        except:
            pass


def main():
    """Start the TCP chat server."""
    global PORT
    
    # Parse command-line arguments for port
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print("Usage: python server.py [port]")
            sys.exit(1)
    
    # Create server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(10)  # Backlog of 10
    
    print("=" * 50)
    print("TCP CHAT SERVER")
    print("=" * 50)
    print(f"Listening on: {HOST}:{PORT}")
    print(f"Idle timeout: {IDLE_TIMEOUT} seconds")
    print("Features: LOGIN, MSG, WHO, DM, PING/PONG")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    try:
        while True:
            conn, addr = server_sock.accept()
            print(f"[Server] New connection from {addr}")
            
            # Spawn thread for each client
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    
    finally:
        # Close all client connections
        with clients_lock:
            for username, conn in clients.items():
                try:
                    conn.close()
                except:
                    pass
        server_sock.close()
        print("[Server] Server stopped")


if __name__ == "__main__":
    main()