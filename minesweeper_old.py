import itertools
import random


class Minesweeper():
    """Minesweeper game representation"""

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """Prints a text-based representation of where mines are located."""

        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """Checks if all mines have been flagged."""

        return self.mines_found == self.mines


class Sentence():
    def __init__(self, cells, count):
        # cells are the mine candidate
        # count is the number of mine
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        # when cells and count are equal
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} contain {self.count} mine" 

    def known_mines(self):
        # when count == cells -> all cells are mines!
        if self.count == len(self.cells):
            return self.cells
        return None

    def known_safes(self):
        # when count = 0 -> all cells are safe!
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        # Update when know that the cell is mine
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        # Update when know that the cell is safe
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    def __init__(self, height, width):
        # Set initial height and width
        self.height = height
        self.width = width

        # Using set() to save (not repeating)
        # Keep track of which cells have been chosen
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of Sentences about the game known to be true
        self.knowledge = []
    def mark_mine(self, cell):
        # marks a cell as a mine
        # update all knowledge to mark all this cell as a mine
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        # Know the cell is safe -> mark and update safes set and knowledge
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        # cell: chosen cell
        # count: the number of mines nearby chosen cell
        # when AI move -> update knowledge base
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        # move and not loss -> this cell is safe
        self.mark_safe(cell)

        # 3) initiate a new sentence to the AI's knowledge base
        cells = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                # Add to the cell collection if the cell is not yet explored
                if 0 <= i < self.height and 0 <= j < self.width:
                    # not yet explored & not mine & not safe
                    if (i, j) not in self.moves_made and (i, j) not in self.mines:
                        cells.add((i, j))
                        
                    # if it is known mine cell, count - 1
                    elif (i, j) in self.mines:
                        count -= 1
        # Add new Sentence (if number of cells and count != 0)
        if len(cells) and count:
            self.knowledge.append(Sentence(cells, count))

        # mark any additional cells as safe or as mines
        for sentence in self.knowledge:
            # Mark safe cells
            safes = sentence.known_safes()
            if safes:
                # remove this cell from all sentence
                for cell in safes.copy():
                    self.mark_safe(cell)
                    
            # Mark mine cells
            mines = sentence.known_mines()
            if mines:
                # remove this cell from all sentence and count-1
                for cell in mines.copy():
                    self.mark_mine(cell)

        # Check for Duplicates and Subsumption
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                # s1 is s2 -> continue
                if s1 is s2:
                    continue
                # s1 and s2 have same cells and count -> Duplicates
                if s1 == s2:
                    self.knowledge.remove(s2)
                # s1 cells is s2 cells' subset -> Subsumption
                elif s1.cells.issubset(s2.cells):
                    update_cells = s2.cells - s1.cells
                    update_count = s2.count - s1.count
                    new_knowledge = Sentence(update_cells, update_count)
                    if new_knowledge not in self.knowledge:
                        self.knowledge.append(new_knowledge)
            # cells = 0 and count = 0 -> meaningless sentence
            for s in self.knowledge:
                if not (s.cells or s.count):
                    self.knowledge.remove(s)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_move = self.safes - self.moves_made
        if len(safe_move) > 0:
            print("safe choice:", len(safe_move))
            return random.choice(tuple(safe_move))
        # no confident safe move
        return None

    # def make_random_move(self):
    #     # safe set is NULL -> random choose (avoid the ensure mine cells)
    #     """
    #     Returns a move to make on the Minesweeper board.
    #     Should choose randomly among cells that:
    #         1) have not already been chosen, and
    #         2) are not known to be mines
    #     """
    #     # if no move can be made
    #     if len(self.mines) + len(self.moves_made) == self.height * self.width:
    #         return None

    #     # loop until an appropriate move is found
    #     while True:
    #         i = random.randrange(self.height)
    #         j = random.randrange(self.width)
    #         if (i, j) not in self.moves_made and (i, j) not in self.mines:
    #             return (i, j)
    
def make_random_move(ai, game):
    # safe set is NULL -> random choose (avoid the ensure mine cells)
    """
    Returns a move to make on the Minesweeper board.
    Should choose randomly among cells that:
        1) have not already been chosen, and
        2) are not known to be mines
    """
    # # if no move can be made
    # if len(self.mines) + len(self.moves_made) == self.height * self.width:
    #     return None

    # loop until an appropriate move is found
    while True:
        i = random.randrange(game.height)
        j = random.randrange(game.width)
        if (i, j) not in ai.moves_made and (i, j) not in game.mines:
            return (i, j)
