import socket
import threading
import random

HOST = '127.0.0.1'
PORT = 5555
WORD_LIST = ["apple", "tree", "house", "sun", "car", "computer", "flower", "robot"]
clients = []  
player_names = {} 
current_word = ""
drawer_socket = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server running on {HOST}:{PORT}")

def broadcast(message, exclude_socket=None):
    """Sends a message to all connected clients, optionally excluding one."""
    for client in clients:
        if client != exclude_socket:
            try:
                # Ensure message ends with newline as a delimiter
                client.send(f"{message}\n".encode('utf-8'))
            except:
                remove_client(client)

def start_new_round():
    """Resets the board, picks a new drawer and a new word."""
    global current_word, drawer_socket
    
    if not clients:
        return

    # 1. Choose a random drawer
    drawer_socket = random.choice(clients)
    
    # 2. Choose a random word
    current_word = random.choice(WORD_LIST)
    
    print(f"New Round! Drawer: {player_names[drawer_socket]}, Word: {current_word}")

    # 3. Notify everyone to clear screen and who is drawing
    broadcast(f"NEW_ROUND:{player_names[drawer_socket]}")
    
    # 4. Tell the drawer the secret word
    try:
        drawer_socket.send(f"SECRET:{current_word}\n".encode('utf-8'))
    except:
        pass

def handle_client(client):
    """Thread function to listen to a specific client."""
    global current_word
    
    try:
        while True:
            # Receive data (buffer size 1024)
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break
            
            # Handle "sticky" packets (multiple messages arriving at once)
            messages = msg.split('\n')
            
            for message in messages:
                if not message: 
                    continue

                # --- PROTOCOL HANDLER ---
                
                if message.startswith("NAME:"):
                    name = message.split(":")[1]
                    player_names[client] = name
                    broadcast(f"CHAT:Server: {name} joined the game!")
                    if len(clients) >= 2 and not current_word:
                        start_new_round()

                elif message.startswith("DRAW:"):
                    # Relay drawing coordinates to everyone else
                    broadcast(message, exclude_socket=client)

                elif message.startswith("CHAT:"):
                    content = message.split(":")[1]
                    
                    # Check if they guessed the word (and they aren't the drawer)
                    if content.lower() == current_word.lower() and client != drawer_socket:
                        broadcast(f"CHAT:Server: {player_names[client]} GUESSED THE WORD!")
                        start_new_round()
                    else:
                        # Normal chat message
                        broadcast(f"CHAT:{player_names[client]}: {content}")
                        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        remove_client(client)

def remove_client(client):
    if client in clients:
        clients.remove(client)
        client.close()
        print("Client disconnected")

# --- MAIN LOOP ---
while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    print(f"Connection from {addr}")
    
    # Start a thread for this client
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()