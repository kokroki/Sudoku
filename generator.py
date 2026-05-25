import random


def is_safe(board, r, c, num):

    # проверка строки
    for col in range(9):
        if col != c and board[r][col] == num:
            return False

    # проверка столбца
    for row in range(9):
        if row != r and board[row][c] == num:
            return False

    # проверка блока 3x3
    br = (r // 3) * 3
    bc = (c // 3) * 3

    for row in range(br, br + 3):
        for col in range(bc, bc + 3):

            if (row, col) != (r, c):

                if board[row][col] == num:
                    return False

    return True

#генерация полного судоку
def generate_board():

    # создаём пустое поле
    board = [[0] * 9 for _ in range(9)]

    # рекурсивное заполнение
    def solve():

        for r in range(9):
            for c in range(9):

                # ищем пустую клетку
                if board[r][c] == 0:

                    nums = list(range(1, 10))
                    random.shuffle(nums)

                    for num in nums:

                        if is_safe(board, r, c, num):

                            board[r][c] = num

                            if solve():
                                return True

                            # откат
                            board[r][c] = 0

                    return False

        return True

    solve()

    return board


def count_solutions(board):

    solutions = 0

    def solve():

        nonlocal solutions

        # если найдено больше одного решения
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

        # найдено решение
        solutions += 1

    solve()

    return solutions


def create_puzzle(solution, difficulty):

    # копия полного решения
    board = [row[:] for row in solution]

    # список клеток
    cells = [(r, c) for r in range(9) for c in range(9)]

    random.shuffle(cells)

    removed = 0
    target = difficulty

    # ограничение попыток
    attempts = 0
    max_attempts = target * 3

    for row, col in cells:

        if removed >= target:
            break

        if attempts >= max_attempts:
            break

        attempts += 1

        backup = board[row][col]

        # временно удаляем число
        board[row][col] = 0

        # копия для проверки
        board_copy = [r[:] for r in board]

        # проверка уникальности
        solutions = count_solutions(board_copy)

        # если решений больше одного — возвращаем число
        if solutions != 1:
            board[row][col] = backup

        else:
            removed += 1

    return board