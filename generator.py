import random


# Проверяет, можно ли поставить num в ячейку (r, c) без нарушения правил судоку
def is_safe(board, r, c, num):
    # проверка строки
    for col in range(9):
        if col != c and board[r][col] == num:
            return False

    # проверка столбца
    for row in range(9):
        if row != r and board[row][c] == num:
            return False

    # проверка блока 3×3
    br = (r // 3) * 3
    bc = (c // 3) * 3
    for row in range(br, br + 3):
        for col in range(bc, bc + 3):
            if (row, col) != (r, c) and board[row][col] == num:
                return False

    return True


# Генерирует случайное полностью заполненное поле судоку методом backtracking
def generate_board():
    board = [[0] * 9 for _ in range(9)]

    def solve():
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_safe(board, r, c, num):
                            board[r][c] = num
                            if solve():
                                return True
                            board[r][c] = 0  # откат
                    return False
        return True

    solve()
    return board


# Считает количество решений у переданного поля (останавливается после 2-х)
def count_solutions(board):
    solutions = 0

    def solve():
        nonlocal solutions
        # Ранний выход: если уже нашли 2 решения, прекращаем
        if solutions > 1:
            return

        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_safe(board, row, col, num):
                            board[row][col] = num
                            solve()
                            board[row][col] = 0
                    return
        solutions += 1

    solve()
    return solutions

# Создаёт пазл из готового решения, удаляя ячейки.
# difficulty — количество ячеек для удаления.
# Каждое удаление проверяется на уникальность решения — пазл всегда имеет ровно один ответ
def create_puzzle(solution, difficulty):
    board = [row[:] for row in solution]
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)

    removed = 0
    attempts = 0
    max_attempts = difficulty * 3

    for row, col in cells:
        if removed >= difficulty or attempts >= max_attempts:
            break
        attempts += 1

        backup = board[row][col]
        board[row][col] = 0

        # если без этой ячейки решение перестаёт быть единственным — возвращаем
        if count_solutions([r[:] for r in board]) != 1:
            board[row][col] = backup
        else:
            removed += 1

    return board
