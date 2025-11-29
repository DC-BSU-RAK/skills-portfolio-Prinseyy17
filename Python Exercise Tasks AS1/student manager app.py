import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

# ============================
# Load Student Data
# ============================
# Path to the data file (use a raw string for Windows backslashes)
STUDENT_FILE = Path(r"C:\Users\Kier\Desktop\Class Stuff\Codelab II\studentMarks.txt")

def load_students():
    students = []
    # If file missing, show an error dialog and return empty list
    if not STUDENT_FILE.exists():
        messagebox.showerror("Error", f"{STUDENT_FILE} not found")
        return students

    # Open the file with utf-8 encoding to be safe for names / special chars
    with STUDENT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            # Strip newline and split by comma expecting 6 fields per line
            parts = line.strip().split(",")
            if len(parts) != 6:
                # If the line doesn't have the expected format, skip it
                continue

            sid = parts[0]
            name = parts[1]
            # coursework components c1..c3 and exam are numeric – convert to int
            c1, c2, c3 = map(int, parts[2:5])
            exam = int(parts[5])

            # Total coursework is sum of three coursework marks (max 60)
            total_course = c1 + c2 + c3
            # Total marks includes coursework + exam (exam max 100)
            total_marks = total_course + exam
            # Percent calculation: total maximum marks = 60 (coursework) + 100 (exam) = 160
            percent = (total_marks / 160) * 100

            # Simple grade boundaries based on percent
            if percent >= 70:
                grade = "A"
            elif percent >= 60:
                grade = "B"
            elif percent >= 50:
                grade = "C"
            elif percent >= 40:
                grade = "D"
            else:
                grade = "F"

            # Append a dictionary per student for easy access later
            students.append({
                "id": sid,
                "name": name,
                "course": total_course,
                "exam": exam,
                "percent": percent,
                "grade": grade
            })

    return students

students = load_students()

# ============================
# Table Handling
# ============================
def clear_table():
    # Remove all existing rows in the Treeview table
    for row in table.get_children():
        table.delete(row)

def insert_student_row(s):
    # Insert a single row into the table.
    # Note: coursework displayed as e.g. "45/60" and exam as "78/100".
    # percent is shown to 1 decimal place followed by '%' sign.
    table.insert("", "end", values=(
        s["id"],
        s["name"],
        f"{s['course']}/60",
        f"{s['exam']}/100",
        f"{s['percent']:.1f}%",
        s["grade"]
    ))

# ============================
# Button Actions
# ============================
def view_all():
    clear_table()
    for s in students:
        insert_student_row(s)

def view_selected_dropdown():
    # Get selected name from OptionMenu's variable
    name = dropdown_var.get()
    clear_table()
    # Find the first student with matching name and display only that row
    for s in students:
        if s["name"] == name:
            insert_student_row(s)
            return

def view_highest():
    clear_table()
    # Use max with a key function to get student with highest percent
    top = max(students, key=lambda s: s["percent"])
    insert_student_row(top)

def view_lowest():
    clear_table()
    # Use min with a key function to get student with lowest percent
    low = min(students, key=lambda s: s["percent"])
    insert_student_row(low)

# ============================
# UI Setup (Modern + Minimal)
# ============================
window = tk.Tk()
window.title("Student Manager")
window.geometry("780x650")
window.resizable(False, False)

# Gradient Canvas
canvas = tk.Canvas(window, width=780, height=650, highlightthickness=0)
canvas.pack(fill="both", expand=True)

def draw_gradient(c, col1, col2):
    # Draw a vertical gradient by drawing many 1px horizontal lines.
    # c.winfo_rgb returns 16-bit RGB (0..65535) for each component.
    # We interpolate each component between col1 and col2 over 650 steps,
    # then shift right by 8 bits to convert 16-bit -> 8-bit for hex formatting.
    for i in range(650):
        r1, g1, b1 = c.winfo_rgb(col1)
        r2, g2, b2 = c.winfo_rgb(col2)
        # Linear interpolation for each color channel
        r = (r1 + (r2 - r1) * i // 650) >> 8
        g = (g1 + (g2 - g1) * i // 650) >> 8
        b = (b1 + (b2 - b1) * i // 650) >> 8
        # Draw 1-pixel-high line with the computed color
        c.create_line(0, i, 780, i, fill=f"#{r:02x}{g:02x}{b:02x}")

# Create a smooth gradient background between two hex colors
draw_gradient(canvas, "#141E30", "#243B55")

# Card Container
# Use a Frame as a centered "card" on top of the gradient canvas.
frame = tk.Frame(canvas, bg="#1f1f2e")
# place the frame in the canvas at center (create_window packs a widget into canvas coords)
canvas.create_window(390, 320, window=frame, width=700, height=580)

# Title label with custom font and colors
tk.Label(frame, text="Student Manager", font=("Poppins", 22, "bold"),
         fg="#00FFFF", bg="#1f1f2e").pack(pady=15)

# ============================
# TABLE (Grid Output)
# ============================
table_frame = tk.Frame(frame, bg="#1f1f2e")
table_frame.pack(pady=10)

columns = ("ID", "Name", "Coursework", "Exam", "Percent", "Grade")
# Treeview is a lightweight table widget; show="headings" hides the default first column
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

# Configure headings and column widths/alignments
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=110, anchor="center")

# Scrollbar: connect vertical scrolling to the Treeview
scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscroll=scroll.set)
scroll.pack(side="right", fill="y")
table.pack()

# ============================
# Buttons
# ============================
def hover_in(e):
    # Change background on mouse enter (e.widget is the Button)
    e.widget.config(bg="#666")

def hover_out(e, color):
    # Restore original background on mouse leave
    e.widget.config(bg=color)

def make_btn(text, color, cmd):
    # Factory to create consistent buttons with hover effects
    btn = tk.Button(frame, text=text, command=cmd, bg=color, fg="white",
                    font=("Poppins", 12, "bold"), width=25, height=2, relief="flat")
    btn.pack(pady=8)
    # Bind hover events
    btn.bind("<Enter>", hover_in)
    btn.bind("<Leave>", lambda e: hover_out(e, color))
    return btn

# Primary action buttons
make_btn("View All Students", "#4caf50", view_all)
make_btn("Highest Score", "#ff9800", view_highest)
make_btn("Lowest Score", "#f44336", view_lowest)

# Dropdown (OptionMenu) to select a student by name.
# The OptionMenu will call view_selected_dropdown when a selection changes.
dropdown_var = tk.StringVar()
dropdown_var.set("Select Student")
names = [s["name"] for s in students]

ttk.OptionMenu(frame, dropdown_var, "Select Student", *names,
               command=lambda _: view_selected_dropdown()).pack(pady=20)

# Quit button — uses window.destroy to close the app
make_btn("Quit", "#777", window.destroy)

window.mainloop()
