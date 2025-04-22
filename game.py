import tkinter as tk
from tkinter import messagebox, ttk
import heapq
import time

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

# Cores acessíveis
COLORS = {
    'background': '#1e1e2f',
    'grid': '#444',
    'wall': '#3a3a7a',
    'start': '#2e7d32',
    'end': '#c62828',
    'path': '#4caf50',
    'explored': '#ff8f00',
    'considered': '#ffcc80',
    'text': '#000000',
    'button_bg': '#333',
    'button_fg': 'white'
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
        self.considered = False
        self.explored = False

    def __lt__(self, other):
        return self.f < other.f


def heuristic(a: Cell, b: Cell):
    dx = abs(a.col - b.col)
    dy = abs(a.row - b.row)
    return 10 * (dx + dy) + 4 * min(dx, dy)


def a_star(grid, start: Cell, end: Cell, app=None):
    open_set = []
    start.g = 0
    start.h = heuristic(start, end)
    start.f = start.h
    heapq.heappush(open_set, start)

    closed_set = set()

    while open_set:
        current = heapq.heappop(open_set)
        current.explored = True

        if app:
            app.update_cell_display(current)
            time.sleep(0.05)

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
                    if (grid[current.row + dy][current.col].is_wall or 
                        grid[current.row][current.col + dx].is_wall):
                        continue

                temp_g = current.g + MOVE_COSTS[(dx, dy)]
                if temp_g < neighbor.g:
                    neighbor.parent = current
                    neighbor.g = temp_g
                    neighbor.h = heuristic(neighbor, end)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.considered = True
                    
                    if app:
                        app.update_cell_display(neighbor)
                        time.sleep(0.03)
                    
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
        self.root.geometry("800x850")
        self.root.resizable(False, False)

        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.start = None
        self.end = None
        self.path = []
        self.setting_mode = None
        self.is_paused = False
        self.step_requested = False
        self.after_id = None
        self.show_cell_numbers = True  # Mostrar números das células por padrão

        self.setup_ui()
        self.draw_grid()
        self.setup_context_menu()

    def setup_ui(self):
        # Configuração do canvas
        self.canvas = tk.Canvas(
            self.root,
            width=GRID_SIZE * CELL_SIZE,
            height=GRID_SIZE * CELL_SIZE,
            bg=COLORS['background'],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, columnspan=5, padx=20, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # Controles de informação
        self.cost_label = tk.Label(
            self.root,
            text="Custo: 0",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#121212",
        )
        self.cost_label.grid(row=1, column=0, pady=5, sticky="w")

        self.status_label = tk.Label(
            self.root,
            text="Status: Pronto",
            font=("Segoe UI", 12),
            fg="white",
            bg="#121212",
        )
        self.status_label.grid(row=1, column=1, columnspan=3, pady=5)

        # Botões de controle
        style = {
            "font": ("Segoe UI", 11, "bold"),
            "bg": COLORS['button_bg'],
            "fg": COLORS['button_fg'],
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
        self.btn_start.grid(row=2, column=0, padx=5, pady=5)

        self.btn_end = tk.Button(
            self.root, 
            text="Definir Fim", 
            command=lambda: self.set_mode("end"), 
            **style
        )
        self.btn_end.grid(row=2, column=1, padx=5, pady=5)

        self.btn_run = tk.Button(
            self.root, 
            text="Executar Tudo", 
            command=self.run_pathfinding, 
            **style
        )
        self.btn_run.grid(row=3, column=0, padx=5, pady=5)

        self.btn_step = tk.Button(
            self.root,
            text="Passo a Passo",
            command=self.step_pathfinding,
            **style,
        )
        self.btn_step.grid(row=3, column=1, padx=5, pady=5)

        self.btn_pause = tk.Button(
            self.root,
            text="Pausar",
            command=self.toggle_pause,
            **style,
        )
        self.btn_pause.grid(row=3, column=2, padx=5, pady=5)

        self.btn_reset = tk.Button(
            self.root, 
            text="Resetar Tudo", 
            command=self.reset, 
            **style
        )
        self.btn_reset.grid(row=3, column=3, padx=5, pady=5)
        
        # Novo botão para alternar a exibição
        self.btn_toggle_display = tk.Button(
            self.root,
            text="Mostrar Valores G/H/F",
            command=self.toggle_cell_display,
            **style,
        )
        self.btn_toggle_display.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

    def toggle_cell_display(self):
        """Alterna entre mostrar números das células ou valores G/H/F"""
        self.show_cell_numbers = not self.show_cell_numbers
        self.btn_toggle_display.config(
            text="Mostrar Números" if not self.show_cell_numbers else "Mostrar Valores G/H/F"
        )
        self.draw_grid()

    def setup_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Definir como início", 
            command=lambda: self.set_cell_from_context("start")
        )
        self.context_menu.add_command(
            label="Definir como fim", 
            command=lambda: self.set_cell_from_context("end")
        )
        self.context_menu.add_command(
            label="Alternar parede", 
            command=lambda: self.set_cell_from_context("wall")
        )

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def set_cell_from_context(self, mode):
        if hasattr(self, 'context_cell'):
            row, col = self.context_cell
            cell = self.grid[row][col]
            
            if mode == "start":
                if cell.is_wall:
                    messagebox.showwarning("Aviso", "Não é possível definir parede como início.")
                    return
                if self.start:
                    self.start.is_start = False
                self.start = cell
                cell.is_start = True
            elif mode == "end":
                if cell.is_wall:
                    messagebox.showwarning("Aviso", "Não é possível definir parede como fim.")
                    return
                if self.end:
                    self.end.is_end = False
                self.end = cell
                cell.is_end = True
            elif mode == "wall":
                if cell.is_start or cell.is_end:
                    messagebox.showwarning("Aviso", "Não é possível transformar início/fim em parede.")
                    return
                cell.is_wall = not cell.is_wall
            
            self.draw_grid()

    def set_mode(self, mode):
        self.setting_mode = mode
        self.status_label.config(text=f"Status: Definindo {mode}")

    def draw_grid(self):
        self.canvas.delete("all")
        num = 1

        wall_numbers = [
            13, 16, 17, 18, 22, 23, 25, 26, 28, 30, 31, 32, 34, 41, 43, 47, 49, 53, 
            55, 56, 57, 58, 60, 62, 64, 66, 67, 68, 72, 73, 74, 76, 81, 83, 85, 89, 91,
            102, 104, 106, 107, 108, 112, 114, 116, 118, 119, 120, 121, 123, 139, 148,
            150, 152, 153, 154, 156, 157, 158, 162, 163, 165, 166, 167, 169, 170, 171,
            173, 174, 175, 177, 178, 179, 183, 184, 186, 187, 188, 204, 205, 211, 213,
            215, 217, 218, 219, 220, 221, 224, 227, 229, 230, 231, 232, 234, 236, 238,
            239, 240, 242, 245, 248, 252, 253, 255, 256, 257, 259, 260, 261, 263, 266,
            269, 271, 273, 281, 284, 287, 290, 292, 294, 296, 302, 305, 308, 311, 313,
            315, 317, 323, 326, 329, 336, 338, 340, 341, 342, 344, 345, 346, 347, 348,
            349, 350, 351, 352, 354, 355, 356, 357, 362, 380, 381, 382, 383, 386, 387,
            389, 390, 391, 394, 395, 397, 398, 407, 410, 412, 415, 416, 418, 419, 423,
            424, 425, 426, 428, 433
        ]

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.grid[row][col]
                cell_number = row * GRID_SIZE + col + 1
                cell.is_wall = cell_number in wall_numbers

                if cell.is_wall:
                    color = COLORS['wall']
                elif cell.is_start:
                    color = COLORS['start']
                elif cell.is_end:
                    color = COLORS['end']
                elif cell in self.path:
                    color = COLORS['path']
                elif cell.explored:
                    color = COLORS['explored']
                elif cell.considered:
                    color = COLORS['considered']
                else:
                    color = "#ffeb3b"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS['grid'])
                
                # Mostra número da célula ou valores G/H/F
                if self.show_cell_numbers:
                    text = str(num)
                    font_size = 8
                else:
                    if cell.g != float('inf') or cell.h != 0 or cell.f != float('inf'):
                        text = f"G:{int(cell.g)}\nH:{int(cell.h)}\nF:{int(cell.f)}"
                        font_size = 6
                    else:
                        text = str(num)
                        font_size = 8
                
                self.canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=text,
                    fill=COLORS['text'],
                    font=("Segoe UI", font_size, "bold"),
                )
                num += 1

    def update_cell_display(self, cell):
        x1 = cell.col * CELL_SIZE
        y1 = cell.row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        if cell.is_wall:
            color = COLORS['wall']
        elif cell.is_start:
            color = COLORS['start']
        elif cell.is_end:
            color = COLORS['end']
        elif cell.explored:
            color = COLORS['explored']
        elif cell.considered:
            color = COLORS['considered']
        else:
            color = "#ffeb3b"

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLORS['grid'])
        
        # Mostra número da célula ou valores G/H/F
        if self.show_cell_numbers:
            text = str(cell.row * GRID_SIZE + cell.col + 1)
            font_size = 8
        else:
            if cell.g != float('inf') or cell.h != 0 or cell.f != float('inf'):
                text = f"G:{int(cell.g)}\nH:{int(cell.h)}\nF:{int(cell.f)}"
                font_size = 6
            else:
                text = str(cell.row * GRID_SIZE + cell.col + 1)
                font_size = 8
        
        self.canvas.create_text(
            (x1 + x2) // 2,
            (y1 + y2) // 2,
            text=text,
            fill=COLORS['text'],
            font=("Segoe UI", font_size, "bold"),
        )

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.context_cell = (row, col)  # Salva para uso no menu de contexto
            cell = self.grid[row][col]
            
            if self.setting_mode == "start":
                if cell.is_wall:
                    messagebox.showwarning("Aviso", "Não é possível definir parede como início.")
                    return
                if self.start:
                    self.start.is_start = False
                self.start = cell
                cell.is_start = True
                self.draw_grid()
            elif self.setting_mode == "end":
                if cell.is_wall:
                    messagebox.showwarning("Aviso", "Não é possível definir parede como fim.")
                    return
                if self.end:
                    self.end.is_end = False
                self.end = cell
                cell.is_end = True
                self.draw_grid()

    def check_path_possible(self):
        if not self.start or not self.end:
            return False
            
        # Verificação simples de conectividade (pode ser melhorada)
        open_set = [self.start]
        closed_set = set()
        
        while open_set:
            current = open_set.pop()
            
            if current == self.end:
                return True
                
            closed_set.add(current)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row = current.row + dy
                new_col = current.col + dx
                
                if (0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE):
                    neighbor = self.grid[new_row][new_col]
                    if not neighbor.is_wall and neighbor not in closed_set:
                        open_set.append(neighbor)
        
        return False

    def run_pathfinding(self):
        if not self.start or not self.end:
            messagebox.showwarning("Aviso", "Defina início e fim.")
            return
            
        if not self.check_path_possible():
            messagebox.showwarning("Aviso", "Não há caminho possível entre início e fim.")
            return
            
        self.reset_pathfinding()
        self.status_label.config(text="Status: Executando...")
        self.root.update()
        
        # Executa em uma thread separada para não travar a interface
        self.path = a_star(self.grid, self.start, self.end, self)
        
        if self.path:
            cost = self.end.g
            self.cost_label.config(text=f"Custo: {cost}")
            self.status_label.config(text="Status: Caminho encontrado!")
        else:
            self.cost_label.config(text="Custo: 0")
            self.status_label.config(text="Status: Nenhum caminho encontrado!")
            messagebox.showwarning("Aviso", "Nenhum caminho encontrado!")
            
        self.draw_grid()

    def step_pathfinding(self):
        if not hasattr(self, 'pathfinder_gen'):
            self.reset_pathfinding()
            self.status_label.config(text="Status: Modo passo a passo")
            self.pathfinder_gen = self.a_star_generator(self.grid, self.start, self.end)
            
        try:
            if not self.is_paused:
                result = next(self.pathfinder_gen)
                if result == "done":
                    if self.path:
                        cost = self.end.g
                        self.cost_label.config(text=f"Custo: {cost}")
                        self.status_label.config(text="Status: Caminho encontrado!")
                    else:
                        self.cost_label.config(text="Custo: 0")
                        self.status_label.config(text="Status: Nenhum caminho encontrado!")
                    del self.pathfinder_gen
        except StopIteration:
            del self.pathfinder_gen

    def a_star_generator(self, grid, start, end):
        open_set = []
        start.g = 0
        start.h = heuristic(start, end)
        start.f = start.h
        heapq.heappush(open_set, start)

        closed_set = set()

        while open_set:
            if self.is_paused and not self.step_requested:
                yield "paused"
                continue
                
            self.step_requested = False
            
            current = heapq.heappop(open_set)
            current.explored = True
            self.update_cell_display(current)
            yield "step"

            if current == end:
                self.path = reconstruct_path(end)
                self.draw_grid()
                yield "done"
                return

            closed_set.add(current)

            for dx, dy in MOVE_COSTS:
                new_row = current.row + dy
                new_col = current.col + dx
                if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                    neighbor = grid[new_row][new_col]

                    if neighbor.is_wall or neighbor in closed_set:
                        continue

                    if dx != 0 and dy != 0:  # movimento diagonal
                        if (grid[current.row + dy][current.col].is_wall or 
                            grid[current.row][current.col + dx].is_wall):
                            continue

                    temp_g = current.g + MOVE_COSTS[(dx, dy)]
                    if temp_g < neighbor.g:
                        neighbor.parent = current
                        neighbor.g = temp_g
                        neighbor.h = heuristic(neighbor, end)
                        neighbor.f = neighbor.g + neighbor.h
                        neighbor.considered = True
                        self.update_cell_display(neighbor)
                        yield "step"
                        
                        if neighbor not in open_set:
                            heapq.heappush(open_set, neighbor)

        self.path = []
        self.draw_grid()
        yield "done"

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.btn_pause.config(text="Continuar" if self.is_paused else "Pausar")
        if not self.is_paused and hasattr(self, 'pathfinder_gen'):
            self.step_pathfinding()

    def reset_pathfinding(self):
        for row in self.grid:
            for cell in row:
                cell.g = float("inf")
                cell.f = float("inf")
                cell.h = 0
                cell.parent = None
                cell.considered = False
                cell.explored = False
        self.path = []
        if hasattr(self, 'pathfinder_gen'):
            del self.pathfinder_gen
        self.is_paused = False
        self.step_requested = False
        self.btn_pause.config(text="Pausar")

    def reset(self):
        self.grid = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
        self.start = None
        self.end = None
        self.path = []
        self.reset_pathfinding()
        self.draw_grid()
        self.status_label.config(text="Status: Pronto")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()