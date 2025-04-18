#!/usr/bin/env python3
"""
QFT Progress Tracker

A Tkinter application for tracking progress through Peskin & Schroeder's "Quantum Field Theory" textbook.
Features include:
- Semester progress tracking
- Textbook page tracking
- Problem completion tracking
- Document upload and management for completed problems
- Visual indicators for progress status
"""

import os
import json
import shutil
import subprocess
from datetime import date
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ------------------ Configuration ------------------ #
# Modify these settings based on your needs
SEMESTER_START = date(2025, 1, 13)
SEMESTER_END = date(2025, 5, 9)
TOTAL_PAGES = 258
INITIAL_PAGE = 0  # Default if no saved page exists

# ------------------ File Paths ------------------ #
COMPLETED_FILE = "completed_problems.json"
UPLOAD_DIR = "uploaded_documents"
CONFIG_FILE = "tracker_config.json"

# ------------------ Data Structures ------------------ #
# Dictionary of chapters and their associated problems
all_problems_dict = {
    "2": ["2.1a", "2.1b", "2.2a", "2.2b", "2.2c", "2.2d", "2.3"],
    "3": ["3.1a", "3.1b", "3.1c", "3.2", "3.3a", "3.3b", "3.3c", "3.4a", "3.4b", "3.4c", "3.4d", "3.4e", "3.5a", "3.5b", "3.5c", "3.6a", "3.6b", "3.6c", "3.7a", "3.7b", "3.7c", "3.8a", "3.8b"],
    "4": ["4.1a", "4.1b", "4.1c", "4.1d", "4.1e", "4.1f", "4.2", "4.3a", "4.3b", "4.3c", "4.3d", "4.4a", "4.4b", "4.4c"],
    "5": ["5.1", "5.2", "5.3a", "5.3b", "5.3c", "5.3d", "5.3e", "5.4a", "5.4b", "5.4c", "5.4d", "5.5a", "5.5b", "5.5c", "5.6a", "5.6b"],
    "6": ["6.1", "6.2a", "6.2b", "6.2c", "6.2d", "6.2e", "6.3a", "6.3b", "6.3c", "6.10"],
    "7": ["7.1", "7.2a", "7.2b", "7.3a", "7.3b"]
}

# ------------------ Data Management Functions ------------------ #
def load_completed_problems():
    """
    Load completed problems from a local JSON file.
    
    Returns:
        dict: Dictionary of completed problems with their attributes.
              Empty dictionary if file doesn't exist or has invalid format.
    """
    if os.path.exists(COMPLETED_FILE):
        try:
            with open(COMPLETED_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Handle legacy format (list) and convert to dictionary
                    return {prob: {"complete": True, "document": None} for prob in data}
                elif isinstance(data, dict):
                    return data
                else:
                    print("Warning: Invalid data format in completed problems file")
                    return {}
        except json.JSONDecodeError:
            print("Warning: Could not decode completed problems file")
            return {}
        except Exception as e:
            print(f"Error loading completed problems: {e}")
            return {}
    else:
        # File doesn't exist yet
        return {}

def save_completed_problems(data):
    """
    Save completed problems to a local JSON file.
    
    Args:
        data (dict): Dictionary of completed problems with their attributes
    """
    try:
        with open(COMPLETED_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save progress: {e}")

def load_config():
    """
    Load configuration settings from a local JSON file.
    
    Returns:
        dict: Dictionary containing configuration settings.
              Default configuration if file doesn't exist or has invalid format.
    """
    default_config = {
        "current_page": INITIAL_PAGE
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure all expected keys exist
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except json.JSONDecodeError:
            print("Warning: Could not decode config file")
            return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    else:
        # File doesn't exist yet, create it with defaults
        save_config(default_config)
        return default_config

def save_config(config):
    """
    Save configuration settings to a local JSON file.
    
    Args:
        config (dict): Dictionary containing configuration settings
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save configuration: {e}")

# ------------------ UI Update Functions ------------------ #
def update_treeview():
    """
    Populate the treeview with chapters and problems.
    Mark completed problems and show document status.
    """
    tree.delete(*tree.get_children())
    for chapter in sorted(all_problems_dict, key=lambda x: int(x)):
        chapter_item = tree.insert("", "end", text=f"Chapter {chapter}", open=False)
        for prob in all_problems_dict[chapter]:
            display_text = prob
            if prob in completed_problems and completed_problems[prob].get("complete"):
                display_text += "  ✓"
                if completed_problems[prob].get("document"):
                    display_text += " (doc)"
            tree.insert(chapter_item, "end", text=display_text, values=(prob,))

def update_widget():
    """
    Update all progress indicators in the UI:
    - Progress bars
    - Status labels
    - Progress calculations
    
    Schedules itself to run every minute to keep the UI updated.
    """
    global current_page
    today = date.today()
    
    # Calculate semester progress
    if today < SEMESTER_START:
        days_elapsed = 0
        days_left = TOTAL_SEMESTER_DAYS
    elif today > SEMESTER_END:
        days_elapsed = TOTAL_SEMESTER_DAYS
        days_left = 0
    else:
        days_elapsed = (today - SEMESTER_START).days
        days_left = (SEMESTER_END - today).days

    # Calculate percentages and expected progress
    semester_percentage = (days_elapsed / TOTAL_SEMESTER_DAYS) * 100
    textbook_percentage = (current_page / TOTAL_PAGES) * 100
    expected_page = (days_elapsed / TOTAL_SEMESTER_DAYS) * TOTAL_PAGES
    page_diff = current_page - expected_page

    # Calculate pages per day needed to complete on time
    remaining_pages = TOTAL_PAGES - current_page
    if days_left > 0:
        pages_per_day = remaining_pages / days_left
        pages_per_day_text = f"You need to read {pages_per_day:.2f} page(s) per day."
    else:
        pages_per_day_text = "Semester is over."

    # Update UI elements
    semester_label.config(text=f"Semester: {semester_percentage:.2f}% complete, {days_left} day(s) left")
    textbook_label.config(text=f"Textbook: {textbook_percentage:.2f}% complete ({current_page}/{TOTAL_PAGES})")
    expected_label.config(text=f"Expected Page: {expected_page:.0f}")
    
    # Set color and text for progress comparison
    if abs(page_diff) < 1:
        diff_text = "On track!"
        color = "black"
    elif page_diff < 0:
        diff_text = f"{abs(page_diff):.0f} page(s) behind schedule"
        color = "red"
    else:
        diff_text = f"{page_diff:.0f} page(s) ahead of schedule"
        color = "green"
    diff_label.config(text=diff_text, foreground=color)
    pages_per_day_label.config(text=pages_per_day_text)

    # Update progress bars
    semester_progress['value'] = semester_percentage
    textbook_progress['value'] = textbook_percentage
    semester_progress['maximum'] = 100
    textbook_progress['maximum'] = 100

    # Refresh UI
    update_treeview()
    
    # Schedule next update
    root.after(60000, update_widget)  # Update every minute

def update_page():
    """
    Update the current page from the entry widget.
    Validates input to ensure it's a valid integer within range.
    Saves the updated page to the configuration file.
    """
    global current_page
    try:
        new_page = int(page_entry.get())
        if 0 <= new_page <= TOTAL_PAGES:
            current_page = new_page
            
            # Save the updated page to configuration
            config = load_config()
            config["current_page"] = current_page
            save_config(config)
            
            # Update UI to reflect changes
            update_widget()
        else:
            messagebox.showwarning("Invalid Input", f"Page number must be between 0 and {TOTAL_PAGES}")
            page_entry.delete(0, tk.END)
            page_entry.insert(0, str(current_page))
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid number")
        page_entry.delete(0, tk.END)
        page_entry.insert(0, str(current_page))

# ------------------ Problem Management Functions ------------------ #
def mark_problem(mark_complete=True):
    """
    Mark the selected problem as complete or incomplete.
    
    Args:
        mark_complete (bool): True to mark as complete, False to mark as incomplete
    """
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("No Selection", "Please select a problem first.")
        return
        
    changes_made = False
    for item in selected:
        parent = tree.parent(item)
        if parent:  # ensure it's a problem, not a chapter
            prob_text = tree.item(item, "text").split()[0]
            if mark_complete:
                current_data = completed_problems.get(prob_text, {})
                current_data["complete"] = True
                if "document" not in current_data:
                    current_data["document"] = None
                completed_problems[prob_text] = current_data
                changes_made = True
            else:
                if prob_text in completed_problems:
                    del completed_problems[prob_text]
                    changes_made = True
    
    if changes_made:
        save_completed_problems(completed_problems)
        update_treeview()

def upload_document():
    """
    Allow the user to upload a file for the selected problem and save its location.
    Creates a copy of the file in the uploads directory.
    """
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("No Selection", "Please select a problem first.")
        return
        
    # Only process the first selected item
    item = selected[0]
    if not tree.parent(item):
        messagebox.showinfo("Selection Error", "Please select a problem, not a chapter.")
        return
        
    prob = tree.item(item, "text").split()[0]
    
    # Check if problem is marked as complete
    if prob not in completed_problems or not completed_problems[prob].get("complete"):
        messagebox.showinfo("Not Complete", "Please mark the problem as complete before uploading a document.")
        return
        
    # Get file from user
    file_path = filedialog.askopenfilename(
        title="Select Document",
        filetypes=[("PDF Files", "*.pdf"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    
    if not file_path:
        return  # User canceled
        
    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Copy file to uploads directory with problem number as filename
    ext = os.path.splitext(file_path)[1]
    new_filename = f"{prob}{ext}"
    destination = os.path.join(UPLOAD_DIR, new_filename)
    
    try:
        shutil.copy(file_path, destination)
        completed_problems[prob]["document"] = destination
        save_completed_problems(completed_problems)
        messagebox.showinfo("Upload Successful", f"Document uploaded for problem {prob}.")
        update_treeview()
    except Exception as e:
        messagebox.showerror("Upload Error", f"Failed to upload document: {e}")

def open_document():
    """
    Open the document associated with the selected completed problem.
    Uses the system's default application to open the file.
    """
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("No Selection", "Please select a problem first.")
        return
        
    # Only process the first selected item
    item = selected[0]
    if not tree.parent(item):
        messagebox.showinfo("Selection Error", "Please select a problem, not a chapter.")
        return
        
    prob = tree.item(item, "text").split()[0]
    
    if prob in completed_problems:
        doc_path = completed_problems[prob].get("document")
        if doc_path and os.path.exists(doc_path):
            try:
                # Use platform-appropriate method to open the file
                if os.name == 'posix':  # Linux/Mac
                    subprocess.call(["xdg-open", doc_path])
                elif os.name == 'nt':   # Windows
                    os.startfile(doc_path)
                else:
                    messagebox.showinfo("Platform Error", "File opening not supported on this platform.")
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open document: {e}")
        else:
            messagebox.showinfo("No Document", f"No document found for problem {prob}.")
    else:
        messagebox.showinfo("Not Complete", f"Problem {prob} is not marked complete.")

# ------------------ Main Application ------------------ #
if __name__ == "__main__":
    # Initialize data
    completed_problems = load_completed_problems()
    config = load_config()
    current_page = config.get("current_page", INITIAL_PAGE)
    TOTAL_SEMESTER_DAYS = (SEMESTER_END - SEMESTER_START).days
    
    # Create and configure root window
    root = tk.Tk()
    root.title("QFT Progress Tracker")
    root.geometry("600x750")
    root.attributes("-topmost", True)
    root.configure(bg="#f0f0f0")
    
    # Create UI components
    title_label = ttk.Label(root, text="QFT Extravaganza!", font=("Helvetica", 20, "bold"))
    title_label.pack(pady=15)
    
    # Progress Frame
    progress_frame = ttk.Frame(root, padding=10, relief="groove")
    progress_frame.pack(pady=10, padx=10, fill="x")
    
    semester_label = ttk.Label(progress_frame, text="", font=("Arial", 12))
    semester_label.pack(pady=5, anchor="w")
    semester_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
    semester_progress.pack(pady=5, anchor="w")
    
    textbook_label = ttk.Label(progress_frame, text="", font=("Arial", 12))
    textbook_label.pack(pady=5, anchor="w")
    textbook_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
    textbook_progress.pack(pady=5, anchor="w")
    
    expected_label = ttk.Label(progress_frame, text="", font=("Arial", 12))
    expected_label.pack(pady=5, anchor="w")
    diff_label = ttk.Label(progress_frame, text="", font=("Arial", 12))
    diff_label.pack(pady=5, anchor="w")
    pages_per_day_label = ttk.Label(progress_frame, text="", font=("Arial", 12))
    pages_per_day_label.pack(pady=5, anchor="w")
    
    entry_frame = ttk.Frame(progress_frame)
    entry_frame.pack(pady=10, anchor="w")
    ttk.Label(entry_frame, text="Current Page:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 5))
    page_entry = ttk.Entry(entry_frame, width=8, font=("Arial", 12))
    page_entry.pack(side=tk.LEFT)
    page_entry.insert(0, str(current_page))
    update_btn = ttk.Button(entry_frame, text="Update", command=update_page)
    update_btn.pack(side=tk.LEFT, padx=5)
    
    # Problems Frame
    problems_frame = ttk.LabelFrame(root, text="Peskin & Schroeder Part 1: Problems", padding=10)
    problems_frame.pack(pady=10, padx=10, fill="both", expand=True)
    
    tree = ttk.Treeview(problems_frame)
    tree.heading("#0", text="Chapter / Problem", anchor="w")
    tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    button_frame = ttk.Frame(problems_frame)
    button_frame.pack(pady=5)
    mark_complete_btn = ttk.Button(button_frame, text="Mark as Complete", command=lambda: mark_problem(True))
    mark_complete_btn.pack(side=tk.LEFT, padx=5)
    mark_incomplete_btn = ttk.Button(button_frame, text="Mark as Incomplete", command=lambda: mark_problem(False))
    mark_incomplete_btn.pack(side=tk.LEFT, padx=5)
    upload_btn = ttk.Button(button_frame, text="Upload Document", command=lambda: upload_document())
    upload_btn.pack(side=tk.LEFT, padx=5)
    open_doc_btn = ttk.Button(button_frame, text="Open Document", command=lambda: open_document())
    open_doc_btn.pack(side=tk.LEFT, padx=5)
    
    # Initialize UI
    update_widget()
    
    # Start main loop
    root.mainloop()
