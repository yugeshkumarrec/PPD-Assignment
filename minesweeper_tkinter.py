import tkinter as tk
import random

ROWS, COLS, MINES = 10, 10, 15
CELL, PAD, TOP = 38, 12, 110
WIDTH = COLS * CELL + PAD * 2
HEIGHT = ROWS * CELL + TOP + PAD

class MineSweeper:
    def __init__(self, root):
        self.root = root
        root.title("Minesweeper - Python Tkinter")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#172334", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Button-2>", self.right_click)
        root.bind("r", self.restart)
        root.bind("R", self.restart)
        self.new_game()

    def new_game(self, event=None):
        self.grid = [[{"mine": False, "revealed": False, "flag": False, "count": 0}
                      for _ in range(COLS)] for _ in range(ROWS)]
        for r, c in random.sample([(r, c) for r in range(ROWS) for c in range(COLS)], MINES):
            self.grid[r][c]["mine"] = True
        self.recalculate_counts()
        self.game_over = self.won = False
        self.flags_used = 0
        self.first_click = True
        self.draw()

    def neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    yield nr, nc

    def recalculate_counts(self):
        for r in range(ROWS):
            for c in range(COLS):
                self.grid[r][c]["count"] = sum(self.grid[nr][nc]["mine"] for nr, nc in self.neighbors(r, c))

    def get_cell(self, event):
        c = (event.x - PAD) // CELL
        r = (event.y - TOP) // CELL
        if 0 <= r < ROWS and 0 <= c < COLS and event.y >= TOP:
            return r, c
        return None

    def left_click(self, event):
        if self.game_over or self.won:
            return
        pos = self.get_cell(event)
        if not pos:
            return
        r, c = pos
        cell = self.grid[r][c]
        if cell["flag"] or cell["revealed"]:
            return
        if self.first_click:
            self.first_click = False
            if cell["mine"]:
                cell["mine"] = False
                rr, cc = random.choice([(i, j) for i in range(ROWS) for j in range(COLS)
                                        if not self.grid[i][j]["mine"] and (i, j) != (r, c)])
                self.grid[rr][cc]["mine"] = True
                self.recalculate_counts()
        self.reveal(r, c)
        self.check_win()
        self.draw()

    def reveal(self, r, c):
        cell = self.grid[r][c]
        if cell["revealed"] or cell["flag"]:
            return
        cell["revealed"] = True
        if cell["mine"]:
            self.game_over = True
            return
        if cell["count"] == 0:
            for nr, nc in self.neighbors(r, c):
                if not self.grid[nr][nc]["revealed"]:
                    self.reveal(nr, nc)

    def right_click(self, event):
        if self.game_over or self.won:
            return
        pos = self.get_cell(event)
        if not pos:
            return
        r, c = pos
        cell = self.grid[r][c]
        if cell["revealed"]:
            return
        if cell["flag"]:
            cell["flag"] = False
            self.flags_used -= 1
        elif self.flags_used < MINES:
            cell["flag"] = True
            self.flags_used += 1
        self.check_win()
        self.draw()

    def check_win(self):
        safe = sum(self.grid[r][c]["revealed"] and not self.grid[r][c]["mine"]
                   for r in range(ROWS) for c in range(COLS))
        if safe == ROWS * COLS - MINES and not self.game_over:
            self.won = True

    def restart(self, event=None):
        self.new_game()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, TOP, fill="#172334", outline="")
        self.canvas.create_text(WIDTH/2, 24, text="MINESWEEPER", fill="#f0d58a", font=("Arial", 19, "bold"))
        self.canvas.create_text(16, 62, anchor="w", text=f"MINES: {MINES}    FLAGS: {self.flags_used}",
                                fill="#e7edf4", font=("Arial", 10, "bold"))
        self.canvas.create_text(WIDTH-16, 62, anchor="e", text="R = NEW GAME", fill="#aebfd0", font=("Arial", 9, "bold"))
        self.canvas.create_text(WIDTH/2, 88, text="Left-click: reveal    Right-click: flag", fill="#b7c6d5", font=("Arial", 9))
        colors = {1:"#2674d8", 2:"#26854a", 3:"#d63d3d", 4:"#633fbd", 5:"#a0442b", 6:"#168b91", 7:"#202020", 8:"#666666"}
        for r in range(ROWS):
            for c in range(COLS):
                cell = self.grid[r][c]
                x1, y1 = PAD+c*CELL, TOP+r*CELL
                x2, y2 = x1+CELL-2, y1+CELL-2
                if cell["revealed"]:
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill="#d5dee7",outline="#a7b5c3")
                    if cell["mine"]:
                        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text="✹",fill="#d83c4b",font=("Arial",17,"bold"))
                    elif cell["count"]:
                        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text=str(cell["count"]),fill=colors[cell["count"]],font=("Arial",15,"bold"))
                else:
                    self.canvas.create_rectangle(x1,y1,x2,y2,fill="#496078",outline="#71869a",width=2)
                    if cell["flag"]:
                        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text="⚑",fill="#ffdc78",font=("Arial",17,"bold"))
                    elif self.game_over and cell["mine"]:
                        self.canvas.create_text((x1+x2)/2,(y1+y2)/2,text="✹",fill="#ff7b7b",font=("Arial",16,"bold"))
        if self.game_over:
            self.banner("BOOM! GAME OVER — Press R", "#722d3b")
        elif self.won:
            self.banner("YOU WIN! — Press R to play again", "#206644")

    def banner(self, text, color):
        self.canvas.create_rectangle(35, HEIGHT/2-24, WIDTH-35, HEIGHT/2+24, fill=color, outline="white", width=2)
        self.canvas.create_text(WIDTH/2, HEIGHT/2, text=text, fill="white", font=("Arial", 11, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = MineSweeper(root)
    root.mainloop()
