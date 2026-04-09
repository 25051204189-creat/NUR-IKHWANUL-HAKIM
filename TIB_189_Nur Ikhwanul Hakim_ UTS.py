import pygame
import random

pygame.init()

GRID_SIZE = 35
COLS, ROWS = 10, 15
PANEL_WIDTH = 180

SCREEN_WIDTH = (COLS * GRID_SIZE) + PANEL_WIDTH
SCREEN_HEIGHT = ROWS * GRID_SIZE

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GOLD = (255, 215, 0)
COLORS = [
    (255, 50, 50),  # Merah
    (50, 255, 50),  # Hijau
    (50, 120, 255),  # Biru
    (255, 150, 50),  # Oranye
    (180, 50, 255)  # Ungu
]


font_small = pygame.font.SysFont("Segoe UI", 22)
font_large = pygame.font.SysFont("Segoe UI", 36, bold=True)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PBO Tetris - Final Project")


class GameObject:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color


class PlayerBlock(GameObject):
    def __init__(self):
        self.shapes = {
            'I': [(0, 0), (0, 1), (0, 2), (0, 3)],
            'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
            'T': [(0, 0), (1, 0), (-1, 0), (0, 1)],
            'L': [(0, 0), (0, 1), (0, 2), (1, 2)]
        }
        self.type = random.choice(list(self.shapes.keys()))
        self.layout = self.shapes[self.type]

        super().__init__(COLS // 2, 0, random.choice(COLORS))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, surface):
        for bx, by in self.layout:
            draw_x = (self.x + bx) * GRID_SIZE
            draw_y = (self.y + by) * GRID_SIZE
            pygame.draw.rect(surface, self.color, (draw_x + 1, draw_y + 1, GRID_SIZE - 2, GRID_SIZE - 2))
            pygame.draw.rect(surface, WHITE, (draw_x + 1, draw_y + 1, GRID_SIZE - 2, GRID_SIZE - 2), 1)


class GameBoard:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False

    def is_valid_move(self, block, dx, dy):
        for bx, by in block.layout:
            new_x = block.x + bx + dx
            new_y = block.y + by + dy
            if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                return False
            if new_y >= 0 and self.grid[new_y][new_x]:
                return False
        return True

    def lock_block(self, block):
        for bx, by in block.layout:
            if block.y + by < 0:
                self.game_over = True
            else:
                self.grid[block.y + by][block.x + bx] = block.color

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell is not None for cell in row)]
        for i in lines_to_clear:
            del self.grid[i]
            self.grid.insert(0, [None for _ in range(COLS)])
            self.score += 100

    def draw(self, surface):
        for r in range(ROWS):
            for c in range(COLS):
                rect = (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, GRAY, rect, 1)
                if self.grid[r][c]:
                    pygame.draw.rect(surface, self.grid[r][c],
                                     (c * GRID_SIZE + 1, r * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2))

        pygame.draw.rect(surface, GRAY, (COLS * GRID_SIZE, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        title_surf = font_large.render("SCORE", True, WHITE)
        score_surf = font_large.render(str(self.score), True, GOLD)
        surface.blit(title_surf, (COLS * GRID_SIZE + 35, 30))
        surface.blit(score_surf, (COLS * GRID_SIZE + 35, 75))

        hint_y = SCREEN_HEIGHT - 100
        surface.blit(font_small.render("KONTROL:", True, WHITE), (COLS * GRID_SIZE + 20, hint_y))
        surface.blit(font_small.render("Panah Kiri/Kanan", True, WHITE), (COLS * GRID_SIZE + 20, hint_y + 30))
        surface.blit(font_small.render("Panah Bawah", True, WHITE), (COLS * GRID_SIZE + 20, hint_y + 55))


def main():
    clock = pygame.time.Clock()
    board = GameBoard()
    current_piece = PlayerBlock()

    fall_speed = 500
    last_fall_time = pygame.time.get_ticks()

    run = True
    while run:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if not board.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and board.is_valid_move(current_piece, -1, 0):
                        current_piece.move(-1, 0)
                    if event.key == pygame.K_RIGHT and board.is_valid_move(current_piece, 1, 0):
                        current_piece.move(1, 0)
                    if event.key == pygame.K_DOWN and board.is_valid_move(current_piece, 0, 1):
                        current_piece.move(0, 1)

        if not board.game_over:
            if current_time - last_fall_time > fall_speed:
                if board.is_valid_move(current_piece, 0, 1):
                    current_piece.move(0, 1)
                else:
                    board.lock_block(current_piece)
                    board.clear_lines()
                    current_piece = PlayerBlock()
                    if not board.is_valid_move(current_piece, 0, 0):
                        board.game_over = True
                last_fall_time = current_time

        board.draw(screen)
        if not board.game_over:
            current_piece.draw(screen)
        else:
            overlay = pygame.Surface((COLS * GRID_SIZE, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            go_text = font_large.render("GAME OVER", True, (255, 50, 50))
            screen.blit(go_text, (50, SCREEN_HEIGHT // 2 - 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()