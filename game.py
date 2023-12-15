# To create & start using python venv:
#       python -m venv venv
#       source venv/bin/activate

# Intall specific modules with pip:
# f.e.:   pip install pygame

# Requirements
# 1. Make simulation real time
# 2. Add pause / resume logic
# 3. Add save / load logic

# High-level logic
# 1. Create and init the simulation grid (Connect with tick)
# 2. Start the simulation with a tick interval of <n> seconds
# 3. At each tick:
#   3.1. Update the grid - loop over each element of the board
#   3.2. Render new generation

# General approach
# 1. Plan & write down the general workflow
#  1.1. Define Input&Output 
#  1.2. Consider adding validation
# 2. Separate the main algorithms / actors in the code. Try to abstract as much common code as possible
# 3. Define communication between the objects
# 4. List the patterns you could apply
# 5. Build PoCs (Proof of concepts). Try to separate implementation of specific steps. Prepare smaller modules
#    and combine them into a complete application
# 6. Refine if needed

# Deadline - 15th of December 2023
# Mail with: 
# 1. short screen recording demonstrating the new features
# 2. Linked code
# 3. Short description of the changes. Which design patterns you used and how you applied them. 

import pygame
import numpy as np
from abc import ABC, abstractmethod

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Game state
game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])
save_state = np.copy(game_state)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)


def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)


def next_generation():
    global game_state
    new_state = np.copy(game_state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y) % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state = new_state


def draw_cells():
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)


def save_game():
    global game_state
    global save_state
    save_state = np.copy(game_state)


def load_game():
    global game_state
    global save_state
    game_state = save_state


# Define abstract class for elements in game

class AbstractGameElement(ABC):
    def __init__(self, position_x, position_y):
        self.position_x = position_x
        self.position_y = position_y

    @abstractmethod
    def draw(self):
        pass


class Buttons(AbstractGameElement):
    def __init__(self, b_width, b_height, position_x, position_y, button_name):
        super().__init__(position_x, position_y)
        self.b_width = b_width
        self.b_height = b_height
        self.position_x = position_x
        self.position_y = position_y
        self.button_name = button_name
        self.draw()

    def draw(self):
        pygame.draw.rect(screen, green, (self.position_x, self.position_y, self.b_width, self.b_height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.button_name, True, black)
        text_rect = text.get_rect(center=(self.position_x + self.b_width // 2, self.position_y + self.b_height // 2))
        screen.blit(text, text_rect)

    def check_event(self):
        if (self.position_x <= event.pos[0] <= self.position_x + self.b_width and self.position_y <= event.pos[1] <=
                self.position_y + self.b_height):
            return True
        return False



# Ticking
generation_interval, generation_timer, generation_active = 1500, 0, False

running = True
while running:
    screen.fill(white)
    draw_grid()
    draw_cells()
    buttonStart = Buttons(120, 50, 64, 540, "Start")
    buttonStop = Buttons(120, 50, 248, 540, "Stop")
    buttonLoad = Buttons(120, 50, 432, 540, "Load")
    buttonSave = Buttons(120, 50, 616, 540, "Save")

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if buttonStart.check_event():
                next_generation()
                generation_active = True
                generation_timer = pygame.time.get_ticks()
            elif buttonStop.check_event():
                generation_active = False
            elif buttonLoad.check_event():
                load_game()
            elif buttonSave.check_event():
                save_game()
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]

    if generation_active:
        current_time = pygame.time.get_ticks()
        if current_time - generation_timer >= generation_interval:
            next_generation()
            generation_timer = current_time

pygame.quit()
