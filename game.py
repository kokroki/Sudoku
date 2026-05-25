from generator import generate_board, create_puzzle


class SudokuGameLogic:

    def __init__(self):
        self.max_errors = 3
        self.difficulty = 45

        self.new_game()

    # создание новой игры
    def new_game(self):
        self.solution = generate_board()    # полное готовое решение (81 число)

        self.puzzle = create_puzzle(    # из готового решения удаляем клетки в зависимости от уровня сложности
            self.solution,
            self.difficulty
        )

        self.errors = 0    # обнуляем счетчик ошибок

        # клетки, которые нельзя изменять (в пазле изначально)
        self.fixed = [ [self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]    # True если число, False если пусто

    # изменение сложности
    def set_difficulty(self, difficulty):
        levels = { "Лёгкий": 35, "Средний": 45, "Сложный": 50 }

        self.difficulty = levels[difficulty]
        self.new_game()    # генерируем новое поле с новой сложностью

    # проверка окончания игры
    def is_game_over(self):
        return self.errors >= self.max_errors #

