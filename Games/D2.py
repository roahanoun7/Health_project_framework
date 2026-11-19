"""Original d2-style attention practice activity (not the official D2 test)."""

import csv
import random
import secrets
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk


CONDITIONS = ("no_break", "walking_break", "doomscrolling_break")
CONDITION_LABELS = {
    "no_break": "No break",
    "walking_break": "Walking break",
    "doomscrolling_break": "Doomscrolling break",
}
TIMEPOINTS = ("pre_break", "after_break", "end_of_experiment")
CSV_FIELDS = (
    "record_type",
    "run_id",
    "participant_id",
    "session",
    "condition",
    "timepoint",
    "timestamp",
    "round_number",
    "n_correct",
    "n_wrong",
    "n_missed",
    "percent_correct",
    "rt_ms",
    "mean_rt_ms",
    "n_enter_presses",
    "timed_out",
)


def make_symbol(is_target):
    letter = "d" if is_target else random.choice(("d", "p"))
    if is_target:
        dash_count = 2
    elif letter == "d":
        dash_count = random.choice((1, 3))
    else:
        dash_count = random.choice((1, 2, 3))
    above_count = random.randint(0, dash_count)
    return letter, above_count, dash_count - above_count


class AttentionPracticeApp(tk.Frame):
    def __init__(
        self,
        parent,
        controller=None,
        rounds=3,
        items_per_round=24,
        seconds_per_round=30,
        participant_id="PENDING",
        session=1,
        condition="no_break",
        timepoint="pre_break",
        results_path=None,
    ):
        if session not in range(1, 25):
            raise ValueError("session must be between 1 and 24")
        if condition not in CONDITIONS:
            raise ValueError(f"condition must be one of: {', '.join(CONDITIONS)}")
        if timepoint not in TIMEPOINTS:
            raise ValueError(f"timepoint must be one of: {', '.join(TIMEPOINTS)}")

        super().__init__(parent)
        self.controller = controller
        self.rounds = rounds
        self.items_per_round = items_per_round
        self.seconds_per_round = seconds_per_round
        self.participant_id = participant_id
        self.session = session
        self.condition = condition
        self.timepoint = timepoint
        self.results_path = (
            Path(results_path)
            if results_path is not None
            else Path(__file__).parent
            / "Results_Data"
            / "attention_practice_results.csv"
        )
        self.start_new_run()
        self.timer_id = None
        self.round_active = False
        self.round_enter_presses = 0

        self.bind("<Return>", self.handle_enter)

        style = ttk.Style(self)
        style.configure(".", font=("TkDefaultFont", 14))
        style.configure("Title.TLabel", font=("TkDefaultFont", 25, "bold"))
        style.configure("Instructions.TLabel", font=("TkDefaultFont", 16))
        style.configure("Timer.TLabel", font=("TkDefaultFont", 17, "bold"))
        style.configure(
            "Action.TButton",
            font=("TkDefaultFont", 18, "bold"),
            padding=(18, 12),
        )
        style.configure("Treeview", font=("TkDefaultFont", 13), rowheight=30)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 13, "bold"))

        self.page = ttk.Frame(self, padding=24)
        self.page.pack(fill="both", expand=True)
        self.show_start_page()

    def start_new_run(self):
        self.run_id = secrets.token_urlsafe(12)
        self.round_number = 0
        self.total_hits = 0
        self.total_misses = 0
        self.total_false_alarms = 0
        self.round_results = []
        self.save_error = None
        self.run_summary = None
        self.game_started_at = None

    def start_game(self, condition=None, timepoint=None):
        """Reset the D2 run and show its condition-selection screen."""
        if self.controller is not None:
            self.participant_id = self.controller.participant_id
            self.session = self.controller.session_number
        if condition is not None:
            if condition not in CONDITIONS:
                raise ValueError(f"condition must be one of: {', '.join(CONDITIONS)}")
            self.condition = condition
        if timepoint is not None:
            if timepoint not in TIMEPOINTS:
                raise ValueError(f"timepoint must be one of: {', '.join(TIMEPOINTS)}")
            self.timepoint = timepoint
        self.start_new_run()
        self.round_active = False
        self.show_start_page()

    def clear_page(self):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        for child in self.page.winfo_children():
            child.destroy()

    def show_start_page(self):
        self.clear_page()
        ttk.Label(
            self.page,
            text="ATTENTION Test",
            style="Title.TLabel",
        ).pack(pady=(36, 20))
        ttk.Label(
            self.page,
            text=(
                "Select each d with exactly two dashes. The dashes may be above, "
                "below, or split between both sides.\n\n"
            ),
            justify="center",
            wraplength=760,
            style="Instructions.TLabel",
        ).pack(pady=12)

        if self.controller is None:
            ttk.Label(
                self.page,
                text="Choose condition:",
                style="Instructions.TLabel",
            ).pack(pady=(12, 8))
            condition_frame = ttk.Frame(self.page)
            condition_frame.pack(pady=(0, 8))
            self.condition_var = tk.StringVar(value=self.condition)
            for condition in CONDITIONS:
                ttk.Radiobutton(
                    condition_frame,
                    text=CONDITION_LABELS[condition],
                    variable=self.condition_var,
                    value=condition,
                ).pack(anchor="w", pady=3)
        else:
            ttk.Label(
                self.page,
                text=(
                    f"Scheduled condition: {CONDITION_LABELS[self.condition]}    "
                    f"Timepoint: {self.timepoint}"
                ),
                style="Instructions.TLabel",
            ).pack(pady=(12, 8))

        ttk.Button(
            self.page,
            text="Start test" if self.controller is not None else "Start practice",
            command=self.start_selected_condition,
            style="Action.TButton",
        ).pack(pady=24)

    def start_selected_condition(self):
        if self.controller is None:
            self.condition = self.condition_var.get()
        if self.condition not in CONDITIONS:
            return
        self.start_round()

    def start_round(self):
        if self.round_number == 0:
            self.game_started_at = datetime.now().astimezone()
        self.round_number += 1
        targets = {
            i
            for i in range(self.items_per_round)
            if random.random() < 0.35
        }
        if not targets:
            targets.add(random.randrange(self.items_per_round))
        self.targets = targets
        self.round_enter_presses = 0
        self.selections = [
            tk.BooleanVar(value=False) for _ in range(self.items_per_round)
        ]

        self.clear_page()
        ttk.Label(
            self.page,
            text=f"Round {self.round_number}/{self.rounds}",
            style="Title.TLabel",
        ).pack(pady=(4, 8))
        self.timer_label = ttk.Label(self.page, style="Timer.TLabel")
        self.timer_label.pack(pady=(0, 12))
        ttk.Label(
            self.page,
            text="Select each d with exactly two dashes.",
            style="Instructions.TLabel",
        ).pack(pady=(0, 16))

        grid_container = ttk.Frame(self.page)
        grid_container.pack(fill="both", expand=True)
        grid_canvas = tk.Canvas(grid_container, highlightthickness=0)
        grid_scrollbar = ttk.Scrollbar(
            grid_container, orient="vertical", command=grid_canvas.yview
        )
        grid_canvas.configure(yscrollcommand=grid_scrollbar.set)
        grid_scrollbar.pack(side="right", fill="y")
        grid_canvas.pack(side="left", fill="both", expand=True)
        grid = ttk.Frame(grid_canvas)
        grid_window = grid_canvas.create_window((0, 0), window=grid, anchor="nw")
        grid.bind(
            "<Configure>",
            lambda _event: grid_canvas.configure(
                scrollregion=grid_canvas.bbox("all")
            ),
        )
        grid_canvas.bind(
            "<Configure>",
            lambda event: grid_canvas.itemconfigure(grid_window, width=event.width),
        )
        available_width = max(1, self.winfo_width() - 140)
        columns = min(
            self.items_per_round,
            max(1, min(8, available_width // 112)),
        )
        for column in range(columns):
            grid.columnconfigure(column, weight=1, uniform="item")
        row_count = (self.items_per_round + columns - 1) // columns
        last_row_items = self.items_per_round - (row_count - 1) * columns
        last_row_offset = (columns - last_row_items) // 2

        for i in range(self.items_per_round):
            letter, above_count, below_count = make_symbol(i in targets)
            row, column = divmod(i, columns)
            if row == row_count - 1:
                column += last_row_offset
            item = ttk.Frame(grid, padding=6, width=104, height=132)
            item.grid(row=row, column=column, padx=6, pady=6)
            item.grid_propagate(False)
            ttk.Label(item, text=str(i + 1)).pack(pady=(0, 2))
            symbol_canvas = tk.Canvas(
                item,
                width=72,
                height=84,
                background="#f7f7f7",
                highlightthickness=0,
            )
            symbol_canvas.pack()
            self.draw_symbol(symbol_canvas, letter, above_count, below_count)
            symbol_canvas.configure(cursor="hand2")
            symbol_canvas.bind(
                "<Button-1>",
                lambda _event, selection=self.selections[i]: selection.set(
                    not selection.get()
                ),
            )
            checkbox = ttk.Checkbutton(item, variable=self.selections[i])
            checkbox.pack(pady=(2, 0))
            checkbox.bind("<Return>", self.handle_enter)

        submit_button = ttk.Button(
            self.page,
            text="Submit round (Enter)",
            command=self.submit_round,
            style="Action.TButton",
        )
        submit_button.pack(pady=24)
        submit_button.bind("<Return>", self.handle_enter)
        self.round_active = True
        self.round_start_time = time.monotonic()
        self.deadline = self.round_start_time + self.seconds_per_round
        self.update_timer()

    @staticmethod
    def draw_symbol(canvas, letter, above_count, below_count):
        canvas.create_text(
            36,
            42,
            text=letter,
            font=("Times New Roman", 30),
            fill="#202020",
        )
        for count, center_y in ((above_count, 14), (below_count, 70)):
            for dash_index in range(count):
                x = 36 + (dash_index - (count - 1) / 2) * 8
                canvas.create_line(
                    x, center_y - 5, x, center_y + 5, fill="#202020", width=2
                )

    def update_timer(self):
        if not self.round_active:
            return
        remaining = max(0, self.deadline - time.monotonic())
        self.timer_label.configure(text=f"Time remaining: {remaining:.1f} seconds")
        if remaining <= 0:
            self.submit_round(timed_out=True)
        else:
            self.timer_id = self.after(100, self.update_timer)

    def handle_enter(self, _event=None):
        if self.round_active:
            self.submit_round()
            return "break"

    def submit_round(self, timed_out=False):
        if not self.round_active:
            return
        self.round_enter_presses = 0 if timed_out else 1
        self.round_active = False

        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        elapsed_seconds = min(
            self.seconds_per_round, time.monotonic() - self.round_start_time
        )
        if timed_out:
            elapsed_seconds = self.seconds_per_round
        rt_ms = round(elapsed_seconds * 1000)
        selected = {
            i for i, variable in enumerate(self.selections) if variable.get()
        }

        hits = len(selected & self.targets)
        misses = len(self.targets - selected)
        false_alarms = len(selected - self.targets)
        percent_correct = (
            100 * hits / (hits + misses) if hits + misses else 0
        )
        self.total_hits += hits
        self.total_misses += misses
        self.total_false_alarms += false_alarms
        self.round_results.append(
            {
                "record_type": "round",
                "run_id": self.run_id,
                "participant_id": self.participant_id,
                "session": self.session,
                "condition": self.condition,
                "timepoint": self.timepoint,
                "timestamp": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                "round_number": self.round_number,
                "n_correct": hits,
                "n_wrong": false_alarms,
                "n_missed": misses,
                "percent_correct": round(percent_correct, 2),
                "rt_ms": rt_ms,
                "mean_rt_ms": rt_ms,
                "n_enter_presses": self.round_enter_presses,
                "timed_out": timed_out,
            }
        )

        if self.round_number < self.rounds:
            self.start_round()
        else:
            self.save_run_results()
            self.show_completion_page()

    def save_run_results(self):
        total_attempted_targets = self.total_hits + self.total_misses
        total_percent_correct = (
            100 * self.total_hits / total_attempted_targets
            if total_attempted_targets
            else 0
        )
        completed_times = [
            row["rt_ms"] for row in self.round_results if not row["timed_out"]
        ]
        mean_rt_ms = (
            round(sum(completed_times) / len(completed_times), 2)
            if completed_times
            else ""
        )
        summary = {
            "record_type": "run_summary",
            "run_id": self.run_id,
            "participant_id": self.participant_id,
            "session": self.session,
            "condition": self.condition,
            "timepoint": self.timepoint,
            "timestamp": datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            "round_number": "total",
            "n_correct": self.total_hits,
            "n_wrong": self.total_false_alarms,
            "n_missed": self.total_misses,
            "percent_correct": round(total_percent_correct, 2),
            "rt_ms": "",
            "mean_rt_ms": mean_rt_ms,
            "n_enter_presses": sum(
                row["n_enter_presses"] for row in self.round_results
            ),
            "timed_out": "",
        }
        self.run_summary = summary

        try:
            self.results_path.parent.mkdir(parents=True, exist_ok=True)
            needs_header = (
                not self.results_path.exists() or self.results_path.stat().st_size == 0
            )
            with self.results_path.open("a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
                if needs_header:
                    writer.writeheader()
                writer.writerows(self.round_results)
                writer.writerow(summary)
        except (OSError, csv.Error) as error:
            self.save_error = str(error)

    def show_completion_page(self):
        self.clear_page()
        self.round_active = False
        ttk.Label(
            self.page,
            text="Activity complete",
            style="Title.TLabel",
        ).pack(pady=(90, 20))
        ttk.Label(
            self.page,
            text="The attention test is complete. Continue to the next stage.",
            style="Instructions.TLabel",
        ).pack(pady=12)
        ttk.Button(
            self.page,
            text="Continue",
            command=self.finish_game,
            style="Action.TButton",
        ).pack(pady=24)
        self.show_results_window()

    def finish_game(self):
        if self.controller is None:
            self.winfo_toplevel().destroy()
            return

        finished_at = datetime.now().astimezone()
        run_results = {
            "run_id": self.run_id,
            "session": self.session,
            "condition": self.condition,
            "timepoint": self.timepoint,
            "total_correct": self.total_hits,
            "total_wrong": self.total_false_alarms,
            "total_missed": self.total_misses,
            "percent_correct": self.run_summary["percent_correct"],
            "mean_rt_ms": self.run_summary["mean_rt_ms"],
            "enter_presses": self.run_summary["n_enter_presses"],
        }
        result_prefix = f"d2_{self.timepoint}"
        self.controller.d2_results.update(
            {f"{result_prefix}_{key}": value for key, value in run_results.items()}
        )
        self.controller.add_game_timestamp((
            self.game_started_at.isoformat(timespec="milliseconds"),
            finished_at.isoformat(timespec="milliseconds"),
        ))
        if self.results_window.winfo_exists():
            self.results_window.destroy()
        self.controller.game_finished()

    def show_results_window(self):
        results_window = tk.Toplevel(self)
        self.results_window = results_window
        results_window.title("Researcher Results")
        results_window.geometry("1000x600")
        results_window.minsize(760, 420)
        results_window.transient(self)
        results_page = ttk.Frame(results_window, padding=24)
        results_page.pack(fill="both", expand=True)

        attempted_targets = self.total_hits + self.total_misses
        accuracy = (
            100 * self.total_hits / attempted_targets if attempted_targets else 0
        )

        ttk.Label(
            results_page,
            text="Researcher results",
            style="Title.TLabel",
        ).pack(pady=(28, 20))
        ttk.Label(
            results_page,
            text=(
                f"Run: {self.run_id}    Participant: {self.participant_id}    "
                f"Session: {self.session}    Condition: {self.condition}    "
                f"Timepoint: {self.timepoint}"
            ),
            wraplength=900,
        ).pack(pady=(0, 12))

        table_frame = ttk.Frame(results_page)
        table_frame.pack(fill="x", pady=(0, 12))
        columns = ("round", "hits", "wrong", "missed", "time", "enter")
        results_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=min(len(self.round_results) + 1, 7),
        )
        headings = {
            "round": "Page",
            "hits": "Hits",
            "wrong": "Wrong",
            "missed": "Missed",
            "time": "Time (ms)",
            "enter": "Enter presses",
        }
        widths = {
            "round": 100,
            "hits": 100,
            "wrong": 100,
            "missed": 100,
            "time": 140,
            "enter": 160,
        }
        for column in columns:
            results_table.heading(column, text=headings[column])
            results_table.column(column, width=widths[column], anchor="center")
        for row in self.round_results:
            results_table.insert(
                "",
                "end",
                values=(
                    row["round_number"],
                    row["n_correct"],
                    row["n_wrong"],
                    row["n_missed"],
                    row["rt_ms"],
                    row["n_enter_presses"],
                ),
            )
        total_enter_presses = sum(
            row["n_enter_presses"] for row in self.round_results
        )
        results_table.insert(
            "",
            "end",
            values=(
                "Total",
                self.total_hits,
                self.total_false_alarms,
                self.total_misses,
                "",
                total_enter_presses,
            ),
            tags=("total",),
        )
        results_table.tag_configure("total", font=("TkDefaultFont", 13, "bold"))
        results_table.pack(fill="x")

        completed_times = [
            row["rt_ms"] for row in self.round_results if not row["timed_out"]
        ]
        mean_rt_ms = (
            sum(completed_times) / len(completed_times) if completed_times else 0
        )
        ttk.Label(
            results_page,
            text=(
                f"Total hits: {self.total_hits}    "
                f"Wrong selections: {self.total_false_alarms}    "
                f"Missed: {self.total_misses}    "
                f"Correct: {accuracy:.1f}%"
            ),
            style="Instructions.TLabel",
        ).pack(pady=4)
        ttk.Label(
            results_page,
            text=f"Mean response time: {mean_rt_ms:.0f} ms",
            style="Instructions.TLabel",
        ).pack(pady=4)
        ttk.Label(
            results_page,
            text=f"Enter key presses: {total_enter_presses}",
            style="Instructions.TLabel",
        ).pack(pady=4)
        save_status = (
            f"Results saved to: {self.results_path}"
            if self.save_error is None
            else f"Could not save results to {self.results_path}: {self.save_error}"
        )
        ttk.Label(results_page, text=save_status, wraplength=900).pack(pady=6)

    def restart(self):
        self.start_new_run()
        self.show_start_page()


def run_test(
    rounds=3,
    items_per_round=24,
    seconds_per_round=30,
    participant_id="PENDING",
    session=1,
    condition="no_break",
    timepoint="pre_break",
    results_path=None,
):
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = min(1000, max(640, screen_width - 40))
    window_height = min(760, max(520, screen_height - 80))
    root.title("Attention Practice")
    root.geometry(f"{window_width}x{window_height}")
    root.minsize(min(760, window_width), min(600, window_height))
    app = AttentionPracticeApp(
        root,
        rounds=rounds,
        items_per_round=items_per_round,
        seconds_per_round=seconds_per_round,
        participant_id=participant_id,
        session=session,
        condition=condition,
        timepoint=timepoint,
        results_path=results_path,
    )
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    run_test()
