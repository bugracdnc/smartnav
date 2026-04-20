import tkinter as tk
import subprocess

def press_left():
    # Uses xdotool to simulate a native Left Arrow key press
    subprocess.run(["xdotool", "key", "Left"])

def press_right():
    # Uses xdotool to simulate a native Right Arrow key press
    subprocess.run(["xdotool", "key", "Right"])

# --- Dragging Logic for the Frameless Window ---
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")

# --- Main Window Setup ---
root = tk.Tk()
root.title("SmartNav")
root.geometry("180x120")           # Size optimized for touch screens
root.attributes("-topmost", True)  # Forces window to be ALWAYS ON TOP
root.overrideredirect(True)        # Removes standard OS window borders/title bar

# --- Custom Title Bar (for dragging and closing) ---
title_bar = tk.Frame(root, bg="#595959", relief="raised", bd=0)
title_bar.pack(fill=tk.X)
title_bar.bind("<ButtonPress-1>", start_move)
title_bar.bind("<ButtonRelease-1>", stop_move)
title_bar.bind("<B1-Motion>", do_move)

# Close Button
close_button = tk.Button(title_bar, text="✕", command=root.destroy, bg="#e74c3c", fg="white", bd=0, padx=15, font=("Arial", 12, "bold"))
close_button.pack(side=tk.RIGHT)

# Drag Label
title_label = tk.Label(title_bar, text=" SmartNav", bg="#595959", fg="white", font=("Arial", 10))
title_label.pack(side=tk.LEFT, pady=2)
title_label.bind("<ButtonPress-1>", start_move)
title_label.bind("<B1-Motion>", do_move)

# --- Navigation Buttons ---
btn_frame = tk.Frame(root, bg="#bdc3c7")
btn_frame.pack(expand=True, fill=tk.BOTH)

# Left Button
btn_left = tk.Button(btn_frame, text="◀", command=press_left, font=("Arial", 40), bg="#ecf0f1", activebackground="#bdc3c7")
btn_left.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)

# Right Button
btn_right = tk.Button(btn_frame, text="▶", command=press_right, font=("Arial", 40), bg="#ecf0f1", activebackground="#bdc3c7")
btn_right.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)

root.mainloop()
