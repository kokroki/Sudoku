import tkinter as tk
from tkinter import ttk, messagebox
from game import SudokuGameLogic


# Цвета
APP_BG = "#f7f3ec"          # фон окна
CELL_BG_1 = "#ffffff"       # светлые блоки 3×3
CELL_BG_2 = "#f0e7da"       # тёмные блоки 3×3
GRID_BG = "#d6c6b3"         # рамка сетки и разделители
TEXT_COLOR = "#1c1c1e"      # весь текст (подсказки и ввод)
BUTTON_BG = "#eadbc8"       # фон кнопок
SELECT_COLOR = "#cfe3ff"    # выбранная ячейка
ERROR_COLOR = "#fde8e8"     # ячейка с ошибкой


# Параметры ячейки сетки
# Шрифт одинаковый для подсказок и ввода — иначе ячейки разного размера,
# потому что width=2 в Entry считается в символах конкретного шрифта
ENTRY_STYLE = {
    "width": 2,
    "font": ("Segoe UI", 18, "bold"),
    "justify": "center",
    "fg": TEXT_COLOR,
    "relief": "flat",
    "bd": 0,
    "highlightthickness": 0,  # убираем стандартную синюю рамку фокуса
    "insertbackground": TEXT_COLOR,
}


# Готовое судоку для декоративного превью в главном меню
_DEMO = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

# Координаты ячеек превью, которые отображаются как заданные (жирные)
_GIVEN = {
    (0, 0), (0, 4), (0, 8),
    (1, 2), (1, 6),
    (2, 1), (2, 5),
    (3, 0), (3, 3), (3, 7),
    (4, 2), (4, 4), (4, 6),
    (5, 1), (5, 5), (5, 8),
    (6, 3), (6, 7),
    (7, 2), (7, 6),
    (8, 0), (8, 4), (8, 8),
}


# Главное меню
class MainMenu:

    # Настраивает окно и запускает отрисовку
    def __init__(self, root):
        self.root = root
        self.root.title("Судоку")
        self.root.geometry("860x540")
        self.root.configure(bg=APP_BG)
        self.root.resizable(False, False)
        self._draw()

    # Строит весь интерфейс меню: левая колонка с превью, разделитель, правая с кнопками
    def _draw(self):
        # Левая колонка — декоративная сетка судоку
        left = tk.Frame(self.root, bg=APP_BG, width=390)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)  # фиксируем ширину, не даём сжаться под содержимое
        self._build_sudoku_canvas(left)

        # Вертикальная линия-разделитель между колонками
        tk.Frame(self.root, bg=GRID_BG, width=1).pack(side="left", fill="y", pady=48)

        # Правая колонка — заголовок и кнопки
        right = tk.Frame(self.root, bg=APP_BG)
        right.pack(side="right", fill="both", expand=True)

        # inner центрируется по вертикали через place
        inner = tk.Frame(right, bg=APP_BG)
        inner.place(relx=0.5, rely=0.47, anchor="center")

        tk.Label(inner, text="数独", font=("Segoe UI", 58, "bold"), bg=APP_BG, fg="#e8d5c0").pack()
        tk.Label(inner, text="СУДОКУ", font=("Segoe UI", 40, "bold"), bg=APP_BG, fg=TEXT_COLOR).pack(pady=(0, 2))
        tk.Label(inner, text="Логическая головоломка", font=("Segoe UI", 13), bg=APP_BG, fg="#a09080").pack(pady=(0, 20))

        tk.Frame(inner, bg=GRID_BG, height=1, width=240).pack(pady=(0, 26))

        self._make_btn(inner, "Играть", BUTTON_BG, TEXT_COLOR, self.start_game, large=True)
        self._make_btn(inner, "Правила", BUTTON_BG, TEXT_COLOR, self.show_rules)
        self._make_btn(inner, "Выход", "#edddd0", "#c0392b", self.root.destroy)

    # Создаёт кнопку на основе Label с подсветкой при наведении.
    # Используем Label вместо Button, чтобы убрать стандартный рельеф tkinter
    def _make_btn(self, parent, text, bg, fg, cmd, large=False):
        lbl = tk.Label(parent, text=text, bg=bg, fg=fg, width=22,
                       font=("Segoe UI", 15, "bold") if large else ("Segoe UI", 13),
                       pady=13 if large else 10)
        lbl.pack(pady=5)
        hover = "#ddd0c0"
        lbl.bind("<Enter>", lambda e: lbl.config(bg=hover))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))
        lbl.bind("<Button-1>", lambda e: cmd())

    # Рисует декоративную сетку 9×9 на Canvas.
    # Граница между блоками — THICK, внутри блока — THIN.
    # Фон сетки (GRID_BG) просвечивает через зазоры между ячейками как линии
    def _build_sudoku_canvas(self, parent):
        CELL = 37   # размер ячейки в пикселях
        THIN = 1    # зазор внутри блока
        THICK = 3   # зазор между блоками
        CW, CH = 390, 540

        grid_size = 9 * CELL + 6 * THIN + 2 * THICK
        ox = (CW - grid_size) // 2  # отступ слева для центрирования
        oy = (CH - grid_size) // 2  # отступ сверху для центрирования

        def cx(c):  # возвращает X-координату левого края ячейки колонки c
            return ox + c * CELL + c * THIN + (c // 3) * (THICK - THIN)

        def cy(r):  # возвращает Y-координату верхнего края ячейки строки r
            return oy + r * CELL + r * THIN + (r // 3) * (THICK - THIN)

        cv = tk.Canvas(parent, bg=APP_BG, highlightthickness=0, width=CW, height=CH)
        cv.pack()

        # Заливаем фон всей сетки — он будет виден как разделители
        cv.create_rectangle(
            ox - THICK, oy - THICK,
            ox + grid_size + THICK, oy + grid_size + THICK,
            fill=GRID_BG, outline=""
        )

        for r in range(9):
            for c in range(9):
                x0, y0 = cx(c), cy(r)
                x1, y1 = x0 + CELL, y0 + CELL

                # Чётные и нечётные блоки чередуются по цвету
                fill = CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2
                cv.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

                is_given = (r, c) in _GIVEN
                cv.create_text(
                    (x0 + x1) // 2, (y0 + y1) // 2,
                    text=str(_DEMO[r][c]),
                    font=("Segoe UI", 13, "bold" if is_given else "normal"),
                    fill=TEXT_COLOR,
                )

    # Показывает диалог с правилами игры
    def show_rules(self):
        messagebox.showinfo(
            "Правила игры",
            "Заполните поле числами от 1 до 9:\n\n"
            "  •  Каждая строка содержит все цифры 1–9\n"
            "  •  Каждый столбец содержит все цифры 1–9\n"
            "  •  Каждый блок 3×3 содержит все цифры 1–9\n\n"
            "Допускается не более 3 ошибок.",
        )

    # Удаляет виджеты меню и запускает игровой экран
    def start_game(self):
        for w in self.root.winfo_children():
            w.destroy()
        SudokuGame(self.root)


# Игровой экран
class SudokuGame:

    # Инициализирует экран: настраивает окно, создаёт логику и строит интерфейс
    def __init__(self, root):
        self.root = root
        self.root.title("Судоку")
        self.root.geometry("850x520")
        self.root.configure(background=APP_BG)

        # ttk.Combobox требует отдельной настройки через ttk.Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TCombobox",
                        fieldbackground=BUTTON_BG, background=BUTTON_BG,
                        foreground=TEXT_COLOR, borderwidth=0, padding=5,
                        font=("Segoe UI", 12))

        self.game = SudokuGameLogic()
        self.cells = {}               # (row, col) → виджет Entry
        self.error_cells = set()      # координаты ячеек с ошибками
        self.selected_position = None # координаты выбранной ячейки
        self.highlighted_cells = set() # координаты подсвеченных ячеек
        self.game_finished = False

        self.create_title()
        self.create_layout()

    # Создаёт кнопку «← Назад» и заголовок «Судоку» вверху экрана
    def create_title(self):
        back_btn = tk.Label(self.root, text="← Назад",
                            bg=BUTTON_BG, fg=TEXT_COLOR,
                            font=("Segoe UI", 12), padx=20, pady=6)
        back_btn.place(x=15, y=15)
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#ddd0c0"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg=BUTTON_BG))
        back_btn.bind("<Button-1>", self.back_to_menu)

        tk.Label(self.root, text="Судоку",
                 font=("Segoe UI", 26, "bold"), background=APP_BG, foreground=TEXT_COLOR
                 ).pack(pady=10)

    # Строит основной макет: центрированная сетка и нижняя панель управления
    def create_layout(self):
        main_frame = tk.Frame(self.root, background=APP_BG)
        main_frame.pack(fill="both", expand=True)

        center_frame = tk.Frame(main_frame, background=APP_BG)
        center_frame.pack(expand=True)

        self.grid_frame = tk.Frame(center_frame, background=GRID_BG)
        self.grid_frame.pack()

        for i in range(9):
            self.grid_frame.grid_rowconfigure(i, weight=1)
            self.grid_frame.grid_columnconfigure(i, weight=1)

        self.create_grid()

        # after(1) нужен потому что tkinter не всегда применяет readonlybackground
        # сразу после grid() — ждём 1 мс и обновляем принудительно
        self.root.after(1, self._fix_readonly_colors)

        # Нижняя панель: выбор сложности, кнопка новой игры, счётчик ошибок
        bottom_panel = tk.Frame(self.root, background=APP_BG)
        bottom_panel.pack(side="bottom", pady=15)

        self.difficulty_box = ttk.Combobox(
            bottom_panel, values=["Лёгкий", "Средний", "Сложный"],
            state="readonly", style="Custom.TCombobox", width=12, font=("Segoe UI", 12))
        self.difficulty_box.current(1)  # средний по умолчанию
        self.difficulty_box.pack(side="left", padx=15)
        self.difficulty_box.bind("<<ComboboxSelected>>", self.change_difficulty)

        self.create_buttons(bottom_panel)

        self.error_label = tk.Label(
            bottom_panel,
            text=f"Ошибки: {self.game.errors}/{self.game.max_errors}",
            bg=BUTTON_BG, fg=TEXT_COLOR, font=("Segoe UI", 12), padx=20, pady=6)
        self.error_label.pack(side="left", padx=15)

    # Создаёт 81 виджет Entry в сетке.
    # Граница ячейки реализована через фон cell_frame: его цвет просвечивает по краям как рамка
    def create_grid(self):
        THIN_LINE = "#6f6f6f"   # граница внутри блока 3×3
        THICK_LINE = "#000000"  # граница между блоками 3×3

        for row in range(9):
            for col in range(9):
                cell_color = CELL_BG_1 if (row // 3 + col // 3) % 2 == 0 else CELL_BG_2

                # Ячейки на краях блоков получают чёрную рамку, остальные — серую
                border_color = THICK_LINE if row % 3 == 0 or col % 3 == 0 else THIN_LINE

                cell_frame = tk.Frame(self.grid_frame, bg=border_color)
                cell_frame.grid(
                    row=row, column=col,
                    # Большой отступ на границах блоков создаёт толстую линию
                    padx=(2 if col % 3 == 0 else 1, 2 if col == 8 else 1),
                    pady=(2 if row % 3 == 0 else 1, 2 if row == 8 else 1),
                )

                entry = tk.Entry(cell_frame, bg=cell_color, **ENTRY_STYLE)
                entry.pack(ipadx=6, ipady=6)
                entry.bind("<Button-1>", lambda e, r=row, c=col: self.select_cell(r, c))
                entry.bind("<KeyRelease>", lambda e, r=row, c=col: self._validate_cell_internal(r, c))

                # Заполняем заданные ячейки и блокируем их от редактирования
                if self.game.puzzle[row][col]:
                    entry.insert(0, self.game.puzzle[row][col])
                    entry.config(state="readonly", readonlybackground=cell_color,
                                 foreground=TEXT_COLOR, font=("Segoe UI", 18, "bold"))

                self.cells[(row, col)] = entry

    # Создаёт кнопки нижней панели
    def create_buttons(self, parent):
        for text, command in [("Новая игра", self.new_game)]:
            btn = tk.Label(parent, text=text, bg=BUTTON_BG, fg=TEXT_COLOR,
                           font=("Segoe UI", 12), padx=20, pady=6)
            btn.pack(side="left", padx=15)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#ddd0c0"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BUTTON_BG))
            btn.bind("<Button-1>", lambda e, cmd=command: cmd())

    # Удаляет виджеты игрового экрана и возвращает в главное меню
    def back_to_menu(self, event=None):
        for w in self.root.winfo_children():
            w.destroy()
        MainMenu(self.root)

    # Вызывается при каждом нажатии клавиши в ячейке.
    # Проверяет введённое значение и помечает ошибку или фиксирует верный ответ
    def _validate_cell_internal(self, row, col):
        if self.game_finished:
            return
        if self.game.fixed and self.game.fixed[row][col]:
            return

        entry = self.cells[(row, col)]
        value = entry.get()

        # Ячейку очистили — снимаем ошибку и обновляем цвет
        if value == "":
            if (row, col) in self.error_cells:
                self.error_cells.remove((row, col))
            self._update_cell_color(row, col)
            return

        # Введено не цифра или вне диапазона 1–9 — удаляем
        if not value.isdigit() or not (1 <= int(value) <= 9):
            entry.delete(0, tk.END)
            return

        num = int(value)
        entry.config(fg=TEXT_COLOR)

        if num != self.game.solution[row][col]:
            if (row, col) not in self.error_cells:
                self.mark_error(row, col)
            return

        # Верно — снимаем ошибку если была, обновляем цвет
        if (row, col) in self.error_cells:
            self.error_cells.remove((row, col))

        self._update_cell_color(row, col)

        # Обновляем клетки с таким же числом
        entered_value = str(num)
        for r in range(9):
            for c in range(9):
                if (r, c) != (row, col) and self.cells[(r, c)].get() == entered_value:
                    self._update_cell_color(r, c)

        self.check_win()

    # Помечает ячейку как ошибочную: красный фон, счётчик +1, проверка лимита
    def mark_error(self, row, col):
        if (row, col) in self.error_cells:
            return
        self.error_cells.add((row, col))
        self.cells[(row, col)].config(background=ERROR_COLOR)
        self.game.errors += 1
        self.error_label.config(text=f"Ошибки: {self.game.errors}/{self.game.max_errors}")
        if self.game.is_game_over():
            self.game_over()

    # Проверяет, заполнено ли всё поле верно. Вызывается после каждого правильного ввода
    def check_win(self):
        for r in range(9):
            for c in range(9):
                if (r, c) in self.error_cells:
                    return
                value = self.cells[(r, c)].get()
                if not value or int(value) != self.game.solution[r][c]:
                    return
        self.game_finished = True
        messagebox.showinfo("Поздравляем!", "Судоку решено!")

    # Генерирует новую головоломку и перерисовывает доску
    def new_game(self, event=None):
        self.game.new_game()
        self.refresh_board()

    # Меняет уровень сложности и сразу начинает новую игру
    def change_difficulty(self, event):
        self.game.set_difficulty(self.difficulty_box.get())
        self.refresh_board()

    # Сбрасывает состояние доски под новую игру, не пересоздавая виджеты Entry
    def refresh_board(self):
        self.game_finished = False
        self.error_cells.clear()
        self.selected_position = None
        self.highlighted_cells = set()
        self.game.errors = 0
        self.error_label.config(text=f"Ошибки: {self.game.errors}/{self.game.max_errors}")

        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]
                base_color = CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2
                entry.config(state="normal")
                entry.delete(0, tk.END)

                if self.game.puzzle[r][c] != 0:
                    entry.insert(0, str(self.game.puzzle[r][c]))
                    entry.config(state="readonly", readonlybackground=base_color,
                                 foreground=TEXT_COLOR, background=base_color,
                                 font=("Segoe UI", 18, "bold"))
                else:
                    entry.config(state="normal", background=base_color,
                                 readonlybackground=base_color,
                                 foreground=TEXT_COLOR, font=("Segoe UI", 18, "bold"))

    # Раскрывает правильное решение, блокирует поле и показывает сообщение о поражении
    def game_over(self):
        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, self.game.solution[r][c])

                # Ячейки с ошибками остаются красными, остальные — базовый цвет
                color = ERROR_COLOR if (r, c) in self.error_cells else (
                    CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2)
                is_clue = self.game.fixed and self.game.fixed[r][c]
                entry.config(state="readonly", readonlybackground=color,
                             foreground=TEXT_COLOR,
                             font=("Segoe UI", 18, "bold"))

        self.game_finished = True
        messagebox.showinfo("Поражение",
                            "Превышено допустимое количество ошибок.\n"
                            "Показано правильное решение.")
        self.error_label.config(text="Игра окончена")

    # Обновляет подсветку при выборе ячейки.
    # Подсвечивает выбранную ячейку, всю её строку и столбец,
    # а также все ячейки с тем же числом
    def select_cell(self, row, col):
        selected_value = self.cells[(row, col)].get()
        new_highlighted = set()

        # Добавляем всю строку и столбец
        for i in range(9):
            new_highlighted.add((row, i))
            new_highlighted.add((i, col))

        # Добавляем ячейки с тем же числом
        if selected_value:
            for r in range(9):
                for c in range(9):
                    if self.cells[(r, c)].get() == selected_value:
                        new_highlighted.add((r, c))

        # Снимаем подсветку с ячеек, которые вышли из нового выделения
        for (r, c) in self.highlighted_cells - new_highlighted:
            if (r, c) not in self.error_cells:
                color = CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2
                self.cells[(r, c)].config(background=color, readonlybackground=color)

        # Красим новые ячейки нужным цветом
        for (r, c) in new_highlighted:
            if (r, c) in self.error_cells:
                continue
            if (r, c) == (row, col):
                color = SELECT_COLOR
            elif selected_value and self.cells[(r, c)].get() == selected_value:
                color = SELECT_COLOR  # одинаковые числа тем же цветом что и выделение
            else:
                color = "#eaf2ff"  # строка/столбец
            self.cells[(r, c)].config(background=color, readonlybackground=color)

        self.highlighted_cells = new_highlighted
        self.selected_position = (row, col)

    def _update_cell_color(self, row, col):
        entry = self.cells[(row, col)]

        if (row, col) in self.error_cells:
            color = ERROR_COLOR
        elif (row, col) == self.selected_position:
            color = SELECT_COLOR
        elif self.selected_position:
            sel_row, sel_col = self.selected_position
            sel_value = self.cells[self.selected_position].get()
            value = entry.get()
            if row == sel_row or col == sel_col:
                color = "#eaf2ff"
            elif sel_value and value == sel_value:
                color = SELECT_COLOR
            else:
                color = self.get_base_color(row, col)
        else:
            color = self.get_base_color(row, col)

        entry.config(background=color, readonlybackground=color)

    # Возвращает базовый цвет ячейки в зависимости от того, в каком блоке она находится
    def get_base_color(self, r, c):
        return CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2

    # tkinter иногда игнорирует readonlybackground сразу после grid().
    # Принудительно обновляем цвет всех ячеек через 1 мс после отрисовки
    def _fix_readonly_colors(self):
        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]
                color = CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2
                entry.config(background=color, readonlybackground=color)