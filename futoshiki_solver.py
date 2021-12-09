import time
import csv
import threading

stop_event = threading.Event()

puzzle_solved = False
 
puzzle = [0] * 25
row_constraints = [[0 for column in range(4)] for row in range(5)]
col_constraints = [[0 for column in range(4)] for row in range(5)]

solutions = [{1,2},{1,3},{1,4},{1,5},{2,3},{2,4},{2,5},{3,4},{3,5},{4,5}]

cell = 50

rel = [[2,6],[1,3,7],[2,4,8],[3,5,9],[4,10],
     [1,7,11],[2,6,8,12],[3,7,9,13],[4,8,10,14],[5,9,15],
     [6,12,16],[7,11,13,17],[8,12,14,18],[9,13,15,19],[10,14,20],
     [11,17,21],[12,16,18,22],[13,17,19,23],[14,18,20,24],[15,19,25],
     [16,22],[17,21,23],[18,22,24],[19,23,25],[20,24]]

squareList = []

class Square:
    def __init__(self,id):
        self.id = id
        self.neighours = rel[id - 1][:]
        if puzzle[id - 1] == 0:
            self.solution = [1,2,3,4,5]
            self.solved = False
        else:
            self.solution = [puzzle[id - 1]]
            self.solved = True
        

    def remove_solutions_rows(self):
        for index in gen_row(self):
            if squareList[index - 1].solved:
                for solution in reversed(self.solution):
                    if solution == squareList[index - 1].solution[0]:
                        self.solution.remove(solution)

    def remove_solutions_cols(self):
        for index in gen_col(self):
            if squareList[index - 1].solved:
                for solution in reversed(self.solution):
                    if solution == squareList[index - 1].solution[0]:
                        self.solution.remove(solution)                  

    def only_solution_row(self):
        # now check if this is the ONLY square in the row that has a particular solution i.e. 5, and no other square in row can be 5
        # select each solution, then check all the other squares
        for solution in self.solution:
            found = False
            for sqr in gen_row(self):
                if solution in squareList[sqr - 1].solution:
                    found = True
                    continue
            if found == False:
                self.solved = True
                #remove other partial solutions
                for item in reversed(self.solution):
                    if solution != item:
                        self.solution.remove(item)

    def only_solution_col(self):    
        for solution in self.solution:
            found = False
            for sqr in gen_col(self):
                if solution in squareList[sqr - 1].solution:
                    found = True
                    continue
            if found == False:
                self.solved = True
                #remove other partial solutions
                for item in reversed(self.solution):
                    if solution != item:
                        self.solution.remove(item)

def print_solution():
    for square in squareList:
        print (square.id,square.solution, square.neighours, square.solved)


def gen_square_ids():
    n = 0
    while True:
        yield n % 25
        n += 1

def gen_row(square):
    #row generator
    if (square.id % 5) == 0:
        index = square.id - 4
    else:
        index = square.id - (square.id % 5) + 1

    for x in range(5):
        if (index + x) != square.id:
            yield index + x

def gen_col(square):
    #col generator
    if (square.id % 5) == 0:
        index = 5
    else:    
        index = square.id % 5

    for x in range(5):
        if (index + (x * 5)) != square.id:
            yield (index + (x * 5))

def ApplyConstraints(square):
    #determine the relationships for the current square
    #the neighbour squares are predefined
    #for each neighour check if there is a relationship (0,1 and 2 for none, less and greater than)

    for neighbour in square.neighours:
        #if difference between square ids is 1 then it is a row else a column
        #the lowest id will give index of col index of rel
        #if difference is 5 then it is a column

        if neighbour == square.id + 1:
                #neighbour is RIGHT
                rowIndex = (square.id - 1) // 5
                colIndex = (square.id - 1) % 5

                if row_constraints[rowIndex][colIndex] == 1:
                    ApplyLTConstraint(square,neighbour)   
                
                if row_constraints[rowIndex][colIndex] == 2:
                    ApplyGTConstraint(square,neighbour)

        if neighbour == square.id - 1:
                #neighbour is LEFT
                rowIndex = (neighbour - 1) // 5
                colIndex = (neighbour - 1) % 5

                if row_constraints[rowIndex][colIndex] == 1:
                    ApplyGTConstraint(square,neighbour)
                
                if row_constraints[rowIndex][colIndex] == 2:
                    ApplyLTConstraint(square,neighbour)

        if neighbour == square.id - 5:
                #neighour is UP
                rowIndex = (neighbour - 1) % 5
                colIndex = (neighbour - 1) // 5

                if col_constraints[rowIndex][colIndex] == 1:
                    ApplyGTConstraint(square,neighbour)

                if col_constraints[rowIndex][colIndex] == 2:
                    ApplyLTConstraint(square,neighbour)
        
        if neighbour == square.id + 5:
                #neighbour is DOWN
                rowIndex = (square.id - 1) % 5
                colIndex = (square.id - 1) // 5

                if col_constraints[rowIndex][colIndex] == 2:
                    ApplyGTConstraint(square,neighbour)

                if col_constraints[rowIndex][colIndex] == 1:
                    ApplyLTConstraint(square,neighbour)

    # now check to see if the SQUARE has been solved i.e. only one solution

    if len(square.solution) == 1:
        square.solved = True
        #continue

def ApplyGTConstraint(square,neighbour):
    # SQUARE is > NEIGHBOUR
    # Find smallest number in Neighbour's PS (Y) and remove Y and below from Square's PS
    if squareList[neighbour - 1].solved == True:
        n = squareList[neighbour - 1].solution[0]
    else:
        n = min(squareList[neighbour - 1].solution)
    for solution in reversed(square.solution):
        if solution <= n:
            square.solution.remove(solution)

def ApplyLTConstraint(square,neighbour):
    # SQUARE is < NEIGHBOUR
    # Find largest number in Neighbour's PS (Y) and remove Y and above from Square's PS
    if squareList[neighbour - 1].solved == True:
        n = squareList[neighbour - 1].solution[0]
    else:
        n = max(squareList[neighbour - 1].solution)
    for solution in reversed(square.solution):
        if solution >= n:
            square.solution.remove(solution)             

def ImportPuzzle(csv_file):
    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for r,row in enumerate(csv_reader):
            if r < 5:
                for c,col in enumerate(row):
                    puzzle[r*5 + c] = int(col)
            if r > 4 and r < 10:
                for c,col in enumerate(row):
                    row_constraints[r-5][c] = int(col)
            if r > 9:
                for c,col in enumerate(row):
                    col_constraints[r-10][c] = int(col)
    
    for x in range(1,26):
        squareList.append(Square(x))

def solve():

    id = gen_square_ids()
    unsolved = [square.id for square in squareList if square.solved == False]

    while len(unsolved) > 0 and not stop_event.is_set():
        #check across row for existing solutions and remove from this squares solution set
        #first need to find start of row (index)

        #if stop_event.is_set():
            #print("stop requested")
            #break
        
        square = squareList[next(id)]

        if square.solved == True:
            continue

        square.remove_solutions_rows()
        square.remove_solutions_cols()

        ApplyConstraints(square)
        
        square.only_solution_row()
        square.only_solution_col()

        # check for 2 other squares that share solution i.e. [x,y]
        # remove [x,y] from this square's solution
        # search for squares that meet the criteria
        result = []
        for index in gen_row(square):
            if len(squareList[index-1].solution) == 2:
                if any(elem in square.solution  for elem in squareList[index-1].solution):
                    #store the results
                    result.append(squareList[index-1].solution)
        #do an exhaustive comparision
        if len(result) > 1:
            x = 0
            for solution1 in result:
                x += 1
                for solution2 in result[x:]:
                    #print (square.id,solution1,solution2)
                    if solution1 == solution2:
                        #remove the 2 solutions
                        for item in solution1:
                            if item in square.solution:
                                square.solution.remove(item)
        
        #repeat for columns
        result = []
        for index in gen_col(square):
            if len(squareList[index-1].solution) == 2:
                if any(elem in square.solution  for elem in squareList[index-1].solution):
                    #store the results
                    result.append(squareList[index-1].solution)
        #do an exhaustive comparision
        if len(result) > 1:
            x = 0
            for solution1 in result:
                x += 1
                for solution2 in result[x:]:
                    #print (square.id,solution1,solution2)
                    if solution1 == solution2:
                        #remove the 2 solutions
                        for item in solution1:
                            if item in square.solution:
                                square.solution.remove(item)

        # this rule was added after trying to solve the Times Futoshiki where there were only 2 squares
        # that shared {1,2} as partial solutions i.e. row = [{3,4,5},{1,2,3,4,5},{1,2,3,4,5},{3,4,5},{4,5}]
        # go through each possible pair in solution space

        # check square's row                
        for s in solutions:
            if s.issubset(square.solution):
                # check if this pair exists in the other squares
                matches = 0
                for index in gen_row(square):
                    if not s.isdisjoint(squareList[index-1].solution):
                        matches += 1
                if matches == 1:
                    squareList[square.id-1].solution = list(s)

        # now repeat for squares's column
        for s in solutions:
            if s.issubset(square.solution):
                # check if this pair exists in the other squares
                matches = 0
                for index in gen_col(square):
                    if not s.isdisjoint(squareList[index-1].solution):
                        matches += 1
                if matches == 1:
                    squareList[square.id-1].solution = list(s)

        unsolved = [square.id for square in squareList if square.solved == False]

        #print (square.id,len(unsolved))

        #for square in squareList:
            #print (square.id,square.solution, square.neighours, square.solved)

    # either puzzle has been solved OR been told by Main Thread to stop !!
    global puzzle_solved

    print("stop event state is ..",stop_event.is_set())

    if len(unsolved) == 0:
        print("thread has solved ")
        puzzle_solved = True
    else:
        print("thread has NOT solved ")
        puzzle_solved = False

#solve()
        
#ImportPuzzle('puzzles/puzzle0.txt')

#for x in range(1,26):
    #squareList.append(Square(x))

#solve()

#for square in squareList:
    #print (square.id,square.solution, square.neighours, square.solved)

#print_solution()