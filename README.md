# File Duplicate Remover

A lightweight Python application to identify and remove duplicate files in a selected directory using a secure content-based comparison.

---

## 📄 Description

This program identifies duplicate files in two phases:

1. **Grouping by File Size**  
   Files are first grouped based on their size. This is a fast way to eliminate obviously non-duplicate files.

2. **Hashing for Content Comparison**  
   Files with the same size are then hashed using SHA-256. This ensures that two files with the same size and the same hash truly have identical content — making the comparison both efficient and reliable.

This two-step process ensures accurate and secure duplicate detection.

---

## 🖥️ Interface

The program includes a minimal Tkinter GUI where you can:
- Browse and select a directory
- Click a button to remove duplicate files from the selected directory

> 💡 Future versions will enhance the interface to improve user experience.

---

## ▶️ Run the Program

```bash
python3 interface.py
