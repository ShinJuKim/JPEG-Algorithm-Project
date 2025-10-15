import customtkinter as tk
from customtkinter import filedialog

def select_file():
    filename = filedialog.askopenfilename(
        initialdir="compressed_photos",  # Change this to your desired directory
        title="Select a file",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))  # Filter by file types
    )
    if filename:  # If a file is selected
        label.configure(text=f"Selected: {filename}")

root = tk.CTk()
root.title("File Selector")

button = tk.CTkButton(root, text="Select a File", command=select_file)
button.pack(pady=20)

label = tk.CTkLabel(root, text="No file selected")
label.pack()

root.mainloop()
