import tkinter as tk
from pathlib import Path
import random
from PIL import Image, ImageTk, ImageDraw, ImageFont

# -----------------------------
# Paths and defaults
# -----------------------------
JOKES_PATH = Path(r"C:\Users\Kier\Desktop\Class Stuff\Codelab II\randomJokes.txt")

DEFAULT_JOKES = [
    ("Why did the chicken cross the road", "To get to the other side"),
    ("What do you call fake spaghetti", "An impasta"),
]

# -----------------------------
# Joke App
# -----------------------------
class JokeApp:
    def __init__(self, root):
        self.root = root
        root.title("Joke Teller")
        root.resizable(False, False)
        self.width, self.height = 400, 220
        root.geometry(f"{self.width}x{self.height}")

        # Canvas background
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Neon gradient background
        self.bg_photo = ImageTk.PhotoImage(self._make_background(self.width, self.height))
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Frame on top for UI controls
        self.frame = tk.Frame(self.canvas, bg="#000000", bd=0)
        self.canvas.create_window(self.width//2, self.height//2, window=self.frame)

        # Load jokes
        self.jokes = self._load_jokes()
        self.current = None
        self.jokes_told = 0
        self.reacts = {"😂": 0, "😐": 0, "👎": 0}

        # Joke label with typewriter effect
        self.label = tk.Label(self.frame, text="Press Enter or click for a joke",
                              wraplength=360, justify="center",
                              font=("Arial", 12, "bold"), fg="#00ffff", bg="#000000")
        self.label.pack(pady=(10,5))

        # Controls
        controls = tk.Frame(self.frame, bg="#000000")
        controls.pack(pady=(5,5))
        self.btn = tk.Button(controls, text="Tell Me a Joke", width=15, command=self.toggle_joke, bg="#8E2DE2", fg="white")
        self.btn.pack(side="left", padx=4)
        tk.Button(controls, text="Quit", width=6, command=root.destroy, bg="#4A00E0", fg="white").pack(side="left", padx=4)

        # Emoji reactions
        react_frame = tk.Frame(self.frame, bg="#000000")
        react_frame.pack(pady=(5,5))
        for e in ["😂", "😐", "👎"]:
            tk.Button(react_frame, text=e, width=4, command=lambda key=e: self.react(key), bg="#4A00E0", fg="white").pack(side="left", padx=3)

        # Count labels
        self.count_label = tk.Label(self.frame, text="Jokes told: 0", fg="#00ffff", bg="#000000")
        self.count_label.pack()
        self.reactions_label = tk.Label(self.frame, text=self._reaction_text(), fg="#00ffff", bg="#000000")
        self.reactions_label.pack()

        # Bind Enter
        root.bind("<Return>", lambda e: self.toggle_joke())

    # -----------------------------
    # Background generator
    # -----------------------------
    def _make_background(self, w, h):
        img = Image.new("RGB", (w, h), "#000000")
        draw = ImageDraw.Draw(img)
        # Neon gradient (blue -> purple)
        for y in range(h):
            t = y / max(1, h-1)
            r = int(74 + (142-74)*t)
            g = int(0 + (45-0)*t)
            b = int(224 + (255-224)*t)
            draw.line([(0,y),(w,y)], fill=(r,g,b))
        return img

    # -----------------------------
    # Load jokes
    # -----------------------------
    def _load_jokes(self):
        if JOKES_PATH.exists():
            out = []
            try:
                with JOKES_PATH.open(encoding="utf-8") as f:
                    for line in f:
                        if "?" in line:
                            s, p = line.strip().split("?", 1)
                            out.append((s.strip(), p.strip()))
            except Exception:
                return DEFAULT_JOKES.copy()
            return out or DEFAULT_JOKES.copy()
        return DEFAULT_JOKES.copy()

    # -----------------------------
    # Toggle joke display
    # -----------------------------
    def toggle_joke(self):
        if not self.jokes:
            self.label.config(text=f"No jokes found.\nCheck the file path.")
            return
        if self.btn.cget("text") in ("Tell Me a Joke", "Tell Another"):
            self.current = random.choice(self.jokes)
            self._typewriter(self.current[0] + "?")
            self.btn.config(text="Show Punchline")
        else:
            self._typewriter(f"{self.current[0]}?\n\n{self.current[1]}")
            self.btn.config(text="Tell Another")
            self.jokes_told += 1
            self.count_label.config(text=f"Jokes told: {self.jokes_told}")

    # -----------------------------
    # Emoji reactions
    # -----------------------------
    def react(self, key):
        self.reacts[key] += 1
        self.reactions_label.config(text=self._reaction_text())

    def _reaction_text(self):
        return "   ".join(f"{k} {v}" for k,v in self.reacts.items())

    # -----------------------------
    # Typewriter effect
    # -----------------------------
    def _typewriter(self, text, delay=25):
        self.label.config(text="")
        self._chars = text
        self._pos = 0
        def step():
            if self._pos < len(self._chars):
                self.label.config(text=self.label.cget("text")+self._chars[self._pos])
                self._pos +=1
                self.root.after(delay, step)
        step()

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = JokeApp(root)
    root.mainloop()
