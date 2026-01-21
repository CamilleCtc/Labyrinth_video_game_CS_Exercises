# import sys
import random as rd
from time import time_ns            ### verif si je l'utilise

import pygame
# from utils import definition_from_str, positive_int_from_str
from display import GridDisplay


# Constants
MODE = None # "auto" or "player" or "battle"

# a voir si je les utilise
DETECTION_DISTANCE = 1 # nombre entier positif different de zero
NB_PIXELS_BY_BOX = 10


# Class robot
class Robot:
    def __init__(self, # the robot
                 x, # x coordinate of the robot
                 y, # y coordinate of the robot
                 type,
                 ):
        #Initialize the robot
        assert isinstance(x, int), "x coordinate of the robot isn't an integer" # x coordinate of the robot must be an integer
        assert isinstance(y, int), "y coordinate of the robot isn't an integer" # y coordinate of the robot must be an integer
        self.position = (x,y)
        self.type = type  # "robot" or "player"
        self.items = 0 # number of items collected by the robot
        
        self.time_drop_bomb = 0  # time when the robot last dropped a bomb
        self.wait_next_bomb = 500  # minimum time between two bomb drops in milliseconds
        
        self.alive = True  # is the robot alive?
        self.color = (0, 0, 255) #color of the robot        (pas sure que ce soit utile)


    def pick_item(self):
        x, y = self.position
        if maze.maze[y][x]==2:
            maze.maze[y][x]=1
            maze.items_positions.remove((x,y))
            maze.nb_items -= 1
            self.items += 1


    def move(self,keys):
        x, y = self.position

        if not self.alive:     # dead robots/players can't move
            return
        
        if MODE == "player" or (MODE == "battle" and self.type == "player"):
            if keys[pygame.K_DOWN] and y<maze.size[1]-1 and maze.maze[y+1][x] != 0:
                y += 1
            elif keys[pygame.K_UP] and y>0 and maze.maze[y-1][x] != 0:
                y -= 1
            elif keys[pygame.K_LEFT] and x>0 and maze.maze[y][x-1] != 0:
                x -= 1
            elif keys[pygame.K_RIGHT] and x<maze.size[0]-1 and maze.maze[y][x+1] != 0:
                x += 1
            
            self.position = (x, y)      # update position
            self.pick_item()

            if MODE == "battle":
                if keys[pygame.K_SPACE]:
                    #drop item
                    if self.items > 0:
                        self.drop_bomb()
        
        elif MODE == "auto":
            # automatic movement using A* pathfinding to the center of the maze
            start = self.position
            goal = (maze.size[0]//2, maze.size[1]//2)
            path = maze.A_star(start, goal)

            if len(path) > 1:
                # move to the next position in the path
                self.position = path[1]  # next position for goal
                self.pick_item()
        
        elif MODE == "battle" and self.type == "robot":
            # automatic movement using A* pathfinding to the player
            start = self.position

            # decide of a goal

            # if the robot doesn't have items, go to the closest item
            if self.items == 0 and maze.items_positions:
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

            if path and len(path) > 1:      #ensure is a path exists
                # move to the next position in the path
                self.position = path[1]  # next position for goal
                self.pick_item()

            # drop bomb if close to player
            if maze.distance(self.position, player.position) == 0:
                self.drop_bomb()


    def drop_bomb(self): 
        x, y = self.position

        current_time = pygame.time.get_ticks()
        if current_time - self.time_drop_bomb < self.wait_next_bomb:
            return  # not enough time has passed since last bomb drop
        
        if self.items < 0:
            return  # no items to drop
        
        maze.list_of_bombs.append(Bomb(x,y))
        maze.maze[y][x] = 3  # place a bomb
        self.items -= 1
        self.time_drop_bomb = current_time  # update last bomb drop time


    def is_dead(self):
        x, y = self.position
        self.alive = not(maze.maze[y][x] == 4)  # 4 represents an explosion so if the robot is on a 4, it was killed in the explosion

# Class Bomb
class Bomb:
    def __init__(self,x,y):
        assert isinstance(x, int), "x coordinate of the bomb isn't an integer" # x coordinate of the bomb must be an integer
        assert isinstance(y, int), "y coordinate of the bomb isn't an integer" # y coordinate of the bomb must be an integer
        self.position = (x,y)
        self.placed_time = pygame.time.get_ticks()
        self.exploded = False
        self.explosion_time = None

        self.color = (128, 128, 128) # color of the bomb


    def update(self):
        current_time = pygame.time.get_ticks()

        # the bombe explodes after 3 seconds 
        if not self.exploded and current_time - self.placed_time >= 3000:
            self.boom()
            self.explosion_time = current_time
            self.exploded = True
        
        # clear explosion after 0.5 seconds
        if self.exploded and current_time - self.explosion_time >= 500:
            self.end_boom()
            return True  # explosion cleared

        return False
           

    def boom(self):
        x, y = self.position

        maze.maze[y][x] = 4  # bomb is placed

        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        for dx, dy in directions:
            if  (0 <= x+dx < maze.size[0]) and (0 <= y+dy < maze.size[1]):
                maze.maze[y+dy][x+dx] = 4


    def end_boom(self):
        x, y = self.position
        maze.maze[y][x] = 5  # clear explosion

        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        for dx, dy in directions:
            if  (0 <= x+dx < maze.size[0]) and (0 <= y+dy < maze.size[1]):
                if  maze.maze[y+dy][x+dx] == 4:
                    maze.maze[y+dy][x+dx] = 5  # clear explosion           
            if maze.items_positions and (x+dx, y+dy) in maze.items_positions:
                maze.maze[y+dy][x+dx] = 2  # restore item if it was on explosion
        maze.place_items(1)  # place a new item in the maze to replace the one used for the bomb
        maze.nb_items += 1

# Class maze
class Maze:
    def __init__(self, width, height, nb_items):
        # Checks
        assert isinstance(width, int) and width > 0
        assert isinstance(height, int) and height > 0
        assert isinstance(nb_items, int) and nb_items >= 0

        self.size = (width, height)

        self.nb_items = nb_items           
        # Items stored as a list of (x,y)
        self.items_positions = []

        self.list_of_bombs = []

        # Maze will be filled with 0 (walls) and 1 (paths)
        self.maze = self.generate_perfect_maze()

        # Place items now
        self.place_items(nb_items)


    # ------------------------------------------------------------
    # PERFECT MAZE GENERATION (DFS / recursive backtracker)        0 = mur, 1 = chemin
    # ------------------------------------------------------------
    def generate_perfect_maze(self):
        w, h = self.size
        maze = [[0 for _ in range(w)] for _ in range(h)]

        directions = [(1,0), (-1,0), (0,1), (0,-1)]

        def inside(x, y):
            return 0 <= x < w and 0 <= y < h

        def neighbors_2steps(x, y):
            N = []
            for dx, dy in directions:
                nx, ny = x + 2*dx, y + 2*dy
                if inside(nx, ny) and maze[ny][nx] == 0:
                    N.append((nx, ny, dx, dy))
            return N

        # Start on an odd cell
        start_x = rd.randrange(0, w, 2)
        start_y = rd.randrange(0, h, 2)
        maze[start_y][start_x] = 1

        stack = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            N = neighbors_2steps(x, y)

            if not N:
                stack.pop()
            else:
                nx, ny, dx, dy = rd.choice(N)

                # Carve wall between cells
                maze[y + dy][x + dx] = 1
                maze[ny][nx] = 1

                stack.append((nx, ny))

        maze[ self.size[1]//2 ][ self.size[0]//2 ] = 1  # Ensure center is a path
        return maze

    # ------------------------------------------------------------
    # PLACE ITEMS IN THE MAZE
    # ------------------------------------------------------------
    def place_items(self, nb_items):
        placed = 0
        w, h = self.size

        while placed < nb_items:
            x = rd.randint(0, w - 1)
            y = rd.randint(0, h - 1)

            # Place item only on path cells
            if self.maze[y][x] != 0:
                self.maze[y][x] = 2
                self.items_positions.append((x, y))
                placed += 1

    # ------------------------------------------------------------
    # PATH FINDER (A* ALGORITHM)        #### A FAIRE
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
        parent = {}      # to reconstruct the path

        while open_set:     # while there are positions to explore
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf'))) # ?????

            if current == goal:     # goal reached
                return self.reconstruct_path(parent, current)

            # update sets
            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self.get_neighbors(current):    # check all neighbors of current position
                if neighbor in closed_set or self.is_wall(neighbor):    # ignore already explored positions and walls
                    continue

                tentative_g_score = g_score[current] + 1    # +1 for each step

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score.get(neighbor, float('inf')):   # not a better path
                    continue

                # This path is the best so far. remember it
                parent[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self.distance(neighbor, goal)

        return []  # No path found


    def reconstruct_path(self, parent, current):
        path = [current]        # reconstruct the path from goal to start
        while current in parent:
            current = parent[current]
            path.append(current)
        path.reverse()         # reverse the path to get it from start to goal
        return path

    def get_neighbors(self, position):
        x, y = position
        neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:   # left, right, up, down, we can only move in straight lines
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size[0] and 0 <= ny < self.size[1]:   # within bounds
                neighbors.append((nx, ny))
        return neighbors

    def is_wall(self, position):
        x, y = position
        return self.maze[y][x] == 0

    def distance(self, start, goal):
        x, y = start
        return abs(x - goal[0]) + abs(y - goal[1])

    


## Main program
# test

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

    if grid.screen_type == "home":
        running = grid.next_period(events)

    # # initialize game
    # if grid.game_start == True:
    #     # Parameters
    #     MODE = grid.MODE

    #     # size/difficulty parameters
    #         # small/easy: 21x21, 10 items
    #         # medium/normal: 35x35, 25 items
    #         # large/hard: 51x51, 50 items

    #     DIFFICULTY = grid.difficulty  # "small" or "medium" or "large"

    #     if DIFFICULTY == "small":
    #         width = 21
    #         height = 21
    #         nb_items = 10
    #     elif DIFFICULTY == "medium":
    #         width = 35
    #         height = 35
    #         nb_items = 25
    #     elif DIFFICULTY == "large":
    #         width = 51
    #         height = 51
    #         nb_items = 50

    #     # Initialize maze
    #     maze = Maze(
    #         width,
    #         height,
    #         nb_items,
    #         )

    #     maze.maze = maze.generate_perfect_maze()
    #     maze.place_items(nb_items)
    #     grid.maze = maze.maze
    #     grid.maze_size = maze.size


    #     # Initialize robot at a random position on the maze border
    #     x = rd.randint(0, maze.size[0]-1)
    #     if x == 0 or x == maze.size[0]-1:
    #         y = rd.randint(0, maze.size[1]-1)
    #     else:
    #         y = rd.choice([0, maze.size[1]-1])

    #     while maze.maze[y][x] != 1:
    #         x = rd.randint(0, maze.size[0]-1)
    #         if x == 0 or x == maze.size[0]-1:
    #             y = rd.randint(0, maze.size[1]-1)
    #         else:
    #             y = rd.choice([0, maze.size[1]-1])
    #     robot = Robot(x, y,"robot")
    #     grid.robot = robot.position

    #     # Initialize player at a random position on the maze border
    #     xp = rd.randint(0, maze.size[0]-1)
    #     if xp == 0 or xp == maze.size[0]-1:
    #         yp = rd.randint(0, maze.size[1]-1)
    #     else:
    #         yp = rd.choice([0, maze.size[1]-1])

    #     while maze.maze[yp][xp] != 1:
    #         xp = rd.randint(0, maze.size[0]-1)
    #         if xp == 0 or xp == maze.size[0]-1:
    #             yp = rd.randint(0, maze.size[1]-1)
    #         else:
    #             yp = rd.choice([0, maze.size[1]-1])
    #     player = Robot(xp, yp,"player")
    #     grid.player = player.position

    #     grid.game_start = False

    keys = pygame.key.get_pressed()
    
    # auto mode
    if MODE == "auto":

        robot.move(keys)
        grid.update_robot_position(robot.position)
        running = grid.next_period(events)

        goal = (maze.size[0]//2, maze.size[1]//2)
        if robot.position == goal:
            print("Goal reached!")
            grid.screen_type = "home"

    # player mode
    if MODE == "player":

        player.move(keys)
        grid.update_player_position(player.position)
        running = grid.next_period(events)

        goal = (maze.size[0]//2, maze.size[1]//2)
        if player.position == goal:
            print("Goal reached!")
            grid.screen_type = "home"

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

        # check if robot or player is dead before moving
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
     

    


