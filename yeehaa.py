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
PROJECTILE_SPEED = 4
HIT_INVULNERABILITY_TIME = 1

# Shooting Constants for Stationary Bandit
BURST_COUNT = 4
SHOT_INTERVAL = 0.75
BURST_DELAY = 0.1
RELOAD_TIME = 1.5
SHOTS_PER_CYCLE = 6

# Horse Constants
HORSE_WIDTH, HORSE_HEIGHT = 60, 60

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gold Rush Getaway")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load assets
player_img = pygame.Surface((40, 40))
player_img.fill((255, 215, 0))

gold_img = pygame.Surface((20, 20))
gold_img.fill((255, 223, 0))

bandit_img = pygame.Surface((40, 40))
bandit_img.fill((139, 0, 0))

projectile_img = pygame.Surface((10, 10))
projectile_img.fill((255, 0, 0))

# Player Class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 40, 40)
        self.gold_count = 0
        self.has_moved = False
        self.last_hit_time = 0
        self.is_invulnerable = False

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
        screen.blit(player_img, self.rect.topleft)
        self.draw_hat()

    def draw_hat(self):
        hat_color = (139, 69, 19)
        hat_width = 50
        hat_height = 15
        hat_x = self.rect.centerx - hat_width // 2
        hat_y = self.rect.top - hat_height - 5
        pygame.draw.rect(screen, hat_color, (hat_x, hat_y, hat_width, hat_height))
        brim_width = 60
        brim_height = 10
        brim_x = self.rect.centerx - brim_width // 2
        brim_y = hat_y + hat_height - 3
        pygame.draw.rect(screen, hat_color, (brim_x, brim_y, brim_width, brim_height))
        pygame.draw.circle(screen, (255, 223, 0), (self.rect.centerx, hat_y + hat_height // 2), 4)

    def lose_gold(self, percentage):
        if not self.is_invulnerable:
            self.gold_count = math.floor(self.gold_count * (1 - percentage))

    def set_invulnerability(self):
        self.is_invulnerable = True
        self.last_hit_time = time.time()

    def check_invulnerability(self):
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
        self.projectiles = []
        self.last_burst_time = 0
        self.shots_fired = 0
        self.burst_shots_fired = 0
        self.last_burst_shot_time = 0
        self.reloading = False
        self.reload_start_time = 0

    def shoot(self, player):
        current_time = time.time()
        if self.reloading:
            if current_time - self.reload_start_time >= RELOAD_TIME:
                self.reloading = False
                self.shots_fired = 0
        else:
            if self.burst_shots_fired < BURST_COUNT:
                if current_time - self.last_burst_shot_time >= BURST_DELAY:
                    self.fire_projectile(player)
                    self.last_burst_shot_time = current_time
                    self.burst_shots_fired += 1
            elif self.shots_fired < SHOTS_PER_CYCLE:
                if current_time - self.last_burst_time >= SHOT_INTERVAL:
                    self.burst_shots_fired = 0
                    self.last_burst_time = current_time
                    self.shots_fired += 1
            else:
                self.reloading = True
                self.reload_start_time = current_time

    def fire_projectile(self, player):
        projectile = pygame.Rect(self.rect.centerx, self.rect.centery, 10, 10)
        angle = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
        projectile_speed_x = PROJECTILE_SPEED * math.cos(angle)
        projectile_speed_y = PROJECTILE_SPEED * math.sin(angle)
        self.projectiles.append([projectile, projectile_speed_x, projectile_speed_y])

    def move_projectiles(self):
        for projectile in self.projectiles[:]:
            projectile[0].x += projectile[1]
            projectile[0].y += projectile[2]
            if projectile[0].x < 0 or projectile[0].x > WIDTH or projectile[0].y < 0 or projectile[0].y > HEIGHT:
                self.projectiles.remove(projectile)

    def move_towards(self, player):
        if not self.is_stationary:
            new_x, new_y = self.rect.x, self.rect.y
            if self.rect.x < player.rect.x:
                new_x += BANDIT_SPEED
            elif self.rect.x > player.rect.x:
                new_x -= BANDIT_SPEED
            if self.rect.y < player.rect.y:
                new_y += BANDIT_SPEED
            elif self.rect.y > player.rect.y:
                new_y -= BANDIT_SPEED
            self.rect.x, self.rect.y = new_x, new_y

    def draw(self):
        screen.blit(self.image, self.rect.topleft)
        self.draw_hat()
        for projectile in self.projectiles:
            screen.blit(projectile_img, projectile[0].topleft)

    def draw_hat(self):
        hat_color = (139, 69, 19)
        hat_width = 50
        hat_height = 15
        hat_x = self.rect.centerx - hat_width // 2
        hat_y = self.rect.top - hat_height - 5
        pygame.draw.rect(screen, hat_color, (hat_x, hat_y, hat_width, hat_height))
        brim_width = 60
        brim_height = 10
        brim_x = self.rect.centerx - brim_width // 2
        brim_y = hat_y + hat_height - 3
        pygame.draw.rect(screen, hat_color, (brim_x, brim_y, brim_width, brim_height))

# Horse Class
class Horse:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH, HEIGHT - HORSE_HEIGHT - 30, HORSE_WIDTH, HORSE_HEIGHT)
        self.speed = 2

    def move(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, (160, 82, 45), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x + 10, self.rect.y + 40, 10, 20))
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x + 40, self.rect.y + 40, 10, 20))
        pygame.draw.circle(screen, (160, 82, 45), (self.rect.x + 60, self.rect.y + 20), 15)  # Head
        pygame.draw.circle(screen, (0, 0, 0), (self.rect.x + 65, self.rect.y + 20), 5)  # Eye
        text = font.render("Hop on, Cowboy!", True, (0, 0, 0))
        screen.blit(text, (self.rect.x - 20, self.rect.y - 30))

# Game setup
player = Player()
gold_list = [Gold() for _ in range(GOLD_COUNT)]
bandits = [Bandit(bandit_img), Bandit(bandit_img, is_stationary=True)]
horse = None

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
    player.check_invulnerability()

    new_gold_list = []
    for gold in gold_list:
        if player.rect.colliderect(gold.rect):
            player.gold_count += 1
            new_gold_list.append(Gold())
        else:
            new_gold_list.append(gold)
    gold_list = new_gold_list

    for gold in gold_list:
        gold.draw()

    for bandit in bandits:
        if bandit.is_stationary:
            bandit.shoot(player)
        else:
            bandit.move_towards(player)
        bandit.move_projectiles()
        bandit.draw()
        for projectile in bandit.projectiles:
            if player.rect.colliderect(projectile[0]):
                if not player.is_invulnerable:
                    player.lose_gold(0.05)
                    player.set_invulnerability()
                    bandit.projectiles.remove(projectile)

    if not bandits[0].is_stationary and player.rect.colliderect(bandits[0].rect):
        if not player.is_invulnerable:
            player.lose_gold(0.10)
            player.set_invulnerability()

    if player.gold_count >= 25 and horse is None:
        horse = Horse()

    if horse:
        horse.move()
        horse.draw()
        if player.rect.colliderect(horse.rect):
            text = font.render("You Win!", True, (0, 255, 0))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False

    score_text = font.render(f"Gold: {player.gold_count}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

pygame.quit()
