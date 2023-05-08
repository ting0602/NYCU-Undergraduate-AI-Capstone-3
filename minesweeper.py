import random
import copy

class Minesweeper():
    """Minesweeper game representation"""
    def __init__(self, height, width, mines):

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
        self.ans_board = None
        self.init_board()
        
    def init_board(self):
        ans_board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            ans_board.append(row)
            
        for i in range(self.height):
            for j in range(self.width):
                if not self.board[i][j]:
                    ans_board[i][j] = self.nearby_mines((i, j))
                else:
                    ans_board[i][j] = -1
        self.ans_board = ans_board

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
class Sentence():
    def __init__(self, cells):
        # cells are the mine candidate
        # count is the number of mine
        self.cells = set(cells) # m unmarked cells
        # cell = (y, x, 1 or -1)

    def __eq__(self, other):
        # when cells and count are equal
        return self.cells == other.cells
    
    def __len__(self):
        return len(self.cells)

    def be_not(self):
        new_cells = set()
        target_cells = self.cells.copy()
        for c in target_cells:
            new_c = (c[0], c[1], -c[2])
            new_cells.add(new_c)
        return new_cells
    
    def matching_sentence(self, other, target):
        # target in other, -target in self
        self_cells = self.cells.copy()
        other_cells = other.cells.copy()

        other_cells.remove(target)
        n_target = (target[0], target[1], -target[2])
        self_cells.remove(n_target)
        new_cells = (other_cells | self_cells)
        s = Sentence(new_cells)
        return s

class MinesweeperAI():
    def __init__(self, height, width, game):
        # Set initial height and width
        self.height = height
        self.width = width
        self.game = game
        # Using set() to save (not repeating)

        self.pos_set = set()

        # Keep track of cells known to be safe or mines
        # positive clauses 
        self.mines = set()
        # negative clauses
        self.safes = set()

        # List of Sentences about the game known to be true
        self.knowledge = []
        self.knowledge0 = []

        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.board.append(row)

    def mark_board(self, board, say=""):
        mark_board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            mark_board.append(row)
        for sentence in self.knowledge0:
            for c in sentence.cells:
                i, j, v = c
                if board[i][j] and v:
                    mark_board[i][j] = 1
                elif not board[i][j] and v == -1:
                    mark_board[i][j] = -1
                # check the mark 
                else:
                    print("in the check:", say)
                    print("Error board")
                    print((i, j), mark_board[i][j], v)
                    for s in self.mines:
                        print(s)
                    return False
        return True

                
    def mark_single_literal(self, sentence):
        if len(sentence) != 1:
            return 0
        for cell in sentence.cells:
            if sentence not in self.knowledge0:
                self.knowledge0.append(sentence)
                
            if cell[2] == 1:
                self.mines.add(cell)
            else:
                self.safes.add(cell)

            if sentence in self.knowledge:
                self.knowledge.remove(sentence)
    
    def inserting(self, s1):
        # About inserting a new clause to the KB:
        for s in self.knowledge0:
            self.unit_propagation(s)

        if len(s1) == 1:
            self.unit_propagation(s1)
            self.knowledge.append(s1)
            return 0
        
        if len(s1) < 1:
            return 0
        elif len(s1) > 1:
            not_append = False
            for s2 in self.knowledge:
                if s1 is s2:
                    not_append = True
                    continue
                elif s1 == s2:
                    not_append = True
                    continue
                # s1 and s2 have same cells and count -> Duplicates
                # s1 cells is s2 cells' subset -> Subsumption
                elif s1.cells.issubset(s2.cells):
                    if s1 not in self.knowledge:
                        self.knowledge.remove(s2)

                elif s2.cells.issubset(s1.cells):
                    not_append = True
            if not not_append:
                self.knowledge.append(s1)
        
    def matching(self, s1):
        # for s1 in self.knowledge:
        for s2 in self.knowledge:
            if s1 is s2:
                continue
            if s1 == s2:
                continue
            n_cells = s1.be_not()
            target = n_cells & s2.cells
            if len(target) == 1 and len(n_cells) == 2 and len(s2.cells) == 2:
                for t in target:
                    new_sentence = s1.matching_sentence(s2, t)
                    self.inserting(new_sentence)
                    
    def unit_propagation(self, sentence):
        # 4. Unit-propagation heuristic:
        if len(sentence) != 1:
            return 0
        for single_literal in sentence.cells:
            n_single_literal = (single_literal[0], single_literal[1], -single_literal[2])
            for multi_literal in self.knowledge:
                # For each multi-literal clause containing A:
                # If the two occurrences of A are both positive or both negative:
                if len(multi_literal) > 1 and single_literal in multi_literal.cells:
                    self.knowledge.remove(multi_literal)
                    
                # Else: Remove A from the multi-literal clause. This is the result of resolution.
                elif len(multi_literal) > 1 and n_single_literal in multi_literal.cells:
                    self.knowledge.remove(multi_literal)
                    new_multi_literal = multi_literal.cells
                    new_multi_literal.remove(n_single_literal)
                    self.inserting(Sentence(new_multi_literal))
        
    def init_knowledge(self, pos=None):
        if pos is None:
            pos = self.make_random_move()
        else:
            print("user move:", pos)
        if pos in self.pos_set:
            return 0
        self.pos_set.add(pos)
        cell_set = set()
        cell_set.add((pos[0], pos[1], -1))
        self.knowledge.append(Sentence(cell_set))
        self.board[pos[0]][pos[1]] = -1
        return pos
    
    def get_nearby_mines(self, pos):
        nearby = self.game.nearby_mines(pos)
        return nearby
    
    def init_neighbors(self, pos):
        cells = set()
        n = self.get_nearby_mines(pos)
        # n = self.game.ans_board[pos[0]][pos[1]]
        # Loop over all cells within one row and column
        for i in range(pos[0] - 1, pos[0] + 2):
            for j in range(pos[1] - 1, pos[1] + 2):
                # Ignore the cell itself
                # Add to the cell collection if the cell is not yet explored
                if 0 <= i < self.height and 0 <= j < self.width:
                    # not yet explored & not mine & not safe
                    if (i, j) not in self.pos_set and (i, j, 1) not in self.mines and (i, j, -1) not in self.safes:
                        cells.add((i, j, -1))
                    if (i, j, 1) in self.mines:
                        n -= 1
        i, j = pos
        if self.game.board[i][j]:
            print("ERROR it is not safe")
        # Initiation
        m = len(cells)
        cells_list = list(cells)
        
        # all mines
        if m == 0:
            return 0
        if m == n:
            for c in cells:
                cell_set = set()
                cell_set.add((c[0], c[1], 1))
                self.inserting(Sentence(cell_set))
                self.mines.add((c[0], c[1], 1))
            if not self.mark_board(self.game.board, "in m==n"):
                return 0
        # all safe
        elif n == 0:
            for c in cells:
                cell_set = set()
                cell_set.add((c[0], c[1], -1))
                self.inserting(Sentence(cell_set))
                self.safes.add((c[0], c[1], -1))
                
            if not self.mark_board(self.game.board, say="in n==0"):
                print("KB", len(self.knowledge), len(self.knowledge0))
                return 0
        # unsure
        else: # m > n > 0
            # C(m, m-n+1)
            for i in range(m):
                s = set()
                for j in range(i, min(m-n+1+m, m)):
                    c = cells_list[j]
                    s.add((c[0], c[1], 1))
                # self.knowledge.append(Sentence(s))
                if len(s) == m-n+1:
                    self.inserting(Sentence(s))
                
            if not self.mark_board(self.game.board, say="C(m, m-n+1)"):
                print("KB", len(self.knowledge), len(self.knowledge0))
                return 0
            
            # C(m, n+1) clauses, each having n+1 negative literals.
            for i in range(m):
                s = set()
                for j in range(i, min(n+1+m, m)):
                    c = cells_list[j]
                    s.add((c[0], c[1], -1))
                # self.knowledge.append(Sentence(s))
                if len(s) == n+1:
                    self.inserting(Sentence(s))
                
            if not self.mark_board(self.game.board, say="C(m, n+1)"):
                print("KB", len(self.knowledge), len(self.knowledge0))
                return 0
    
    def check_state(self, old_kb):
        if len(self.knowledge) == 0 and len(self.mines) == len(self.game.mines):
            return False
        elif len(self.knowledge) == 0:
            return False
        elif old_kb == self.knowledge:
            return False
        return True
            
    def add_knowledge(self):
        copy_knowledge = []
        loop = True
        while(loop):
            copy_knowledge = copy.deepcopy(self.knowledge)
            for k in copy_knowledge:
                # If there is a single-lateral clause in the KB:
                if len(k) < 1:
                    continue
                elif len(k) == 1:
                    # Mark that cell as safe or mined.
                    # Move that clause to KB0.
                    self.mark_single_literal(k)
                    self.unit_propagation(k)
                    # if not self.mark_board(self.game.board, "after unit_pro"):
                    #     print("STEP2 ERROR", k.cells)
                    #     return 0

                    for c in k.cells:
                        if c[2] == -1:
                            self.init_neighbors(c[:2])
                    # if not self.mark_board(self.game.board, "after neighbor"):
                    #     return 0
                else:
                    self.matching(k)
                    # if not self.mark_board(self.game.board, "after matching"):
                    #     print("matching ERROR", k.cells)
                    #     print("KB", len(self.knowledge), len(self.knowledge0))
                    #     return 0
            loop = self.check_state(copy_knowledge)
        return 0
    
            
            
    def make_random_move(self):
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
            i = random.randrange(self.game.height)
            j = random.randrange(self.game.width)
            if (i, j) not in self.pos_set and (i, j) not in self.game.mines:
                return (i, j)
