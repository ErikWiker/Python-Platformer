import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
#dynamically loading sprite sheets, we will be using a function for this (like animations)

pygame.init()

pygame.display.set_caption("Platformer")

#BG_COLOR = (255, 255, 255) #not used since you draw everything
WIDTH, HEIGHT = 1000, 800 #depends on monitor size
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

#need to split sprite sheets into individual sprite images and call them/loop through as needed
#also need to get rotated version if you are moving in a different direction

def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))] #load every single file that is inside the directory (for loop in  a list)
    
    all_sprites = {}
    
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #load transparent bkg image
        
        sprites = []
        for i in range(sprite_sheet.get_width() // width): #width is individual sprite in the sheet
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect) #drawing at 0,0 of the new surface, drawing my frame from the the sprite sheet that you want
            sprites.append(pygame.transform.scale2x(surface)) #from 32x32 to 64x64
            
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites #takes off the png, append the _right
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites) #flip for left side since they originally face right
        else:
            all_sprites[image.replace(".png","")] = sprites
    
    return all_sprites
            
def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size) #position from the sprite sheet you want to load, adjust for different terrain
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)                
            

class Player(pygame.sprite.Sprite): #inheriting sprite, sprites good for pixel perfect collision
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True) #true for multidirection sprites (left and right side)
    ANIMATION_DELAY = 3 #how fast it cycles through sprites
    
    def __init__(self, x, y,  width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0   
            
    def loop(self, fps): #called once every frame to update animation/move char/etc
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) 
        self.move(self.x_vel, self.y_vel)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2: #two seconds
            self.hit = False
            self.hit_count = 0
        
        self.fall_count += 1
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1
        
    
    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
          sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel !=0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite) #solve problem of rectangular hitbox, so it allows for pixel perfect collision
        
    
    
    def draw(self, win, offset_x): #image definition, takes window
        #pygame.draw.rect(win, self.COLOR, self.rect) #for a rectangle
        #self.sprite = self.SPRITES["idle_" + self.direction][0] #accessing key (action) and frame (first frame)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# this is a base class to define all properties needed for a valid sprite
#there will be inheritance, this is for saving from rewritting
# modify this image, when we change it => draw function will draw it accurately and other variables are saved if we need 
class Object(pygame.sprite.Sprite):
    def __init__ (self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height):
        super().__init__(x , y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height) #represents fire pngs/sprites
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
        
    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"
        
    def loop(self):

        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        
        if self.animation_count // self.ANIMATION_DELAY > len(sprites): #to prevent the count from getting to large
            self.animation_count = 0
        
        

#this only works because you are actively in the correct directory
def get_background(name): #return a list of all background tiles we need to draw, input is color of bkg
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect() #don't care about x/y
    tiles = []
    
    for i in range(WIDTH // width +1): #WIDTH is screen, and width is of tile image
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j* height)
            tiles.append(pos)
    
    return tiles, image
   
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)
    
    for obj in objects:
        obj.draw(window, offset_x)
    
    player.draw(window, offset_x)
    
    pygame.display.update()



def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0) #if the player would move left or right, would they hit a block
    player.update() #need to update rect and mask before checking collision
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
        
    player.move(-dx, 0)
    player.update()
    return collided_object #you might want to return all objects from here as well...




def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0 #only want to move when holding down key (there are other ways to do this)
    collide_left = collide(player, objects, -PLAYER_VEL *2) #a bit of a hack with the *2
    collide_right = collide(player, objects, PLAYER_VEL *2) #it causes a bit more space for horizontal collision, 
                                                            #to count for sprite movement so you don't have a bug of ignoring collision horizontally
        
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

#this is where you will handle the event loop
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Green.png")
    
    block_size = 96
    
    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32) #if the size is too large can give an out of bound error
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    #blocks = [Block(0, HEIGHT - block_size, block_size)]
    
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               fire]
    
    offset_x = 0
    scroll_area_width = 200
    
    run = True
    while run:
        clock.tick(FPS) #ensures while loop will run no more than 60 FPS (slower PCs could be slower)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN: #done here instead of handle move, since if it was done there it would continue to happen if the key was held down, like movement
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        
        player.loop(FPS) #this is what actually moves player, moving every single frame
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        
        
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0)
        or (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0)):
            offset_x += player.x_vel
    
    pygame.quit()
    quit()
            

#so we only call the main function if we run this file directly, not if we import something the file
if __name__ == "__main__": 
        main(window)