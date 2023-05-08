import pygame
import sys
import time
import argparse
import math

from minesweeper import *
def positive_nonzero_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive non-zero integer")
    return ivalue

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--setting",type=positive_nonzero_int, default=[], nargs=3, 
                    help="Board hight, Board width, The number of mines in the board")


args = parser.parse_args()

if not args.setting:
    h = 9
    w = 9
    m = 10
else:
    h, w, m = args.setting
    if (h * w) // 2 < m:
        print("too many mines!")
        exit(1)
    if h < 3 or w < 3:
        print("the size of board is too small!")
        exit(1)
HEIGHT = h
WIDTH = w
MINES = m
print("HEIGHT =", h)
print("WIDTH =", w)
print("MINES =", m)

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
YELLOW = (240, 230, 140)

NUM_COLOR = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
             (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

# Create game
pygame.init()
size = width, height = 900, 500
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH, game=game)


# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
safes = set()
lost = False
stuck = False
win = False
revealed_count = 0
ans_board = game.ans_board
print("initiate board:")
for b in game.ans_board:
    print(b)

# Show instructions initially
instructions = True
init_flag = True

while True:
    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Minesweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, WHITE)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        # Play game button
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Play Game", True, BLACK)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, WHITE, buttonRect)
        screen.blit(buttonText, buttonTextRect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                time.sleep(0.3)

        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            if (i, j) in revealed:
                pygame.draw.rect(screen, WHITE, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif game.is_mine((i, j)) and stuck:
                screen.blit(mine, rect)
            elif (i, j) in revealed:
                nearby = game.nearby_mines((i, j))
                if nearby:
                    neighbors = smallFont.render(
                        str(nearby),
                        True, NUM_COLOR[nearby - 1]
                    )
                    neighborsTextRect = neighbors.get_rect()
                    neighborsTextRect.center = rect.center
                    screen.blit(neighbors, neighborsTextRect)
            elif (i, j) in safes:
                nearby = game.nearby_mines((i, j))
                if nearby:
                    neighbors = smallFont.render(
                        str(nearby),
                        True, GRAY
                    )
                    pygame.draw.rect(screen, YELLOW, rect)
                    neighborsTextRect = neighbors.get_rect()
                    neighborsTextRect.center = rect.center
                    screen.blit(neighbors, neighborsTextRect)
                else:
                    pygame.draw.rect(screen, YELLOW, rect)
            elif (lost or stuck) and (i, j) not in safes:
                nearby = game.nearby_mines((i, j))
                if nearby:
                    neighbors = smallFont.render(
                        str(nearby),
                        True, BLACK
                    )
                    pygame.draw.rect(screen, GRAY, rect)
                    neighborsTextRect = neighbors.get_rect()
                    neighborsTextRect.center = rect.center
                    screen.blit(neighbors, neighborsTextRect)
                else:
                    pygame.draw.rect(screen, GRAY, rect)

            row.append(rect)
        cells.append(row)
        if revealed_count >= round(math.sqrt(h*w)) and init_flag:
            init_flag = False

    # AI Move button
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Move", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # Display text
    if lost:
        text = "Lost"
    elif stuck:
        text = "Stuck"
    elif win:
        text = "Win"
    else:
        text = ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, (2 / 3) * height)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    
    if init_flag:
        move = ai.init_knowledge()
        revealed_count += 1
    # Check for a right-click to toggle flagging    
    elif right == 1 and not lost:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)
                    
    elif left == 1:
        mouse = pygame.mouse.get_pos()
        # TODO: AI move part
        if aiButton.collidepoint(mouse) and not lost:
            time.sleep(0.2)

            ai.add_knowledge()
            print("KB len:", len(ai.knowledge))
            print("KB0 len:", len(ai.knowledge0))
            print("Known mines:", len(ai.mines))
            print("Unknown mines:", len(game.mines) - len(ai.mines))
            print("Safe", len(ai.safes))
            
            # check the board
            if not ai.mark_board(game.board, "Total check"):
                print("ERROR!")
                time.sleep(1)
            safe_list = []
            for s in ai.safes:
                safe_list.append(s[:2])
            safes = set(safe_list)

            if len(ai.mines) == len(game.mines):
                find_mine = ai.mines.copy()
                mine_list = []
                for m in find_mine:
                    mine_list.append(m[:2])
                flags = set(mine_list)
                win = True
                print("WIN!!")

            else:
                find_mine = ai.mines.copy()
                mine_list = []
                for m in find_mine:
                    mine_list.append(m[:2])
                flags = set(mine_list)
                stuck = True
                print("Stuck")
                
        # Reset
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH, game=game)
            revealed = set()
            flags = set()
            safes = set()
            lost = False
            stuck = False
            win = False
            init_flag = True
            revealed_count = 0
            ans_board = game.ans_board
            print("initiate board:")
            for b in game.ans_board:
                print(b)
            continue

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)
                        ai.init_knowledge(move)

    def make_move(move):
        
        if game.is_mine(move):
            return True
        else:
            # get the number of nearby mines
            nearby = game.nearby_mines(move)
            revealed.add(move)
            if not nearby:
                # Loop over all cells within one row and column
                for i in range(move[0] - 1, move[0] + 2):
                    for j in range(move[1] - 1, move[1] + 2):

                        # Ignore the cell itself
                        if (i, j) == move:
                            continue

                        # Add to the cell collection if the cell is not yet explored
                        # and is not the mine already none
                        if 0 <= i < HEIGHT and 0 <= j < WIDTH and (i, j) not in revealed:
                            make_move((i, j))
    if move:
        if make_move(move):
            lost = True

    pygame.display.flip()
