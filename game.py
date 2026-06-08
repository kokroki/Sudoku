from generator import generate_board, create_puzzle


class SudokuGameLogic:

    def __init__(self):
        self.max_errors = 3
        self.difficulty = 45
        self.new_game()

    # Генерирует новое поле: полное решение, пазл и список заблокированных ячеек
    def new_game(self):
        self.solution = generate_board()
        self.puzzle = create_puzzle(self.solution, self.difficulty)
        self.errors = 0
        # True если ячейка задана изначально, False если пустая
        self.fixed = [[self.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]

    # Меняет сложность и сразу запускает новую игру
    def set_difficulty(self, difficulty):
        levels = {"Лёгкий": 35, "Средний": 45, "Сложный": 50}
        self.difficulty = levels[difficulty]
        self.new_game()

    # Возвращает True если игрок исчерпал лимит ошибок
    def is_game_over(self):
        return self.errors >= self.max_errors
