import pygame
import sys
import subprocess
import os

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ChronoChaos Menu")

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

try:
    pygame.mixer.music.load(resource_path("assets/music.mp3"))
except pygame.error as e:
    print(f"Error loading music file: {e}")

BACKGROUND_COLOR = (146, 244, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 200, 0)

font_title = pygame.font.Font(None, 74)
font_buttons = pygame.font.Font(None, 50)
font_instructions = pygame.font.Font(None, 24)
font_description = pygame.font.Font(None, 30)

MENU = 0
LEVEL1_STORY_MODE = 1
LEVEL2_STORY_MODE = 2
EXIT = 3

game_state = MENU

class Button:
    def __init__(self, x, y, width, height, text, default_color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.default_color = default_color
        self.hover_color = hover_color
        self.current_color = self.default_color

    def draw(self, surface, is_selected):
        if is_selected:
            self.current_color = self.hover_color
        else:
            self.current_color = self.default_color

        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        text_surf = font_buttons.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

button_width = 300
button_x = (SCREEN_WIDTH - button_width) // 2
level1_button = Button(button_x, SCREEN_HEIGHT // 2 + 80, button_width, 60, "Story Mode: Easy", GRAY, GREEN)
level2_button = Button(button_x, SCREEN_HEIGHT // 2 + 160, button_width, 60, "Story Mode: Hard", GRAY, GREEN)
exit_button = Button(button_x, SCREEN_HEIGHT // 2 + 240, button_width, 60, "Exit", GRAY, GREEN)

buttons = [level1_button, level2_button, exit_button]
selected_index = 0

descriptions = {
    0: "Embark on an epic adventure to defeat the evil witch.",
    1: "Continue your journey and face new challenges.",
    2: "Exit the game."
}

def main_menu():
    global game_state, selected_index
    
    try:
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Could not play music. The file may not have loaded.")
    
    while game_state == MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = EXIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(buttons)
                elif event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_index == 0:
                        game_state = LEVEL1_STORY_MODE
                    elif selected_index == 1:
                        game_state = LEVEL2_STORY_MODE
                    elif selected_index == 2:
                        game_state = EXIT

        screen.fill(BACKGROUND_COLOR)

        title_surf = font_title.render("ChronoChaos", True, BLACK)
        title_rect = title_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_surf, title_rect)

        instructions_surf = font_instructions.render("Use W/S to navigate and ENTER/SPACE to select.", True, BLACK)
        instructions_rect = instructions_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 225))
        screen.blit(instructions_surf, instructions_rect)

        for i, button in enumerate(buttons):
            button.draw(screen, i == selected_index)

        description_text = descriptions[selected_index]
        description_surf = font_description.render(description_text, True, BLACK)
        description_rect = description_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 200))
        screen.blit(description_surf, description_rect)

        pygame.display.flip()
    

def start_level1_story_mode():
    global game_state
    

    try:
        cutscene_image1 = pygame.image.load(resource_path(r"assets/cutscene1.jpg")).convert()
        cutscene_image1 = pygame.transform.scale(cutscene_image1, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        return

    screen.blit(cutscene_image1, (0, 0))
    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting_for_key = False

    try:
        cutscene_image2 = pygame.image.load(resource_path(r"assets/cutscene2.jpg")).convert()
        cutscene_image2 = pygame.transform.scale(cutscene_image2, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        return

    screen.blit(cutscene_image2, (0, 0))
    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting_for_key = False
    
    pygame.quit()

    try:
        subprocess.run([sys.executable, resource_path("Story_Mode_Easy.py")])
    except FileNotFoundError:
        return
    
    sys.exit()

def start_level2_story_mode():
    global game_state

    
    try:
        cutscene_image1 = pygame.image.load(resource_path(r"assets/cutscene1.jpg")).convert()
        cutscene_image1 = pygame.transform.scale(cutscene_image1, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        return

    screen.blit(cutscene_image1, (0, 0))
    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting_for_key = False

    try:
        cutscene_image2 = pygame.image.load(resource_path(r"assets/cutscene2.jpg")).convert()
        cutscene_image2 = pygame.transform.scale(cutscene_image2, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error:
        return

    screen.blit(cutscene_image2, (0, 0))
    pygame.display.flip()

    waiting_for_key = True
    while waiting_for_key:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting_for_key = False
    
    pygame.quit()

    try:
        subprocess.run([sys.executable, resource_path("Story_Mode_Hard.py")])
    except FileNotFoundError:
        return
    
    sys.exit()

while game_state != EXIT:
    if game_state == MENU:
        main_menu()
    elif game_state == LEVEL1_STORY_MODE:
        start_level1_story_mode()
    elif game_state == LEVEL2_STORY_MODE:
        start_level2_story_mode()
    elif game_state == EXIT:
        pygame.quit()
        sys.exit()
