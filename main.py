import random as rd

import pygame
from display import GridDisplay


# Constants
MODE = None # "auto" or "player" or "battle"
DIFFICULTY = None # "small" or "medium" or "large"
NB_PIXELS_BY_BOX = 10


# Class robot
class Robot:
    def __init__(self, # the robot
                 x, # x coordinate of the robot
                 y, # y coordinate of the robot
                 type, # "robot" or "player"
                 ):
        
        #Initialize the robot
        assert isinstance(x, int), "x coordinate of the robot isn't an integer" # x coordinate of the robot must be an integer
        assert isinstance(y, int), "y coordinate of the robot isn't an integer" # y coordinate of the robot must be an integer
        self.position = (x,y)   # position of the robot in the maze
        self.type = type  # "robot" or "player"
        self.items = 0 # number of items collected by the robot
        
        self.time_drop_bomb = 0  # time when the robot last dropped a bomb
        self.wait_next_bomb = 500  # minimum time between two bombs drops in milliseconds
        
        self.alive = True  # is the robot alive?

    # ------------------------------------------------------------
    # Pick item from the maze
    # ------------------------------------------------------------
    def pick_item(self):
        x, y = self.position
        if maze.maze[y][x]==2:  # we verify if the robot is on an item
            maze.maze[y][x]=1   # we collect the item the cell became a normal path
            maze.items_positions.remove((x,y))  # we remove the item from the list of the items
            maze.nb_items -= 1
            self.items += 1     # the robot gain 1 item

    # ------------------------------------------------------------
    # Control of the movement of the robot
    # ------------------------------------------------------------
    def move(self,keys):
        x, y = self.position

        if not self.alive:     # dead robots can't move
            return
        
        if MODE == "player" or (MODE == "battle" and self.type == "player"):    # check if the robot is controlled by the player
            # arrow keys control the robot mouvments
            if keys[pygame.K_DOWN] and y<maze.size[1]-1 and maze.maze[y+1][x] != 0:
                y += 1
            elif keys[pygame.K_UP] and y>0 and maze.maze[y-1][x] != 0:
                y -= 1
            elif keys[pygame.K_LEFT] and x>0 and maze.maze[y][x-1] != 0:
                x -= 1
            elif keys[pygame.K_RIGHT] and x<maze.size[0]-1 and maze.maze[y][x+1] != 0:
                x += 1
            
            self.position = (x, y)      # update position
            self.pick_item()            # will pick up the item if there is one

            if MODE == "battle":        # in the mode battle the robot can drop bomb
                if keys[pygame.K_SPACE]:    # the space bar allows the player to drop the bomb
                    if self.items > 0:      # we can only drop a bomb if we own one (item = bomb in the inventary)
                        self.drop_bomb()
        
        elif MODE == "auto":    # automatic movement using A* pathfinding to the center of the maze
            start = self.position
            goal = (maze.size[0]//2, maze.size[1]//2)
            path = maze.A_star(start, goal) # the A* algorithm will give us the shortest path to the goal (centre od the maze)

            if path and len(path) > 1:   # ensure is a path exists
                # move to the next position in the path
                self.position = path[1]     # next position for goal
                self.pick_item()            # we pick up the item automatically if we pass them
        
        elif MODE == "battle" and self.type == "robot": # automatic movement using A* pathfinding to the player
            start = self.position

            # We decide of a goal

            # if the robot doesn't have items, go to the closest item
            if self.items == 0 and maze.items_positions:
                # we look at all the items to go to the closest one
                best_distance = maze.distance(self.position, maze.items_positions[0])
                best_item = maze.items_positions[0]
                for item_pos in maze.items_positions:
                    d = maze.distance(self.position, item_pos)
                    if d < best_distance:
                        best_distance = d
                        best_item = item_pos

                goal = best_item   
            
            # if the robot has items, go to the player
            else:
                goal = player.position

            # find path to the goal
            path = maze.A_star(start, goal)

            if path and len(path) > 1:      # ensure is a path exists
                # move to the next position in the path
                self.position = path[1]     # next position for goal
                self.pick_item()            # we pick up the item automatically if we pass them

            # drop bomb if close to player
            if maze.distance(self.position, player.position) == 0:
                self.drop_bomb()

    # ------------------------------------------------------------
    # Drop a bomb in the maze
    # ------------------------------------------------------------
    def drop_bomb(self): 
        x, y = self.position
        # we ensure we doesn't drop a bomb to soon (when the bomb stacking is implemented it won't be necessary anymore)
        current_time = pygame.time.get_ticks()
        if current_time - self.time_drop_bomb < self.wait_next_bomb:
            return  # not enough time has passed since last bomb drop
        
        if self.items < 0:
            return  # not enough items to drop a bomb
        
        # We create the bomb and initialize the explosion process
        maze.list_of_bombs.append(Bomb(x,y))
        maze.maze[y][x] = 3     # place a bomb
        self.items -= 1         # we use an item to drop the bomb
        self.time_drop_bomb = current_time  # update last bomb drop time

    # ------------------------------------------------------------
    # Check if the robot is dead
    # ------------------------------------------------------------
    def is_dead(self):
        x, y = self.position
        self.alive = not(maze.maze[y][x] == 4)  # 4 represents an explosion so if the robot is on a 4, it was killed in the explosion

# Class Bomb
class Bomb:
    def __init__(self,x,y):
        assert isinstance(x, int), "x coordinate of the bomb isn't an integer" # x coordinate of the bomb must be an integer
        assert isinstance(y, int), "y coordinate of the bomb isn't an integer" # y coordinate of the bomb must be an integer
        self.position = (x,y)
        self.placed_time = pygame.time.get_ticks()  # time the bomb was placed 
        self.exploded = False   # has the bomb exploded ?
        self.explosion_time = None  # time the bomb exploded

    # ------------------------------------------------------------
    # Update the cells affected by the bomb
    # ------------------------------------------------------------
    def update(self):
        current_time = pygame.time.get_ticks()

        # the bombe explodes after 3 seconds if it hasn't already exploded
        if not self.exploded and current_time - self.placed_time >= 3000:
            self.boom()
            self.explosion_time = current_time
            self.exploded = True
        
        # clear explosion after 0.5 seconds if the bomb has already exploded
        if self.exploded and current_time - self.explosion_time >= 500:
            self.end_boom()
            return True  # explosion cleared

        return False    # explosion is not cleared yet
           
    # ------------------------------------------------------------
    # Bomb explosion effect
    # ------------------------------------------------------------
    def boom(self):
        x, y = self.position

        maze.maze[y][x] = 4  # bomb exploded from its centre

        directions = [(1,0), (-1,0), (0,1), (0,-1)] # the bomb exploded in a cross shape

        for dx, dy in directions:
            if  (0 <= x+dx < maze.size[0]) and (0 <= y+dy < maze.size[1]):  # we ensure we are inside the maze
                maze.maze[y+dy][x+dx] = 4   # the cells around the bomb are affected by the explosion

    # ------------------------------------------------------------
    # Clean the bomb effect
    # ------------------------------------------------------------
    def end_boom(self):
        x, y = self.position
        maze.maze[y][x] = 5  # clear explosion

        directions = [(1,0), (-1,0), (0,1), (0,-1)] 

        for dx, dy in directions:
            if  (0 <= x+dx < maze.size[0]) and (0 <= y+dy < maze.size[1]):  # we ensure we are inside the maze
                if  maze.maze[y+dy][x+dx] == 4: # we ensure that the bomb has exploded
                    maze.maze[y+dy][x+dx] = 5  # clear explosion           
            if maze.items_positions and (x+dx, y+dy) in maze.items_positions:
                maze.maze[y+dy][x+dx] = 2  # restore item if it was affected by the explosion
        maze.place_items(1)  # place a new item in the maze to replace the one used for the bomb
        maze.nb_items += 1

# Class maze
class Maze:
    def __init__(self, width, height, nb_items):
        
        assert isinstance(width, int) and width > 0         # we ensure the width is an integer positif
        assert isinstance(height, int) and height > 0       # we ensure the height is an integer positif
        assert isinstance(nb_items, int) and nb_items >= 0  # we ensure the number of items in the maze is an integer positif or equal to 0

        self.size = (width, height)     # the maze's size is width*height

        self.nb_items = nb_items           
        self.items_positions = []       # Items' positions are stored in a list of (x,y)
        self.list_of_bombs = []         # The bombs dropped are stored in a list of Bomb

        self.maze = self.generate_perfect_maze()    # Maze will be filled with 0 (walls) and 1 (paths)
        self.place_items(nb_items)                  # Once the maze is generated, we place the items


    # ------------------------------------------------------------
    # PERFECT MAZE GENERATION (Deep First Search backtracking)        0 = wall, 1 = path
    # ------------------------------------------------------------
    def generate_perfect_maze(self):
        w, h = self.size
        maze = [[0 for _ in range(w)] for _ in range(h)]    # we create a 2-dimension table filled with 0 (walls)

        directions = [(1,0), (-1,0), (0,1), (0,-1)]     # we only move in primary direction (up, down, left, right)

        def inside(x, y):       # we ensure the cell is inside the maze
            return 0 <= x < w and 0 <= y < h

        def neighbors_2steps(x, y):     # we look at the neighbour cells 2 cells over (to leave a wall around the path)
            N = []      # we store all the neighbouring cell in a list
            for dx, dy in directions:
                nx, ny = x + 2*dx, y + 2*dy
                if inside(nx, ny) and maze[ny][nx] == 0:    # we ensure the neighbour cells are in the maze and weren't explored yet
                    N.append((nx, ny, dx, dy))      # we want to know the neighbour cell position and its direction
            return N

        # Start on a random cell
        start_x = rd.randrange(0, w, 2)
        start_y = rd.randrange(0, h, 2)
        maze[start_y][start_x] = 1

        stack = [(start_x, start_y)]        # we store the path we are creating in a stack

        while stack:        # while the stack isn't empty (we are not back at the beginning) we creat a path
            x, y = stack[-1]    # we are working with the cell on the top of the stack (the last one added)
            N = neighbors_2steps(x, y)  # we collect its neighbours not yet explored

            if not N:
                stack.pop() # if all the neighbours were explored we backtrack and repeat the process
            else:
                nx, ny, dx, dy = rd.choice(N)   # we choose a random neighbour to continue the path

                # Carve a path from the cell and the neighbour to ensure we only have 1 cell wide path
                maze[y + dy][x + dx] = 1
                maze[ny][nx] = 1

                stack.append((nx, ny))  # we put the neighbour on top of the stack then reapeat the process

        maze[ self.size[1]//2 ][ self.size[0]//2 ] = 1  # Ensure center is a path
        return maze

    # ------------------------------------------------------------
    # PLACE ITEMS IN THE MAZE
    # ------------------------------------------------------------
    def place_items(self, nb_items):
        placed = 0  # we count the number of items that were successfully place
        w, h = self.size

        while placed < nb_items:    # we continue to place item until they were all placed
            # We randomly choose a position to place the item
            x = rd.randint(0, w - 1)
            y = rd.randint(0, h - 1)

            # Place item only on path cells
            if self.maze[y][x] != 0:
                self.maze[y][x] = 2
                self.items_positions.append((x, y)) # we add the item to the list of item's position
                placed += 1

    # ------------------------------------------------------------
    # PATH FINDER (A* ALGORITHM)       
    # ------------------------------------------------------------
    def A_star(self, start, goal):
        # initialize open and closed sets
        open_set = set()        # positions to explore
        closed_set = set()      # positions already explored
        open_set.add(start)     # starting point of the exploration

        # initialize positions properties

        g_score = {start: 0}        # cost from start to start is 0
        h_score = {start: self.distance(start, goal)}   # estimated distance to goal
        f_score = {start: g_score[start] + h_score[start]}   # total estimated cost
        parent = {}      # we store the path to be able to reconstruct it

        while open_set:     # while there are positions to explore
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf'))) # we look at the closest/cheapest adjacent cell

            if current == goal:     # goal reached
                return self.reconstruct_path(parent, current)   # we reconstruct the path

            # update sets
            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self.get_neighbors(current):    # check all neighbors of current position
                if neighbor in closed_set or self.is_wall(neighbor):    # ignore already explored positions and walls
                    continue

                tentative_g_score = g_score[current] + 1    # +1 for each step (varying price for cell not implement yet)

                if neighbor not in open_set:    # we add the neighbouring cells to the list of cell to explore
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):   # not a better path
                    continue

                # This path is the best so far. remember it
                parent[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self.distance(neighbor, goal)

        return []  # No path found

    # ------------------------------------------------------------
    # Reconstruct path for the A* ALGORITHM  
    # ------------------------------------------------------------
    def reconstruct_path(self, parent, current):
        path = [current]        # reconstruct the path from goal to start
        while current in parent:    # as long as the cell is in parent (= we haven't reach the start) we continue
            current = parent[current]
            path.append(current)
        path.reverse()         # reverse the path to get it from start to goal
        return path

    # ------------------------------------------------------------
    # get neighbour fot the A* ALGORITHM  
    # ------------------------------------------------------------
    def get_neighbors(self, position):
        x, y = position
        neighbors = []      # we collect all the neighbouring cells
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:   # left, right, up, down, we can only move in straight lines
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size[0] and 0 <= ny < self.size[1]:   # the neighbour is in the maze 
                neighbors.append((nx, ny))
        return neighbors

    # ------------------------------------------------------------
    # Calculate the distance between 2 cells for the A* ALGORITHM  
    # ------------------------------------------------------------
    def distance(self, start, goal):
        x, y = start
        return abs(x - goal[0]) + abs(y - goal[1])

    # ------------------------------------------------------------
    # is the cell a wall ? collect the information to ensure collision are properly manage     
    # ------------------------------------------------------------
    def is_wall(self, position):
        x, y = position
        return self.maze[y][x] == 0


## Main program
# test for the modes and difficulty

# Parameters
MODE = "battle"

# size/difficulty parameters
    # small/easy: 21x21, 10 items
    # medium/normal: 35x35, 25 items
    # large/hard: 51x51, 50 items

DIFFICULTY = "medium"  # "small" or "medium" or "large"

if DIFFICULTY == "small":
    width = 21
    height = 21
    nb_items = 10
elif DIFFICULTY == "medium":
    width = 35
    height = 35
    nb_items = 25
elif DIFFICULTY == "large":
    width = 51
    height = 51
    nb_items = 50

# Initialize maze
maze = Maze(
    width,
    height,
    nb_items,
    )

maze.maze = maze.generate_perfect_maze()
maze.place_items(nb_items)

# Initialize robot at a random position on the maze border
# I arbitrarly to first choose the x coordinate so the robot is most likely to be on the top or bottom border
x = rd.randint(0, maze.size[0]-1)
if x == 0 or x == maze.size[0]-1:   
    y = rd.randint(0, maze.size[1]-1)
else:
    y = rd.choice([0, maze.size[1]-1])

while maze.maze[y][x] != 1:
    x = rd.randint(0, maze.size[0]-1)
    if x == 0 or x == maze.size[0]-1:
        y = rd.randint(0, maze.size[1]-1)
    else:
        y = rd.choice([0, maze.size[1]-1])
robot = Robot(x, y,"robot")

# Initialize player at a random position on the maze border
# I arbitrarly to first choose the x coordinate so the player is most likely to be on the top or bottom border
xp = rd.randint(0, maze.size[0]-1)
if xp == 0 or xp == maze.size[0]-1:
    yp = rd.randint(0, maze.size[1]-1)
else:
    yp = rd.choice([0, maze.size[1]-1])

while maze.maze[yp][xp] != 1:
    xp = rd.randint(0, maze.size[0]-1)
    if xp == 0 or xp == maze.size[0]-1:
        yp = rd.randint(0, maze.size[1]-1)
    else:
        yp = rd.choice([0, maze.size[1]-1])
player = Robot(xp, yp,"player")

# Initialize display
grid = GridDisplay(maze=maze.maze,
                   robot=robot.position,
                   player=player.position,
                    MODE=MODE,
                    size=maze.size,
                    nb_pixels_by_box=NB_PIXELS_BY_BOX,
                    period_duration=100
                    )

# Main loop
running = True
while running:
    events = pygame.event.get()

    # exit conditions
    for event in pygame.event.get():
        if grid._is_quit_event(event):
            running = False

    keys = pygame.key.get_pressed()
    
    # auto mode
    if MODE == "auto":

        robot.move(keys)    # move the robot with A*
        grid.update_robot_position(robot.position) # update its position
        running = grid.next_period(events)  # update the screen

        goal = (maze.size[0]//2, maze.size[1]//2)   # goal is the centre of the maze
        if robot.position == goal:  # winning condition
            print("Goal reached!")

    # player mode
    if MODE == "player":

        player.move(keys)   # move the player according to the keys press
        grid.update_player_position(player.position)    # update its position
        running = grid.next_period(events)  # update the screen

        goal = (maze.size[0]//2, maze.size[1]//2)   # goal is the centre of the maze
        if player.position == goal:  # winning condition
            print("Goal reached!")

    # battle mode
    if MODE == "battle":
        
        player.move(keys)   # move the player according to the keys press
        grid.update_player_position(player.position)    # update its position
        robot.move(keys)    # move the robot with A*
        grid.update_robot_position(robot.position)  # update its position
        running = grid.next_period(events)  # update the screen

        for bomb in maze.list_of_bombs[:]:  # update the bombs status
            if bomb.update():   # if the bomb is done exploding it doesn't exist anymore
                maze.list_of_bombs.remove(bomb)

        # check if robot or player are dead
        robot.is_dead()
        player.is_dead()

        # Win/lose conditions
        if not robot.alive and not player.alive:
            print("It's a draw!")
        elif not robot.alive:
            print("You win!")
        elif not player.alive:
            print("You lose!")
     

    
# Test for the interactive title screens


# Initialize display
grid = GridDisplay(
                    nb_pixels_by_box=NB_PIXELS_BY_BOX,
                    period_duration=100
                    )


# Main loop
running = False     # to test this part, put True here and False in the previous loop
while running:
    events = pygame.event.get()

    # exit conditions
    for event in pygame.event.get():
        if grid._is_quit_event(event):
            running = False


    # initialize a game
    if grid.game_start == True:
        # Parameters
        MODE = grid.MODE                # "palyer" or "auto" or "battle"
        DIFFICULTY = grid.difficulty    # "small" or "medium" or "large"

        if DIFFICULTY == "small":
            width = 21
            height = 21
            nb_items = 10
        elif DIFFICULTY == "medium":
            width = 35
            height = 35
            nb_items = 25
        elif DIFFICULTY == "large":
            width = 51
            height = 51
            nb_items = 50

        # Initialize maze
        maze = Maze(
            width,
            height,
            nb_items,
            )

        maze.maze = maze.generate_perfect_maze()
        maze.place_items(nb_items)

        # Update the grid
        grid.maze = maze.maze
        grid.maze_size = maze.size

        # Initialize robot at a random position on the maze border
        x = rd.randint(0, maze.size[0]-1)
        if x == 0 or x == maze.size[0]-1:
            y = rd.randint(0, maze.size[1]-1)
        else:
            y = rd.choice([0, maze.size[1]-1])

        while maze.maze[y][x] != 1:
            x = rd.randint(0, maze.size[0]-1)
            if x == 0 or x == maze.size[0]-1:
                y = rd.randint(0, maze.size[1]-1)
            else:
                y = rd.choice([0, maze.size[1]-1])
        robot = Robot(x, y,"robot")
        grid.robot = robot.position

        # Initialize player at a random position on the maze border
        xp = rd.randint(0, maze.size[0]-1)
        if xp == 0 or xp == maze.size[0]-1:
            yp = rd.randint(0, maze.size[1]-1)
        else:
            yp = rd.choice([0, maze.size[1]-1])

        while maze.maze[yp][xp] != 1:
            xp = rd.randint(0, maze.size[0]-1)
            if xp == 0 or xp == maze.size[0]-1:
                yp = rd.randint(0, maze.size[1]-1)
            else:
                yp = rd.choice([0, maze.size[1]-1])
        player = Robot(xp, yp,"player")
        grid.player = player.position

        grid.game_start = False # the game was initialize we don't need to initialize it again before the next game

    keys = pygame.key.get_pressed() # keys press
    
    # auto mode
    if MODE == "auto":

        robot.move(keys)
        grid.update_robot_position(robot.position)
        running = grid.next_period(events)

        goal = (maze.size[0]//2, maze.size[1]//2)
        if robot.position == goal:
            print("Goal reached!")
            grid.screen_type = "home"   # when the game is done we go back to the home screen

    # player mode
    if MODE == "player":

        player.move(keys)
        grid.update_player_position(player.position)
        running = grid.next_period(events)

        goal = (maze.size[0]//2, maze.size[1]//2)
        if player.position == goal:
            print("Goal reached!")
            grid.screen_type = "home"   # when the game is done we go back to the home screen

    # battle mode
    if MODE == "battle":
        
        player.move(keys)
        grid.update_player_position(player.position)
        robot.move(keys)
        grid.update_robot_position(robot.position)
        running = grid.next_period(events)

        for bomb in maze.list_of_bombs[:]:
            if bomb.update():
                maze.list_of_bombs.remove(bomb)

        # check if robot or player is dead
        robot.is_dead()
        player.is_dead()

        if not robot.alive and not player.alive:
            print("It's a draw!")
            grid.screen_type = "home"
            robot.alive = True
            player.alive = True
        elif not robot.alive:
            print("You win!")
            grid.screen_type = "home"
            robot.alive = True
        elif not player.alive:
            print("You lose!")
            grid.screen_type = "home"
            player.alive = True
        # when the game is done we go back to the home screen and revive the dead characters     
