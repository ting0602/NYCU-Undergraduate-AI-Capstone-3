import itertools
import random
import copy
random.seed (5)

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

class literal():
    def __init__(self, pos, value=1):
        self.pos = pos
        self.value = value
        
    def __eq__(self, other):
        # when cells and count are equal
        return self.cells == other.cells and self.value == other.value

class Sentence():
    def __init__(self, cells):
        # cells are the mine candidate
        # count is the number of mine
        self.cells = set(cells) # m unmarked cells

    def __eq__(self, other):
        # when cells and count are equal
        return self.cells == other.cells

    # def __str__(self):
    #     return f"{self.cells} contain {self.count} mine" 
    
    def __len__(self):
        return len(self.cells)

    def be_not(self):
        new_cells = set()
        for c in self.cells:
            new_c = (c[0], c[1], -c[2])
            new_cells.add(new_c)
        return new_cells
    
    def matching_sentence(self, other, target):
        # target in other, -target in self
        self_cells = self.cells
        other_cells = other.cells

        other_cells.remove(target)
        n_target = (target[0], target[1], -target[2])
        self_cells.remove(n_target)
        new_cells = (other_cells | self_cells)

        s = Sentence(new_cells)
        return s
    # def known_mines(self):
    #     # when count == cells -> all cells are mines!
    #     if self.count == len(self.cells):
    #         return self.cells
    #     return None

    # def known_safes(self):
    #     # when count = 0 -> all cells are safe!
    #     if self.count == 0:
    #         return self.cells
    #     return None

    # def mark_mine(self, cell):
    #     # Update when know that the cell is mine
    #     if cell in self.cells:
    #         self.cells.remove(cell)
    #         self.count -= 1

    # def mark_safe(self, cell):
    #     # Update when know that the cell is safe
    #     if cell in self.cells:
    #         self.cells.remove(cell)


class MinesweeperAI():
    def __init__(self, height, width):
        # Set initial height and width
        self.height = height
        self.width = width
        # Using set() to save (not repeating)
        # Keep track of which cells have been chosen
        self.moves_made = set()
        
        self.pos_set = set()

        # Keep track of cells known to be safe or mines
        # positive clauses 
        self.mines = set()
        # negative clauses
        self.safes = set()

        # List of Sentences about the game known to be true
        self.knowledge = []
        self.knowledge0 = []

        self.game = None
        
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            self.board.append(row)
    # def mark_mine(self, cell):
    #     # marks a cell as a mine
    #     # update all knowledge to mark all this cell as a mine
    #     self.mines.add(cell)
    #     for sentence in self.knowledge:
    #         sentence.mark_mine(cell)

    # def mark_safe(self, cell):
    #     # Know the cell is safe -> mark and update safes set and knowledge
    #     self.safes.add(cell)
    #     for sentence in self.knowledge:
    #         sentence.mark_safe(cell)

    def mark_board(self, board, say=""):
        mark_board = []
        print("in the check:", say)
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
                    print("Error board")
                    print((i, j), mark_board[i][j], v)
                    for s in self.mines:
                        print(s)
                    return False
        #             # exit(1)
        # print("-------mark -----------")
        # for i in range(self.height):
        #     print(mark_board[i])
        # print("-------mark -----------")
        
        # print("-------origin -----------")
        # for i in range(self.height):
        #     print(board[i])
        # print("-------origin -----------")
        return True

                
    def mark_single_literal(self, sentence):
        if len(sentence) != 1:
            return 0
        for cell in sentence.cells:
            if cell[2] == 1:
                self.mines.add(cell)
            else:
                self.safes.add(cell)
            # self.get_kb0()
            # for kk in self.knowledge0:
            #     print(kk.cells)       
            self.knowledge0.append(sentence)
            if sentence in self.knowledge:
                self.knowledge.remove(sentence)
    
    def inserting(self, s1):
        # About inserting a new clause to the KB:
        # for s1 in self.knowledge:
        # self.get_kb0()
        
        for s in self.knowledge0:
            self.unit_propagation(s)
                
        #     for s2 in self.knowledge:
        #         if s.cells.issubset(s2.cells) and len(s2) > 1:
        #             self.knowledge.remove(s2)
        #             s2.cells = s2.cells - s.cells
        #             new_s2 = Sentence(s2.cells)
        #             if len(new_s2) > 0:
        #                 self.knowledge.append(new_s2)
        if len(s1) == 1:
            self.mark_single_literal(s1)
            self.unit_propagation(s1)
        elif len(s1) > 1:
            for s2 in self.knowledge:
                if s1 is s2:
                    continue
                # # s1 and s2 have same cells and count -> Duplicates
                # elif s1 == s2: -> subset
                #     continue
                # s1 cells is s2 cells' subset -> Subsumption
                elif s1.cells.issubset(s2.cells):
                    if s1 not in self.knowledge:
                        # self.knowledge.append(s1)
                        # self.knowledge.remove(s1)
                        self.knowledge.remove(s2)
                        # return 0
                elif s2.cells.issubset(s1.cells):
                    if s1 not in self.knowledge:
                        # not insert the s1
                        
                        # self.knowledge.append(s1)
                        # self.knowledge.remove(s1)
                        # self.knowledge.remove(s2)
                        return 0
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
            if len(target) == 1:
                for t in target:
                    # print(n_cells, "\n=====\n",s2.cells)
                    # print(target)
                    new_sentence = s1.matching_sentence(s2, t)
                    if len(new_sentence) > 0:
                        self.inserting(new_sentence)
                    # self.knowledge.append(new_sentence)
                    
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
                    # Check against the list of single-literal clauses first.
                    self.inserting(Sentence(new_multi_literal))
                    # try:
                    #     self.inserting(Sentence(new_multi_literal))
                    # except:
                    #     print("check error", multi_literal.cells)
                    #     print(new_multi_literal)
        
    def init_knowledge(self, pos):
        if pos in self.pos_set:
            return 0
        self.pos_set.add(pos)
        cell_set = set()
        cell_set.add((pos[0], pos[1], -1))
        self.knowledge.append(Sentence(cell_set))
        self.moves_made.add((pos[0], pos[1], -1))
        self.board[pos[0]][pos[1]] = -1
        
    def get_nearby_mines(self, pos):
        nearby = self.game.nearby_mines(pos)
        return nearby
    
    def init_neighbors(self, pos):
        cells = set()
        n = self.get_nearby_mines(pos)
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
        print("m, n", m, n, ", pos:", pos)
        
        # all mines
        if m == 0:
            return 0
        if m == n:
            for c in cells:
                cell_set = set()
                cell_set.add((c[0], c[1], 1))
                # self.knowledge.append(Sentence(cell_set))
                self.inserting(Sentence(cell_set))
            if not self.mark_board(self.game.board, "in m==n"):
                print("KB", len(self.knowledge), len(self.knowledge0))
                return 0
        # all safe
        elif n == 0:
            for c in cells:
                cell_set = set()
                cell_set.add(c)
                # self.knowledge.append(Sentence(cell_set))
                self.inserting(Sentence(cell_set))
                
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
            
    def add_knowledge(self, game, move=None):
        # if move is not None:
        #     self.init_knowledge(move)
        
        # cell: chosen cell
        # count: the number of mines nearby chosen cell
        # when AI move -> update knowledge base
        self.game = game

        copy_knowledge = []
        copy_knowledge = copy.deepcopy(self.knowledge)
        # for k in copy_knowledge:
        #     rr += 1
        #     print(k.cells)
        #     if rr == 4:
        #         print(" ========= ")
        #         break
        # count = 0
        # rr = 0
        for k in copy_knowledge:
            # If there is a single-lateral clause in the KB:
            if len(k) == 1:
                
                # Mark that cell as safe or mined.
                # Move that clause to KB0.
                self.mark_single_literal(k)

                # count += 1
                # self.matching(k)
                self.unit_propagation(k)
                if not self.mark_board(game.board, "after unit_pro"):
                    print("STEP2 ERROR", k.cells)
                    return 0
                          
                # print("update k")
                # for k in self.knowledge:
                #     print(k.cells)
                print("KB", len(self.knowledge), len(self.knowledge0))
                for c in k.cells:
                    if c[2] == -1:
                        self.init_neighbors(c[:2])
                if not self.mark_board(game.board, "after neighbor"):
                    print("STEP3 ERROR", k.cells)
                    print("KB", len(self.knowledge), len(self.knowledge0))
                    return 0
            else:
                self.matching(k)
                if not self.mark_board(game.board, "after matching"):
                    print("matching ERROR", k.cells)
                    print("KB", len(self.knowledge), len(self.knowledge0))
                    return 0
                        
        # copy_knowledge = []
        # copy_knowledge = copy.deepcopy(self.knowledge)
        # for k in copy_knowledge:
        #     if len(k) == 1:
        #         print("not clear!!!")
        #     self.matching(k)
        #         # print("matching22")
        #         # self.clear_kb()
        print(len(self.knowledge), len(self.knowledge0))
        # exit(1)      

        print("======================")   
        for sentence in self.knowledge:
            print(sentence.cells)
        print("======================")
        
        # count = 0
        # self.get_kb0()
        # for s in self.knowledge0:
        #     print(s.cells)
        #     for k in self.knowledge:
        #         if s.cells.issubset(k.cells):
        #             # print(s.cells)
        #             count += 1
        print("count:")
        print(len(self.knowledge), len(self.knowledge0))
        print(len(self.moves_made), len(self.safes), len(self.mines))
        # print(self.mines)
        # print("======================")   
        
        return 0
    
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_move = self.safes - self.moves_made
        safe_move = []
        for safe in self.safes:
            if safe[:2] not in self.pos_set:
                safe_move.append(safe[:2])
        if len(safe_move) > 0:
            print("safe choice:", len(safe_move))
            action = random.choice(tuple(safe_move))
            print("move to:", action)
            
            return action
        # no confident safe move
        print("pos", len(self.safes), len(self.pos_set))
        return None
            
            
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
