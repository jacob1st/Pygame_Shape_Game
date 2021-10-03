# A 2D game where the player jumps around the screen on platforms, avoiding falling enemies #

# Ideas: Add enemies that move along the floor that are killable, and maybe enemies that can fly a little

# The libraries that are imported. I think it's easier to read than 'import pygame, sys, random, time'
import pygame
import sys
import random
import time

### DEFINING OUR CLASSES AND FUNCTIONS ###

# Make a player class
class Player:
    def __init__(self, x, y, x_speed, y_speed, health, width, length):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.health = health
        self.run_speed = 3
    # Ability to draw the player
    def draw_char(self, dplay):
        pygame.draw.rect(dplay, (255, 255, 255), pygame.Rect(self.x, self.y, self.width, self.length), 5)

# Define a platform class
class Platform:
    def __init__(self, x, y, width, length):
        self.x = x
        self.y = y
        self.width = width
        self.length = length
    # Ability to draw the platforms
    def draw_platform(self, dplay):
        pygame.draw.rect(dplay, (0,0,255), pygame.Rect(self.x, self.y, self.width, self.length))
        pygame.draw.line(dplay, (0, 155, 0), (self.x, self.y + 1), (self.x + self.width, self.y + 1), 3)

# Define a class for the enemies
class Enemy:
    def __init__(self, x, y, x_speed, y_speed, length, width):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.x_speed = x_speed
        self.y_speed = y_speed
        # Ability to draw the enemies
    def draw_enemy(self, dplay):
        pygame.draw.rect(dplay, (50, 100, 50), pygame.Rect(self.x, self.y, self.width, self.length))

# Define a class for the powerups
class Powerup:
    def __init__(self, x, y, x_speed, y_speed, length, width, power_type):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.power_type = power_type
        # Ability to draw the powerups
    def draw_powerup(self, dplay):
        pygame.draw.rect(dplay, self.power_type[1], pygame.Rect(self.x, self.y, self.width, self.length)) 

# Determine which powerup you picked up
def get_effect(power):
    if power == 'Heal' and player.health < 40:   
        player.health += 10
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('powerup.wav'))
    if power == 'Speed' and player.run_speed < 4:
        player.run_speed += 3
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('speed.wav'))
    if power == "Shrink" and player.width == 30: 
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('shrink.wav'))
        player.width = 13
        player.length = 22

### SETTING UP STUFF FOR PYGAME ###

# Dimensions 900 width 700 height
pygame.init()
dplay = pygame.display.set_mode((900, 700)) 
pygame.display.set_caption("Shape survive") 
clock = pygame.time.Clock() 
pygame.mixer.init() 
myfont = pygame.font.SysFont("Arial", 18) 
lose_font = pygame.font.SysFont("Arial", 60)

### DEFINING SOME IMPORTANT VARIABLES ### (Also generating the map)


player = Player(100, 600, 0, 0, 30, 30, 50)
enemies = []
powerups = []
powers = [["Heal", (255,0,0)], ["Heal", (255, 0, 0)], ["Speed", (0, 0, 255)], ["Shrink", (255,255,255)]]

# Create the platforms and add them to a list of platforms
platforms = []
platform_y = random.randint(550, 620) 
platform_x = random.randint(100, 600) 
for i in range(7): 
    platforms.append(Platform(platform_x, platform_y, random.randint(10, 130), random.randint(10, 70)))
    if platform_x < 100: 
        platform_x += random.randint(100, 500)
    elif platform_x > 800: 
        platform_x -= random.randint(100, 500)
    else:
        neg_pos = random.randint(1,2) 
        if neg_pos == 1:
            platform_x += random.randint(100, 500)
        else:
            platform_x -= random.randint(100, 500)

    platform_y -= random.randint(50, 100)

### THE 'PHYSICS' ###

JUMP_STRENGTH = 50 
MAX_JUMPS = 3 
jump_strength = JUMP_STRENGTH
max_jumps = MAX_JUMPS 
GRAVITY = 0.1
ENEMY_GRAVITY = 0.1  
jumped = False
on_floor = False

### THE VARIABLES FOR THE SCORING AND THE CLOCK (Not the clock which controls FPS, but one that gets time) ###

waves = 0 
score = 0 
score_amount = 2
score_to_beat = 10 
start = int(time.time()) #  this time is changed throught the game
start_full = int(time.time()) # this is not

### THE MAIN GAME LOOP ###

# The loop that the main part of the game actually runs through
while True:            
    # Check if window was closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    dplay.fill((0,0,0)) 
    clock.tick(60)

    ### DISPLAY THE SCREEN ###

    label = myfont.render(str(score), 1, (255, 255, 255))
    dplay.blit(label, (800, 50))

    player.draw_char(dplay)

    pygame.draw.line(dplay, (150, 255, 150), [player.x, player.y - 10], [player.x + jump_strength*3/5, player.y - 10], 10)

    pygame.draw.line(dplay, (250, 0, 0), [player.x, player.y - 20], [player.x + player.health, player.y - 20], 10)

    pygame.draw.line(dplay, (0, 255, 0), [0, 700], [900, 700], 100)

    for i in platforms:
        i.draw_platform(dplay)

    # Re-Generate the map
    if score > score_to_beat:
        pygame.mixer.Channel(3).play(pygame.mixer.Sound('regen.wav')) 
        score_to_beat += 15 
        platforms = [] 
        platform_y = random.randint(550, 620) # The following should really be a function
        platform_x = random.randint(100, 600)
        for i in range(7):
            platforms.append(Platform(platform_x, platform_y, random.randint(10, 130), random.randint(10, 70)))
            if platform_x < 100:
                platform_x += random.randint(100, 500)
            elif platform_x > 800:
                platform_x -= random.randint(100, 500)
            else:
                neg_pos = random.randint(1,2)
                if neg_pos == 1:
                    platform_x += random.randint(100, 500)
                else:
                    platform_x -= random.randint(100, 500)

            platform_y -= random.randint(50, 100)

    ### CREATE ENEMIES AND POWERUPS ###

    # Create and draw the enemies and powerups every two seconds as well as increasing your score and lowering any active effects
    if int(time.time()) - start == 2 and player.health > 0:
        start = int(time.time()) 
        score += score_amount 
        waves += 1 
        pygame.mixer.Channel(5).play(pygame.mixer.Sound('falling_enemies.wav')) 

        # Reduce the effects of any powerups
        if player.run_speed > 3: 
            player.run_speed -= 0.5
        if player.width == 13: 
            player.y -= 5
            player.width = 15
            player.length = 25
        elif player.width == 15:
            player.width = 20
            player.length = 25
        elif player.width == 20:
            player.y -= 30
            player.width = 30
            player.length = 50
        
        # Depending on how many waves you've survived the amount of enemies increases
        if waves < 70: 
            min_e = int(waves / 5) + 1
            max_e = int(waves / 5) + 5
        else: 
            min_e = 15
            max_e = 20

        if score > 20 and random.randint(1,2) == 1: # 50% of the time after your score hits twenty, 1,2, or 3 powerups will fall with the wave
            for i in range(random.randint(1,3)):
                powerups.append(Powerup(random.randint(10, 890), random.randint(0, 10), random.randint(-1, 1), 0, 20, 20, random.choice(powers))) 
        for i in range(random.randint(min_e, max_e)): 
            enemies.append(Enemy(random.randint(10, 890), random.randint(0, 10), random.randint(-1, 1), 0, 20, 20))
    
    for i in enemies:
        i.draw_enemy(dplay)

    for i in powerups:
        i.draw_powerup(dplay)

    ### MOVEMENT ###

    player.y -= player.y_speed
    player.x += player.x_speed

    for enemy in enemies:
        enemy.y += enemy.y_speed
        enemy.x += enemy.x_speed
        enemy.y_speed += ENEMY_GRAVITY

    for powerup in powerups:
        powerup.y += powerup.y_speed
        powerup.x += powerup.x_speed
        powerup.y_speed += ENEMY_GRAVITY


    # Check for wsd input by getting all key presses and comparing them
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        if jump_strength > 0 and max_jumps > 0: 
            jumping_noise = pygame.mixer.Sound('jumping.wav') 
            jumping_noise.play()
            player.y_speed = 2 
            jump_strength -= 1 
            jumped = True 
    elif jumped: 
        jumped = False 
        max_jumps -= 1 
    
    # If movement keys are pressed
    if keys[pygame.K_a]:
        player.x_speed = -(player.run_speed) 
    elif keys[pygame.K_d]:
            player.x_speed = player.run_speed 
    else:
        player.x_speed = 0 
        
    ### COLLISION ###
    #(I just read about a built-in function in pygame called collidepoint that could probably be used to make this way easier, but since it's already written I'll keep it for now)

    # If the player is high enough he gets a higher score
    if player.y < 100: # (Remember in Pygame (0,0) is at the top left so 100 on the y is high up not low)
        score_amount = 5
        bonus = myfont.render("Bonus: +5", 1, (255, 255, 255))
        dplay.blit(bonus, (650, 50))       
    elif player.y < 220: 
        score_amount = 3
        bonus = myfont.render("Bonus: +3", 1, (255, 255, 255))
        dplay.blit(bonus, (650, 50))
    elif player.y < 350:
        score_amount = 2
        bonus = myfont.render("Bonus: +2", 1, (255, 255, 255))
        dplay.blit(bonus, (650, 50))
    else:
        score_amount = 1
        bonus = myfont.render("No point bonus", 1, (255, 255, 255))
        dplay.blit(bonus, (650, 50))


    # Check if the player is on the floor or platform
    for i in platforms: 
        if player.y > 650 - player.length: 
            player.y = 650 - player.length
            on_floor = True
            break
        elif player.y + player.length > i.y and player.y + player.length < i.y + i.length and player.x > i.x - player.width + 5 and player.x < i.x + i.width - 5: # If you are on a platform
            player.y = i.y - player.length 
            on_floor = True
            break
        else:
            on_floor = False 
    
    if on_floor == True:
        if jump_strength < 50 or player.x_speed != 0: 
            pygame.mixer.Channel(2).play(pygame.mixer.Sound('landing.wav'))
        player.y_speed = 0 
        jump_strength = JUMP_STRENGTH 
        max_jumps = MAX_JUMPS 
    else: 
        player.y_speed -= GRAVITY

    # Check if you hit a wall
    if player.x < 10:
        player.x = 10

    if player.x > 860:
        player.x = 860

    # Check if a player is under or beside a platform. If you are then you can't move them
    for i in platforms:
        if player.y < i.y + i.length and int(player.y > i.y + i.length - i.length*.2) and player.x > i.x - player.width and player.x < i.x + i.width: # Under a plat
            player.y = i.y + i.length
            break
        elif player.x + player.width > i.x and player.x < i.x and player.y + player.length > i.y and player.y < i.y + i.length: # To the left of a plat
            player.x = i.x - player.width
            break
        elif player.x < i.x + i.width and player.x > i.x and player.y + player.length > i.y and player.y < i.y + i.length: # To the Right of a plat
            player.x = i.x + i.width
            break

    # Check for collissions with enemies. If you hit them lose health, play a sound, and remove the enemy
    for enemy in enemies:
        if player.x > enemy.x and player.x < enemy.x + enemy.width and player.y + player.length > enemy.y and player.y < enemy.y + enemy.length: # Right side of enemy
            enemy.y = 1000
            player.health -= 10
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('jump.wav'))
        elif player.x + player.width > enemy.x and player.x < enemy.x and player.y + player.length > enemy.y and player.y < enemy.y + enemy.length: # To the left of an enemy
            enemy.y = 1000
            player.health -= 10
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('jump.wav'))
        elif player.y < enemy.y + enemy.length and int(player.y > enemy.y + enemy.length - enemy.length*.2) and player.x > enemy.x - player.width and player.x < enemy.x + enemy.width: # Under an enemy
            enemy.y = 1000
            player.health -= 10
            pygame.mixer.Channel(1).play(pygame.mixer.Sound('jump.wav'))

    # Check for collissions with Powerups. If you hit them Get their effect and remove the powerup
    for power in powerups:
        if player.x > power.x and player.x < power.x + power.width and player.y + player.length > power.y and player.y < power.y + power.length: # Right side of powerup
            power.y = 1000
            get_effect(power.power_type[0])
        elif player.x + player.width > power.x and player.x < power.x and player.y + player.length > power.y and player.y < power.y + power.length: # To the left of an powerup
            power.y = 1000
            get_effect(power.power_type[0])
        elif player.y < power.y + power.length and int(player.y > power.y + power.length - power.length*.2) and player.x > power.x - player.width and player.x < power.x + power.width: # Under an powerup
            power.y = 1000
            get_effect(power.power_type[0])

    ### WHEN THE GAME ENDS ###

    # If the player dies break out of the mian loop otherwise update the display with all of the changes
    if player.health <= 0:
        break
    else:
        pygame.display.update() 


# The loop for after you die
while True:
    # Check if window was closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        clock.tick(60)

    if player.health <= -5:
        pass
    else:
        dplay.fill((0,0,0))

        pygame.mixer.Channel(1).play(pygame.mixer.Sound('lost.wav'))

        # Display game info
        time_survived = int(time.time() - start_full) # How long you survived
        final_score = score - int(time_survived/10) # The longer it took the lower your score (if you are higher you get points faster)
        lost = lose_font.render(f"You Lose. Waves Survived : {int(waves)}", 1, (100, 0, 0))
        time_sur = lose_font.render(f"Time Survived : {time_survived}", 1, (100, 0, 0))
        display_final_score = lose_font.render(f"Final Score: {final_score}", 1, (100, 0, 0))
        dplay.blit(lost, (50, 200))
        dplay.blit(time_sur, (200, 300))
        dplay.blit(display_final_score, (200, 400))

        # Set player health to -5 so the display no longer updates
        player.health = -5

        pygame.display.update()



