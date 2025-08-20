import pygame
import sys

# --- Settings ---
WIDTH, HEIGHT = 600, 650   # Extra 50px for status bar
LINE_COLOR = (0, 0, 0)
BG_COLOR = (245, 245, 245)
X_COLOR = (200, 0, 0)
O_COLOR = (0, 0, 200)
LINE_WIDTH = 3
BIG_LINE_WIDTH = 6
CELL_SIZE = WIDTH // 9
STATUS_HEIGHT = 50

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Tic Tac Toe")
font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 120, bold=True)   # for small board winners
status_font = pygame.font.SysFont(None, 30)

# --- Game Classes ---
class SmallBoard:
    def __init__(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.winner = None
        self.win_line = None  # store winning line

    def make_move(self, r, c, player):
        if self.board[r][c] == " " and not self.winner:
            self.board[r][c] = player
            if self.check_winner(player):
                self.winner = player
            return True
        return False

    def check_winner(self, player):
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                self.win_line = ("row", i)
                return True
            if all(self.board[j][i] == player for j in range(3)):
                self.win_line = ("col", i)
                return True
        if all(self.board[i][i] == player for i in range(3)):
            self.win_line = ("diag", 0)
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):
            self.win_line = ("diag", 1)
            return True
        return False

    def is_full(self):
        return all(cell != " " for row in self.board for cell in row)


class UltimateTicTacToe:
    def __init__(self):
        self.boards = [[SmallBoard() for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.main_winner = None
        self.forced_board = None  # (row, col)

    def check_main_winner(self, player):
        for i in range(3):
            if all(self.boards[i][j].winner == player for j in range(3)) or \
               all(self.boards[j][i].winner == player for j in range(3)):
                return True
        if all(self.boards[i][i].winner == player for i in range(3)) or \
           all(self.boards[i][2 - i].winner == player for i in range(3)):
            return True
        return False

    def make_move(self, big_r, big_c, small_r, small_c):
        board = self.boards[big_r][big_c]
        if not board.make_move(small_r, small_c, self.current_player):
            return False

        if self.check_main_winner(self.current_player):
            self.main_winner = self.current_player

        # Update forced board
        self.forced_board = (small_r, small_c)
        if self.boards[small_r][small_c].winner or self.boards[small_r][small_c].is_full():
            self.forced_board = None  # Free choice if blocked

        # Switch turn
        self.current_player = "O" if self.current_player == "X" else "X"
        return True


# --- Drawing Functions ---
def draw_win_line(big_r, big_c, win_line):
    bx = big_c * 3 * CELL_SIZE
    by = big_r * 3 * CELL_SIZE

    if win_line[0] == "row":
        row = win_line[1]
        y = by + row * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, (150, 150, 150), (bx, y), (bx + 3 * CELL_SIZE, y), 5)

    elif win_line[0] == "col":
        col = win_line[1]
        x = bx + col * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.line(screen, (150, 150, 150), (x, by), (x, by + 3 * CELL_SIZE), 5)

    elif win_line[0] == "diag":
        if win_line[1] == 0:
            pygame.draw.line(screen, (150, 150, 150), (bx, by), (bx + 3 * CELL_SIZE, by + 3 * CELL_SIZE), 5)
        else:
            pygame.draw.line(screen, (150, 150, 150), (bx + 3 * CELL_SIZE, by), (bx, by + 3 * CELL_SIZE), 5)


def draw_board(game):
    screen.fill(BG_COLOR)

    # Draw small grid lines
    for i in range(1, 9):
        lw = LINE_WIDTH
        if i % 3 == 0:
            lw = BIG_LINE_WIDTH
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT - STATUS_HEIGHT), lw)
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), lw)

    # Draw marks
    for big_r in range(3):
        for big_c in range(3):
            sb = game.boards[big_r][big_c]
            bx, by = big_c * 3 * CELL_SIZE, big_r * 3 * CELL_SIZE

            if sb.winner:
                # Dim background
                s = pygame.Surface((3 * CELL_SIZE, 3 * CELL_SIZE))
                s.set_alpha(80)
                s.fill((200, 200, 200))
                screen.blit(s, (bx, by))

                # Draw win line
                if sb.win_line:
                    draw_win_line(big_r, big_c, sb.win_line)

                # Draw big symbol
                center_x = bx + (3 * CELL_SIZE) // 2
                center_y = by + (3 * CELL_SIZE) // 2
                text = big_font.render(sb.winner, True, X_COLOR if sb.winner == "X" else O_COLOR)
                rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, rect)
            else:
                # Otherwise draw small moves
                for small_r in range(3):
                    for small_c in range(3):
                        mark = sb.board[small_r][small_c]
                        if mark != " ":
                            x = bx + small_c * CELL_SIZE + CELL_SIZE // 2
                            y = by + small_r * CELL_SIZE + CELL_SIZE // 2
                            text = font.render(mark, True, X_COLOR if mark == "X" else O_COLOR)
                            rect = text.get_rect(center=(x, y))
                            screen.blit(text, rect)

    # Highlight forced board
    if game.forced_board and not game.main_winner:
        br, bc = game.forced_board
        rect = pygame.Rect(bc * 3 * CELL_SIZE, br * 3 * CELL_SIZE, 3 * CELL_SIZE, 3 * CELL_SIZE)
        pygame.draw.rect(screen, (180, 255, 180), rect, 5)


def draw_status(game):
    pygame.draw.rect(screen, (220, 220, 220), (0, HEIGHT - STATUS_HEIGHT, WIDTH, STATUS_HEIGHT))
    if game.main_winner:
        msg = f"🎉 Player {game.main_winner} wins the BIG BOARD!"
    else:
        if game.forced_board:
            br, bc = game.forced_board
            msg = f"Player {game.current_player}'s turn → play in board ({br},{bc})"
        else:
            msg = f"Player {game.current_player}'s turn → play anywhere"

    text = status_font.render(msg, True, (0, 0, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT - STATUS_HEIGHT // 2))
    screen.blit(text, rect)
    pygame.display.flip()


def get_click_pos(pos):
    x, y = pos
    if y >= HEIGHT - STATUS_HEIGHT:  # ignore clicks in status bar
        return None
    big_c, small_c = divmod(x // CELL_SIZE, 3)
    big_r, small_r = divmod(y // CELL_SIZE, 3)
    return big_r, big_c, small_r, small_c


# --- Main Game Loop ---
def main():
    game = UltimateTicTacToe()
    clock = pygame.time.Clock()

    while True:
        draw_board(game)
        draw_status(game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game.main_winner and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = get_click_pos(event.pos)
                if not click:
                    continue
                big_r, big_c, small_r, small_c = click

                # Enforce forced board rule
                if game.forced_board and (big_r, big_c) != game.forced_board:
                    print("Must play in highlighted board!")
                    continue

                game.make_move(big_r, big_c, small_r, small_c)

        clock.tick(30)


if __name__ == "__main__":
    main()
