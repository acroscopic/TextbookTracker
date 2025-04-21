#!/usr/bin/env python3

# Textbook Progress Tracker (TPT)

#         _            _        _       
#        /\ \         /\ \     /\ \     
#        \_\ \       /  \ \    \_\ \    
#        /\__ \     / /\ \ \   /\__ \   
#       / /_ \ \   / / /\ \_\ / /_ \ \  
#      / / /\ \ \ / / /_/ / // / /\ \ \ 
#     / / /  \/_// / /__\/ // / /  \/_/ 
#    / / /      / / /_____// / /        
#   / / /      / / /      / / /         
#  /_/ /      / / /      /_/ /          
#  \_\/       \/_/       \_\/           


# A Tkinter Application forked from tank321's Peskin-and-Schroeder-Tracker 
# Used to track progress through textbooks for academics or personal use
# Features:
# Multiple textbooks
# Semester/personal deadlines
# Page tracking
# Problem Completion
# indicators for progress status



###################### Imports ######################
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import date
import json
import os

###################### Textbook Class & Data Handling ######################
textbooks_file = "textbooks.json" # persistent textbook data storage

class Textbook:
    # Ccass to represent a textbook and its progress tracking data
    def __init__(self, name, author, total_pages, problems_dict, start_date, end_date, current_page=0):  # Modified
        # initialize textbook properties
        self.name = name
        self.author = author
        self.total_pages = total_pages
        self.current_page = current_page
        self.problems_dict = problems_dict
        self.start_date = start_date
        self.end_date = end_date
        self.completed_problems = {}

    def to_dict(self):
        # converts textbook to dictionary for json file
        return {
            "name": self.name,
            "author": self.author,
            "total_pages": self.total_pages,
            "current_page": self.current_page,
            "problems_dict": self.problems_dict,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "completed_problems": self.completed_problems
        }

    @classmethod
    def from_dict(cls, data):
        # creates textbook from dictionary
        return cls(
            data["name"],
            data["author"],
            data["total_pages"],
            data["problems_dict"],
            date.fromisoformat(data["start_date"]),
            date.fromisoformat(data["end_date"]),
            data["current_page"]
        )

def load_textbooks():
    # loads textbooks from textbooks.json
    if os.path.exists(textbooks_file):
        with open(textbooks_file, "r") as f:
            return [Textbook.from_dict(td) for td in json.load(f)]
    return [] # returns empty list if the file doesn't exist
              # file gets created, but not in this line

def save_textbooks(textbooks):
    # saves all textbooks to json file
    with open(textbooks_file, "w") as f:
        json.dump([t.to_dict() for t in textbooks], f)

###################### Core Functionality ######################


# window for adding new textbooks
def add_textbook_dialog():
    dialog = tk.Toplevel()
    dialog.title("Add New Textbook")
    entries = {}
    
    # input fields for name, author, pages, etc
    ttk.Label(dialog, text="Name:").grid(row=0, column=0)
    entries['name'] = ttk.Entry(dialog)
    entries['name'].grid(row=0, column=1)
    
    ttk.Label(dialog, text="Author:").grid(row=1, column=0)
    entries['author'] = ttk.Entry(dialog)
    entries['author'].grid(row=1, column=1)
    
    ttk.Label(dialog, text="Total Pages:").grid(row=2, column=0)
    entries['pages'] = ttk.Entry(dialog)
    entries['pages'].grid(row=2, column=1)
    
    ttk.Label(dialog, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0)
    entries['start'] = ttk.Entry(dialog)
    entries['start'].grid(row=3, column=1)
    
    ttk.Label(dialog, text="End Date (YYYY-MM-DD):").grid(row=4, column=0)
    entries['end'] = ttk.Entry(dialog)
    entries['end'].grid(row=4, column=1)
    

# form submission and validation, e.g. page numbers have to be int, dates have to be dates
    def parse_and_add():
        try:
            start_date = date.fromisoformat(entries['start'].get())
            end_date = date.fromisoformat(entries['end'].get())

            if start_date > end_date:
                raise ValueError("End date must be after start date")    

            problems = parse_problems(entries['problems'].get("1.0", tk.END))

            # new textbook instance
            new_textbook = Textbook(
                name=entries['name'].get(),
                author=entries['author'].get(),
                total_pages=int(entries['pages'].get()),
                problems_dict=problems,
                start_date=date.fromisoformat(entries['start'].get()),
                end_date=date.fromisoformat(entries['end'].get())
            )

            # updates the textbook
            textbooks.append(new_textbook)
            save_textbooks(textbooks)
            textbooks_list.insert(tk.END, new_textbook.name)
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    

    # chapter problem section
    ttk.Label(dialog, text="Chapters/Problems:").grid(row=5, column=0, columnspan=2)
    
    entries['problems'] = tk.Text(dialog, height=15, width=50, wrap=tk.NONE)
    entries['problems'].grid(row=6, column=0, columnspan=2, sticky='ew')
    
    # Formatting example for how to type in problems
    example = ttk.Label(
        dialog,
        text="Example format:\n"
             "Chapter 1\n"
             "1.1, 1.2a, 1.2b\n"
             "Chapter 2\n"
             "2.1, 2.2, 2.3, 2.4",
        foreground="#666666",
        font=("Spectral", 9)
    )
    example.grid(row=7, column=0, columnspan=2, sticky="w")

    # submit new textbook! 
    ttk.Button(dialog, text="Add", command=parse_and_add).grid(row=8, column=0, columnspan=2)


# converts csv text input 1.1, 1.2, 1.3, etc to a problem dictionary
def parse_problems(text):
    problems = {}
    current_chapter = None
    for line in text.strip().split('\n'):
        line = line.strip()
        # seperating Chapter i
        if line.lower().startswith("chapter "):
            current_chapter = line.split()[1]
            problems[current_chapter] = []
        # add problem to chapter    
        elif current_chapter and line:
            problems[current_chapter].extend([p.strip() for p in line.split(',')])
    return problems

# update progress indicators
def update_display():
    if not current_textbook:
        return
    
    # calculate date related stuff
    today = date.today()
    start = current_textbook.start_date
    end = current_textbook.end_date
    total_days = (end - start).days
    days_elapsed = max(0, (today - start).days) if start <= today else 0
    days_left = max(0, (end - today).days) if today <= end else 0
    
    # update progress bars
    semester_progress['value'] = (days_elapsed / total_days * 100) if total_days else 0
    textbook_progress['value'] = (current_textbook.current_page / current_textbook.total_pages * 100) if current_textbook.total_pages else 0
    
    # update labels
    title_label.config(text=f"{current_textbook.name} by {current_textbook.author}")
    semester_label.config(text=f"Timeframe: {days_elapsed}/{total_days} days ({semester_progress['value']:.1f}%)")
    textbook_label.config(text=f"Pages: {current_textbook.current_page}/{current_textbook.total_pages} ({textbook_progress['value']:.1f}%)")
    
    # calculate reading pace
    if days_left > 0:
        pages_needed = current_textbook.total_pages - current_textbook.current_page
        pages_per_day_label.config(text=f"Required pace: {pages_needed / days_left:.2f} pages/day")
    else:
        pages_per_day_label.config(text="")
    
    update_tree() # refresh

def update_tree():
    tree.delete(*tree.get_children()) # clear existing items
    if not current_textbook:
        return
    
    # sort chapters
    for chap in sorted(current_textbook.problems_dict, key=lambda x: int(x)):
        # create parent item for chapter
        parent = tree.insert("", tk.END, text=f"Chapter {chap}", open=False)
        # create child item for problems
        for prob in current_textbook.problems_dict[chap]:
            status = " ✓" if prob in current_textbook.completed_problems else ""
            tree.insert(parent, tk.END, text=f"{prob}{status}", values=(prob,))

# problem completion status
def mark_problem(complete=True):
    if not current_textbook:
        return
    
    # process selected item
    for item in tree.selection():
        if tree.parent(item): # don't process chapters
            # update this in the future, add a way to process chapters
            prob = tree.item(item, "values")[0]
            if complete:
                current_textbook.completed_problems[prob] = {"complete": True}
            else:
                current_textbook.completed_problems.pop(prob, None)
    
    save_textbooks(textbooks) # persistence
    update_tree() # refresh

# update page number
def update_page():
    if current_textbook and page_entry.get().isdigit():
        try:
            new_page = int(page_entry.get())
            if 0 <= new_page <= current_textbook.total_pages:
                current_textbook.current_page = new_page
                save_textbooks(textbooks)  # explicit save after update
                update_display() #refresh
        except ValueError:
            pass # ignore non integer values


# textbook selection
def on_select(event):
    global current_textbook
    selection = textbooks_list.curselection()
    if selection:
        current_textbook = textbooks[selection[0]]
        page_entry.delete(0, tk.END)
        page_entry.insert(0, str(current_textbook.current_page))
        update_display()



def delete_textbook():
    selection = textbooks_list.curselection()
    if not selection:
        messagebox.showinfo("Error", "No textbook selected")
        return
    
    index = selection[0]
    textbook_name = textbooks_list.get(index)
    
    # confirmation dialog
    confirm = messagebox.askyesno(
        "Confirm Delete", 
        f"Are you sure you want to delete '{textbook_name}'?\nThis will permanently remove all associated data!"
    )
    if not confirm:
        return
    
    # remove from list and update UI
    textbooks.pop(index)
    textbooks_list.delete(index)
    save_textbooks(textbooks)
    
    # clear display if deleted textbook was selected
    global current_textbook
    if current_textbook and current_textbook.name == textbook_name:
        current_textbook = None
        clear_display()
    
    # select next textbook
    if textbooks:
        new_index = min(index, len(textbooks)-1)
        textbooks_list.selection_set(new_index)
        textbooks_list.event_generate("<<ListboxSelect>>")

# clear all progress indicators
def clear_display():
    
    title_label.config(text="")
    semester_label.config(text="")
    textbook_label.config(text="")
    pages_per_day_label.config(text="")
    semester_progress['value'] = 0
    textbook_progress['value'] = 0
    tree.delete(*tree.get_children())
    page_entry.delete(0, tk.END)



###################### GUI Setup ######################
# creates main window
root = tk.Tk()
root.title("Textbook Progress Tracker")
root.geometry("800x750")
root.configure(bg="#f0f0f0")

###################### Sidebar Frame ######################
sidebar_frame = ttk.Frame(root, width=200, padding=10)
sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

# textbook list
textbooks_list = tk.Listbox(sidebar_frame)
textbooks_list.pack(fill=tk.BOTH, expand=True, pady=5)

# button container
btn_container = ttk.Frame(sidebar_frame)  # ▲ New container for buttons
btn_container.pack(pady=5)

# action buttons
add_textbook_btn = ttk.Button(btn_container, text="Add", command=lambda: add_textbook_dialog())
add_textbook_btn.pack(side=tk.LEFT, padx=2)
delete_textbook_btn = ttk.Button(btn_container, text="Delete", command=delete_textbook)
delete_textbook_btn.pack(side=tk.LEFT, padx=2)

###################### Main Content Frame ######################
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# nitialize current textbook
current_textbook = None

###################### Progress Section ######################
progress_frame = ttk.Frame(main_frame, padding=10)
progress_frame.pack(fill=tk.X)

# title display settings
title_label = ttk.Label(progress_frame, text="", font=("Spectral", 16, "bold"))
title_label.pack(pady=10)

# timeframe progress
semester_label = ttk.Label(progress_frame, text="", font=("Spectral", 12))
semester_label.pack(anchor="w")
semester_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500)
semester_progress.pack(pady=5, anchor="w")

# page progress
textbook_label = ttk.Label(progress_frame, text="", font=("Spectral", 12))
textbook_label.pack(anchor="w")
textbook_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500)
textbook_progress.pack(pady=5, anchor="w")

# reading pace
pages_per_day_label = ttk.Label(progress_frame, text="", font=("Spectral", 12))
pages_per_day_label.pack(anchor="w")


# page input section
entry_frame = ttk.Frame(progress_frame)
entry_frame.pack(pady=10)
ttk.Label(entry_frame, text="Current Page:").pack(side=tk.LEFT)
page_entry = ttk.Entry(entry_frame, width=8)
page_entry.pack(side=tk.LEFT, padx=5)
update_btn = ttk.Button(entry_frame, text="Update", command=lambda: [update_page(), update_display()])
update_btn.pack(side=tk.LEFT)

###################### Problem Tracker ######################
problems_frame = ttk.LabelFrame(main_frame, text="Problems", padding=10)
problems_frame.pack(fill=tk.BOTH, expand=True)

# treeview widget
tree = ttk.Treeview(problems_frame, show="tree")
tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


# problem action buttons
button_frame = ttk.Frame(problems_frame)
button_frame.pack(pady=5)
ttk.Button(button_frame, text="Mark Problem Complete", command=lambda: mark_problem(True)).pack(side=tk.LEFT, padx=2)
ttk.Button(button_frame, text="Mark Problem Incomplete", command=lambda: mark_problem(False)).pack(side=tk.LEFT, padx=2)



###################### Initialization ######################

textbooks = load_textbooks()
for textbook in textbooks:
    textbooks_list.insert(tk.END, textbook.name)

# textbook selection
textbooks_list.bind("<<ListboxSelect>>", on_select)
if textbooks:
    textbooks_list.selection_set(0)
    on_select(None) # initial display

# runs the program
root.mainloop()
