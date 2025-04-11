import tkinter as tk
import random
import math

# Constants for configuration
ROW_COUNT = 5
COLUMN_COUNT = 39
HIGHLIGHT_INDEX = 18
TIME_LIMIT = 5
CELL_WIDTH = 20
CELL_HEIGHT = 30
SPIN_PHASES_TEMPLATE = [
    (50, 5),   # Fast spins (burst)
    (100, 5),  # Deceleration start
    (200, 4),  # Medium
    (300, 3),  # Slower
    (500, 2),  # Final slow
]

# Initial values per row designed to span the range 1 to 50, randomized
initial_values = [
    random.sample(range(1, 51), 50),
    random.sample(range(1, 51), 50),
    random.sample(range(1, 51), 50),
    random.sample(range(1, 51), 50),
    random.sample(range(1, 51), 50),
]

def generate_random_instructions():
    return [(random.randint(1, 7), random.choice(['left', 'right'])) for _ in range(ROW_COUNT)]

def rotate(lst, steps, direction):
    steps = steps % len(lst)
    return lst[-steps:] + lst[:-steps] if direction == 'right' else lst[steps:] + lst[:steps]

def adjust_rows_for_uniqueness(rows):
    for col in range(COLUMN_COUNT):
        seen = set()
        for row in range(ROW_COUNT):
            while rows[row][col] in seen:
                rows[row] = rotate(rows[row], 1, 'left')
            seen.add(rows[row][col])

class NumberGeneratorGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Lottery Number Generator")

        self.rows = [initial_values[i][:] for i in range(ROW_COUNT)]
        self.rectangles = []
        self.texts = []

        self.setup_ui()
        self.setup_drag_and_drop()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=800, height=ROW_COUNT * CELL_HEIGHT)
        self.canvas.pack()

        self.cycles_label = tk.Label(self.root, text="Enter number of results:")
        self.cycles_label.pack()
        self.cycles_entry = tk.Entry(self.root)
        self.cycles_entry.pack()

        self.start_button = tk.Button(self.root, text="Generate", command=self.start_game)
        self.start_button.pack()

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_game)
        self.refresh_button.pack()

        self.timer_label = tk.Label(self.root, text="Time left: 10 seconds")
        self.timer_label.pack()

        self.status_label = tk.Label(self.root, text="Status: Ready")
        self.status_label.pack()

        self.status_bar = tk.Canvas(self.root, width=200, height=20, bg="white")
        self.status_bar.pack()

        self.recorded_label = tk.Label(self.root, text="Recorded Numbers:")
        self.recorded_label.pack()
        self.recorded_listbox = tk.Listbox(self.root, width=50, height=10)
        self.recorded_listbox.pack()

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        self.rectangles = []
        self.texts = []
        for i in range(ROW_COUNT):
            row_rects = []
            row_texts = []
            for j in range(COLUMN_COUNT):
                x0, y0 = j * CELL_WIDTH, i * CELL_HEIGHT
                x1, y1 = x0 + CELL_WIDTH, y0 + CELL_HEIGHT
                color = 'orange' if j == HIGHLIGHT_INDEX else 'white'
                rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                text = self.canvas.create_text(x0 + CELL_WIDTH // 2, y0 + CELL_HEIGHT // 2, text=str(self.rows[i][j]))
                row_rects.append(rect)
                row_texts.append(text)
            self.rectangles.append(row_rects)
            self.texts.append(row_texts)

    def update_grid(self):
        for i in range(ROW_COUNT):
            for j in range(COLUMN_COUNT):
                self.canvas.itemconfig(self.texts[i][j], text=str(self.rows[i][j]))

    def rotate_rows(self):
        instructions = generate_random_instructions()
        for i in range(ROW_COUNT):
            steps, direction = instructions[i]
            self.rows[i] = rotate(self.rows[i], steps, direction)
        adjust_rows_for_uniqueness(self.rows)
        self.update_grid()

    def start_game(self):
        try:
            self.num_results = int(self.cycles_entry.get())
            if self.num_results <= 0:
                raise ValueError
        except ValueError:
            self.num_results = 1
            self.status_label.config(text="Invalid input. Defaulting to 1 result.")

        self.results_generated = 0
        self.phase_index = 0
        self.phase_steps = [list(phase) for phase in SPIN_PHASES_TEMPLATE]
        self.status_label.config(text="Status: Running")
        self.run_game()

    def run_game(self):
        if self.results_generated < self.num_results:
            self.phase_index = 0
            self.phase_steps = [list(phase) for phase in SPIN_PHASES_TEMPLATE]
            self.spin_phase()
        else:
            self.stop_game()

    def spin_phase(self):
        if self.phase_index < len(self.phase_steps):
            delay, count = self.phase_steps[self.phase_index]
            if count > 0:
                self.rotate_rows()
                self.phase_steps[self.phase_index][1] -= 1
                self.root.after(delay, self.spin_phase)
            else:
                self.phase_index += 1
                self.root.after(0, self.spin_phase)
        else:
            self.record_numbers()
            self.results_generated += 1
            self.update_status_bar()
            self.run_game()

    def update_status_bar(self):
        fill_width = (self.results_generated / self.num_results) * 200
        self.status_bar.delete("all")
        self.status_bar.create_rectangle(0, 0, fill_width, 20, fill="green")

    def record_numbers(self):
        recorded_numbers = [str(self.rows[i][HIGHLIGHT_INDEX]) for i in range(ROW_COUNT)]
        self.recorded_listbox.insert(tk.END, f"Result {self.results_generated}: " + ", ".join(recorded_numbers))

    def stop_game(self):
        self.status_label.config(text="Status: Finished")

    def refresh_game(self):
        self.rows = [random.sample(range(1, 51), 50) for _ in range(ROW_COUNT)]
        self.recorded_listbox.delete(0, tk.END)
        self.cycles_entry.delete(0, tk.END)
        self.status_label.config(text="Status: Ready")
        self.update_status_bar()
        self.draw_grid()

    def setup_drag_and_drop(self):
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        self.dragging_row = event.y // CELL_HEIGHT
        self.dragging_start_x = event.x

    def on_drag(self, event):
        if self.dragging_row is not None:
            dx = event.x - self.dragging_start_x
            steps = dx // CELL_WIDTH
            self.rows[self.dragging_row] = rotate(self.rows[self.dragging_row], steps, 'left')
            self.update_grid()
            self.dragging_start_x = event.x

    def end_drag(self, event):
        self.dragging_row = None
        self.dragging_start_x = None

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGeneratorGame(root)
    root.mainloop()
