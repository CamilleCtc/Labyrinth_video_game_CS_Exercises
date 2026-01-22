import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from typing import Tuple

Coordinate = Tuple[int, int]
Color = Tuple[int, int, int]
pygame.init()

class GridDisplay:
    def __init__(self,
                 maze: list,
                 robot: list,
                 player: list,
                 MODE: str,
                 size: Coordinate,
                 nb_pixels_by_box: int,
                 grid_color: Color=(220, 220, 220),
                 bg_color: Color=(200, 200, 200),
                 text_color: Color=(0, 0, 0),
                 period_duration: int=100):
        
        self.maze = maze
        self.robot = robot
        self.player = player

        self.MODE = MODE              # "auto", "player", "battle"
        self.maze_size = size

        self.screen_size = (60, 60)
        self.nb_pixels_by_box = nb_pixels_by_box
        self.colors = {"gr": grid_color, "bg": bg_color, "tx": text_color}
        self.screen_type = "game"   # "home", "mode", "difficulty", "game"

        self.period_duration = period_duration
        self.period = 0

        self._initialize_display()

# Uncomment this init to test the interactive screens
    # def __init__(self,
    #              nb_pixels_by_box: int=4,
    #              grid_color: Color=(220, 220, 220),
    #              bg_color: Color=(200, 200, 200),
    #              text_color: Color=(0, 0, 0),
    #              period_duration: int=100):
        
    #     self.maze = None
    #     self.robot = None
    #     self.player = None

    #     self.MODE = "auto"              # default setting
    #     self.difficulty = "small"       # default setting
    #     self.maze_size = None

    #     self.screen_size = (60, 60)
    #     self.nb_pixels_by_box = nb_pixels_by_box
    #     self.colors = {"gr": grid_color, "bg": bg_color, "tx": text_color}
    #     self.screen_type = "home"   # "home", "mode", "difficulty", "game"
    #     self.game_start = False

    #     self.period_duration = period_duration
    #     self.period = 0

    #     self._initialize_display()

    # ------------------------------------------------------------
    # Initialize the display
    # ------------------------------------------------------------
    def _initialize_display(self) -> None:              
        pygame.init()
        self.font = pygame.font.SysFont("monospace", 12)
        
        # initialize the screen
        self.screen = pygame.display.set_mode(
            (self.screen_size[0] * self.nb_pixels_by_box,
             self.screen_size[1] * self.nb_pixels_by_box + 20)
        )

        # maze screen
        self.draw_mode_screen(events=[])

        # # home screen for when i test the interactive screen
        # self.draw_home_screen

    # ------------------------------------------------------------
    # manage the exit condition
    # ------------------------------------------------------------
    def _is_quit_event(self, event):                    
        mods = pygame.key.get_mods()
        if event.type == pygame.QUIT:
            return True
        elif (event.type == pygame.KEYDOWN 
              and (event.key == pygame.K_q or event.key == pygame.K_c)
              and mods & pygame.KMOD_CTRL):
            return True
        return False

    # ------------------------------------------------------------
    # Update the display
    # ------------------------------------------------------------     
    def next_period(self,events) -> bool:                 
        cont = True
        pygame.display.flip()

        for event in events:    # we don't update the screen if we have exit the software
            if self._is_quit_event(event):
                cont = False

        if cont:
            pygame.time.wait(self.period_duration)  # we don't want to update the display too often so we wait for a bit
            self.period += 1
            self._draw_maze()
            # Uncomment the part below and comment the line above to test the interactive screen

            # if self.screen_type == "home":
            #     self.draw_home_screen(events)
            # elif self.screen_type == "difficulty":
            #     self.draw_difficulty_screen(events)
            # elif self.screen_type == "mode":  
            #     self.draw_mode_screen(events)
            # elif self.screen_type == "game":
            #     self._draw_maze()
        return cont

    # ------------------------------------------------------------
    # Draw the maze
    # ------------------------------------------------------------             
    def _draw_maze(self) -> None:                     

        self.screen.fill(self.colors["bg"])
        # we draw a black square under the maze for aesthetics
        pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    (((self.screen_size[0] - self.maze_size[0])//2 - 1) * self.nb_pixels_by_box,
                      ((self.screen_size[1] - self.maze_size[1])//2 - 1) * self.nb_pixels_by_box,
                      (self.maze_size[0] + 2) * self.nb_pixels_by_box,
                      (self.maze_size[1] + 2) * self.nb_pixels_by_box)
                )
        
        # we go through all the cell of the maze
        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                # we calculate the position of the cell
                x = ((self.screen_size[0] - self.maze_size[0])//2 + j) * self.nb_pixels_by_box
                y = ((self.screen_size[1] - self.maze_size[1])//2 + i) * self.nb_pixels_by_box

                cell = self.maze[i][j]

                if cell == 0:
                    color = (0, 0, 0)  # wall = black
                elif self.MODE == "player" and i == self.robot[1] and j == self.robot[0]:
                    color = (255, 255, 255) # we dont show the robot in player mode
                elif i == self.robot[1] and j == self.robot[0]:
                    color = (0, 0, 255)  # robot = blue
                elif self.MODE == "auto" and i == self.player[1] and j == self.player[0]:
                    color = (255, 255, 255) # we dont show the player in robot mode
                elif i == self.player[1] and j == self.player[0]:
                    color = (128, 0, 128)  # player = purple
                elif i == self.maze_size[1]//2 and j == self.maze_size[0]//2:
                    color = (0, 255, 0)  # goal = green
                elif cell == 1:
                    color = (255, 255, 255)  # path = white
                elif cell == 2:
                    color = (255, 0, 0)  # item = red
                elif cell == 3:
                    color = (255, 165, 0)  # bomb = orange
                elif cell == 4:
                    color = (255, 255, 0)  # explosion = yellow
                elif cell == 5:
                    color = (200, 200, 200)  # cleared explosion = light gray
                else:
                    color = (100, 100, 100)

                # we draw the cell at the right position and the right colour
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x, y, self.nb_pixels_by_box, self.nb_pixels_by_box)
                )

    # ------------------------------------------------------------
    # Draw the home title screen and manage the interaction
    # ------------------------------------------------------------ 
    def draw_home_screen(self, events) -> None:
        self.screen.fill(self.colors["bg"])
        color = (100, 100, 100)

        # Mode button
        button_rect_mode = pygame.Rect(
                        20 * self.nb_pixels_by_box,
                        10 * self.nb_pixels_by_box,
                        200,50
                        )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_mode
        )
        text_surface = self.font.render("MODE", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_mode.center)
        self.screen.blit(text_surface, text_rect)
        
        
        # Difficulty button
        button_rect_difficulty = pygame.Rect(
                20 * self.nb_pixels_by_box,
                20 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_difficulty
        )

        text_surface = self.font.render("Difficulty", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_difficulty.center)
        self.screen.blit(text_surface, text_rect)

        # score button (just for aesthetics because the functionnality isn't implemented yet)
        button_rect = pygame.Rect(
                20 * self.nb_pixels_by_box,
                30 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect
        )

        text_surface = self.font.render("Score", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)

        # play button
        button_rect_play = pygame.Rect(
                20 * self.nb_pixels_by_box,
                40 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_play
        )
        text_surface = self.font.render("Play", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_play.center)
        self.screen.blit(text_surface, text_rect)

        # Manage the interaction with the buttons
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # left click
                pos = event.pos
                if button_rect_mode.collidepoint(pos):  # mouse on the mode button
                    self.screen_type = "mode"
                    
                elif button_rect_difficulty.collidepoint(pos):  # mouse on the difficulty button
                    self.screen_type = "difficulty"
                    
                elif button_rect_play.collidepoint(pos):    # mouse on the game button
                    self.game_start = True  # start a game and thus generate a maze
                    self.screen_type = "game"

    # ------------------------------------------------------------
    # Draw the difficulty title screen and manage the interaction
    # ------------------------------------------------------------ 
    def draw_difficulty_screen(self, events) -> None:
        self.screen.fill(self.colors["bg"])
        color = (100, 100, 100)

        # Easy button
        button_rect_easy = pygame.Rect(
                        20 * self.nb_pixels_by_box,
                        10 * self.nb_pixels_by_box,
                        200,50
                        )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_easy
        )
        text_surface = self.font.render("EASY", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_easy.center)
        self.screen.blit(text_surface, text_rect)


        # Medium button
        button_rect_medium = pygame.Rect(
                20 * self.nb_pixels_by_box,
                20 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_medium
        )

        text_surface = self.font.render("MEDIUM", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_medium.center)
        self.screen.blit(text_surface, text_rect)

        # Hard button
        button_rect_hard = pygame.Rect(
                20 * self.nb_pixels_by_box,
                30 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_hard
        )

        text_surface = self.font.render("HARD", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_hard.center)
        self.screen.blit(text_surface, text_rect)

        # back button
        button_rect_home = pygame.Rect(
                20 * self.nb_pixels_by_box,
                40 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_home
        )
        text_surface = self.font.render("BACK", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_home.center)
        self.screen.blit(text_surface, text_rect)

        # Manage the interaction with the buttons
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:    # left click
                pos = event.pos
                if button_rect_easy.collidepoint(pos):   # mouse on the easy button
                    self.difficulty = "easy"
                    self.screen_type = "home"
                elif button_rect_medium.collidepoint(pos):   # mouse on the medium button
                    self.difficulty = "medium"
                    self.screen_type = "home"
                elif button_rect_hard.collidepoint(pos):     # mouse on the hard button
                    self.difficulty = "hard"
                    self.screen_type = "home"
                elif button_rect_home.collidepoint(pos):     # mouse on the back button
                    self.screen_type = "home"

    # ------------------------------------------------------------
    # Draw the mode title screen and manage the interaction
    # ------------------------------------------------------------ 
    def draw_mode_screen(self, events) -> None:
        self.screen.fill(self.colors["bg"])
        color = (100, 100, 100)

        # auto button
        button_rect_auto = pygame.Rect(
                        20 * self.nb_pixels_by_box,
                        10 * self.nb_pixels_by_box,
                        200,50
                        )
        
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_auto
        )
        text_surface = self.font.render("AUTO", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_auto.center)
        self.screen.blit(text_surface, text_rect)

        # labyrinth button
        button_rect_labyrinth = pygame.Rect(
                20 * self.nb_pixels_by_box,
                20 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_labyrinth
        )

        text_surface = self.font.render("LABYRINTH", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_labyrinth.center)
        self.screen.blit(text_surface, text_rect)

        # battle button
        button_rect_battle = pygame.Rect(
                20 * self.nb_pixels_by_box,
                30 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_battle
        )

        text_surface = self.font.render("BATTLE", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_battle.center)
        self.screen.blit(text_surface, text_rect)

        # back button
        button_rect_home = pygame.Rect(
                20 * self.nb_pixels_by_box,
                40 * self.nb_pixels_by_box,
                200,50
                )
        pygame.draw.rect(
            self.screen,
            color,
            button_rect_home
        )
        
        text_surface = self.font.render("BACK", True, (0,0,0))
        text_rect = text_surface.get_rect(center=button_rect_home.center)
        self.screen.blit(text_surface, text_rect)

        # Manage the interaction with the buttons
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:    # left click
                pos = event.pos
                if button_rect_auto.collidepoint(pos):   # mouse on the auto button
                    self.MODE = "auto"
                    self.screen_type = "home"
                elif button_rect_labyrinth.collidepoint(pos):    # mouse on the player button
                    self.MODE = "player"
                    self.screen_type = "home"
                elif button_rect_battle.collidepoint(pos):       # mouse on the battle button
                    self.MODE = "battle"
                    self.screen_type = "home"
                elif button_rect_home.collidepoint(pos):     # mouse on the back button
                    self.screen_type = "home"

    # ------------------------------------------------------------
    # Update the robot position
    # ------------------------------------------------------------ 
    def update_robot_position(self, new_position: Coordinate) -> None:
        self.robot = new_position
    
    # ------------------------------------------------------------
    # Update the player position
    # ------------------------------------------------------------ 
    def update_player_position(self, new_position: Coordinate) -> None:
        self.player = new_position

