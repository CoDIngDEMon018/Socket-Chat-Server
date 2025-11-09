#!/usr/bin/env python3
"""
Simple TCP Chat Client
"""
import socket
import threading
import sys


def receive_messages(sock):
    """Receive messages from server"""
    while True:
        try:
            data = sock.recv(1024).decode().strip()
            if not data:
                print("\n[Disconnected]")
                break
            print(f"\n{data}")
            print("You: ", end="", flush=True)
        except:
            break


def main():
    host = '127.0.0.1'
    port = 4000
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))
        print("Connected!\n")
    except Exception as e:
        print(f"Could not connect: {e}")
        return
    
    # Login
    while True:
        username = input("Enter username: ").strip()
        if not username or ' ' in username:
            print("Invalid username (no spaces allowed)")
            continue
        
        sock.sendall(f"LOGIN {username}\n".encode())
        response = sock.recv(1024).decode().strip()
        print(f"{response}\n")
        
        if response == "OK":
            print("=== Commands ===")
            print("Just type to chat")
            print("/who - list users")
            print("/dm <user> <msg> - private message")
            print("/quit - exit\n")
            break
    
    # Start receiver thread
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    
    # Main loop
    try:
        while True:
            text = input("You: ")
            if not text:
                continue
            if text.lower() == '/quit':
                break
            elif text.lower() == '/who':
                sock.sendall(b"WHO\n")
            elif text.startswith('/dm '):
                parts = text[4:].split(' ', 1)
                if len(parts) == 2:
                    sock.sendall(f"DM {parts[0]} {parts[1]}\n".encode())
            else:
                sock.sendall(f"MSG {text}\n".encode())
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()


if __name__ == "__main__":
    main()