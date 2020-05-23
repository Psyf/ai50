# Solving CrossWord 
# using BackTracking Search (optimal) + AC-3 (fast pruning) + Heuristics (make is faster)

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

            # if new domain is null set
            if len(self.domains[x]) == 0:
                return False

            # if something was revised, have to add more arcs back into queue
            elif revised:
                for k in self.crossword.neighbors(x):
                    arcs.add((x, k))

        # all arcs consistent, no domains went to NULL set
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
            # repeated words are not consistent
            if assignment[var] in used_words: 
                return False 
            else: 
                used_words.add(assignment[var])
            
            # words that are not of correct length 
            if len(assignment[var]) != var.length: 
                return False 
            else: 
                for var_2 in self.crossword.neighbors(var): 
                    if var_2 in assignment: 
                        # nodes that do not satisfy overlap constraint
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
        ordered_val = []
        for item in self.domains[var]: 
            count = 0 
            for neighbor in self.crossword.neighbors(var): 
                if item in self.domains[neighbor]: 
                    count += 1

            ordered_val.append((count, item))
        
            # perhaps a better option would be to use a fill AC-3 here to see how many are eliminated. 
            # But that maybe defeats the purpose of choosing a good heuristic to make the process faster...

        ordered_val.sort(key=lambda item: item[0])
        return [x for _, x in ordered_val]

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


        if len(candidates) == 1: 
            return candidates[0]
        else: 
            max_degree = float('-inf')
            result = None
            for item in candidates:
                if len(self.crossword.neighbors(item)) > max_degree: 
                    max_degree = len(self.crossword.neighbors(item))
                    result = item 

            return result

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # base case
        if self.assignment_complete(assignment): 
            return assignment
        else: 
            # save copy in case of backtracking
            domains_copy = self.domains.copy()

            # select one variable 
            var = self.select_unassigned_variable(assignment)

            # order in which to try values from its domain
            trial_order = self.order_domain_values(var, assignment)

            # try the value
            for trial in trial_order:
                # again, make a copy so we don't alter original state
                # in case we need to come back 
                trial_assignment = assignment.copy()
                trial_assignment[var] = trial 

                # if the new assignment makes sense primarily
                if self.consistent(trial_assignment): 

                    # see if you can eliminate more of the domain by arc consistency 
                    # asking AC3 to run on entire graph because as problem becomes smaller, 
                    # less steps needed anyway. 
                    # Possible improvement is to give it only relevant arcs. 
                    if self.ac3() == False: 

                        # if AC3 test fails, load saved state
                        self.domains = domains_copy.copy()

                        # and try next value 
                        continue
                    else: 

                        # if consistent with entire graph UNTIL NOW, 
                        # try assigning the next unassigned variable 
                        # recursive call. Dynamic Programming. 
                        resulting_assignment = self.backtrack(trial_assignment)

                        # if we've actually gone through to max_depth and found a valid assignment!
                        if resulting_assignment is not None: 
                            return resulting_assignment
                        else: 
                            self.domains = domains_copy.copy()

        # if none of the values of the var we selected works out
        # this set of assignments given to this backtrack() was wrong.
        # bubble back up. 
        return None
                
        

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


if __name__ == "__main__":
    main()
