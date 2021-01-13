import random, os
from math import *
from pygame import *
init()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" %(5, 30)

SIZE = (1000,700)
screen = display.set_mode(SIZE)

#COLOURS
BLACK = (0, 0, 0)
SCORE = (187, 191, 205)
RED = (201, 54, 54)
BLUE = (153, 197, 202)
WHITE = (255, 255, 255)

#----------images----------
#start screen
title = image.load("titlefont.png")
#menu
menuback = image.load("menuback.png")
menutext = image.load("menutext.png")
# order: endless mode, play, how to play, leaderboard, volume, quit
menuRect = [Rect(286, 273, 434, 50), Rect(409, 360, 200, 70), Rect(303, 471, 400, 50), Rect(30, 620, 70, 65), Rect(910, 622, 60, 60), Rect(905, 20, 85, 30)]
playhover = image.load("playhover.png")
endlesshover = image.load("endlesshover.png")
howtohover = image.load("howtohover.png")
leadericon = image.load("leaderboard.png")
volume = image.load("vol.png")
vol_curve = image.load("vol_on.png")
quitter = image.load("quitter.png")

#leaderboard
leftarrow = image.load("leftarrow.png")
rightarrow = image.load("rightarrow.png")
backinblack = image.load("backinblack.png")

#howto
howto_main = image.load("howto.png")
#order: space, water, desert
infoRect = [Rect(52, 442, 133, 133), Rect(235, 442, 133, 133), Rect(413, 442, 133, 133)]
spaceinfo =  image.load("spaceinfo.png")
waterinfo =  image.load("waterinfo.png")
desertinfo =  image.load("desertinfo.png")
#in game
pauseRect = [Rect(219, 392, 262, 45), Rect(540, 394, 215, 45)]
level1text = image.load("level1text.png").convert()
level2text =  image.load("level2text.png").convert()
level3text  = image.load("level3text.png").convert()
back =  image.load("back.png")

gameover = image.load("gameover.png")
gameoverw = image.load("gameoverwhite.png")
winscreen = image.load("winscreen.png")
#order: level 1, level 2, level 3, back button
levelRect = [Rect((0, 100), (333, 600)), Rect((333, 0), (333, 700)), Rect((666, 0), (333, 700)), Rect((0, 0), (186, 106))]
#left arrow, right arrow
leaderRect = [Rect(315, 60, 47, 32), Rect(650, 60, 47, 32)]
#frames for gif images
redDragon = [
    image.load('red (1).gif'), image.load('red (2).gif'), 
    image.load('red (3).gif'), image.load('red (4).gif'),
    image.load('red (5).gif'), image.load('red (6).gif'),
    image.load('red (7).gif'), image.load('red (8).gif'),
    image.load('red (9).gif'), image.load('red (10).gif'),
]

city = [
    image.load('city (1).gif'), image.load('city (2).gif'),
    image.load('city (3).gif'), image.load('city (4).gif'),
    image.load('city (5).gif'), image.load('city (6).gif'), 
    image.load('city (7).gif'), image.load('city (8).gif'),
]

# SPACE LEVEL
progressbar = image.load("progressbar.png")
progressslider = transform.rotate(image.load("dragon.png"),90)
meteor = [image.load('bigm.gif'), image.load('smallm.gif'), image.load('medm.gif')]
space_junk = [image.load('sat.png'), image.load('comp.png'), image.load('astro.png')] 

# WATER LEVEL
trash = [image.load('chip.png'), image.load('cpu.png'), image.load('comp.png')] 
waterdrop = image.load('waterdrop.png')
bullet = image.load("bullet.png")    

#DESERT LEVEL
rocks = [image.load('bigrock.png'), image.load('biggerrock.png'), image.load('medrock.png')]

#fonts
tfont = font.SysFont("monogramextended", 30) 
lfont =  font.SysFont("monogramextended", 40) 
sfont =  font.SysFont("monogramextended", 100) 
mfont =  font.SysFont("monogramextended", 60) 
SCREENRECT = Rect(0, 0, SIZE[0], SIZE[1])

START_TILE = (20, 20) #starting tile of dragon
START_SEGMENTS = 5 #starting number of body segments

MOVE_RATE = 2 #speed 
MOVE_THRESHOLD = 4 # dragon moves when MOVE_RATE counts to this
SPEED_INCREASE = .025 #used to increase speed after each piece of waste eaten/shot

#BLOCK
BLOCK_SPAWN_RATE = 3 #limits spawn rate of meteors in space level

TILE_SIZE = (20, 20) #size of 1 tile, food and dragon body tiles are always blitted on multiples of 20 so they align perfectly  
SCREENTILES = ((SIZE[0] / TILE_SIZE[0]) - 2, (SIZE[1] / TILE_SIZE[1]) - 2) #total number of tiles that fit screen

#used later in segment class for movement. Controls tilepos change, which is used to calculate blitting position of image tile rect
MOVE_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)] #order: left, right, down, up
MOVE_DIRECTIONS_TILES = [(-TILE_SIZE[0], 0),(TILE_SIZE[0], 0),(0, -TILE_SIZE[1]), (0, TILE_SIZE[1])]

#----------classes---------#
class Segment(sprite.Sprite):
    def __init__(self, tilepos, segment_groups, image = image.load('seg.png')): #basic init for master segment class. segment_groups is the sprite groups it is a part of
        sprite.Sprite.__init__(self)
        self.original_image = image #original image used as starting point for segment angle transformations
        self.image = self.original_image         
        self.rect = self.image.get_rect()
        self.tilepos = tilepos
        #makes segment occupy a tile space by making blit location a complete tile with TILE_SIZE. Ensures it joins with other segments in solid block with no gaps
        self.rect.topleft = (tilepos[0] * TILE_SIZE[0], tilepos[1] * TILE_SIZE[1])  
        self.angle = 0 #init angle used later to rotate head and body tiles
        #adds self to all lists in segment_groups argument. Used later to ensure food doesnt appear on body, collisions, etc. 
        self.segment_groups = segment_groups 
        for group in segment_groups:
            group.add(self) 
            
        self.behind_segment = None #no segment behind yet
        self.move_direction = 0 
        
    def add_segment(self):       
        segment = self 
        while True:
            if segment.behind_segment == None: #finds current last segment so that added segment is at the end
                x = segment.tilepos[0]
                y = segment.tilepos[1]
                if segment.move_direction == 0:   #calculates new tilepos blit location from direction of previous tile so it is behind it
                    x += 1
                elif segment.move_direction == 1:
                    x -= 1
                elif segment.move_direction == 2:
                    y += 1
                elif segment.move_direction == 3:
                    y -= 1
                segment.behind_segment = Segment((x, y), segment.segment_groups) #calls a new segment
                segment.behind_segment.move_direction = segment.move_direction #same move direction as previous tile
                break
            else:
                segment = segment.behind_segment #if already has behind segment

    def update(self):
        if self.move_direction == 0:   #finds required rotation of image from move direction for a body segment
            self.angle = 0
        elif self.move_direction == 1:
            self.angle = 0
        elif self.move_direction == 2:
            self.angle = 90
        elif self.move_direction == 3:
            self.angle = 90     
        self.image = transform.rotate(self.original_image, self.angle) #rotates image        
        self.angle = self.angle % 360 
        
    def move(self):
        self.tilepos = (self.tilepos[0] + MOVE_DIRECTIONS[self.move_direction][0], self.tilepos[1] + MOVE_DIRECTIONS[self.move_direction][1])
        self.rect.move_ip(MOVE_DIRECTIONS_TILES[self.move_direction])  #move_ip moves image rect in place. 'move' only returned a new rect, didn't work with move_directions list   
        if self.behind_segment != None: #segments move in direction of previous segment
            self.behind_segment.move()
            self.behind_segment.move_direction = self.move_direction 

class dragonHead(Segment):
    def __init__(self, tilepos, move_direction, segment_groups):
        Segment.__init__(self, tilepos, segment_groups, image = transform.rotate(image.load("dragon.png"),90))
        self.move_direction = move_direction
        self.movecount = 0 #controls movement, used later for updates
        self.mask = mask.from_surface(self.image)
        
    def update(self):
        self.image = transform.rotate(self.original_image, self.angle) #rotates head later in main loop
        self.angle = self.angle % 360 
        self.movecount += MOVE_RATE 
        if self.movecount > MOVE_THRESHOLD: #moves every 4 increments
            self.move()
            self.movecount = 0
            
class Food(sprite.Sprite):
    def __init__(self, takenup_group, tilepos, image): #order: sprite groups it belongs to, initial tilepos, type of waste
        sprite.Sprite.__init__(self)
        self.image = image 
        self.rect = self.image.get_rect()         
        end = False
        while True:
            self.rect.topleft = tilepos
            for sprt in takenup_group:
                if sprite.collide_rect(self, sprt) == False: #checks food against all the sprites in takenup_group, so it doesnt overlap with any obstacles/the dragon
                    end = True
                    break # no collision, Food can go here                     

                else:
                    continue  #keeps checking until empty spot is found           
            if end:
                break    #was experiencing odd infinite loops with the continue, this fixed it       

global missed
missed = []
class desertFood(Food):
    def __init__(self, takenup_group, tilepos, image):
        Food.__init__(self, takenup_group, tilepos, image)
    def update(self):
        if self.rect.x > -20: #moves towards dragon along with background in the desert level
            self.rect.x -= 1   
        if self.rect.x < -10: #list is used later to check if any food was uneaten and went off screen
            missed.append(self)
        
#water level 
class Water(sprite.Sprite): #water bullets
    def __init__(self, takenup_group, tilepos, move_direction):
        sprite.Sprite.__init__(self)
        self.image = waterdrop
        self.rect = self.image.get_rect()          
        #movement
        self.move_direction = move_direction
        self.rect.topleft = (tilepos)

    def update(self):
        if self.move_direction == 0:  #movement
            self.rect.x -= 30
        elif self.move_direction == 1:
            self.rect.x += 30
        if self.move_direction == 2:
            self.rect.y -= 30
        elif self.move_direction == 3:
            self.rect.y += 30   
        if self.rect.x < -50 or self.rect.x > 1000 or self.rect.y < -50 or self.rect.y > 700: #if they go past screen, kills sprite
            self.kill()

class Bullet(sprite.Sprite):
    def __init__(self, x, y, target_x, target_y): #initial x and y of self, target location
        sprite.Sprite.__init__(self)
        self.image = bullet
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)        
        self.original_x = self.rect.x #originals are used later to calculate direction (slope) of bullet movement
        self.original_y = self.rect.y
        self.target_x = target_x
        self.target_y = target_y
        self.vel = 20
    
    def update(self):
        self.rect.x += int((self.vel * (self.target_x - self.original_x)) / (sqrt((self.target_x - self.original_x) ** 2 + (self.target_y - self.original_y) ** 2)))
        self.rect.y += int((self.vel * (self.target_y - self.original_y)) / (sqrt((self.target_x - self.original_x) ** 2 + (self.target_y - self.original_y) ** 2)))
        #credit goes to timur's bullet class for the math 
        if self.rect.x < 0 or self.rect.y > 1000:
            self.kill()

class Terminator(sprite.Sprite): #was made a class for easier collision detection.
    def __init__(self, tilepos):
        sprite.Sprite.__init__(self)    
        self.image = image.load("term.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = tilepos
        self.mask = mask.from_surface(self.image) #self.mask uses alpha mask of image, which only takes pixels above a certain transparency, for collision detection
        
#desert level
class Rock(sprite.Sprite): #rock obstacles in desert level
    def __init__(self, takenup_group, tilepos_x): 
        sprite.Sprite.__init__(self)
        self.image = rocks[random.randint(0,2)] #randomly selects type of rock
        self.rect = self.image.get_rect()
        self.mask = mask.from_surface(self.image)
        end = False       
        while True:
            self.rect.topleft = (tilepos_x, random.randint(20, (SCREENTILES[1]) * TILE_SIZE[1]-100)) 
            for sprt in takenup_group:
                if sprite.collide_rect(self, sprt) == False:
                    end = True
                    break # no collision, Food can go here                     

                else:
                    continue              
            if end:
                break #same as food logic
                     
    def update(self):
        if self.rect.x > -400: #moves towards dragon
            self.rect.x -= 1   
        else:
            self.kill() #kills sprite if it goes off screen
            
#space level 
class Meteor(sprite.Sprite):
    def __init__(self, takenup_group):
        sprite.Sprite.__init__(self)
        self.image = meteor[random.randint(0,2)]
        self.rect = self.image.get_rect()
        self.mask = mask.from_surface(self.image)
        end = False
        
        while True:
            self.rect.topleft = (1000, random.randint(2, SCREENTILES[1]) * TILE_SIZE[1]) #blits meteor at end of screen, aligned with a tile
            for sprt in takenup_group:
                if self.rect.colliderect(sprt):
                    continue 

                else:
                    end = True
                    break 
            if end:
                break    
            
    def update(self):
        if self.rect.x > -90: #moves towards dragon
            self.rect.x -= 1   
        else:
            self.kill()

#-----------pages-------------            
def startUp(frame, dragonX):
    screen.fill(BLACK)
    screen.blit(redDragon[frame], (dragonX,150))  #moving dragon image as loading screen
    screen.blit(title, (200, 350))
 
def mainMenu(frame):
    screen.blit(city[frame], (0,0)) #draws moving background
    screen.blit(menuback, (0, 0))
    screen.blit(menutext, (171, 0))
    screen.blit(leadericon, (30, 620))
    screen.blit(volume, (910, 622))
    screen.blit(quitter, (905, 20))
    if vol_on:
        screen.blit(vol_curve, (962, 632))
    if menuRect[0].collidepoint(mx, my):
        screen.blit(endlesshover, (171,0)) #draws hover effect
    elif menuRect[1].collidepoint(mx, my):
        screen.blit(playhover, (171,0))
    elif menuRect[2].collidepoint(mx, my):
        screen.blit(howtohover, (171,0))   

def drawLeaderboard(currentLevel, frame):
    scoreList = [] #temporary score and name lists
    nameList = []
    screen.blit(city[frame], (0,0)) #draws moving background
    if currentLevel == 0:
        displayLevel = sfont.render("ENDLESS", 1, BLACK) #for displaying endless mode
    else:
        displayLevel = sfont.render("LEVEL %i" %currentLevel, 1, BLACK)
    screen.blit(displayLevel, (380, 30))
    if currentLevel != 1:
        screen.blit(leftarrow, (315, 60)) #doesn't blit left arrow for level 1 
    if currentLevel != 0:
        screen.blit(rightarrow, (650, 60)) #doesn't blit right arrow for endless (last) page
    screen.blit(backinblack, (0, 0))
    username = mfont.render("USERNAME", 1, BLACK)
    screen.blit(username, (170, 140))
    if currentLevel != 0:
        userTime = mfont.render("BEST TIME", 1, BLACK)
    else:
        userTime = mfont.render("BEST SCORE", 1, BLACK)
    screen.blit(userTime, (600, 140))
    
    numFile = open("irenetimes.dat", "r")  #opens high scores file
    while True:
        text = numFile.readline()
        #rstrip removes the newline character read at the end of the line
        text = text.rstrip("\n")     
        if text == "": #breaks loop if empty line
            break
        record = text.split("^") #splits text using '^' seperator, returns each line as tuple item in list 
        if int(record[0]) == currentLevel or (record[0] == "5" and currentLevel == 0): #finds corresponding level scores for page 
            scoreList.append(float(record[1])) #adds scores and names to lists
            nameList.append(record[2]) 
    sortedList = []       
    for i in scoreList:
        sortedList.append(i)
    if currentLevel == 0:
        sortedList.sort(reverse=True) #if endless mode, sorts according to highest score first
    else:
        sortedList.sort() #else, sorts by fastest time
    sortedList = list(map(str, sortedList)) #makes all items in list string to check against original lists
    scoreList = list(map(str, scoreList))
    sorted_nameList = []
    for i in range(len(sortedList)):
        for j in range(len(scoreList)): 
            if sortedList[i] == scoreList[j]: #finds same scores 
                if sorted_nameList.count(nameList[j]) == 0: #will only display each username once, even if 2 usernames have same score
                    sorted_nameList.append(nameList[j])
                else:
                    if nameList.count(nameList[j]) > sorted_nameList.count(nameList[j]): #if name had more than one highscore in original list, add to sorted
                        sorted_nameList.append(nameList[j])
                        
    sortedList = sortedList[:10]
    sorted_nameList = sorted_nameList[:10]  #only displays top 10 scores
    for i in range(len(sortedList)): #only draws the number of names in the lists
        name =  lfont.render("%i. %s" %(i+1, sorted_nameList[i]), 1, BLACK) #i+1 is the rank
        screen.blit(name, (170, (205 + (i*45)))) #i*45 calculates spacing depending on rank
        score = lfont.render("%s" %sortedList[i], 1, BLACK)
        screen.blit(score, (600, (205 + (i*45))))  
    numFile.close()  

def drawHowTo(frame): #draws how to play page
    screen.blit(city[frame], (0,0))
    screen.blit(howto_main, (0,0))
    screen.blit(backinblack, (0, 0))
    if button == 0:
        if infoRect[0].collidepoint(mx, my): #if buttons hovered over, gives information on waste type in each level
            screen.blit(spaceinfo, (250, 175))  
        elif infoRect[1].collidepoint(mx, my):
            screen.blit(waterinfo, (250, 175))
        elif infoRect[2].collidepoint(mx, my):
            screen.blit(desertinfo, (250, 175))

#i chose to make permanent background items a function so that it doesnt have to redraw constant images
def backMenu(lose, level, image, win): #function draws background of levels page and game over/win screens
    global bg #global as it is used in main loop
    bg = Surface(SIZE).convert()
    BACKGROUND = image   
    bg.blit(BACKGROUND, (0, 0))
    if lose:
        if level == 0: #if on main level select page
            if button == 0:
                if levelRect[0].collidepoint(mx, my): #hover effects
                    bg.blit(level1text, (0, 0))
                elif levelRect[1].collidepoint(mx, my):
                    bg.blit(level2text, (333, 0))
                elif levelRect[2].collidepoint(mx, my):
                    bg.blit(level3text, (666, 0))  
            bg.blit(back, (0, 0)) #back button
        else:
            if level == 5: #text color for game over screens is different for darker/lighter levels
                COLOR = BLACK
            else:
                COLOR = WHITE            
            if keepScore: #draws all the prompts and user input for adding high score
                bg.blit(BACKGROUND, (220, 500), Rect((220, 500), (600, 80)))
                keep = tfont.render("Add your score to the leaderboard (Y/N)?", 1, COLOR)
                bg.blit(keep, (220, 500))  
                drawYorN = tfont.render("%s" %YorN.upper(), 1, COLOR)
                bg.blit(drawYorN, (670, 500))   
               
            if askUser:
                bg.blit(BACKGROUND, (220, 500), Rect((220, 500), (600, 80)))
                whatName = tfont.render("What is your name?", 1, COLOR)
                bg.blit(whatName, (380, 500))  
                drawuserName =  tfont.render("%s" %userName, 1, COLOR) 
                bg.blit(drawuserName, (590, 500))  
                
            elif askUser == False:
                bg.blit(BACKGROUND, (220, 500), Rect((220, 500), (600, 80)))
                fine = tfont.render("Suit yourself.", 1, COLOR)
                bg.blit(fine, (445, 500))                           
            
            if thankYou:
                bg.blit(BACKGROUND, (220, 500), Rect((220, 500), (600, 80)))
                thank = tfont.render("Thank you! You have been added to the leaderboard.", 1, COLOR)
                bg.blit(thank, (220, 500))  
                
            if win:
                bg.blit(winscreen, (0, 0)) #winscreen if win is true
                
            else:
                if level == 2:
                    bg.blit(gameover, (0, 0)) #white or black gameover text for visibility
                else:
                    bg.blit(gameoverw, (0, 0))
    if level == 1:
        bg.blit(progressbar, (0, 550))   #draws progress bar on screen if space level     
    screen.blit(bg, (0, 0)) #draws bg to screen
    display.flip()

#------general var init-------

running = True 
clock = time.Clock()
timeCheck = time.get_ticks()

frame = 0
button = 0
dragonX = 220 #used for dragon in startup screen
currentLevel = 1 #used for leaderboard

startScreen = True
menu = False
leaderboard = False
howTo = False
game = False
lose = True
win = False
level = 0
song = ""
vol_on = True

#all sprite groups
dragon_group = sprite.Group() #dragon body segments
head_group = sprite.Group() #dragon head
food_group = sprite.Group() #food tiles
block_group = sprite.Group() #block tiles 
water_group = sprite.Group() #water bullet tiles
takenup_group = sprite.Group() #taken up tiles
bullet_group = sprite.Group() #terminator bullets
term_group = sprite.GroupSingle() #terminator image. single group to prevent it from calling over and over again, taking up memory
all = sprite.RenderUpdates()  #used to update only sprites on screen rather than flipping whole screen, as I have a lot of images

elapsed = 0 #used for timer to calculate elapsed time in between starting game

#initials for user input
userInput = ""
submitted = False
keepScore = None
askUser = None
thankYou = None

while running: 
    if startScreen:
        startUp(frame, dragonX)
        if time.get_ticks() - timeCheck > 100:
            frame += 1
            timeCheck = time.get_ticks()
            if timeCheck > 2000:
                dragonX -= 20 #YOU CHANGED THIS
                if dragonX < -640:
                    frame = 0
                    startScreen = False
                    menu = True
            frame %= 10    
        display.flip()
        
    if menu:
        for evnt in event.get():
            if evnt.type == MOUSEBUTTONDOWN:
                button = evnt.button
            if evnt.type == MOUSEBUTTONUP:
                button = 0  
            mx, my  = mouse.get_pos() 
            if button == 1:
                if menuRect[1].collidepoint(mx, my):
                    game = True
                    menu = False
                if menuRect[0].collidepoint(mx, my): #endless mode
                    level = 5
                    backImage = image.load("sky.png").convert()
                    if vol_on:
                        mixer.music.stop()
                        song = "up.mp3" #I've managed to use the up song in all of my projects... I have to stick with the brand.
                        mixer.music.load(song)
                        mixer.music.play(-1)                    
                    game = True
                    lose = False
                if menuRect[2].collidepoint(mx, my):
                    menu = False
                    howTo = True                
                if menuRect[3].collidepoint(mx, my):
                    menu = False
                    leaderboard = True
                if menuRect[4].collidepoint(mx, my):
                    vol_on = not vol_on
                if menuRect[5].collidepoint(mx, my):
                    menu = False
                    running = False
                        
        if vol_on:
            if song != "home_theme.ogg" and level != 5 or not mixer.music.get_busy(): #if default music isn't already playing, start playing
                song = "home_theme.ogg"
                mixer.music.load(song)
                mixer.music.play(-1)   
        else:
            mixer.music.stop() #if user toggles speaker, volume is off
        mainMenu(frame) 
        if time.get_ticks() - timeCheck > 100: #changes frames for background
            frame += 1
            timeCheck = time.get_ticks()
            frame %= 8
        display.flip()
        
    if leaderboard:
        for evnt in event.get():
            if evnt.type == MOUSEBUTTONDOWN:
                button = evnt.button
            if evnt.type == MOUSEBUTTONUP:
                button = 0     
            mx, my  = mouse.get_pos() 
            if button == 1:
                if levelRect[3].collidepoint(mx, my):
                    leaderboard = False #goes back to menu
                    menu = True   
                elif leaderRect[0].collidepoint(mx, my):
                    currentLevel -= 1
                elif leaderRect[1].collidepoint(mx, my):
                    currentLevel += 1
        currentLevel %= 4
        drawLeaderboard(currentLevel, frame)
        if time.get_ticks() - timeCheck > 100:
            frame += 1
            timeCheck = time.get_ticks()
            frame %= 8
        display.flip()        
    
    if howTo:
        for evnt in event.get():
            if evnt.type == MOUSEBUTTONDOWN:
                button = evnt.button
            if evnt.type == MOUSEBUTTONUP:
                button = 0     
            mx, my  = mouse.get_pos() 
            if button == 1:
                if levelRect[3].collidepoint(mx, my):
                    howTo = False #goes back to menu
                    menu = True 
       
        drawHowTo(frame)
        if time.get_ticks() - timeCheck > 100:
            frame += 1
            timeCheck = time.get_ticks()
            frame %= 8
        display.flip()        

    while game: 
        for evnt in event.get():
            if evnt.type == MOUSEBUTTONDOWN:
                button = evnt.button
            if evnt.type == MOUSEBUTTONUP:
                button = 0     
            mx, my  = mouse.get_pos() 
            if button == 1:
                if level == 0:
                    if levelRect[3].collidepoint(mx, my):
                        game = False #goes back to menu, resets lose and level
                        menu = True
                    if levelRect[0].collidepoint(mx, my): #sets music, background image and level 
                        level = 1
                        backImage = image.load("space.png").convert()
                        song = "space_theme.ogg"
                        lose = False
                    elif levelRect[1].collidepoint(mx, my):
                        level = 2
                        backImage = image.load("water.png").convert()
                        song = "water_theme.ogg"
                        lose = False  
                    elif levelRect[2].collidepoint(mx, my):
                        level = 3
                        backImage = image.load("parallax.png").convert()
                        song = "desert_theme.ogg"
                        lose = False  
                        
        SCREENSIZE = SIZE
        if level == 0: #level select page
            backMenu(lose, level, image.load("levels.png").convert(), win)   
            if vol_on:
                if song != "home_theme.ogg":
                    mixer.music.stop()
                    song = "home_theme.ogg"
                    mixer.music.load(song)
                    mixer.music.set_volume(0.5)
                    mixer.music.play(-1)            

        else:
            if vol_on:
                mixer.music.stop()
                mixer.music.load(song)
                if song == "water_theme.ogg": #starts water level song at 1 second as it took too long to start
                    mixer.music.play(-1, start = 1)
                else:
                    mixer.music.play(-1)
                    
            backMenu(lose, level, backImage, win)
            elapsed = time.get_ticks() #elapsed time is time in between game loop
            dragon = dragonHead(START_TILE, 1, [all, dragon_group, takenup_group]) 
            head_group.add(dragon) #calls a dragon head sprite
            fps = 45
            
            for segments in range(START_SEGMENTS):
                dragon.add_segment() #adds 5 segments to dragon head
            
            currentFood = 'none' #initial game variables
            currentScore = 0
            
            lastDirection = 0
            lastHeadXChange = 0
            lastHeadYChange = 0
            
            head_xchange = -16
            head_ychange = -16 
            xchange = -16
            ychange = -16     
            dontmove = 0
            move = 1
            angle = 0
            dontangle = 180          
            
            #various other variables specific to each level
            if level == 1:
                block_frame = 0
                progX = 260
                
            if level == 2:
                health = 200
                term_health = 75
                bulletTime = 0
                boss = False
                temp = Surface(SIZE).convert()  
                t = Terminator((350, 120))
                healthy = image.load("healthy.png")
                dirt = image.load("dirt.png").convert() 
                blood = image.load('blood.png').convert_alpha()
                term_group.add(t)     
                r_width = 120 #initial health bar widths
                b_width = 120
                x = 40
                y = 40
                opacity = 160 #opacity of dirt layer
                #DR stands for dragon run!!
                formation = [
                    
                     "P                                   P",
                     "P                 F                 P",
                     "C                FFF                C",
                     "C               FFFFF               C",
                     "P              FFFFFFF              P",    
                     "P             F       F             P",
                     "C            FFF     FFF            C",
                     "C           FFFFF   FFFFF           C",
                     "P          FFFFFFF FFFFFFF          P",
                     "P                                   P",
                     "C           P P     P P P           C",
                     "C           P   P   P   P           C",
                     "P           P   P   P P             P",
                     "P           P P     P   P           P",] 
                
                # builds the level
                for row in formation:
                    for col in row:
                        if col == "P": #depending on letter, calls a different piece of waste
                            currentFood = Food(takenup_group, (x,y), trash[1])
                            food_group.add(currentFood)
                            takenup_group.add(currentFood)
                            all.add(currentFood)  
                        elif col == "F":
                            currentFood = Food(takenup_group, (x,y), trash[0])
                            food_group.add(currentFood)
                            takenup_group.add(currentFood)
                            all.add(currentFood)         
                        elif col == "C":
                            currentFood = Food(takenup_group, (x,y), trash[2])
                            food_group.add(currentFood)
                            takenup_group.add(currentFood) 
                            all.add(currentFood)   
                        x += 25 #moves 25 over for next piece
                    y += 45 #resets x and goes to next row for each line
                    x = 40 
                    
            if level == 3:
                fps = 35 #slightly slower for moving level
                flag = image.load("flag.png")
                flag_x = 1000
                x = 0
                addBlock = 0
                addFood = 0
                foodLimit = 287 
                BACKGROUND = backImage
                r = Rock(takenup_group, 700) #calls first rock and piece of waste
                block_group.add(r)
                takenup_group.add(r)
                all.add(r)  
                currentFood = desertFood(takenup_group, (300, random.randint(2, SCREENTILES[1]) * TILE_SIZE[1]), trash[random.randint(0,2)])
                food_group.add(currentFood)
                takenup_group.add(currentFood)
                all.add(currentFood) 
            display.flip()         
          
        while not lose:
            #everything in game loop is first drawn on to bg and blitted as necessary, display.flip slowed it down too much
                # move is an integer as the value is used to take item in the MOVE_DIRECTIONS/MOVE_DIRECTIONS_TILES list          
            for evnt in event.get():
                if evnt.type == QUIT:
                    running = False
                elif evnt.type == KEYDOWN:
                    currentmove_direction = dragon.move_direction
                    if evnt.key == K_UP:
                        move = 2 
                        dontmove = 3 #ensures dragon cannot move back towards itself
                        angle = 90
                        dontangle = 270
                        xchange = -16 #xchange and ychange align dragon head sprite with body
                        ychange = -36
                    elif evnt.key == K_DOWN:
                        move = 3
                        dontmove = 2
                        angle = 270
                        dontangle = 90
                        xchange = -16
                        ychange = -16
                    elif evnt.key == K_LEFT:
                        move = 0
                        dontmove = 1
                        angle = 180
                        dontangle = 0
                        xchange = -36
                        ychange = -16
                    elif evnt.key == K_RIGHT:
                        move = 1
                        dontmove = 0
                        angle = 0
                        dontangle = 180
                        xchange = -16
                        ychange = -16

                    if currentmove_direction != dontmove:
                        dragon.move_direction = move
                        dragon.angle = angle
                        head_xchange = xchange
                        head_ychange = ychange  
                    if level == 2:
                        if evnt.key == K_SPACE: #for shooting water bullets
                            w = Water(takenup_group, (dragon.tilepos[0] * 20, (dragon.tilepos[1] * 20)-10), dragon.move_direction)
                            water_group.add(w)
                            takenup_group.add(w)
                            all.add(w) 
                        if evnt.key == K_m:
                            food_group.empty()
            
            # updates
            if (dragon.move_direction != lastDirection): #if new direction, changes head location changes
                dragon.rect.x -= lastHeadXChange
                dragon.rect.x += head_xchange
                dragon.rect.y -= lastHeadYChange
                dragon.rect.y += head_ychange
                
            lastDirection = dragon.move_direction
            lastHeadXChange = head_xchange
            lastHeadYChange = head_ychange
            
            # clearing
            all.clear(screen, bg)
            
            if level == 2:
                temp.blit(dirt, (0, 0)) #dirty water layer on temp surface. convert_alpha() didnt work properly for the image, so i had to set the entire layer opacity
                temp.set_alpha(opacity) 
                bg.blit(backImage, (0,0))
                bg.blit(temp, (0, 0))
                dirt2 = screen.blit(bg, (0, 0))
                
            if level == 3:
                scroll_x = x % BACKGROUND.get_rect().width  #draws moving background for desert level. use mod so that it goes back to beginning after cycling through image                              
                scroll1 = bg.blit(BACKGROUND, (scroll_x - BACKGROUND.get_rect().width, 0)) 
                if scroll_x < 1000: #if scroll_x is less than 1000, start blitting image at beginning for smooth transition
                    scroll2 = bg.blit(BACKGROUND, (scroll_x, 0))
                scroll = screen.blit(bg, (0,0)) 
                x -= 1  
                
                if abs(x) - abs(addBlock) > 500: #adds block every 500 pixels 
                    r = Rock(takenup_group, 1000)
                    block_group.add(r)
                    takenup_group.add(r)
                    all.add(r)  
                    addBlock = x  
                    
                if abs(x) - abs(addFood) > foodLimit: #adds food depending on food limit
                    offset = random.randint(-50, 0) #offset so that they're never drawn too close
                    currentFood = desertFood(takenup_group, (1000 + offset, random.randint(2, SCREENTILES[1]) * TILE_SIZE[1]), trash[random.randint(0,2)])
                    food_group.add(currentFood)
                    all.add(currentFood)  
                    for sprt in takenup_group: #checks to make sure it doesnt collide with rock mask
                        if sprite.collide_rect(currentFood, sprt):  
                            currentFood.kill()
                            
                    takenup_group.add(currentFood)
                    addFood = x
                        
            all.update()
            #render score for endless mode, else renders time   
            if level == 5:
                score = tfont.render("SCORE:%i" % currentScore, 1, BLACK)
                sc = screen.blit(bg, (20, 10), Rect((20, 10), (100, 30)))
                sc2 = screen.blit(score, (20, 10))
                
            else:
                if level == 1:
                    s = screen.blit(bg, (progX-50, 597), Rect((progX-50, 597), (100, 100)))
                    s2 = screen.blit(progressslider, (progX, 597))   
                currentTime = time.get_ticks() - elapsed
                if level == 2:
                    if not boss:
                        if len(food_group) < 15: #warns player of incoming terminator if they are about to clear food
                            incoming = mfont.render("TERMINATOR INCOMING", 1, RED)
                            i1 = screen.blit(incoming, (300, 150)) 
                            drawScreen.append(i1)
                        
                    timer = tfont.render("TIME:%.2f" % (currentTime / 1000), 1, BLACK)            
                else:
                    timer = tfont.render("TIME:%.2f" % (currentTime / 1000), 1, SCORE)
                c = screen.blit(bg, (20, 15), Rect((20, 15), (120, 40)))
                c2 = screen.blit(timer, (20, 15))                
            
            if currentFood == 'none': #if food is eaten, calls new
                if level == 1:
                    currentFood = Food(takenup_group, (random.randint(2, SCREENTILES[0]) * TILE_SIZE[0], random.randint(2, SCREENTILES[1]) * TILE_SIZE[1]), space_junk[random.randint(0,2)])
                elif level == 5:
                    currentFood = Food(takenup_group, (random.randint(2, SCREENTILES[0]) * TILE_SIZE[0], random.randint(2, SCREENTILES[1]) * TILE_SIZE[1]), trash[random.randint(0,2)])
                food_group.add(currentFood)
                takenup_group.add(currentFood)
                all.add(currentFood)
    
            pos = dragon.rect.topleft #if dragon hits edges of screen, lose is true
            if pos[0] < -10:
                lose = True
            if pos[0] >= SCREENSIZE[0]-30:
                lose = True
            if pos[1] < -10:
                lose = True
            if pos[1] >= SCREENSIZE[1]-38:
                lose = True
         
            #COLLISIONS
            # dragonHead -> tail
            collide = sprite.groupcollide(head_group, dragon_group, False, False, collided = sprite.collide_rect_ratio(0.8)) #second argument is kill, collided makes rect slightly smaller for accuracy
            i = 0
            for d in collide: #note: the dragon collide is supposed to count the horns! you are not allowed to make tight turns as the horn goes into the body
                for tail in collide[d]: #makes sure it is head
                    if tail.move_direction != dragon.move_direction: #checks to make sure it is not first connected body tile
                        i += 1
                        if i > 3: #this is to ensure that temporary overlaps during turns don't count
                            lose = True
            
            # dragonHead -> Food
            if level != 2: #dragon can eat food if not underwater level
                collide = sprite.groupcollide(head_group, food_group, False, True)
                for d in collide:
                    for tail in collide[d]:
                        if level == 3:
                            foodLimit -= 15 #foodlimit is reduced with each piece eaten, thus the faster you get to the food the better your time is
                        else:
                            currentFood = 'none' #level 3 does not call normal food
                        dragon.add_segment()
                        currentScore += 1
                        MOVE_RATE += SPEED_INCREASE #speed increased
                        if level == 1:
                            #space level only
                            progX += 20
                            block_frame += 1 
                            if block_frame >= BLOCK_SPAWN_RATE: #if it matches spawn rate, new meteor is added
                                block_frame = 0
                                b = Meteor(takenup_group)
                                block_group.add(b)
                                takenup_group.add(b)
                                all.add(b)
                                
            # dragonHead -> Meteor
            if level == 1:
                collide = sprite.groupcollide(head_group, block_group, False, False, sprite.collide_mask) #alpha mask as meteors are irregularly shaped
                for d in collide:
                    for collidedblock in collide[d]:
                        lose = True 
                        
            #Water bullets -> Food           
            if level == 2:                
                collide = sprite.groupcollide(water_group, food_group, False, True) 
                if collide:
                    dragon.add_segment()
                    currentScore += 1
                    MOVE_RATE += SPEED_INCREASE
                    opacity -= 1. #water gets clearer for every piece of waste consumed
                if boss:
                    collide = sprite.groupcollide(dragon_group, bullet_group, False, False) #bullets from terminator reduce health
                    if collide:
                        health -= 1
                        try:  #error handling as it raised error for zero division
                            b_width = int(120/(200/health)) #calculates width of health bar 
                        except:
                            pass                        
                       
                        if health < 1:
                            win = False
                            lose = True
                    col = sprite.groupcollide(water_group, term_group, False, False)
                    if col:
                        term_health -= 1
                        try: #error handling as it raises error for zero division
                            r_width = int(120/(75/term_health)) #calculates width of health bar
                        except:
                            pass
                        if term_health < 1: #if term_health reaches 0, wins
                            win = True
                    collide = sprite.groupcollide(head_group, term_group, False, False, sprite.collide_mask) #cannot collide into terminator
                    if collide:
                        lose = True
                        
            #DragonHead -> Rocks for desert level                
            if level == 3:              
                collide = sprite.groupcollide(head_group, block_group, False, False, sprite.collide_mask)
                for d in collide:
                    for collidedblock in collide[d]:
                        lose = True                
                                     
            # drawing
            drawScreen = all.draw(screen)  
            if level == 5:         
                drawScreen.append(sc) #draws score
                drawScreen.append(sc2)  
              
            else:               
                if level == 1:
                    drawScreen.append(s) #draws dragon slider
                    drawScreen.append(s2)
                elif level == 2:                
                    drawScreen.append(dirt2) #draws dirt layer
                    if boss:
                        if health < 40:
                            bl1 = screen.blit(blood, (0, 0)) #if health falls below 40, warns 
                            drawScreen.append(bl1)                        
                        d_healthy = screen.blit(healthy, (850, 20)) #draws grey health bar back
                        t_healthy = screen.blit(healthy, (442, 420))  
                        r_bar = draw.rect(screen, BLUE,(855,28,b_width,12)) #draws health bars
                        b_bar = draw.rect(screen, RED,(447,428,r_width,12))
                        drawScreen.append(d_healthy)
                        drawScreen.append(t_healthy)   
                        drawScreen.append(b_bar)
                        drawScreen.append(r_bar)  
                        all.add(t)                     
                elif level == 3:
                    drawScreen.append(scroll)  #draws scrolling background
                    if currentScore > 9:
                        flag1 = screen.blit(flag, (flag_x, 200)) #if score becomes 10, finish flag appears
                        flag_x -= 1
                        drawScreen.append(flag1)
                        if flag_x < 710: #if flag comes into view completely, player wins
                            win = True
                drawScreen.append(c)
                drawScreen.append(c2)    #draws time for levels         
            
            # updating
            display.update(drawScreen)
            if level == 1:
                if progX >= 640: #if slider reaches end, win is true
                    win = True           
            if level == 2:
                if not food_group: #if food is emptied, boss fight begins
                    boss = True 
                    if song != "boss_theme.ogg":
                        mixer.music.stop() 
                        song = "boss_theme.ogg"
                        mixer.music.load(song)
                        mixer.music.play(-1)
                    MOVE_RATE = 2.5 #slows down movement                  
                    if dragon.rect.y > 300 and dragon.rect.x < 700: #terminator shoots if dragon in line of vision
                        if time.get_ticks() - bulletTime > 200: #calls bullets
                            b = Bullet(380, 270, dragon.rect.x, dragon.rect.y)
                            b2 = Bullet(500, 340, dragon.rect.x, dragon.rect.y)
                            bullet_group.add(b, b2)
                            takenup_group.add(b, b2)
                            all.add(b, b2) #adds bullets to render updates
                            bulletTime = time.get_ticks()
             
            if level == 3:
                if len(missed) > 0:
                    win = False
                    missed[:] = [] #resets missed for next run
                    lose = True #if piece of food is left uneaten, player loses
                    
            if win:
                time.wait(500)
                winTime = (currentTime/1000) #wintime used for leader board
                lose = True
                
            # waiting
            clock.tick(fps)
            button = 0 #sets button as 0 so click becomes false again
        
        #------end of game loop----------
        
        if level != 0: #resets all variables after game over, sees if adding score to leaderboard is necessary
            if currentScore != 0:
                if level == 5:
                    winTime = currentScore                
                time.wait(500)
                numFile = open("irenetimes.dat", "r") 
                scoreList = []
                while True:
                    text = numFile.readline()
                    #rstrip removes the newline character read at the end of the line
                    text = text.rstrip("\n")     
                    if text == "": 
                        break
                    record = text.split("^")
                    if int(record[0]) == level:
                        scoreList.append(record[1])

                if len(scoreList) < 8: #if there are less than 8 scores for the level, adds win time
                    if level != 5:
                        if win:
                            keepScore = True
                    else:
                        keepScore = True
                else:
                    for item in scoreList: #if more than 8, checks if it is better than any current scores, adds it if it is
                        if level == 5:
                            if float(winTime) > float(item):
                                keepScore = True
                        else:
                            if win:
                                if float(winTime) < float(item):
                                    keepScore = True
                                
                thankYou = None
            
            if keepScore:
                YorN = userInput
                if submitted:
                    YorN = YorN.upper()
                    if YorN == "Y": #checks if user said yes or no, used to draw corresponding message in backMenu function
                        askUser = True                         
                        keepScore = False
                        userInput = "" 
                        submitted = False
                        
                    elif YorN == "N":
                        askUser = False
                                               
                    else:
                        print ("invalid input for (Y/N).") #error handling if not Y or N
                        userInput = ""
                        submitted = False

            if askUser:
                userName = userInput
                if submitted:
                    if not thankYou: #adds it once, as after it is added thank you becomes true
                        numFile = open("irenetimes.dat", "a")       
                        numFile.write(str(level) + "^" + str(winTime) + "^" + userName + "\n")
                        numFile.close()                           
                    thankYou = True
               
            mixer.music.set_volume(0) #stops music
            dragon_group.empty()
            head_group.empty()
            food_group.empty()
            takenup_group.empty()
            block_group.empty()
            bullet_group.empty()
            term_group.empty()
            water_group.empty()
            drawScreen = None
            all.empty() 
            
            MOVE_RATE = 2
            elapsed = time.get_ticks()
            progX = 260
            currentScore = 0 
            currentFood = 'none'
            boss = False
             
            for evnt in event.get():
                if level != 0:
                    if evnt.type == KEYDOWN: #converts literal text input to the actual things they are supposed to do. e.g. space is " " instead of "space"
                        if key.name(evnt.key) == "backspace":
                                userInput = userInput[:-1]  
                        elif key.name(evnt.key) == "space":
                                userInput += " "   
                        elif key.name(evnt.key) == "return":
                            submitted = True   
                        else:
                            if len(userInput) < 18: #sets a maximum character length of 18 so that it doesn't go out of the bar, and adds the inputted letter on if the length is below 18
                                userInput+=evnt.unicode 
                            else:
                                print ("the string you've submitted is too long")
                     
                    if evnt.type == MOUSEBUTTONUP:
                        button = 0                  
                    elif evnt.type == MOUSEBUTTONDOWN:
                        button = evnt.button                        
                        mx, my  = mouse.get_pos()     
                   
                    if button == 1: #resets user input variables and some specific game variables after restart or return are clicked
                        if pauseRect[0].collidepoint(mx, my): 
                            askUser = None
                            keepScore = None
                            submitted = None
                            thankYou = None
                            userInput = ""                                 
                            mixer.music.set_volume(1)
                            level = level
                            if level == 2:
                                term_health = 75
                                health = 200
                            win = False
                            lose = False #set lose as false to restart the while not lose loop
                        elif pauseRect[1].collidepoint(mx, my):
                            askUser = None
                            keepScore = None
                            submitted = False
                            thankYou = None
                            userInput = ""   
                            button = 0
                            if level == 5:
                                mixer.music.set_volume(0.5)
                                win = False
                                lose = True
                                level = 0  
                                game = False
                                menu = True
                            else:
                                mixer.music.set_volume(1)
                                win = False
                                lose = True
                                level = 0
   
                      
quit()