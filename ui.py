import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from game import SudokuGameLogic

APP_BG = "#f7f3ec"

CELL_BG_1 = "#ffffff"
CELL_BG_2 = "#f0e7da"

GRID_BG = "#d6c6b3"

TEXT_COLOR = "#1c1c1e"

BUTTON_BG = "#eadbc8"

SELECT_COLOR = "#cfe3ff"
ROW_COL_HIGHLIGHT = "#eaf2ff"
SAME_NUMBER_HIGHLIGHT = "#cfe3ff"

ERROR_CELL_COLOR = "#fde8e8"

CLUE_COLOR = "#1c1c1e"

ENTRY_STYLE = {
    "width": 2,
    "font": ("Segoe UI", 18, "bold"),
    "justify": "center",
    "fg": TEXT_COLOR,
    "relief": "flat",
    "bd": 0,
    "highlightthickness": 0,
    "insertbackground": TEXT_COLOR
}

BUTTON_STYLE = {
    "bg": BUTTON_BG,
    "fg": TEXT_COLOR,
    "font": ("Segoe UI", 12),
    "padx": 20,
    "pady": 6
}

class MainMenu:

    def __init__(self, root):

        self.root = root
        self.root.title("Судоку")
        self.root.geometry("850x520")
        self.root.configure(bg=APP_BG)

        self.draw()

    def draw(self):

        tk.Label(
            self.root,
            text="СУДОКУ",
            font=("Segoe UI", 34, "bold"),
            bg=APP_BG,
            fg=TEXT_COLOR
        ).place(
            relx=0.5,
            y=70,
            anchor="center"
        )

        self.create_preview()

        buttons = [
            ("Играть", 380, BUTTON_BG, TEXT_COLOR, self.start_game),
            ("Правила", 435, BUTTON_BG, TEXT_COLOR, self.show_rules),
            ("Выход", 490, "#e56a6a", "white", self.root.destroy)
        ]

        for text, y, bg, fg, command in buttons:
            btn = tk.Label(
                self.root,
                text=text,
                bg=bg,
                fg=fg,
                font=("Segoe UI", 13),
                width=18,
                pady=10
            )

            btn.place(
                relx=0.5,
                y=y,
                anchor="center"
            )

            btn.bind(
                "<Button-1>",
                lambda e, cmd=command: cmd()
            )


    def create_preview(self):
        img = Image.open("preview.png")

        img = img.resize((230, 230), Image.Resampling.LANCZOS)

        self.preview_photo = ImageTk.PhotoImage(img)

        label = tk.Label(self.root, image=self.preview_photo, bg=APP_BG)
        label.place(relx=0.5, y=220, anchor="center")


    def show_rules(self):

        messagebox.showinfo(
            "Правила",
            "Заполните поле числами от 1 до 9:\n\n"
            "- без повторений в строках\n"
            "- без повторений в столбцах\n"
            "- без повторений в блоках 3×3"
        )


    def start_game(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        SudokuGame(self.root)

class SudokuGame:

    def __init__(self, root):

        self.root = root
        self.root.title("Судоку")
        self.root.geometry("850x520")
        self.root.configure(background=APP_BG)


        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.TCombobox",
            fieldbackground=BUTTON_BG,
            background=BUTTON_BG,
            foreground=TEXT_COLOR,
            borderwidth=0,
            padding=5
        )

        self.game = SudokuGameLogic()

        self.cells = {}
        self.error_cells = set()

        self.selected_position = None
        self.highlighted_cells = set()
        self.game_finished = False

        self.create_title()
        self.create_layout()

    def create_title(self):

        back_btn = tk.Label(
            self.root,
            text="← Назад",
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 12),
            padx=20,
            pady=6
        )

        back_btn.place(
            x=15,
            y=15
        )

        back_btn.bind(
            "<Button-1>",
            self.back_to_menu
        )

        tk.Label(
            self.root,
            text="Судоку",
            font=("Segoe UI", 26, "bold"),
            background=APP_BG,
            foreground=TEXT_COLOR
        ).pack(
            pady=10
        )

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
        self.root.after(1, self._fix_readonly_colors)

        bottom_panel = tk.Frame(self.root, background=APP_BG)
        bottom_panel.pack(side="bottom", pady=15)

        self.difficulty_box = ttk.Combobox(
            bottom_panel,
            values=["Лёгкий", "Средний", "Сложный"],
            state="readonly",
            style="Custom.TCombobox",
            width=12
        )

        self.difficulty_box.current(1)
        self.difficulty_box.pack(side="left", padx=15)

        self.difficulty_box.bind(
            "<<ComboboxSelected>>",
            self.change_difficulty
        )

        self.create_buttons(bottom_panel)

        self.error_label = tk.Label(
            bottom_panel,
            text=f"Ошибки: {self.game.errors}/{self.game.max_errors}",
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 12),
            padx=20,
            pady=6
        )

        self.error_label.pack(side="left", padx=15)

    def create_grid(self):

        THIN_LINE = "#6f6f6f"
        THICK_LINE = "#000000"

        for row in range(9):
            for col in range(9):

                cell_color = self.get_base_color(row, col)

                border_color = (
                    THICK_LINE
                    if row % 3 == 0 or col % 3 == 0
                    else THIN_LINE
                )

                cell_frame = tk.Frame(
                    self.grid_frame,
                    bg=border_color
                )

                cell_frame.grid(
                    row=row,
                    column=col,
                    padx=(
                        2 if col % 3 == 0 else 1,
                        2 if col == 8 else 1
                    ),
                    pady=(
                        2 if row % 3 == 0 else 1,
                        2 if row == 8 else 1
                    )
                )

                entry = tk.Entry(
                    cell_frame,
                    bg=cell_color,
                    **ENTRY_STYLE
                )

                entry.pack(ipadx=6, ipady=6)

                # Оба события — ко всем клеткам сразу
                entry.bind(
                    "<Button-1>",
                    lambda e, r=row, c=col:
                    self.select_cell(r, c)
                )
                entry.bind(
                    "<KeyRelease>",
                    lambda e, r=row, c=col:
                    self._validate_cell_internal(r, c)
                )

                # Заполняем подсказки
                if self.game.puzzle[row][col]:

                    entry.insert(
                        0,
                        self.game.puzzle[row][col]
                    )

                    entry.config(
                        state="readonly",
                        readonlybackground=cell_color,
                        foreground=CLUE_COLOR
                    )

                self.cells[(row, col)] = entry

    def _validate_cell_internal(self, row, col):
        # Игра окончена — не реагируем
        if self.game_finished:
            return

        # Подсказка — не реагируем
        if self.game.fixed and self.game.fixed[row][col]:
            return

        entry = self.cells[(row, col)]
        value = entry.get()

        # Пустое значение
        if value == "":
            if (row, col) in self.error_cells:
                self.error_cells.remove((row, col))
            # Пересобираем подсветку: подсветка «одинаковых» должна
            # исчезнуть, когда ячейка стала пустой
            if self.selected_position:
                self.select_cell(*self.selected_position)
            return

        # Не число
        if not value.isdigit():
            entry.delete(0, tk.END)
            return

        num = int(value)

        if num < 1 or num > 9:
            entry.delete(0, tk.END)
            return

        # Проверка на соответствие решению
        if num != self.game.solution[row][col]:
            if (row, col) not in self.error_cells:
                self.mark_error(row, col)
            return

        # Верно! Убираем ошибку если была
        if (row, col) in self.error_cells:
            self.error_cells.remove((row, col))

        # Пересобираем подсветку целиком, чтобы highlighted_cells
        # всегда был синхронен с визуальным состоянием.
        # Без этого ячейки с одинаковой цифрой красились, но не
        # попадали в highlighted_cells — и при следующем клике
        # не сбрасывались.
        if self.selected_position:
            self.select_cell(*self.selected_position)

        self.check_win()

    def mark_error(self, row, col):
        # Проверяем, не помечена ли уже ячейка как ошибочная
        if (row, col) in self.error_cells:
            return

        entry = self.cells[(row, col)]

        # Добавляем в множество ошибочных ячеек
        self.error_cells.add((row, col))

        # Меняем цвет фона на красный
        entry.config(background=ERROR_CELL_COLOR)

        # Увеличиваем счетчик ошибок
        self.game.errors += 1

        # Обновляем отображение счетчика
        self.error_label.config(
            text=f"Ошибки: {self.game.errors}/{self.game.max_errors}"
        )

        # Обновляем выделение, чтобы сохранить красный цвет
        if self.selected_position:
            self.select_cell(*self.selected_position)

        # Проверяем, не закончилась ли игра
        if self.game.is_game_over():
            self.game_over()

    def check_win(self):
        for r in range(9):
            for c in range(9):
                # Пропускаем ячейки с ошибками
                if (r, c) in self.error_cells:
                    return

                value = self.cells[(r, c)].get()

                if value == "":
                    return

                if int(value) != self.game.solution[r][c]:
                    return

        self.game_finished = True
        messagebox.showinfo("Поздравляем", "Судоку решено!")

    def create_buttons(self, parent):

        buttons = [("Новая игра", self.new_game)]

        for text, command in buttons:
            btn = tk.Label(
                parent,
                text=text,
                **BUTTON_STYLE
            )

            btn.pack(
                side="left",
                padx=15
            )

            btn.bind(
                "<Button-1>",
                lambda e, cmd=command: cmd()
            )

    def back_to_menu(self, event=None):

        for widget in self.root.winfo_children():
            widget.destroy()

        MainMenu(self.root)

    def new_game(self, event=None):
        self.game.new_game()  # Это правильно
        self.refresh_board()

    def change_difficulty(self, event):
        level = self.difficulty_box.get()
        self.game.set_difficulty(level)  # Это правильно
        self.refresh_board()

    def refresh_board(self):
        self.game_finished = False
        self.error_cells.clear()
        self.selected_position = None
        self.highlighted_cells = set()  # сбрасываем, иначе первый клик
                                        # попытается снять подсветку из старой игры

        self.game.errors = 0

        self.error_label.config(
            text=f"Ошибки: {self.game.errors}/{self.game.max_errors}"
        )

        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]

                entry.config(state="normal")
                entry.delete(0, tk.END)

                base_color = self.get_base_color(r, c)

                if self.game.puzzle[r][c] != 0:
                    entry.insert(0, str(self.game.puzzle[r][c]))
                    entry.config(
                        state="readonly",
                        readonlybackground=base_color,
                        foreground=CLUE_COLOR,
                        background=base_color
                    )
                else:
                    entry.config(
                        state="normal",
                        background=base_color,
                        readonlybackground=base_color,
                        foreground=TEXT_COLOR
                    )
                    # unbind/bind убраны — события уже привязаны в create_grid()

        if self.selected_position:
            self.select_cell(*self.selected_position)

    def game_over(self):
        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, self.game.solution[r][c])

                # Ошибочные клетки оставляем красными
                color = (
                    ERROR_CELL_COLOR
                    if (r, c) in self.error_cells
                    else self.get_base_color(r, c)
                )

                entry.config(
                    state="readonly",
                    readonlybackground=color,
                    foreground=TEXT_COLOR
                )

        self.game_finished = True

        messagebox.showinfo(
            "Поражение",
            "Превышено допустимое количество ошибок.\nПоказано правильное решение."
        )

        self.error_label.config(text="Игра окончена")

        self.error_label.config(text="Игра окончена")

    def select_cell(self, row, col):
        selected_value = self.cells[(row, col)].get()

        # Собираем клетки которые нужно подсветить
        new_highlighted = set()

        # Строка и столбец (17 клеток)
        for i in range(9):
            new_highlighted.add((row, i))  # строка
            new_highlighted.add((i, col))  # столбец

        # Одинаковые числа
        if selected_value:
            for r in range(9):
                for c in range(9):
                    if self.cells[(r, c)].get() == selected_value:
                        new_highlighted.add((r, c))

        # Восстанавливаем только те, которые больше не нужны
        for (r, c) in self.highlighted_cells - new_highlighted:
            if (r, c) not in self.error_cells:
                color = self.get_base_color(r, c)
                self.cells[(r, c)].config(
                    background=color,
                    readonlybackground=color
                )

        # Красим только новые клетки
        for (r, c) in new_highlighted:
            if (r, c) in self.error_cells:
                continue

            if (r, c) == (row, col):
                color = SELECT_COLOR
            elif selected_value and self.cells[(r, c)].get() == selected_value:
                color = SAME_NUMBER_HIGHLIGHT
            else:
                color = ROW_COL_HIGHLIGHT

            self.cells[(r, c)].config(
                background=color,
                readonlybackground=color
            )

        # Запоминаем текущее состояние
        self.highlighted_cells = new_highlighted
        self.selected_position = (row, col)

    def get_base_color(self, r, c):
        return CELL_BG_1 if (r // 3 + c // 3) % 2 == 0 else CELL_BG_2

    def _fix_readonly_colors(self):
        for r in range(9):
            for c in range(9):
                entry = self.cells[(r, c)]
                color = self.get_base_color(r, c)
                entry.config(
                    background=color,
                    readonlybackground=color
                )

    def _update_cell_color(self, row, col):
        """Обновляет цвет одной клетки без перерисовки всех 81"""
        entry = self.cells[(row, col)]

        # Ошибочная — всегда красная
        if (row, col) in self.error_cells:
            color = ERROR_CELL_COLOR

        # Выбранная — синяя
        elif (row, col) == self.selected_position:
            color = SELECT_COLOR

        # Если есть выбранная клетка — проверяем связи
        elif self.selected_position:
            sel_row, sel_col = self.selected_position
            sel_value = self.cells[self.selected_position].get()
            value = entry.get()

            if row == sel_row or col == sel_col:
                # Та же строка или столбец
                color = ROW_COL_HIGHLIGHT
            elif sel_value and value == sel_value:
                # Одинаковое число
                color = SAME_NUMBER_HIGHLIGHT
            else:
                color = self.get_base_color(row, col)

        else:
            color = self.get_base_color(row, col)

        entry.config(background=color, readonlybackground=color)