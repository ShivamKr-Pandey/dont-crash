import pygame
import random
import json
from enum import Enum

# Initialize Pygame and its modules
pygame.init()
pygame.mixer.init()

# Load custom font
try:
    game_font_large = pygame.font.Font("python/dont-crash/assets/fonts/Bytesized-Regular.ttf", 74)
    game_font_medium = pygame.font.Font("python/dont-crash/assets/fonts/Bytesized-Regular.ttf", 30)
    game_font_small = pygame.font.Font("python/dont-crash/assets/fonts/Bytesized-Regular.ttf", 22)
except Exception as e:
    print(f"Error loading font: {e}")
    game_font_large = pygame.font.Font(None, 74)
    game_font_medium = pygame.font.Font(None, 30)
    game_font_small = pygame.font.Font(None, 22)

# Game Window Settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Don't Crash!!")
clock = pygame.time.Clock()

# Game Object Sizes
PLAYER_WIDTH = 60 
PLAYER_HEIGHT = 80 
OBSTACLE_WIDTH = 60 
OBSTACLE_HEIGHT = 80
POWER_UP_SIZE = 50

# Load player car image
try:
    player_car_img = pygame.image.load("python/dont-crash/assets/images/car.png")
    img_rect = player_car_img.get_rect()
    scale_factor = min(PLAYER_WIDTH / img_rect.width, PLAYER_HEIGHT / img_rect.height)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    player_car_img = pygame.transform.scale(player_car_img, (new_width, new_height))
except Exception as e:
    print(f"Error loading car image: {e}")
    player_car_img = None

def load_high_scores():
    try:
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    except:
        return {'top_scores': []}

def save_high_score(score):
    scores = load_high_scores()
    scores['top_scores'].append(score)
    scores['top_scores'] = sorted(scores['top_scores'], reverse=True)[:5]  # Keep top 5
    with open('high_scores.json', 'w') as f:
        json.dump(scores, f)

# Sound Effects and Music
try:
    collision_sound = pygame.mixer.Sound("python/dont-crash/assets/sounds/collision.mp3")
    power_up_sound = pygame.mixer.Sound("python/dont-crash/assets/sounds/power-up.mp3")
   # score_sound = pygame.mixer.Sound("python/dont-crash/assets/sounds/score.mp3")
    
    pygame.mixer.music.load("python/dont-crash/assets/sounds/bg-music.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Sound initialization error: {e}")
    print("Game will run with limited or no sound.")

# COLORS
DARK_NIGHT_BLUE = (12, 10, 30) 
MIDNIGHT_PURPLE = (25, 15, 45) 
ASPHALT_GREY = (35, 35, 55)  


NEON_CYAN = (0, 255, 255)       
NEON_MAGENTA = (255, 20, 147)  
NEON_LIME_GREEN = (57, 255, 20) 
NEON_ORANGE = (255, 165, 0)     


GLOW_WHITE = (240, 240, 240)    
ELECTRIC_YELLOW = (255, 255, 50) 

# Game States
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    HIGH_SCORES = 4

# Power-up Types
class PowerUpType(Enum):
    SHIELD = 1
    SLOW_TIME = 2
    SPEED_BOOST = 3


# Load player car image
try:
    player_car_img = pygame.image.load("python/dont-crash/assets/images/car.png")
    img_rect = player_car_img.get_rect()
    scale_factor = min(PLAYER_WIDTH / img_rect.width, PLAYER_HEIGHT / img_rect.height)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    player_car_img = pygame.transform.scale(player_car_img, (new_width, new_height))
except Exception as e:
    print(f"Error loading car image: {e}")
    player_car_img = None

# Load opponent car image
try:
    opponent_car_img = pygame.image.load("python/dont-crash/assets/images/opp-car.png")
    img_rect = opponent_car_img.get_rect()
    scale_factor = min(OBSTACLE_WIDTH / img_rect.width, OBSTACLE_HEIGHT / img_rect.height)
    new_width = int(img_rect.width * scale_factor)
    new_height = int(img_rect.height * scale_factor)
    opponent_car_img = pygame.transform.scale(opponent_car_img, (new_width, new_height))
except Exception as e:
    print(f"Error loading opponent car image: {e}")
    opponent_car_img = None

# Load power-up images
try:
    shield_img = pygame.image.load("python/dont-crash/assets/images/shield.png")
    slow_time_img = pygame.image.load("python/dont-crash/assets/images/slow-time.png")
    speed_boost_img = pygame.image.load("python/dont-crash/assets/images/speed-increase.png")
    
    # Scale power-up images
    power_up_images = {}
    for power_type, img in [
        (PowerUpType.SHIELD, shield_img),
        (PowerUpType.SLOW_TIME, slow_time_img),
        (PowerUpType.SPEED_BOOST, speed_boost_img)
    ]:
        scaled_img = pygame.transform.scale(img, (POWER_UP_SIZE, POWER_UP_SIZE))
        power_up_images[power_type] = scaled_img
except Exception as e:
    print(f"Error loading power-up images: {e}")
    power_up_images = None

player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - 120
player_speed = 7
player_shield = False
player_speed_boost = False

# Obstacle Properties
OBSTACLE_WIDTH = 60
OBSTACLE_HEIGHT = 60
obstacle_x = random.randint(200, 600 - OBSTACLE_WIDTH)
obstacle_y = -OBSTACLE_HEIGHT
obstacle_speed = 5

# Power-up Properties
power_up_x = random.randint(200, 600 - POWER_UP_SIZE)
power_up_y = -POWER_UP_SIZE
power_up_speed = 5
power_up_active = False
current_power_up = None
power_up_duration = 0

# Road Properties
ROAD_WIDTH = 400
road_y = 0
road_speed = 5

# Game State
score = 0
game_over = False

def draw_player(x, y):
    if player_car_img is not None:
        border_color = NEON_CYAN
        if player_shield:
            border_color = NEON_MAGENTA
        elif player_speed_boost:
            border_color = ELECTRIC_YELLOW
            
        for i in range(2):
            pygame.draw.rect(screen, border_color, 
                           (x-i-1, y-i-1, PLAYER_WIDTH+2*(i+1), PLAYER_HEIGHT+2*(i+1)), 1)
            
        car_rect = player_car_img.get_rect()
        centered_x = x + (PLAYER_WIDTH - car_rect.width) // 2
        centered_y = y + (PLAYER_HEIGHT - car_rect.height) // 2

        screen.blit(player_car_img, (centered_x, centered_y))

        if player_shield:
            shield_radius = max(PLAYER_WIDTH, PLAYER_HEIGHT) + 10
            pygame.draw.circle(screen, NEON_MAGENTA, (x + PLAYER_WIDTH//2, y + PLAYER_HEIGHT//2), shield_radius, 2)
    else:
        color = ELECTRIC_YELLOW if player_shield else NEON_CYAN
        pygame.draw.rect(screen, color, (x, y, PLAYER_WIDTH, PLAYER_HEIGHT))

def draw_obstacle(x, y):
    if opponent_car_img is not None:
        pulse = (pygame.time.get_ticks() % 1000) / 1000.0
        alpha = int(128 + 127 * pulse) 
        
        for i in range(2):
            glow_surface = pygame.Surface((OBSTACLE_WIDTH+4+2*i, OBSTACLE_HEIGHT+4+2*i), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*NEON_ORANGE[:3], alpha), 
                           (0, 0, OBSTACLE_WIDTH+4+2*i, OBSTACLE_HEIGHT+4+2*i), 1)
            screen.blit(glow_surface, (x-2-i, y-2-i))
        
        screen.blit(opponent_car_img, (x, y))
    else:
        for i in range(3):
            pygame.draw.rect(screen, NEON_ORANGE, (x-i, y-i, OBSTACLE_WIDTH+i*2, OBSTACLE_HEIGHT+i*2), 1)
        pygame.draw.rect(screen, NEON_ORANGE, (x, y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

def draw_power_up(x, y, power_up_type):
    if power_up_images and power_up_type in power_up_images:
        power_up_img = power_up_images[power_up_type]
        
        if power_up_type == PowerUpType.SHIELD:
            bg_color = NEON_CYAN
            glow_color = NEON_MAGENTA
        elif power_up_type == PowerUpType.SLOW_TIME:
            bg_color = NEON_MAGENTA
            glow_color = NEON_CYAN
        elif power_up_type == PowerUpType.SPEED_BOOST:
            bg_color = ELECTRIC_YELLOW
            glow_color = ELECTRIC_YELLOW
        else:
            bg_color = NEON_MAGENTA
            glow_color = NEON_MAGENTA
        
        pulse = (pygame.time.get_ticks() % 1000) / 1000.0
        glow_alpha = int(128 + 127 * pulse)
        
        bg_surface = pygame.Surface((POWER_UP_SIZE + 1, POWER_UP_SIZE + 1), pygame.SRCALPHA)
        pygame.draw.circle(bg_surface, (*bg_color[:3], 100),
                         (POWER_UP_SIZE//2 + 4, POWER_UP_SIZE//2 + 4), 
                         POWER_UP_SIZE//2 + 4)
        screen.blit(bg_surface, (x - 4, y - 4))
        
        for i in range(2):
            glow_surface = pygame.Surface((POWER_UP_SIZE+4+2*i, POWER_UP_SIZE+4+2*i), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*glow_color[:3], glow_alpha),
                             (POWER_UP_SIZE//2 + 2 + i, POWER_UP_SIZE//2 + 2 + i),
                             POWER_UP_SIZE//2 + 2 + i, 1)
            screen.blit(glow_surface, (x-2-i, y-2-i))
        
        screen.blit(power_up_img, (x, y))
    else:
        if power_up_type == PowerUpType.SHIELD:
            color = NEON_CYAN
        elif power_up_type == PowerUpType.SLOW_TIME:
            color = NEON_MAGENTA
        elif power_up_type == PowerUpType.SPEED_BOOST:
            color = ELECTRIC_YELLOW
        else:
            color = NEON_MAGENTA
        
        pygame.draw.circle(screen, (*color[:3], 178), 
                         (x + POWER_UP_SIZE//2, y + POWER_UP_SIZE//2),
                         POWER_UP_SIZE//2)

def draw_road(y):
    pygame.draw.rect(screen, ASPHALT_GREY, (200, y, ROAD_WIDTH, HEIGHT))
    pygame.draw.rect(screen, ASPHALT_GREY, (200, y - HEIGHT, ROAD_WIDTH, HEIGHT))
    
    line_y = y % 80
    while line_y < HEIGHT:
        pygame.draw.rect(screen, GLOW_WHITE, (WIDTH//2 - 5, line_y, 10, 40))
        line_y += 80

def move_player(keys, x):
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and x > 200:
        x -= player_speed
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and x < 600 - PLAYER_WIDTH:
        x += player_speed
    return x

def update_road(y):
    y += road_speed
    if y >= HEIGHT:
        y = 0
    return y

def check_collision(player_x, player_y, obstacle_x, obstacle_y):
    player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
    obstacle_rect = pygame.Rect(obstacle_x, obstacle_y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
    return player_rect.colliderect(obstacle_rect)

def reset_obstacle():
    return random.randint(200, 600 - OBSTACLE_WIDTH), -OBSTACLE_HEIGHT

def draw_score():
    score_text = game_font_medium.render(f'Score: {score}', True, NEON_LIME_GREEN)
    screen.blit(score_text, (10, 10))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(MIDNIGHT_PURPLE)
    overlay.set_alpha(178) 
    screen.blit(overlay, (0, 0))
    
    text = game_font_medium.render('Game Over!', True, NEON_ORANGE)
    score_text = game_font_medium.render(f'Final Score: {score}', True, NEON_LIME_GREEN)
    restart_text = game_font_medium.render('Press R to Restart', True, GLOW_WHITE)
    
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 10))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 70))

def draw_menu():
    title_font = game_font_large
    menu_font = game_font_medium
    control_font = game_font_small
    
    title_text = "Dont't Crash!!"
    title_pos = (WIDTH//2, HEIGHT//4)
    
    # Create flickering effect
    flicker = random.random()
    time_ms = pygame.time.get_ticks()
    
    light_green = (180, 255, 180)
    light_cyan = (180, 255, 255)
    
    base_alpha = 255 if flicker > 0.1 else 180
    
    if flicker > 0.05:
        for i in range(2):
            alpha = int(base_alpha * (0.3 - i * 0.1)) 
            glow_surface = title_font.render(title_text, True, light_cyan)
            glow_surface.set_alpha(alpha)
            glow_rect = glow_surface.get_rect(center=title_pos)
            
            offset = 2 if flicker > 0.5 else 1 
            screen.blit(glow_surface, (glow_rect.x + offset, glow_rect.y))
            screen.blit(glow_surface, (glow_rect.x - offset, glow_rect.y))
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y + offset))
            screen.blit(glow_surface, (glow_rect.x, glow_rect.y - offset))
    
    main_color = light_green if flicker > 0.1 else NEON_LIME_GREEN 
    title = title_font.render(title_text, True, main_color)
    
    pos_shift = 1 if random.random() > 0.95 else 0 
    title_rect = title.get_rect(center=(title_pos[0] + pos_shift, title_pos[1]))
    
    if (time_ms % 16) < 14:
        screen.blit(title, title_rect)
    
    start_text = menu_font.render('Press SPACE to Start', True, NEON_CYAN)
    scores_text = menu_font.render('Press H for High Scores', True, ELECTRIC_YELLOW)
    quit_text = menu_font.render('Press Q to Quit', True, NEON_ORANGE)
    
    # Add control instructions
    controls_text1 = control_font.render('Controls: Arrow Keys or A/D to move', True, NEON_MAGENTA)
    controls_text2 = control_font.render('R to Restart when Game Over', True, NEON_MAGENTA)
    controls_text3 = control_font.render('M to Mute/Unmute Music', True, NEON_MAGENTA)
    
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
    screen.blit(scores_text, (WIDTH//2 - scores_text.get_width()//2, HEIGHT//2 + 50))
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 100))
    
    # Display control instructions
    screen.blit(controls_text1, (WIDTH//2 - controls_text1.get_width()//2, HEIGHT//2 + 150))
    screen.blit(controls_text2, (WIDTH//2 - controls_text2.get_width()//2, HEIGHT//2 + 180))
    screen.blit(controls_text3, (WIDTH//2 - controls_text3.get_width()//2, HEIGHT//2 + 210))

def draw_high_scores():
    scores = load_high_scores()
    title_font = game_font_large
    score_font = game_font_medium
    
    title = title_font.render('HIGH SCORES', True, NEON_LIME_GREEN)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
    
    for i, score in enumerate(scores['top_scores']):
        score_text = score_font.render(f'{i+1}. {score}', True, ELECTRIC_YELLOW)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + i*40))
    
    back_text = score_font.render('Press BACKSPACE to return', True, NEON_ORANGE)
    screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 100))

def reset_game():
    global score, player_x, obstacle_x, obstacle_y, obstacle_speed, power_up_active, player_shield, player_speed_boost
    score = 0
    player_x = WIDTH // 2 - PLAYER_WIDTH // 2
    obstacle_x, obstacle_y = reset_obstacle()
    obstacle_speed = 5
    power_up_active = False
    player_shield = False
    player_speed_boost = False

def spawn_power_up():
    global power_up_x, power_up_y, power_up_active, current_power_up
    power_up_x = random.randint(200, 600 - POWER_UP_SIZE)
    power_up_y = -POWER_UP_SIZE
    power_up_active = True
    current_power_up = random.choice(list(PowerUpType))

# Game Loop
running = True
game_state = GameState.MENU
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    game_state = GameState.PLAYING
                    reset_game()
                elif event.key == pygame.K_h:
                    game_state = GameState.HIGH_SCORES
                elif event.key == pygame.K_q:
                    running = False
            elif game_state == GameState.GAME_OVER:
                if event.key == pygame.K_r:
                    game_state = GameState.PLAYING
                    reset_game()

                    try:
                        pygame.mixer.music.unpause()
                    except:
                        pass
                elif event.key == pygame.K_BACKSPACE:
                    game_state = GameState.MENU
            elif game_state == GameState.HIGH_SCORES:
                if event.key == pygame.K_BACKSPACE:
                    game_state = GameState.MENU
           
            if event.key == pygame.K_m:
                try:
                    if pygame.mixer.music.get_volume() > 0:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(0.6)
                except:
                    pass

    if game_state == GameState.PLAYING:
        # Game Logic
        keys = pygame.key.get_pressed()
        current_speed = player_speed * (1.5 if player_speed_boost else 1)
        player_x = move_player(keys, player_x)
        road_y = update_road(road_y)
        
        # Update obstacle position
        current_obstacle_speed = obstacle_speed * (0.5 if player_speed_boost else 1)
        obstacle_y += current_obstacle_speed
        
        # Power-up logic
        if not power_up_active and random.random() < 0.002:
            spawn_power_up()
        
        if power_up_active:
            power_up_y += power_up_speed
            if power_up_y > HEIGHT:
                power_up_active = False
            elif check_collision(player_x, player_y, power_up_x, power_up_y):
                power_up_active = False
                if current_power_up == PowerUpType.SHIELD:
                    player_shield = True
                    power_up_duration = 300 
                elif current_power_up == PowerUpType.SPEED_BOOST:
                    player_speed_boost = True
                    power_up_duration = 180 
                try:
                    power_up_sound.play()
                except:
                    pass
        
        # Update power-up durations
        if player_shield and power_up_duration > 0:
            power_up_duration -= 1
            if power_up_duration <= 0:
                player_shield = False
        
        if player_speed_boost and power_up_duration > 0:
            power_up_duration -= 1
            if power_up_duration <= 0:
                player_speed_boost = False
        
        if obstacle_y > HEIGHT:
            obstacle_x, obstacle_y = reset_obstacle()
            score += 1
            obstacle_speed = min(obstacle_speed + 0.5, 15)  # Increase speed up to a limit
        
        # Check collision
        if check_collision(player_x, player_y, obstacle_x, obstacle_y):
            if player_shield:
                player_shield = False
                obstacle_x, obstacle_y = reset_obstacle()
            else:
                try:
                    pygame.mixer.music.pause()
                    collision_sound.play()
                except:
                    pass
                game_state = GameState.GAME_OVER
                save_high_score(score)

        screen.fill(DARK_NIGHT_BLUE)  
        pygame.draw.rect(screen, MIDNIGHT_PURPLE, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        draw_road(road_y)
        if power_up_active:
            draw_power_up(power_up_x, power_up_y, current_power_up)
        draw_player(player_x, player_y)
        draw_obstacle(obstacle_x, obstacle_y)
        draw_score()
        
    elif game_state == GameState.MENU:
        screen.fill(DARK_NIGHT_BLUE)
        pygame.draw.rect(screen, MIDNIGHT_PURPLE, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        draw_menu()
        
    elif game_state == GameState.HIGH_SCORES:
        screen.fill(DARK_NIGHT_BLUE)
        pygame.draw.rect(screen, MIDNIGHT_PURPLE, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        draw_high_scores()
        
    elif game_state == GameState.GAME_OVER:
        draw_game_over()

    # Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()