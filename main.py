from customtkinter import *
from tkinter import *
from PIL import Image 
import os
from JPEGEncoder import JPEGEncoder
import threading
compresselect = ""
filname = ""
decompresselect = ""
#encoder = JPEGEncoder()

def select_file():
    global compresselect
    global filname
    filename = filedialog.askopenfilename(
        initialdir="input_photos",  # Change this to your desired directory
        title="Select a file",
        filetypes=(("Image files", "*.bmp"), ("Image files", "*.png"), ("All files", "*.*"))  # Filter by file types
    )
    if filename:  # If a file is selected
        filname = os.path.basename(filename)
        label.configure(text=f"Selected: {os.path.basename(filename)}")
        compresselect = f"input_photos/{os.path.basename(filename)}"
        print(compresselect)

def select_file2():
    global filname
    global decompresselect
    filename = filedialog.askopenfilename(
        initialdir="compressed_photos",  # Change this to your desired directory
        title="Select a file",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))  # Filter by file types
    )
    if filename:  # If a file is selected
        filname = os.path.basename(filename)
        label2.configure(text=f"Selected: {os.path.basename(filename)}")
        decompresselect = f"compressed_photos/{os.path.basename(filename)}"
        print(decompresselect)

def start_encode():
    global compresselect
    encoder = JPEGEncoder()
    threading.Thread(target=encoder.encode, args=(compresselect, "compressed_photos", filname ), daemon=True).start()

def start_decode():
    global decompresselect
    encoder = JPEGEncoder()
    threading.Thread(target=encoder.decode, args=(decompresselect, "output_photos", filname ), daemon=True).start()

app = CTk()
app.geometry("500x400")
app.title("Custom semi-JPEG Compressor by shinju")

set_appearance_mode("dark")
set_default_color_theme("blue")
tabview = CTkTabview(master=app)

tabview.pack(padx=20, pady=20)

tabview.add("Compress Image")
tabview.add("Decompress Image")
tabview.add("Settings")




button = CTkButton(master=tabview.tab("Compress Image"), text="Select a File", command=select_file)
button.pack(pady=20)

label = CTkLabel(master=tabview.tab("Compress Image"), text="No file selected")
label.pack()

btn = CTkButton(master=tabview.tab("Compress Image"), text="compress", corner_radius=3, border_width=2, command=start_encode
                )
btn.pack()




button = CTkButton(master=tabview.tab("Decompress Image"), text="Select a File", command=select_file2)
button.pack(pady=20)

label2 = CTkLabel(master=tabview.tab("Decompress Image"), text="No file selected")
label2.pack()

btn = CTkButton(master=tabview.tab("Decompress Image"), text="decompress", corner_radius=3, border_width=2, command=start_decode
                )
btn.pack()

app.mainloop() 