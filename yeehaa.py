import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
PLAYER_SPEED = 5
GOLD_COUNT = 5
BANDIT_SPEED = 2
PROJECTILE_SPEED = 4  # Reduced shot speed
SHOTS_PER_BURST = 6  # Number of shots before reload
RELOAD_TIME = 1.5  # Time to wait before bandit can shoot again
HIT_INVULNERABILITY_TIME = 1  # Time after getting hit where the player is invulnerable

# Horse Constants
HORSE_WIDTH, HORSE_HEIGHT = 60, 60

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gold Rush Getaway")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)  # Font for displaying score

# Load assets
player_img = pygame.Surface((40, 40))
player_img.fill((255, 215, 0))  # Gold color

gold_img = pygame.Surface((20, 20))
gold_img.fill((255, 223, 0))

bandit_img = pygame.Surface((40, 40))
bandit_img.fill((139, 0, 0))  # Dark red for bandits

projectile_img = pygame.Surface((10, 10))  # Square projectiles
projectile_img.fill((255, 0, 0))  # Red color for projectiles

# Horse Constants
horse_img = pygame.Surface((HORSE_WIDTH, HORSE_HEIGHT))


# Player Class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
        self.gold_count = 0  # Coin purse
        self.has_moved = False  # Track if player has started moving
        self.last_hit_time = 0  # Track last time player was hit
        self.is_invulnerable = False  # If the player is invulnerable after being hit

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
            self.has_moved = True
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED
            self.has_moved = True
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
            self.has_moved = True
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += PLAYER_SPEED
            self.has_moved = True

    def draw(self):
        # Draw player (with the hat on top)
        screen.blit(player_img, self.rect.topleft)

    def lose_gold(self, percentage):
        # Only lose gold if the player isn't in invulnerability
        if not self.is_invulnerable:
            self.gold_count = math.floor(self.gold_count * (1 - percentage))  # Lose specified percentage of gold

    def set_invulnerability(self):
        self.is_invulnerable = True
        self.last_hit_time = time.time()

    def check_invulnerability(self):
        # If invulnerability time has passed, reset it
        if self.is_invulnerable and time.time() - self.last_hit_time >= HIT_INVULNERABILITY_TIME:
            self.is_invulnerable = False


# Gold Class
class Gold:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20)

    def draw(self):
        screen.blit(gold_img, self.rect.topleft)


# Bandit Class
class Bandit:
    def __init__(self, image, is_stationary=False):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40), 40, 40)
        self.image = image
        self.is_stationary = is_stationary
        self.projectiles = []  # List to hold projectiles
        self.last_shot_time = 0  # Time of last shot
        self.shooting_delay = RELOAD_TIME  # Time to wait before shooting again
        self.shot_count = 0  # Number of shots fired in the current burst
        self.last_shot_burst_time = 0  # Time when last burst of shots was fired

    def shoot_projectile(self, player):
        current_time = time.time()

        # If it's time to shoot a new burst of shots (no delay between individual shots)
        if self.shot_count < SHOTS_PER_BURST:
            if current_time - self.last_shot_burst_time >= 0.0:  # No delay between shots
                # Shoot 1 projectile for each shot in the burst
                projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 10)  # Square projectiles
                angle = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
                projectile_speed_x = PROJECTILE_SPEED * math.cos(angle)
                projectile_speed_y = PROJECTILE_SPEED * math.sin(angle)
                self.projectiles.append([projectile, projectile_speed_x, projectile_speed_y])
                self.last_shot_burst_time = current_time  # Reset time for next shot
                self.shot_count += 1
        else:
            # If all 6 shots have been fired, reset after the reload time
            if current_time - self.last_shot_time >= RELOAD_TIME:
                self.shot_count = 0
                self.last_shot_time = current_time  # Reset last shot time for reload

    def move_projectiles(self):
        for projectile in self.projectiles[:]:
            projectile[0].x += projectile[1]
            projectile[0].y += projectile[2]
            if projectile[0].x < 0 or projectile[0].x > WIDTH or projectile[0].y < 0 or projectile[0].y > HEIGHT:
                self.projectiles.remove(projectile)

    def move_towards(self, player):
        # Bandit follows the player
        new_x, new_y = self.rect.x, self.rect.y
        if self.rect.x < player.rect.x:
            new_x += BANDIT_SPEED
        elif self.rect.x > player.rect.x:
            new_x -= BANDIT_SPEED

        if self.rect.y < player.rect.y:
            new_y += BANDIT_SPEED
        elif self.rect.y > player.rect.y:
            new_y -= BANDIT_SPEED

        # Check for collision with player before updating position
        potential_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        if not potential_rect.colliderect(player.rect):
            collision = False
            for other_bandit in bandits:
                if other_bandit != self and potential_rect.colliderect(other_bandit.rect):
                    collision = True
                    break
            if not collision:
                self.rect.x, self.rect.y = new_x, new_y

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
        for projectile in self.projectiles:
            screen.blit(projectile_img, projectile[0].topleft)


# Horse Class
class Horse:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH, random.randint(HEIGHT // 2, HEIGHT - 50), HORSE_WIDTH, HORSE_HEIGHT)
        self.speed = 2

    def move(self):
        self.rect.x -= self.speed  # Horse moves from right to left

    def draw(self):
        # Drawing the horse using basic shapes
        # Body of the horse
        pygame.draw.rect(screen, (139, 69, 19), self.rect)
        # Horse legs
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.rect.x + 10, self.rect.y + 40, 10, 20))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(self.rect.x + 40, self.rect.y + 40, 10, 20))
        # Horse head
        pygame.draw.rect(screen, (139, 69, 19), pygame.Rect(self.rect.x + 45, self.rect.y + 10, 20, 20))
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.x + 50, self.rect.y + 15), 5)  # Eye
        # Text above the horse
        win_text = font.render("Hop on, Cowboy!", True, (0, 0, 0))
        screen.blit(win_text, (self.rect.x + self.rect.width // 2 - win_text.get_width() // 2, self.rect.y - 30))


# Game setup
player = Player()
gold_list = [Gold() for _ in range(GOLD_COUNT)]
bandits = [Bandit(bandit_img), Bandit(bandit_img, is_stationary=True)]  # One stationary bandit and one following bandit
horse = Horse()

# Game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.move()
    player.draw()

    # Gold Collection
    new_gold_list = []
    for gold in gold_list:
        if player.rect.colliderect(gold.rect):
            player.gold_count += 1  # Increase coin purse count
            gold_list.append(Gold())  # Respawn new gold
        else:
            new_gold_list.append(gold)
    gold_list = new_gold_list

    for gold in gold_list:
        gold.draw()

    # Bandit Movement and Shooting
    for bandit in bandits:
        bandit.shoot_projectile(player)
        bandit.move_projectiles()
        if not bandit.is_stationary:
            bandit.move_towards(player)  # Following bandit moves towards the player
        bandit.draw()

    # Horse Movement and Win Condition
    if player.gold_count >= 25:
        horse.move()
        horse.draw()
        if player.rect.colliderect(horse.rect):
            win_text = font.render("YEEHAA Cowboy!!", True, (0, 0, 0))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 50))
            pygame.display.flip()
            pygame.time.wait(3000)  # Wait 3 seconds before closing
            running = False  # End the game

    # Display the gold count
    gold_text = font.render(f"Gold: {player.gold_count}", True, (0, 0, 0))
    screen.blit(gold_text, (10, 10))

    pygame.display.flip()

# Quit Pygame
pygame.quit()
