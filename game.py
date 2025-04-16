import tkinter as tk
from tkinter import messagebox
import heapq

GRID_SIZE = 21
CELL_SIZE = 30

MOVE_COSTS = {
    (0, 1): 10, (1, 0): 10, (0, -1): 10, (-1, 0): 10,
    (1, 1): 14, (-1, -1): 14, (1, -1): 14, (-1, 1): 14
}

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_wall = False
        self.is_start = False
        self.is_end = False
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a: Cell, b: Cell):
    dx = abs(a.col - b.col)
    dy = abs(a.row - b.row)
    return 10 * (dx + dy) + (4 * min(dx, dy))

def a_star(grid, start: Cell, end: Cell):
    open_set = []
    start.g = 0
    start.h = heuristic(start, end)
    start.f = start.h
    heapq.heappush(open_set, start)

    while open_set:
        current = heapq.heappop(open_set)

        if current == end:
            return reconstruct_path(end)

        for dx, dy in MOVE_COSTS:
            new_row, new_col = current.row + dy, current.col + dx
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                neighbor = grid[new_row][new_col]
                if neighbor.is_wall:
                    continue
                temp_g = current.g + MOVE_COSTS[(dx, dy)]
                if temp_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = temp_g
                    neighbor.h = heuristic(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h
                    if neighbor not in open_set:
                        heapq.heappush(open_set, neighbor)
    return []

def reconstruct_path(end_cell):
    path = []
    current = end_cell
    while current:
        path.append(current)
        current = current.parent
    return path[::-1]

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Labirinto com A* (A Estrela)")
        self.root.configure(bg='#121212')
        self.root.geometry("750x800")
        self.root.resizable(False, False)
        self.root.tk_setPalette(background='#121212', foreground='white')

        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.start = None
        self.end = None
        self.path = []
        self.setting_mode = None

        self.setup_ui()
        self.draw_grid()

    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg='#1e1e2f', highlightthickness=0, bd=0)
        self.canvas.grid(row=0, column=0, columnspan=5, padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_click)

        self.cost_label = tk.Label(self.root, text="Custo: 0", font=("Segoe UI", 16, "bold"), fg="white", bg="#121212")
        self.cost_label.grid(row=1, column=0, pady=10)

        style = {
            "font": ("Segoe UI", 11, "bold"),
            "bg": "#333",
            "fg": "white",
            "activebackground": "#555",
            "activeforeground": "white",
            "width": 16,
            "relief": tk.FLAT,
            "cursor": "hand2",
            "bd": 2,
            "highlightbackground": "#555",
            "highlightcolor": "#888"
        }

        self.btn_start = tk.Button(self.root, text="Definir Início", command=lambda: self.set_mode('start'), **style)
        self.btn_start.grid(row=1, column=1, padx=5)

        self.btn_end = tk.Button(self.root, text="Definir Fim", command=lambda: self.set_mode('end'), **style)
        self.btn_end.grid(row=1, column=2, padx=5)

        self.btn_wall = tk.Button(self.root, text="Definir Paredes", command=lambda: self.set_mode('wall'), **style)
        self.btn_wall.grid(row=1, column=3, padx=5)

        self.btn_run = tk.Button(self.root, text="Iniciar Caminho", command=self.run_pathfinding, **style)
        self.btn_run.grid(row=2, column=1, pady=10)

        self.btn_reset = tk.Button(self.root, text="Resetar Tudo", command=self.reset, **style)
        self.btn_reset.grid(row=2, column=2, pady=10)

    def set_mode(self, mode):
        self.setting_mode = mode

    def draw_grid(self):
        self.canvas.delete("all")
        for row in self.grid:
            for cell in row:
                x1 = cell.col * CELL_SIZE
                y1 = cell.row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = "#2d2d2d"
                if cell.is_wall:
                    color = "#111"
                elif cell.is_start:
                    color = "#4caf50"
                elif cell.is_end:
                    color = "#e53935"
                elif cell in self.path:
                    color = "#1e88e5"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444")
                if cell.g != float('inf') and not cell.is_wall:
                    self.canvas.create_text((x1 + x2)//2, (y1 + y2)//2, text=str(int(cell.g)), fill="#cccccc", font=("Segoe UI", 8, "bold"))

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            cell = self.grid[row][col]
            if self.setting_mode == 'start':
                if self.start:
                    self.start.is_start = False
                self.start = cell
                cell.is_start = True
            elif self.setting_mode == 'end':
                if self.end:
                    self.end.is_end = False
                self.end = cell
                cell.is_end = True
            elif self.setting_mode == 'wall':
                if cell != self.start and cell != self.end:
                    cell.is_wall = not cell.is_wall
            self.draw_grid()

    def run_pathfinding(self):
        if not self.start or not self.end:
            messagebox.showwarning("Aviso", "Defina início e fim.")
            return
        self.reset_pathfinding()
        self.path = a_star(self.grid, self.start, self.end)
        cost = self.end.g if self.path else 0
        self.cost_label.config(text=f"Custo: {cost}")
        self.draw_grid()

    def reset_pathfinding(self):
        for row in self.grid:
            for cell in row:
                cell.g = float('inf')
                cell.h = 0
                cell.f = float('inf')
                cell.parent = None
        self.path = []

    def reset(self):
        self.start = None
        self.end = None
        for row in self.grid:
            for cell in row:
                cell.is_wall = False
                cell.is_start = False
                cell.is_end = False
        self.reset_pathfinding()
        self.cost_label.config(text="Custo: 0")
        self.draw_grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
