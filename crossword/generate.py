import sys

from crossword import *

call_count = 0

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for item in self.domains[var].copy():
                if len(item) != var.length:
                    self.domains[var].remove(item)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False

        x_idx, y_idx = self.crossword.overlaps[x, y]

        possible_letters = set()

        for item_y in self.domains[y]:
            possible_letters.add(item_y[y_idx])

        for item_x in self.domains[x].copy():
            if item_x[x_idx] not in possible_letters:
                self.domains[x].remove(item_x)
                revision = True

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # add everything
        if arcs is None:
            arcs = set()
            for var in self.domains:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    arcs.add((var, neighbor))
                    # adds each arc twice but shouldn't be a problem

        while len(arcs) != 0:
            x, y = arcs.pop()
            revised = self.revise(x, y)

            if len(self.domains[x]) == 0:
                return False
            elif revised:
                for k in self.crossword.neighbors(x):
                    arcs.add((x, k))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = set()
        for var in assignment: 
            if assignment[var] in used_words: 
                return False 
            else: 
                used_words.add(assignment[var])
            
            if len(assignment[var]) != var.length: 
                return False 
            else: 
                for var_2 in self.crossword.neighbors(var): 
                    if var_2 in assignment: 
                        if not self.pair_consistent((var, assignment[var]), (var_2, assignment[var_2])): 
                            return False 

        return True

    def pair_consistent(self, x, y): 
        x_idx, y_idx = self.crossword.overlaps[x[0], y[0]]
        if x[1][x_idx] != y[1][y_idx]: 
            return False
        
        return True 

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # TODO 
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_num = float('inf')
        candidates = []
        for item in self.domains:
            if item not in assignment:
                if min_num > len(self.domains[item]):
                    candidates = [item]
                    min_num = len(self.domains[item])
                elif min_num == len(self.domains[item]):
                    candidates.append(item)

        return candidates[0]

        # if len(candidates) == 1: 
        #     return candidates[0]
        # else: 
        #     sorted_candidates = []

        #     for item in candidates:
        #         sorted_candidates.append((len(self.crossword.neighbors(item)), item))
        #     sorted_candidates = sorted(sorted_candidates)

        #     return sorted_candidates[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment): 
            return assignment
        else: 
            domains_copy = self.domains.copy()
            var = self.select_unassigned_variable(assignment)
            trial_order = self.order_domain_values(var, assignment)
            for trial in trial_order:
                global call_count 
                call_count += 1
                trial_assignment = assignment.copy()
                trial_assignment[var] = trial 
                if self.consistent(trial_assignment): 
                    if self.ac3() == False: 
                        self.domains = domains_copy.copy()
                        continue
                    else: 
                        resulting_assignment = self.backtrack(trial_assignment)
                        if resulting_assignment is not None: 
                            return resulting_assignment
                        else: 
                            self.domains = domains_copy.copy()

                

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure=sys.argv[1]
    words=sys.argv[2]
    output=sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword=Crossword(structure, words)
    creator=CrosswordCreator(crossword)
    assignment=creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)

    print(call_count)

if __name__ == "__main__":
    main()
