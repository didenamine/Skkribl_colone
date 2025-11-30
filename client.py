import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

HOST = '127.0.0.1'
PORT = 5555

class PictionaryClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((HOST, PORT))
        except:
            messagebox.showerror("Error", "Could not connect to server")
            return

        # 2. Game State
        self.is_drawer = False
        self.last_x = 0
        self.last_y = 0
        
        # 3. GUI Setup
        self.root = tk.Tk()
        self.root.title("Python Pictionary")
        
        # Ask for name
        self.name = simpledialog.askstring("Name", "Enter your name:")
        if not self.name: self.name = "Guest"
        self.client.send(f"NAME:{self.name}\n".encode('utf-8'))

        # Top Info Bar
        self.info_label = tk.Label(self.root, text="Waiting for players...", font=("Arial", 14))
        self.info_label.pack(pady=5)

        # Canvas (The Drawing Board)
        self.canvas = tk.Canvas(self.root, width=500, height=400, bg="white")
        self.canvas.pack()
        
        # Bind Mouse Events
        self.canvas.bind("<Button-1>", self.start_draw) # Click
        self.canvas.bind("<B1-Motion>", self.drawing)   # Drag

        # Chat Section
        self.chat_log = tk.Text(self.root, height=10, width=60, state='disabled')
        self.chat_log.pack(pady=5)
        
        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.pack(side=tk.LEFT, padx=10)
        self.entry_box.bind("<Return>", self.send_chat) # Press Enter to send

        self.send_btn = tk.Button(self.root, text="Send", command=self.send_chat)
        self.send_btn.pack(side=tk.LEFT)

        # 4. Start Listening Thread
        listen_thread = threading.Thread(target=self.receive_messages)
        listen_thread.daemon = True
        listen_thread.start()

        self.root.mainloop()

    def start_draw(self, event):
        """Records the starting point of a line."""
        self.last_x = event.x
        self.last_y = event.y

    def drawing(self, event):
        """Calculates line, draws locally, and sends to server."""
        if not self.is_drawer:
            return # Stop non-drawers from drawing

        x, y = event.x, event.y
        
        # Draw locally so it feels instant
        self.canvas.create_line(self.last_x, self.last_y, x, y, width=2, fill="black", capstyle=tk.ROUND)
        
        # Send coords to server: DRAW:x1,y1,x2,y2
        msg = f"DRAW:{self.last_x},{self.last_y},{x},{y}\n"
        self.client.send(msg.encode('utf-8'))
        
        self.last_x = x
        self.last_y = y

    def send_chat(self, event=None):
        """Sends chat message to server."""
        msg = self.entry_box.get()
        if msg:
            self.client.send(f"CHAT:{msg}\n".encode('utf-8'))
            self.entry_box.delete(0, tk.END)

    def add_chat_log(self, msg):
        """Updates the chat text box safely."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, msg + "\n")
        self.chat_log.see(tk.END) # Auto-scroll down
        self.chat_log.config(state='disabled')

    def receive_messages(self):
        """Listens for messages from the Server."""
        while True:
            try:
                msg = self.client.recv(1024).decode('utf-8')
                messages = msg.split('\n')
                
                for message in messages:
                    if not message: continue

                    # --- CLIENT PROTOCOL HANDLER ---

                    if message.startswith("DRAW:"):
                        # Format: DRAW:x1,y1,x2,y2
                        coords = message.split(":")[1].split(",")
                        x1, y1, x2, y2 = map(int, coords)
                        self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black", capstyle=tk.ROUND)

                    elif message.startswith("CHAT:"):
                        text = message.split(":", 1)[1]
                        self.add_chat_log(text)

                    elif message.startswith("NEW_ROUND:"):
                        # Reset canvas
                        self.canvas.delete("all")
                        drawer_name = message.split(":")[1]
                        
                        if drawer_name == self.name:
                            self.is_drawer = True
                            self.info_label.config(text="YOU ARE DRAWING! Wait for word...")
                        else:
                            self.is_drawer = False
                            self.info_label.config(text=f"{drawer_name} is drawing. GUESS!")

                    elif message.startswith("SECRET:"):
                        secret_word = message.split(":")[1]
                        self.info_label.config(text=f"DRAW THIS: {secret_word.upper()}")

            except Exception as e:
                print(f"Error: {e}")
                self.client.close()
                break

if __name__ == "__main__":
    PictionaryClient()