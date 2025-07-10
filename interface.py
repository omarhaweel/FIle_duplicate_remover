import tkinter as tk
from tkinter import filedialog, messagebox
from hasher import Hasher

root = tk.Tk()
root.title("Duplicate files remover")
root.geometry("400x200")
root.resizable(False, False)

entry_dir = tk.Entry(root, width=50)
entry_dir.grid(row=0, column=0, padx=10, pady=10)

hasher = Hasher(chunk_size=1024 * 1024)

btn_browse = tk.Button(root, text="Browse", command=lambda: entry_dir.insert(0, filedialog.askdirectory()))
btn_browse.grid(row=0, column=1, padx=10, pady=10)

btn_remove = tk.Button(root, text="Remove Duplicates", command=lambda: hasher.remove_duplicates(entry_dir.get()))
btn_remove.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
