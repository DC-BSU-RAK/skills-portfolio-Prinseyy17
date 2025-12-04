import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

# -----------------------------
# Styling / Constants
# -----------------------------
BG_COLOR = "#1E1E2F"
CARD_COLOR = "#2E2E44"
BTN_COLOR = "#4E9F3D"
BTN_HOVER = "#3E8C2E"
TEXT_COLOR = "#FFFFFF"

FONT_MAIN = ("Poppins", 16)
FONT_TITLE = ("Poppins", 20, "bold")
FONT_BTN = ("Poppins", 12, "bold")

QUESTIONS_TOTAL = 10


class QuizApp:
    def __init__(self):
        # Quiz state
        self.difficulty = 1
        self.score = 0
        self.question_number = 0
        self.first_attempt = True
        self.num1 = 0
        self.num2 = 0
        self.operation = "+"
        self.answer_entry = None
        self.current_progress = None

        # Timer / animation state
        self.timer_seconds = 0
        self.timer_total = 1.0
        self.timer_remaining = 0.0
        self.timer_job = None
        self.timer_label = None
        self.timer_canvas = None
        self.timer_arc = None

        # Build UI
        self.window = tk.Tk()
        self.window.title("Maths Quiz")
        self.window.geometry("500x550")
        self.window.resizable(False, False)
        self.window.config(bg=BG_COLOR)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            troughcolor=BG_COLOR,
            background="#4E9F3D",
            bordercolor=BG_COLOR,
            lightcolor="#4E9F3D",
            darkcolor="#4E9F3D",
        )

        self.frame = tk.Frame(self.window, bg=CARD_COLOR, bd=2, relief="ridge")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=500)

        self.timer_label = tk.Label(
            self.window,
            text="Time: --",
            font=("Poppins", 12, "bold"),
            fg="#FFD700",
            bg=BG_COLOR,
        )
        self.timer_label.place(relx=0.88, rely=0.04, anchor="center")

        # Global Enter binding
        self.window.bind("<Return>", self.check_answer)

    # ---------- UI helpers ----------
    def make_button(self, text, command):
        btn = tk.Button(
            self.frame,
            text=text,
            font=FONT_BTN,
            fg="white",
            bg=BTN_COLOR,
            activebackground=BTN_HOVER,
            activeforeground="white",
            relief="flat",
            width=25,
            pady=10,
            command=command,
        )
        btn.pack(pady=8)
        return btn

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def create_header(self, title_text):
        tk.Label(
            self.frame,
            text=title_text,
            font=("Poppins", 22, "bold"),
            fg="#00FFFF",
            bg=CARD_COLOR,
        ).pack(pady=10)

    # ---------- Timer / Canvas ----------
    # This was created to provide a visual countdown timer using a canvas arc.
    # The timer counts down from a set number of seconds, updating both a label and the arc.
    # When time runs out, it triggers the on_timeout method.
    # The timer can be reset and started as needed for each question.
    # The arc shrinks clockwise to indicate remaining time visually.
    # This was helped made by AI assistance.
    def create_timer_canvas(self):
        if self.timer_canvas:
            try:
                self.timer_canvas.destroy()
            except Exception:
                pass

        self.timer_canvas = tk.Canvas(
            self.window, width=60, height=60, bg=BG_COLOR, highlightthickness=0
        )
        self.timer_canvas.place(relx=0.88, rely=0.13, anchor="center")
        self.timer_canvas.create_oval(5, 5, 55, 55, outline="#444444", width=4)
        self.timer_arc = self.timer_canvas.create_arc(
            5, 5, 55, 55, start=90, extent=359.9, style="arc", outline="#FFD700", width=4
        )

    def timer_set(self, seconds):
        self.timer_seconds = int(seconds)
        self.timer_total = float(seconds)
        self.timer_remaining = float(seconds)
        if self.timer_label:
            self.timer_label.config(text=f"Time: {max(0, math.ceil(self.timer_remaining))}s")
        self.create_timer_canvas()

    def timer_cancel(self):
        if self.timer_job:
            try:
                self.window.after_cancel(self.timer_job)
            except Exception:
                pass
        self.timer_job = None

    def timer_start(self):
        self.timer_cancel()

        if self.timer_total <= 0:
            self.timer_remaining = 0.0
            if self.timer_label:
                self.timer_label.config(text="Time: 0s")
            self.on_timeout()
            return

        def animate():
            self.timer_remaining -= 0.05
            if self.timer_remaining < 0:
                self.timer_remaining = 0.0

            if self.timer_label:
                self.timer_label.config(text=f"Time: {max(0, math.ceil(self.timer_remaining))}s")

            if self.timer_canvas and self.timer_arc is not None:
                fraction = self.timer_remaining / self.timer_total if self.timer_total > 0 else 0
                extent = max(0, 360 * fraction)
                try:
                    # negative extent to animate clockwise shrinking
                    self.timer_canvas.itemconfig(self.timer_arc, extent=-extent)
                except Exception:
                    pass

            if self.timer_remaining <= 0:
                self.timer_job = None
                self.on_timeout()
                return

            self.timer_job = self.window.after(50, animate)

        animate()

    def on_timeout(self):
        self.timer_cancel()
        if self.first_attempt:
            self.first_attempt = False
            messagebox.showwarning("Time's up", "Time's up! One more try.")
            if self.answer_entry:
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.focus()
            secs = {1: 10, 2: 20, 3: 30}.get(self.difficulty, 10)
            self.timer_set(secs)
            self.timer_start()
        else:
            messagebox.showinfo("Time's up", "Time's up! Moving to the next question.")
            self.timer_cancel()
            self.next_question()

    # ---------- Quiz logic ----------
    def display_menu(self):
        self.clear_frame()
        self.create_header("🧮 MATHS QUIZ 🧠")
        tk.Label(
            self.frame,
            text="Select Difficulty Level",
            font=FONT_TITLE,
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
        ).pack(pady=20)

        self.make_button("1. Easy (Single-digit)", lambda: self.start_quiz(1))
        self.make_button("2. Moderate (Double-digit)", lambda: self.start_quiz(2))
        self.make_button("3. Advanced (Four-digit)", lambda: self.start_quiz(3))

    @staticmethod
    def random_int(difficulty_level):
        if difficulty_level == 1:
            return random.randint(1, 9), random.randint(1, 9)
        if difficulty_level == 2:
            return random.randint(10, 99), random.randint(10, 99)
        return random.randint(1000, 9999), random.randint(1000, 9999)

    @staticmethod
    def decide_operation():
        return random.choice(["+", "-"])

    def start_quiz(self, level):
        self.difficulty = level
        self.score = 0
        self.question_number = 0
        self.first_attempt = True
        self.next_question()

    def next_question(self):
        self.timer_cancel()

        if self.question_number >= QUESTIONS_TOTAL:
            self.display_results()
            return

        self.clear_frame()
        self.create_header("🧮 MATHS QUIZ 🧠")

        progress = ttk.Progressbar(self.frame, orient="horizontal", length=300, mode="determinate")
        progress["value"] = int((self.question_number / QUESTIONS_TOTAL) * 100)
        progress["maximum"] = 100
        progress.pack(pady=10)
        self.current_progress = progress

        self.first_attempt = True
        self.question_number += 1
        self.num1, self.num2 = self.random_int(self.difficulty)
        self.operation = self.decide_operation()

        tk.Label(
            self.frame,
            text=f"Question {self.question_number} of {QUESTIONS_TOTAL}",
            font=("Poppins", 14),
            fg="#BBBBBB",
            bg=CARD_COLOR,
        ).pack(pady=10)

        tk.Label(
            self.frame,
            text=f"{self.num1} {self.operation} {self.num2} =",
            font=("Poppins", 24, "bold"),
            fg="#FFD700",
            bg=CARD_COLOR,
        ).pack(pady=20)

        self.answer_entry = tk.Entry(self.frame, font=("Poppins", 18), justify="center", width=10)
        self.answer_entry.pack(pady=10)
        self.answer_entry.focus()
        self.answer_entry.bind("<Return>", self.check_answer)

        self.make_button("Submit Answer", self.check_answer)

        secs = {1: 10, 2: 20, 3: 30}.get(self.difficulty, 10)
        self.timer_set(secs)
        self.timer_start()

    def is_correct(self, user_answer):
        return user_answer == (self.num1 + self.num2 if self.operation == "+" else self.num1 - self.num2)

    def check_answer(self, event=None):
        if self.answer_entry is None:
            return

        try:
            user_answer = int(self.answer_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a number.")
            return

        progress = self.current_progress

        if self.is_correct(user_answer):
            self.timer_cancel()
            if self.first_attempt:
                self.score += 10
                messagebox.showinfo("Correct!", "Excellent! +10 points.")
            else:
                self.score += 5
                messagebox.showinfo("Correct!", "Good! +5 points.")
            if progress:
                progress["value"] = int((self.question_number / QUESTIONS_TOTAL) * 100)
            self.next_question()
        else:
            if self.first_attempt:
                self.first_attempt = False
                messagebox.showwarning("Incorrect", "Wrong! Try once more.")
                if self.answer_entry:
                    self.answer_entry.delete(0, tk.END)
                    self.answer_entry.focus()
                secs = {1: 10, 2: 20, 3: 30}.get(self.difficulty, 10)
                self.timer_set(secs)
                self.timer_start()
            else:
                self.timer_cancel()
                messagebox.showinfo("Incorrect", "Sorry, moving to next question.")
                if progress:
                    progress["value"] = int((self.question_number / QUESTIONS_TOTAL) * 100)
                self.next_question()

    def display_results(self):
        self.clear_frame()
        self.create_header("🎯 RESULTS 🎯")
        grade = self.get_grade(self.score)

        score_label = tk.Label(
            self.frame,
            text="Your Final Score: 0/100",
            font=("Poppins", 20, "bold"),
            fg="#FFD700",
            bg=CARD_COLOR,
        )
        score_label.pack(pady=20)

        grade_label = tk.Label(
            self.frame,
            text=f"Your Rank: {grade}",
            font=("Poppins", 18),
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
        )
        grade_label.pack(pady=10)

        self.animate_score(score_label, self.score)
        self.make_button("Play Again", self.display_menu)
        self.make_button("Exit", self.window.destroy)

    def animate_score(self, label, final_score):
        current = 0

        def update():
            nonlocal current
            if current < final_score:
                current += 2
                label.config(text=f"Your Final Score: {min(current, final_score)}/100")
                self.frame.after(30, update)
            else:
                label.config(text=f"Your Final Score: {final_score}/100")

        update()

    @staticmethod
    def get_grade(score_val):
        if score_val >= 90:
            return "A+"
        if score_val >= 80:
            return "A"
        if score_val >= 70:
            return "B"
        if score_val >= 60:
            return "C"
        if score_val >= 50:
            return "D"
        return "F"

    def run(self):
        self.display_menu()
        self.window.mainloop()


if __name__ == "__main__":
    QuizApp().run()
