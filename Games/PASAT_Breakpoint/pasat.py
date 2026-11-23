"""
PASAT (Paced Serial Addition Test) for the Breakpoint study.

Run:  python pasat.py        (Python 3.9+, nothing to install)

How it works: a digit (1-9) appears every few seconds. The participant adds it to
the digit BEFORE it and types the sum. No Enter needed: whatever is in the field
when the next digit appears is recorded as the answer. Every answer is saved to
CSV files in the "data" folder, ready to load with pandas.

Timing: response_time_ms = first keystroke after the digit appeared,
        last_key_ms      = last keystroke (answer complete).
"""
import csv
import platform
import random
import subprocess
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

# ======================= SETTINGS: change these =======================
INTERVAL_SECONDS = 3.0        # time between digits (3.0 is the classic slow version)
N_DIGITS = 21                 # 21 digits = 20 answers
PRACTICE_DIGITS = 8           # length of the practice round
SHOW_DIGIT_ON_SCREEN = True   # False = audio only (needs the audio folder below)
CONDITIONS = ["no_break", "walking", "doomscrolling"]
TIMEPOINTS = ["pre_break", "post_break", "final"]
SESSIONS = ["1", "2", "3"]

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"      # CSV files are saved here
AUDIO_DIR = BASE / "audio"    # spoken digits 1.wav ... 9.wav (create them with make_audio.py)
USE_AUDIO = True              # False = no voice, even if the audio files exist

# Colours and font
BG, CARD, CARD2 = "#0f172a", "#1e293b", "#334155"
TEXT, MUTED = "#e2e8f0", "#94a3b8"
ACCENT, GOOD, BAD = "#38bdf8", "#34d399", "#f87171"
FONT = "Helvetica"
# ======================================================================


# ---------------------------- helpers ----------------------------
def make_sequence(n):
    """Random digits 1-9, never the same digit twice in a row."""
    digits = [random.randint(1, 9)]
    while len(digits) < n:
        d = random.randint(1, 9)
        if d != digits[-1]:
            digits.append(d)
    return digits


def audio_ready():
    """True when the voice is switched on and all nine digit files exist."""
    return USE_AUDIO and all((AUDIO_DIR / f"{d}.wav").exists() for d in range(1, 10))


def voice_status():
    """Text for the start screen, so you can see at once if the voice is ready."""
    if not USE_AUDIO:
        return "Voice: off (USE_AUDIO is False)", BAD
    if audio_ready():
        return "Voice: on (9 audio files found)", GOOD
    return "Voice: off. No audio files found. Run make_audio.py first.", BAD


def play_audio(digit):
    """Play audio/<digit>.wav if the voice is on. Does nothing otherwise."""
    path = AUDIO_DIR / f"{digit}.wav"
    if not audio_ready():
        return
    try:
        system = platform.system()
        if system == "Windows":
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif system == "Darwin":
            subprocess.Popen(["afplay", str(path)])
        else:
            subprocess.Popen(["aplay", "-q", str(path)])
    except Exception as error:   # the test keeps running; the problem shows in the terminal
        print("Audio problem:", error)


def append_csv(path, rows):
    """Add rows to a CSV file. The header is written only when the file is new."""
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if is_new:
            writer.writeheader()
        writer.writerows(rows)


def label(parent, text, size=14, color=TEXT, bold=False, **kw):
    return tk.Label(parent, text=text, bg=parent["bg"], fg=color,
                    font=(FONT, size, "bold" if bold else "normal"), **kw)


def button(parent, text, command, primary=True):
    """A flat button (a Label, so it looks the same on Windows, Mac and Linux)."""
    bg, fg = (ACCENT, "#06202e") if primary else (CARD2, TEXT)
    b = tk.Label(parent, text=text, bg=bg, fg=fg, font=(FONT, 13, "bold"),
                 padx=30, pady=12, cursor="hand2")
    b.bind("<Button-1>", lambda e: command())
    b.bind("<Enter>", lambda e: b.config(bg="#7dd3fc" if primary else "#475569"))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


# ---------------------------- the app ----------------------------
class PasatPage(tk.Frame):
    def __init__(self, parent, controller=None, results_dir=None):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.results_dir = Path(results_dir) if results_dir is not None else DATA_DIR
        self.configure(bg=BG)
        self.job = None            # pending timer, so we can cancel it
        self.info = {}             # participant ID, session, condition, timepoint
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(fill="both", expand=True, padx=40, pady=30)
        if self.controller is None:
            self.bind("<Escape>", lambda e: self.show_setup())  # Esc = stop, nothing saved
            self.show_setup()

    def clear(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None
        for w in self.main.winfo_children():
            w.destroy()

    # ---- screen 1: setup ----
    def show_setup(self):
        self.clear()
        label(self.main, "PASAT", 44, ACCENT, True).pack(pady=(10, 0))
        label(self.main, "Paced Serial Addition Test  ·  Breakpoint study", 13, MUTED).pack(pady=(0, 24))

        card = tk.Frame(self.main, bg=CARD, padx=36, pady=28)
        card.pack()
        self.v_pid = tk.StringVar(value=self.info.get("participant_id", ""))
        self.v_ses = tk.StringVar(value=self.info.get("session", SESSIONS[0]))
        self.v_con = tk.StringVar(value=self.info.get("condition", CONDITIONS[0]))
        self.v_tp = tk.StringVar(value=self.info.get("timepoint", TIMEPOINTS[0]))
        self.v_prac = tk.BooleanVar(value=True)

        label(card, "Participant ID", 11, MUTED).grid(row=0, column=0, sticky="w")
        entry = tk.Entry(card, textvariable=self.v_pid, font=(FONT, 16), width=22, bg=BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat", highlightthickness=2,
                         highlightbackground=CARD2, highlightcolor=ACCENT)
        entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(2, 16), ipady=6)
        entry.focus()
        entry.bind("<Return>", lambda e: self.check_setup())

        for col, (name, var, options) in enumerate([("Session", self.v_ses, SESSIONS),
                                                    ("Condition", self.v_con, CONDITIONS),
                                                    ("Timepoint", self.v_tp, TIMEPOINTS)]):
            label(card, name, 11, MUTED).grid(row=2, column=col, sticky="w", padx=(0, 12))
            if name == "Condition":
                menu = tk.OptionMenu(
                    card, var, *options, command=self.update_timepoint_options
                )
            else:
                menu = tk.OptionMenu(card, var, *options)
            menu.config(font=(FONT, 12), bg=CARD2, fg=TEXT, relief="flat", highlightthickness=0, width=12)
            menu.grid(row=3, column=col, sticky="ew", padx=(0, 12), pady=(2, 16))
            if name == "Timepoint":
                self.timepoint_menu = menu
        self.update_timepoint_options()

        tk.Checkbutton(card, text="Do a short practice round first", variable=self.v_prac, bg=CARD, fg=TEXT,
                       selectcolor=BG, activebackground=CARD, activeforeground=TEXT,
                       font=(FONT, 12)).grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 18))
        button(card, "Continue", self.check_setup).grid(row=5, column=0, columnspan=3)
        text, color = voice_status()
        label(self.main, text, 12, color).pack(pady=14)

    def update_timepoint_options(self, *_):
        """Only offer timepoints that are valid for the selected condition."""
        if self.v_con.get() == "no_break":
            options = ("final",)
        else:
            options = ("pre_break", "post_break")

        menu = self.timepoint_menu["menu"]
        menu.delete(0, "end")
        for option in options:
            menu.add_radiobutton(
                label=option,
                variable=self.v_tp,
                value=option,
            )
        if self.v_tp.get() not in options:
            self.v_tp.set(options[0])

    def check_setup(self):
        pid = self.v_pid.get().strip()
        if not pid or not pid.replace("-", "").replace("_", "").isalnum():
            label(self.main, "Enter an ID using letters, numbers, - or _ (no names).", 12, BAD).pack(pady=10)
            return
        self.info = {"participant_id": pid, "session": self.v_ses.get(),
                     "condition": self.v_con.get(), "timepoint": self.v_tp.get()}
        self.practice_first = self.v_prac.get()
        self.show_instructions()

    def start_session(self, participant_id, session, condition, timepoint):
        """Start the framework's PASAT stage with metadata supplied by its session."""
        self.info = {
            "participant_id": participant_id,
            "session": str(session),
            "condition": condition,
            "timepoint": timepoint,
        }
        self.practice_first = True
        self.show_instructions()

    # ---- screen 2: instructions ----
    def show_instructions(self):
        self.clear()
        label(self.main, "How it works", 32, ACCENT, True).pack(pady=(10, 16))
        text = ("A digit appears every few seconds.\n\n"
                "Add it to the digit BEFORE it, and type the sum. No need to press Enter.\n"
                "Answer before the next digit appears.\n\n"
                "Example:  3  →  5  →  2\n"
                "Answer 8 (3 + 5) when the 5 appears, then 7 (5 + 2) when the 2 appears.\n\n"
                "Do not add running totals. If you miss one, just carry on.\n"
                "The first digit needs no answer.")
        box = tk.Frame(self.main, bg=CARD, padx=40, pady=30)
        box.pack()
        label(box, text, 15, TEXT, justify="left").pack()
        row = tk.Frame(self.main, bg=BG)
        row.pack(pady=26)
        button(row, "Back", self.show_setup, primary=False).pack(side="left", padx=8)
        button(row, "Start", lambda: self.start_run(self.practice_first)).pack(side="left", padx=8)

    # ---- screen 3: the test ----
    def start_run(self, practice):
        self.clear()
        self.practice = practice
        self.digits = make_sequence(PRACTICE_DIGITS if practice else N_DIGITS)
        self.trials, self.i = [], -1
        self.answer = self.rt = None
        self.onset = self.t_first = self.t_last = None

        label(self.main, "PRACTICE" if practice else "TEST", 14, MUTED, True).pack()
        self.digit_lbl = label(self.main, "", 150, ACCENT, True)
        self.digit_lbl.pack(pady=(20, 10), expand=True)
        # Only digits, max 2 characters (the biggest sum is 9 + 8 = 17)
        only_digits = self.register(lambda s: s == "" or (s.isdigit() and len(s) <= 2))
        self.entry = tk.Entry(self.main, font=(FONT, 34), width=5, justify="center", bg=CARD, fg=TEXT,
                              insertbackground=TEXT, relief="flat", highlightthickness=2,
                              highlightbackground=CARD2, highlightcolor=ACCENT,
                              validate="key", validatecommand=(only_digits, "%P"))
        self.entry.pack(ipady=8)
        self.entry.bind("<Key>", self.on_key)        # no Enter: we just note the timing
        self.entry.focus_force()
        self.status = label(self.main, "", 13, MUTED)
        self.status.pack(pady=12)
        self.bar = tk.Canvas(self.main, height=8, bg=CARD2, highlightthickness=0)
        self.bar.pack(fill="x", pady=(10, 0))
        self.countdown(3)

    def countdown(self, n):
        if n == 0:
            self.t_start = time.perf_counter()
            self.tick()
            return
        self.digit_lbl.config(text=str(n), fg=MUTED)
        self.status.config(text="Get ready…")
        self.job = self.after(1000, self.countdown, n - 1)

    def tick(self):
        """Runs once per digit: score the previous pair, then show the next digit."""
        self.score_previous_pair()
        self.i += 1
        if self.i >= len(self.digits):
            self.finish()
            return
        digit = self.digits[self.i]
        self.onset = time.perf_counter()
        self.t_first = self.t_last = None
        self.entry.delete(0, "end")
        self.digit_lbl.config(text=str(digit) if SHOW_DIGIT_ON_SCREEN else "•", fg=ACCENT)
        play_audio(digit)
        # progress bar
        self.bar.update_idletasks()
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, self.bar.winfo_width() * (self.i + 1) / len(self.digits), 8,
                                  fill=ACCENT, width=0)
        # schedule the next digit at an exact time (no drift)
        next_time = self.t_start + (self.i + 1) * INTERVAL_SECONDS
        self.job = self.after(max(1, int((next_time - time.perf_counter()) * 1000)), self.tick)

    def on_key(self, event=None):
        """Note when the participant starts and last touches the field."""
        if self.i < 1:
            return
        now = time.perf_counter()
        if self.t_first is None:
            self.t_first = now
        self.t_last = now

    def score_previous_pair(self):
        if self.i < 1:
            return
        text = self.entry.get().strip()              # whatever is in the field right now
        self.answer = int(text) if text.isdigit() else None
        self.rt = int((self.t_first - self.onset) * 1000) if self.t_first else None
        rt_last = int((self.t_last - self.onset) * 1000) if self.t_last else None

        prev, now = self.digits[self.i - 1], self.digits[self.i]
        correct_sum = prev + now
        is_correct = int(self.answer == correct_sum) if self.answer is not None else 0
        self.trials.append({"trial": self.i, "digit_prev": prev, "digit_now": now,
                            "correct_sum": correct_sum, "answer": self.answer,
                            "is_correct": is_correct,
                            "response_time_ms": self.rt,        # first keystroke
                            "last_key_ms": rt_last})            # last keystroke
        if self.practice:
            if self.answer is None:
                self.status.config(text=f"missed (it was {correct_sum})", fg=BAD)
            elif is_correct:
                self.status.config(text="correct ✓", fg=GOOD)
            else:
                self.status.config(text=f"not quite (it was {correct_sum})", fg=BAD)

    # ---- screen 4: results ----
    def finish(self):
        t = self.trials
        n_ok = sum(x["is_correct"] for x in t)
        n_missed = sum(x["answer"] is None for x in t)
        n_wrong = len(t) - n_ok - n_missed
        rts = [x["response_time_ms"] for x in t if x["response_time_ms"] is not None]
        mean_rt = round(sum(rts) / len(rts)) if rts else ""
        percent = round(100 * n_ok / len(t), 1)

        saved = ""
        if not self.practice:
            run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            common = {"run_id": run_id, **self.info}
            append_csv(self.results_dir / "pasat_trials.csv",
                       [{**common, **x, "interval_s": INTERVAL_SECONDS} for x in t])
            append_csv(self.results_dir / "pasat_summary.csv",
                       [{**common, "timestamp": datetime.now().isoformat(timespec="seconds"),
                         "interval_s": INTERVAL_SECONDS,
                         "mode": ("audio+screen" if SHOW_DIGIT_ON_SCREEN else "audio") if audio_ready() else "screen",
                         "n_trials": len(t), "n_correct": n_ok, "n_wrong": n_wrong,
                         "n_missed": n_missed, "percent_correct": percent, "mean_rt_ms": mean_rt}])
            saved = (
                f"Saved to {self.results_dir / 'pasat_summary.csv'} "
                "and pasat_trials.csv"
            )

        self.clear()
        label(self.main, "Practice done" if self.practice else "Finished", 32, ACCENT, True).pack(pady=(10, 4))
        label(self.main, f"{percent}%", 80, GOOD if percent >= 50 else TEXT, True).pack()
        label(self.main, "correct", 13, MUTED).pack(pady=(0, 20))
        stats = tk.Frame(self.main, bg=BG)
        stats.pack()
        for name, value in [("Correct", n_ok), ("Wrong", n_wrong), ("Missed", n_missed),
                            ("Avg. time (ms)", mean_rt if mean_rt != "" else "-")]:
            c = tk.Frame(stats, bg=CARD, padx=24, pady=16)
            c.pack(side="left", padx=8)
            label(c, str(value), 26, TEXT, True).pack()
            label(c, name, 11, MUTED).pack()
        label(self.main, saved or "Practice results are not saved.", 12, MUTED).pack(pady=20)
        row = tk.Frame(self.main, bg=BG)
        row.pack(pady=8)
        if self.practice:
            if self.controller is None:
                button(row, "Practice again", lambda: self.start_run(True), primary=False).pack(side="left", padx=8)
            button(row, "Start the real test", lambda: self.start_run(False)).pack(side="left", padx=8)
        elif self.controller is not None:
            button(row, "Continue", self.controller.game_finished).pack(side="left", padx=8)
        else:
            button(row, "New participant / run", self.show_setup, primary=False).pack(side="left", padx=8)
            button(row, "Quit", self.winfo_toplevel().destroy).pack(side="left", padx=8)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Breakpoint | PASAT")
    root.geometry("920x680")
    root.minsize(760, 600)
    page = PasatPage(root)
    page.pack(fill="both", expand=True)
    root.bind("<Escape>", lambda event: page.show_setup())
    root.mainloop()
