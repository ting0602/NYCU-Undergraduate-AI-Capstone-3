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

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

NUM_COLOR = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 128),
             (128, 0, 0), (0, 128, 128), (0, 0, 0), (128, 128, 128)]

# Create game
pygame.init()
size = width, height = 600, 400
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
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

ans_board = [[0 for _ in range(game.height)] for _ in range(game.width)]
for i in range(game.height):
    for j in range(game.width):
        if not game.board[i][j]:
            ans_board[i][j] = game.nearby_mines((i, j))
        else:
            ans_board[i][j] = -1
print("initiate board:")
for b in ans_board:
    print(b)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False
stuck = False

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
    revealed_count = 0
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
                revealed_count += 1
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
            row.append(rect)
        cells.append(row)
        if revealed_count > round(math.sqrt(h*w)) and init_flag:
            # print("revealed_count", revealed_count, round(math.sqrt(h*w)))
            init_flag = False
            # print("Before change flag:", len(ai.knowledge), len(ai.knowledge0))
            # # ai.add_knowledge(game, init_flag, None)
            # print("change flag:", len(ai.knowledge), len(ai.knowledge0))
            # print("find mine/safe/pos_set:", len(ai.mines), len(ai.safes), len(ai.pos_set))

            # if not ai.mark_board(game.board):
            #     print("ERRRRRR")

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
    text = "Lost" if lost else "Won" if game.mines == flags else ""
    text = "Stuck" if stuck else text
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, (2 / 3) * height)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    
    if init_flag:
        move = make_random_move(ai, game)
        
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

            ai.add_knowledge(game)
            move = ai.make_safe_move()
            print("len:", len(ai.knowledge), len(ai.knowledge0))
            print("Known mines:", len(ai.mines))
            print("Unknown mines:", len(game.mines) - len(ai.mines))
            print("Safe", len(ai.safes), len(ai.pos_set))
            for m in ai.mines:
                print(m)
            ai.mark_board(game.board, "Total check")
            if move is None:
                if len(ai.mines) == len(game.mines):
                    find_mine = ai.mines.copy()
                    mine_list = []
                    print("ensure mines:")
                    for m in find_mine:
                        mine_list.append(m[:2])
                        print(m[:2])
                    flags = mine_list
                    
                    if ai.mark_board(game.board, "Win check"):
                        print("WIN!!")
                    else:
                        print("ERROR BOARD")
                else:
                    print("[X] No known safe moves, AI can not make safe move")
                    print("Stop the game")
                    
                    find_mine = ai.mines.copy()
                    mine_list = []
                    print("ensure mines:")
                    for m in find_mine:
                        mine_list.append(m[:2])
                        print(m[:2])
                    flags = mine_list
                    stuck = True
            else:
                print("[O] AI can make safe move")

        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            stuck = False
            init_flag = True
            continue

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Make move and update AI knowledge
    def make_move(move):
        
        if game.is_mine(move):
            return True
        else:
            # get the number of nearby mines
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.init_knowledge(move)
            # ai.add_knowledge(game, init_flag, move)
            # for b in ai.board:
            #     print(b)
            
            # if init_flag:
            #     ai.init_knowledge(move)
            # else:
            #     ai.add_knowledge(move, game)
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
