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
    if power == 'Heal' and player.health < 40:    # Add 10 to the players health with a cap at 40
        player.health += 10
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('powerup.wav'))
    if power == 'Speed' and player.run_speed < 4: # Increase the speed by 3 unless the player is too fast already (from a different speed boost)
        player.run_speed += 3
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('speed.wav'))
    if power == "Shrink" and player.width == 30:  # Shrink the player Unless they are already shrunken
        pygame.mixer.Channel(4).play(pygame.mixer.Sound('shrink.wav'))
        player.width = 13
        player.length = 22

### SETTING UP STUFF FOR PYGAME ###

# Dimensions 900 width 700 height
pygame.init()
dplay = pygame.display.set_mode((900, 700)) # Dimensions of the window
pygame.display.set_caption("Shape survive") # Title of the window
clock = pygame.time.Clock() # How many times per second the game will 'run'. Later is hard-coded to 60 FPS
pygame.mixer.init() # Initialize for the sounds
myfont = pygame.font.SysFont("Arial", 18) # define fonts to be used later
lose_font = pygame.font.SysFont("Arial", 60)

### DEFINING SOME IMPORTANT VARIABLES ### (Also generating the map)

# Create the player
player = Player(100, 600, 0, 0, 30, 30, 50)

# Create list of enemies
enemies = []

# Create list of powerups
powerups = []

# The powerup options
powers = [["Heal", (255,0,0)], ["Heal", (255, 0, 0)], ["Speed", (0, 0, 255)], ["Shrink", (255,255,255)]]

# Create the platforms and add them to a list of platforms
platforms = []
platform_y = random.randint(550, 620) # The starting platforms y value
platform_x = random.randint(100, 600) # The starting platforms x value
for i in range(7): # Create 7 platforms
    platforms.append(Platform(platform_x, platform_y, random.randint(10, 130), random.randint(10, 70))) # Actually create a platform object and append it to the platforms list (has a random width and length)
    if platform_x < 100: # If the previous platform was close to the left wall then the next one will be to the right
        platform_x += random.randint(100, 500)
    elif platform_x > 800: # If the previous platform was close to the right wall then the next one will be to the left
        platform_x -= random.randint(100, 500)
    else: # If the previous platform was somewhat in the middle then the next platform will be randomly to the left or the right
        neg_pos = random.randint(1,2) 
        if neg_pos == 1:
            platform_x += random.randint(100, 500)
        else:
            platform_x -= random.randint(100, 500)

    platform_y -= random.randint(50, 100) # The platforms will rise like steps

### THE 'PHYSICS' ###

JUMP_STRENGTH = 50 # The constant which defines the starting jump strength - the 'fuel' for how long you can jump
MAX_JUMPS = 3 # The constant which determines how many jumps you can have
jump_strength = JUMP_STRENGTH # Assign jump_strength to the starting value of JUMP_STRENGTH
max_jumps = MAX_JUMPS # Assign max_jumps to the starting value of MAX_JUMPS
GRAVITY = 0.1 # The constant for how fast things will accelerate downwards
ENEMY_GRAVITY = 0.1 # The constant for how fast enemies anf powerups will accelerate downwards (It's different then GRAVITY so that you can test different numbers) 
jumped = False # start on the floor without using any jumps
on_floor = False # Even though you start and this will be assigned True in the beginning, eventually the player might start mid-air in a new level of somekind

### THE VARIABLES FOR THE SCORING AND THE CLOCK (Not the clock which controls FPS, but one that gets time) ###

waves = 0 # The number of enemy waves
score = 0 # Your score determined by how many waves and high you were (Not the final score, but a factor of it)
score_amount = 2 # How much your score goes up every wave (unless changed by a bonus) 
score_to_beat = 10 # The score you hit before the map regenerates
start = int(time.time()) # The time in seconds of when the game begins (The value is changed throught the game)
start_full = int(time.time()) # The time in seconds of whne the game begins (does not change throught the game)

### THE MAIN GAME LOOP ###

# The loop that the main part of the game actually runs through
while True:            
    # Check if window was closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Color the background
    dplay.fill((0,0,0)) 

    # Hard-coded 60 FPS
    clock.tick(60)

    ### DISPLAY THE SCREEN ###

    # Write the score
    label = myfont.render(str(score), 1, (255, 255, 255))
    dplay.blit(label, (800, 50))

    # Draw the player
    player.draw_char(dplay)

    # Draw the jump line
    pygame.draw.line(dplay, (150, 255, 150), [player.x, player.y - 10], [player.x + jump_strength*3/5, player.y - 10], 10)

    # Draw player health
    pygame.draw.line(dplay, (250, 0, 0), [player.x, player.y - 20], [player.x + player.health, player.y - 20], 10)

    # Draw the floor
    pygame.draw.line(dplay, (0, 255, 0), [0, 700], [900, 700], 100)

    # Draw the platforms
    for i in platforms:
        i.draw_platform(dplay)

    # Re-Generate the map
    if score > score_to_beat:
        pygame.mixer.Channel(3).play(pygame.mixer.Sound('regen.wav')) # Play a noise to siganl the map is redrawing
        score_to_beat += 15 # The next score before it happens again
        platforms = [] # Empty the list of platforms
        platform_y = random.randint(550, 620) # This code is exactly the same as before (Should be in a function)
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
        start = int(time.time()) # The new time to compare when two seconds pass
        score += score_amount # Your score goes up
        waves += 1 # The number of waves goes up
        pygame.mixer.Channel(5).play(pygame.mixer.Sound('falling_enemies.wav')) # Play a noise as the enemies fall

        # Reduce the effects of any powerups
        if player.run_speed > 3: # Speed slowly goes back to normal
            player.run_speed -= 0.5
        if player.width == 13: # So does size
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
        if waves < 70: # Vefore wave 70 the number of enemies increases each round
            min_e = int(waves / 5) + 1
            max_e = int(waves / 5) + 5
        else: # After wave 70 there is always between 15-20 enemies
            min_e = 15
            max_e = 20
        # Use a random value for the x, y, and x_speed. y_speed is 0 and width and height are 20
        if score > 20 and random.randint(1,2) == 1: # 50% of the time after your score hits twenty, 1,2, or 3 powerups will fall with the wave
            for i in range(random.randint(1,3)): # The next line creats a powerup and appends it to the powerup list
                powerups.append(Powerup(random.randint(10, 890), random.randint(0, 10), random.randint(-1, 1), 0, 20, 20, random.choice(powers))) # Draw a powerup with the wave
        for i in range(random.randint(min_e, max_e)): # The next line creates enemies and adds them to the enemies list
            enemies.append(Enemy(random.randint(10, 890), random.randint(0, 10), random.randint(-1, 1), 0, 20, 20))
    
    # Draw enemies
    for i in enemies:
        i.draw_enemy(dplay)

    # Draw powerups
    for i in powerups:
        i.draw_powerup(dplay)

    ### MOVEMENT ###

    # Move the player depending on their speeds (affected by gravity and inputs)
    player.y -= player.y_speed
    player.x += player.x_speed

    # Send enemies falling
    for enemy in enemies:
        enemy.y += enemy.y_speed
        enemy.x += enemy.x_speed
        enemy.y_speed += ENEMY_GRAVITY

    # Send powerups falling
    for powerup in powerups:
        powerup.y += powerup.y_speed
        powerup.x += powerup.x_speed
        powerup.y_speed += ENEMY_GRAVITY


    # Check for wsd input by getting all key presses and comparing them
    keys = pygame.key.get_pressed()

    # If w is pressed Jump
    if keys[pygame.K_w]:
        if jump_strength > 0 and max_jumps > 0: # Check if you have the strength and jumps available
            jumping_noise = pygame.mixer.Sound('jumping.wav') # Play a jumping sound
            jumping_noise.play()
            player.y_speed = 2 # The upward motion from the jump
            jump_strength -= 1 # Slowly lose your jump 'fuel'
            jumped = True # Mark that you jumped
    elif jumped: # Once you are no longer pressing 'w' if you pressed it before and have 'jumped' then lose a jump
        jumped = False # Reset the fact that you jumped
        max_jumps -= 1 # Lose a jump
    
    # If movement keys are pressed
    if keys[pygame.K_a]:
        player.x_speed = -(player.run_speed) # If 'a' is pressed move to the left
    elif keys[pygame.K_d]:
            player.x_speed = player.run_speed # If 'd' is pressed move to the right
    else:
        player.x_speed = 0 # If none of the above are pressed; don't move
        
    ### COLLISION ###
    #(I just read about a built-in function in pygame called collidepoint that could probably be used to make this way easier, but since it's already written I'll keep it for now)

    # If the player is high enough he gets a higher score
    if player.y < 100: # If the player's 'y' is higher then 100 get a +5 from every wave (Remember in Pygame (0,0) is at the top left so 100 on the y is high up not low)
        score_amount = 5
        bonus = myfont.render("Bonus: +5", 1, (255, 255, 255)) # Write that you got a +5 bonus in the font we defined earlier
        dplay.blit(bonus, (650, 50))       
    elif player.y < 220: # These are the same as before but less bonuses for lower down
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
    for i in platforms: # Check if you are on any platforms or the floor
        if player.y > 650 - player.length: # > because as stated before (0,0) is the top left so greater on the y is lower down
            player.y = 650 - player.length
            on_floor = True
            break
        elif player.y + player.length > i.y and player.y + player.length < i.y + i.length and player.x > i.x - player.width + 5 and player.x < i.x + i.width - 5: # If you are on a platform
            player.y = i.y - player.length # Place the player on the platform
            on_floor = True
            break
        else:
            on_floor = False # If you are not on the floor or platform you are in the air
    
    # If you are on the floor...
    if on_floor == True:
        if jump_strength < 50 or player.x_speed != 0: # If you are walking or have fallen play a sound
            pygame.mixer.Channel(2).play(pygame.mixer.Sound('landing.wav'))
        player.y_speed = 0 # reset you y speed
        jump_strength = JUMP_STRENGTH # Reset your 'fuel'
        max_jumps = MAX_JUMPS # Give you back all your jumps
    else: # otherwise get effected by gravity
        player.y_speed -= GRAVITY

    # Check if you hit a wall
    if player.x < 10: # Right wall
        player.x = 10

    if player.x > 860: # Left wall
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
        # Update the display
        pygame.display.update() 


# The loop for after you die
while True:
    # Check if window was closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Hard-coded 60 FPS
        clock.tick(60)

    if player.health <= -5:
        pass
    else:
        # Fill the screen black
        dplay.fill((0,0,0))

        # Play the losing music
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



