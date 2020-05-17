import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

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
        """
        Prints a text-based representation
        of where mines are located.
        """
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
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.safe_cells = set()
        self.mine_cells = set()

        if self.count == len(self.cells):   # all are mines
            self.mine_cells = self.cells.copy()
        elif self.count == 0:               # all are safe
            self.safe_cells = self.cells.copy()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mine_cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safe_cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.mine_cells.add(cell)

        # If I've discovered all the mines, rest are safe
        if len(self.mine_cells) == self.count:
            discovered_safes = self.cells.difference(self.mine_cells)
            self.safe_cells = self.safe_cells.union(discovered_safes)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.safe_cells.add(cell)

        # I've discovered all the safes, rest are mines
        if len(self.cells.difference(self.safe_cells)) == self.count:
            discovered_mines = self.cells.difference(self.safe_cells)
            self.mine_cells = self.mine_cells.union(discovered_mines)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
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
        self.moves_made.add(cell)
        self.mark_safe(cell)

        new_sentence = Sentence(self.get_neighbour_cells(cell), count)

        # let the new_sentence know the global state,
        # so that it could take it into account and update internal representations
        for mine in self.mines:
            new_sentence.mark_mine(mine)
        for safe in self.safes:
            new_sentence.mark_safe(safe)

        self.knowledge.append(new_sentence)

        while True:
            change_counter = 0
            for sentence in self.knowledge:
                # ask each sentence if it discovered new_safes or new_mines
                new_safes = sentence.known_safes().difference(self.safes)
                new_mines = sentence.known_mines().difference(self.mines)

                change_counter += len(new_safes) + len(new_mines)

                # synchronize with all the sentences
                for safe in new_safes:
                    self.mark_safe(safe)
                for mine in new_mines:
                    self.mark_mine(mine)

            if change_counter == 0:
                break

        print("Known Safeties Left: ", len(self.safes.difference(self.moves_made)), self.safes.difference(self.moves_made))
        print("Known Mines at: ", len(self.mines), self.mines)
        print("Moves Left: ", self.height*self.width-len(self.moves_made))

    def get_neighbour_cells(self, cell):
        x, y = cell[0], cell[1]

        neighbour_list = []
        for i in range(max(0, x-1), min(self.width, x+1+1)):
            for j in range(max(0, y-1), min(self.height, y+1+1)):
                if not (x == i and y == j):
                    neighbour_list.append((i, j))

        return neighbour_list

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        rand_list = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    rand_list.append((i, j))

        if len(rand_list) == 0:
            return None
        else:
            return rand_list[random.randint(0, len(rand_list)-1)]