import tkinter as tk
from tkinter import messagebox
import random, copy, time, json, os

# --- Sudoku Logic ---
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[box_row + i][box_col + j] == num:
                return False
    return True

def solve(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                for num in range(1, 10):
                    if is_valid(board, i, j, num):
                        board[i][j] = num
                        if solve(board):
                            return True
                        board[i][j] = 0
                return False
    return True

def generate_full_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    return board

def remove_cells(board, difficulty='medium'):
    puzzle = copy.deepcopy(board)
    remove_count = {'easy': 30, 'medium': 40, 'hard': 55}[difficulty]
    removed = 0
    while removed < remove_count:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if puzzle[r][c] != 0:
            puzzle[r][c] = 0
            removed += 1
    return puzzle

# --- GUI App ---
class SudokuApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Sudoku Trainer")
        master.resizable(True, True)

        self.entries = [[None]*9 for _ in range(9)]
        self.prefilled = [[False]*9 for _ in range(9)]
        self.difficulty = 'medium'
        self.start_time = None
        self.timer_id = None
        self.solution = None
        self.starting_puzzle = None
        self.stats_file = "sudoku_stats.json"
        self.load_stats()

        self.top_frame = tk.Frame(master)
        self.top_frame.pack(pady=10)

        self.timer_label = tk.Label(self.top_frame, text="Time: 0s", font=('Arial', 12))
        self.timer_label.pack(side=tk.LEFT, padx=10)

        self.score_label = tk.Label(self.top_frame, text=f"Score: {self.stats['score']}", font=('Arial', 12))
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.diff_var = tk.StringVar(value=self.difficulty)
        tk.OptionMenu(self.top_frame, self.diff_var, 'easy', 'medium', 'hard', command=self.set_difficulty).pack(side=tk.LEFT)

        self.board_frame = tk.Frame(master)
        self.board_frame.pack()

        for i in range(9):
            for j in range(9):
                e = tk.Entry(self.board_frame, width=2, font=('Arial', 18), justify='center')
                e.grid(row=i, column=j, padx=2, pady=2)
                self.entries[i][j] = e

        self.bottom_frame = tk.Frame(master)
        self.bottom_frame.pack(pady=10)

        tk.Button(self.bottom_frame, text="New Puzzle", command=self.new_puzzle).pack(side=tk.LEFT, padx=5)
        tk.Button(self.bottom_frame, text="Reset", command=self.reset_puzzle).pack(side=tk.LEFT, padx=5)
        tk.Button(self.bottom_frame, text="Check", command=self.check_solution).pack(side=tk.LEFT, padx=5)
        tk.Button(self.bottom_frame, text="Hint", command=self.give_hint).pack(side=tk.LEFT, padx=5)
        tk.Button(self.bottom_frame, text="Clear", command=self.clear_board).pack(side=tk.LEFT, padx=5)

        self.new_puzzle()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f:
                self.stats = json.load(f)
        else:
            self.stats = {"score": 0}
            self.save_stats()

    def save_stats(self):
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f)

    def set_difficulty(self, value):
        self.difficulty = value
        self.new_puzzle()

    def new_puzzle(self):
        self.start_time = time.time()
        self.update_timer()
        full = generate_full_board()
        puzzle = remove_cells(full, difficulty=self.difficulty)
        self.solution = full
        self.starting_puzzle = puzzle
        self.load_puzzle(puzzle)

    def load_puzzle(self, puzzle):
        for i in range(9):
            for j in range(9):
                e = self.entries[i][j]
                e.config(state='normal')
                e.delete(0, tk.END)
                if puzzle[i][j] != 0:
                    e.insert(0, str(puzzle[i][j]))
                    e.config(state='disabled', disabledforeground='black')
                    self.prefilled[i][j] = True
                else:
                    self.prefilled[i][j] = False

    def reset_puzzle(self):
        self.load_puzzle(self.starting_puzzle)
        self.start_time = time.time()

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                if not self.prefilled[i][j]:
                    self.entries[i][j].delete(0, tk.END)

    def check_solution(self):
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if not val.isdigit() or int(val) != self.solution[i][j]:
                    messagebox.showwarning("Oops!", "❌ Incorrect solution.")
                    return
        self.stats["score"] += 1
        self.save_stats()
        self.score_label.config(text=f"Score: {self.stats['score']}")
        messagebox.showinfo("Well done!", "✅ Sudoku solved correctly!")
        self.new_puzzle()

    def give_hint(self):
        for i in range(9):
            for j in range(9):
                if not self.prefilled[i][j] and not self.entries[i][j].get().isdigit():
                    self.entries[i][j].insert(0, str(self.solution[i][j]))
                    return

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed}s")
        self.timer_id = self.master.after(1000, self.update_timer)

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()

