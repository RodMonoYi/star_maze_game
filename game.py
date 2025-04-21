import tkinter as tk
from tkinter import messagebox
import heapq

GRID_SIZE = 21
CELL_SIZE = 30

MOVE_COSTS = {
    (0, 1): 10,
    (1, 0): 10,
    (0, -1): 10,
    (-1, 0): 10,
    (1, 1): 14,
    (-1, -1): 14,
    (1, -1): 14,
    (-1, 1): 14,
}


class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_wall = False
        self.is_start = False
        self.is_end = False
        self.g = float("inf")
        self.h = 0
        self.f = float("inf")
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f


def heuristic(a: Cell, b: Cell):
    dx = abs(a.col - b.col)
    dy = abs(a.row - b.row)
    return 10 * (dx + dy) + 4 * min(dx, dy)


def a_star(grid, start: Cell, end: Cell):
    open_set = []
    start.g = 0
    start.h = heuristic(start, end)
    start.f = start.h
    heapq.heappush(open_set, start)

    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)

        if current == end:
            return reconstruct_path(end)

        closed_set.add(current)

        for dx, dy in MOVE_COSTS:
            new_row = current.row + dy
            new_col = current.col + dx
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                neighbor = grid[new_row][new_col]

                if neighbor.is_wall or neighbor in closed_set:
                    continue

                if dx != 0 and dy != 0:  # movimento diagonal
                    if (
                        grid[current.row + dy][current.col].is_wall
                        or grid[current.row][current.col + dx].is_wall
                    ):
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
        self.root.configure(bg="#121212")
        self.root.geometry("750x800")
        self.root.resizable(False, False)

        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.start = None
        self.end = None
        self.path = []
        self.setting_mode = None

        self.setup_ui()
        self.draw_grid()

    def setup_ui(self):
        self.canvas = tk.Canvas(
            self.root,
            width=GRID_SIZE * CELL_SIZE,
            height=GRID_SIZE * CELL_SIZE,
            bg="#1e1e2f",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, columnspan=5, padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_click)

        self.cost_label = tk.Label(
            self.root,
            text="Custo: 0",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#121212",
        )
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
            "highlightcolor": "#888",
        }

        self.btn_start = tk.Button(
            self.root,
            text="Definir Início",
            command=lambda: self.set_mode("start"),
            **style,
        )
        self.btn_start.grid(row=1, column=1, padx=5)

        self.btn_end = tk.Button(
            self.root, text="Definir Fim", command=lambda: self.set_mode("end"), **style
        )
        self.btn_end.grid(row=1, column=2, padx=5)

        self.btn_run = tk.Button(
            self.root, text="Iniciar Caminho", command=self.run_pathfinding, **style
        )
        self.btn_run.grid(row=2, column=1, pady=10)

        self.btn_reset = tk.Button(
            self.root, text="Resetar Tudo", command=self.reset, **style
        )
        self.btn_reset.grid(row=2, column=2, pady=10)

    def set_mode(self, mode):
        self.setting_mode = mode

    def draw_grid(self):
        self.canvas.delete("all")
        num = 1

        wall_numbers = [
            13,
            16,
            17,
            18,
            22,
            23,
            25,
            26,
            28,
            30,
            31,
            32,
            34,
            41,
            43,
            47,
            49,
            53,
            55,
            56,
            57,
            58,
            60,
            62,
            64,
            66,
            67,
            68,
            72,
            73,
            74,
            76,
            81,
            83,
            85,
            89,
            91,
            102,
            104,
            106,
            107,
            108,
            112,
            114,
            116,
            118,
            119,
            120,
            121,
            123,
            139,
            148,
            150,
            152,
            153,
            154,
            156,
            157,
            158,
            162,
            163,
            165,
            166,
            167,
            169,
            170,
            171,
            173,
            174,
            175,
            177,
            178,
            179,
            183,
            184,
            186,
            187,
            188,
            204,
            205,
            211,
            213,
            215,
            217,
            218,
            219,
            220,
            221,
            224,
            227,
            229,
            230,
            231,
            232,
            234,
            236,
            238,
            239,
            240,
            242,
            245,
            248,
            252,
            253,
            255,
            256,
            257,
            259,
            260,
            261,
            263,
            266,
            269,
            271,
            273,
            281,
            284,
            287,
            290,
            292,
            294,
            296,
            302,
            305,
            308,
            311,
            313,
            315,
            317,
            323,
            326,
            329,
            336,
            338,
            340,
            341,
            342,
            344,
            345,
            346,
            347,
            348,
            349,
            350,
            351,
            352,
            354,
            355,
            356,
            357,
            362,
            380,
            381,
            382,
            383,
            386,
            387,
            389,
            390,
            391,
            394,
            395,
            397,
            398,
            407,
            410,
            412,
            415,
            416,
            418,
            419,
            423,
            424,
            425,
            426,
            428,
            433,
        ]

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                color = "#ffeb3b"
                cell_number = row * GRID_SIZE + col + 1

                cell = self.grid[row][col]
                cell.is_wall = cell_number in wall_numbers
                if cell.is_wall:
                    color = "#0000ff"
                elif cell.is_start:
                    color = "#4caf50"
                elif cell.is_end:
                    color = "#e53935"
                elif cell in self.path:
                    color = "#4caf50"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444")
                self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=str(num),
                    fill="#000000",
                    font=("Segoe UI", 8, "bold"),
                )
                num += 1

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            cell = self.grid[row][col]
            if self.setting_mode == "start":
                if self.start:
                    self.start.is_start = False
                self.start = cell
                cell.is_start = True
            elif self.setting_mode == "end":
                if self.end:
                    self.end.is_end = False
                self.end = cell
                cell.is_end = True
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
                cell.g = float("inf")
                cell.f = float("inf")
                cell.h = 0
                cell.parent = None
        self.path = []

    def reset(self):
        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.start = None
        self.end = None
        self.path = []
        self.draw_grid()


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
