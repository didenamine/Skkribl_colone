import tkinter as tk
from tkinter import colorchooser

class WhiteboardApp:
    def __init__(self, master):
        self.master = master
        master.title("Python Tkinter Whiteboard")

        self.last_x, self.last_y = None, None  
        self.current_color = "black"          
        self.line_width = 5                  


        # 1. Drawing Canvas
        self.canvas = tk.Canvas(master, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas.bind('<Button-1>', self.start_line)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.stop_line)

        self.controls = tk.Frame(master, pady=10)
        self.controls.pack(fill=tk.X)

        # 3. Clear Button
        tk.Button(self.controls, text="Clear Canvas", command=self.clear_canvas,
                  bg="#FFCDD2", fg="black", activebackground="#E57373").pack(side=tk.LEFT, padx=5)

        # 4. Coor Chooser Button
        tk.Button(self.controls, text="Choose Color", command=self.choose_color,
                  bg="#B3E5FC", fg="black", activebackground="#4FC3F7").pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.controls, text="Line Thickness:").pack(side=tk.LEFT, padx=(15, 5))
        self.width_scale = tk.Scale(self.controls, from_=1, to=20, orient=tk.HORIZONTAL, command=self.set_line_width, length=150)
        self.width_scale.set(self.line_width)
        self.width_scale.pack(side=tk.LEFT, padx=5)



    def start_line(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    fill=self.current_color,
                                    width=self.line_width,
                                    capstyle=tk.ROUND,
                                    smooth=tk.TRUE)
            self.last_x, self.last_y = event.x, event.y

    def stop_line(self, event):
        self.last_x, self.last_y = None, None
    def clear_canvas(self):
        self.canvas.delete("all")
        self.last_x, self.last_y = None, None # Ensure no line segment is waiting
    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Drawing Color")
        if color_code[1]:  # Check if a color was selected (not None)
            self.current_color = color_code[1]

    def set_line_width(self, val):
        self.line_width = int(val)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("820x700")
    app = WhiteboardApp(root)
    root.mainloop()
