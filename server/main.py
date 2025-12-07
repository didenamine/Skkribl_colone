import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from server.core import ServerCore

class SkkriblServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Skkribl Server Control Panel")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        self.msg_queue = queue.Queue()
        
        # Instantiate Core
        self.core = ServerCore(log_callback=self.log_queue, update_count_callback=self.update_count)

        self.create_widgets()
        self.root.after(100, self.process_queue)

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#3f51b5", pady=15)
        header.pack(fill=tk.X)
        tk.Label(header, text="Skkribl Game Server", font=("Segoe UI", 18, "bold"), bg="#3f51b5", fg="white").pack()

        # Controls
        controls = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        controls.pack(fill=tk.X, padx=10)

        tk.Label(controls, text="Port:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.port_entry = tk.Entry(controls, width=6)
        self.port_entry.insert(0, str(config.PORT))
        self.port_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(controls, text="Max Players:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(15, 0))
        self.players_entry = tk.Entry(controls, width=4)
        self.players_entry.insert(0, str(config.DEFAULT_PLAYERS))
        self.players_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(controls, text="Rounds:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(15, 0))
        self.rounds_entry = tk.Entry(controls, width=4)
        self.rounds_entry.insert(0, str(config.DEFAULT_ROUNDS))
        self.rounds_entry.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(controls, text="Start Server", command=self.start_server, bg="#4CAF50", fg="white", width=12)
        self.start_btn.pack(side=tk.LEFT, padx=20)

        self.stop_btn = tk.Button(controls, text="Stop Server", command=self.stop_server, bg="#f44336", fg="white", width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Status
        self.status_frame = tk.Frame(self.root, bg="#e0e0e0", pady=5, padx=10)
        self.status_frame.pack(fill=tk.X)
        self.status_label = tk.Label(self.status_frame, text="Status: STOPPED", bg="#e0e0e0", fg="red")
        self.status_label.pack(side=tk.LEFT)
        self.count_label = tk.Label(self.status_frame, text="Players: 0/0", bg="#e0e0e0")
        self.count_label.pack(side=tk.RIGHT)

        # Logs
        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled', font=("Consolas", 9))
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def log_queue(self, msg):
        self.msg_queue.put(("LOG", msg))

    def update_count(self, current, expected):
        self.msg_queue.put(("COUNT", (current, expected)))

    def process_queue(self):
        while not self.msg_queue.empty():
            type, data = self.msg_queue.get()
            if type == "LOG":
                self.log_area.config(state='normal')
                self.log_area.insert(tk.END, data + "\n")
                self.log_area.see(tk.END)
                self.log_area.config(state='disabled')
            elif type == "COUNT":
                current, expected = data
                self.count_label.config(text=f"Players: {current}/{expected}")
        self.root.after(100, self.process_queue)

    def start_server(self):
        try:
            port = int(self.port_entry.get())
            players = int(self.players_entry.get())
            rounds = int(self.rounds_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Input")
            return

        if self.core.start(port, players, rounds):
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.DISABLED)
            self.players_entry.config(state=tk.DISABLED)
            self.rounds_entry.config(state=tk.DISABLED)
            self.status_label.config(text="Status: RUNNING", fg="green")

    def stop_server(self):
        self.core.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.port_entry.config(state=tk.NORMAL)
        self.players_entry.config(state=tk.NORMAL)
        self.rounds_entry.config(state=tk.NORMAL)
        self.status_label.config(text="Status: STOPPED", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = SkkriblServerGUI(root)
    root.mainloop()
