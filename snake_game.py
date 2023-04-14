import pygame
import time
import random
import sys

BLOCK_SIZE = 75
DISTANCE_REQUIREMENT = 30
INIT_X = 100
INIT_Y = 100
SURFACE_DIMENSIONS = (750,750)
BACKGROUND_COLOR = (252,220,242)
INITIAL_SLEEP_TIME = 2.5/1000
ITEM_DICT = {"mario hat":"images/mario_hat.png", "luigi hat": "images/mario_hat.png", "peach hair":"images/mario_hat.png",
              "harry potter":"images/wizard_hat.png", "dumbledore":"images/wizard_hat.png", "voldemort":"images/wizard_hat.png",
              "coraline jacket": "images/coraline_jacket.png",
            "charmander": "images/pokeball.png", "squirtle": "images/pokeball.png", 
            "chimchar": "images/pokeball.png", "totodile":"images/pokeball.png",
               #"chikorita": "pokeball.png","bulbasoar":"pokeball.png",
              "no face": "images/haku.png", "yubaba": "images/haku.png", "totoro":"images/ghibli_dust.png", 
              "ponyo":"images/ghibli_dust.png", "mononoke":"images/haku.png",
              "ryuk":"images/deathnote.png", "L":"images/deathnote.png"}

KIRBY_DICT = {"mario hat":"images/mario_kirby.png", "luigi hat": "images/luigi_kirby.png", "peach hair": "images/peach_kirby.png",
               "harry potter":"images/harry_potter_kirby.png", "dumbledore":"images/dumbledore_kirby.png", "voldemort":"images/voldemort_kirby.png",
               "coraline jacket": "images/coraline_mom_kirby.png",
               "charmander": "images/charmander_kirby.png", "squirtle": "images/squirtle_kirby.png", "bulbasoar": "images/bulbasoar_kirby.png",
                "chikorita":"images/chikorita_kirby.png", "chimchar": "images/chimchar_kirby.png", "totodile":"images/totodile_kirby.png",
                "no face": "images/no_face_kirby.png", "yubaba": "images/yubaba_kirby.png", "totoro":"images/totoro_kirby.png",
                "ponyo":"images/ponyo_kirby.png", "mononoke":"images/mononoke_kirby.png",
                "ryuk":"images/ryuk_kirby.png", "L":"images/L_kirby.png", }

# ALL SNAKE BLOCKS WILL MOVE BY 1
# ALL BLOCKS WILL BE A SET DISTANCE APART - this distance must be one dimensional and depends on the direction of the block in front of it
# ALL BLOCKS KEEP TRACK OF THEIR PREVIOUS MOVE (the number of tracked moves depends on the distance apart, ie direction at T+0, and direction at T-30 (DISTANCE IS 30))
# DIRECTION 1 AND 2 WILL TRACK WHEN THE BLOCK IS MADE.
# IF THERE IS A NEW BLOCK MADE BEFORE THE PREVIOUS BLOCK WAS ALIVE FOR 30 UNITS, THEN THE NEW BLOCK IS STATIONARY UNTIL THE OLD BLOCK IS ALIVE FOR 30 UNITS.
# ALL BLOCKS FOLLOW THE DIRECTION OF THE BLOCK IN FRONT OF IT AT TIME T - DISTANCE
# IF THE BLOCK IN FRONT HAD A DIRECTION CHANGE THIS TURN, THE FOLLOWING BLOCK WILL USE THE DIRECTION OF T+1
# IF THERE IS A TURN BEFORE T - DISTANCE CAN BE CALCULATED FOR THE NEXT BLOCK, THEN see two below??? (CALCULATE LAST TWO DIRECTIONS AND MAKE THE TURN WHEN DISTANCE )
# NEW BLOCKS WILL BE STATIONARY UNTIL THE ONE DIMENSIONAL DISTANCE IS MET
# A NEW BLOCK CAN MOVE WHEN THE TOTAL DISTANCE TO THE NEXT BLOCK MEETS THE CRITERIA, BUT IT WILL MOVE IN THE DIRECTION OF THE TURN COORDINATE
# this should cover everything

class Item:
    def __init__(self, parent_screen):
        self.name, self.image_path = random.choice(list(ITEM_DICT.items()))
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE - 10,BLOCK_SIZE - 10))
        self.parent_screen = parent_screen
        self.x = 250
        self.y = 250

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))

    def respawn(self):

        # need to avoid the chance of two items being respawned within DISTANCE_REQUIREMENT distance from another
        # this will mess up the snake

        while 1:
            new_x = random.randint(0, SURFACE_DIMENSIONS[0] - BLOCK_SIZE)
            new_y = random.randint(0, SURFACE_DIMENSIONS[1] - BLOCK_SIZE)

            if abs(self.x - new_x) >DISTANCE_REQUIREMENT and abs(self.y - new_y) > DISTANCE_REQUIREMENT:
                self.x = new_x
                self.y = new_y
                break

        self.name, self.image_path = random.choice(list(ITEM_DICT.items()))
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE - 10,BLOCK_SIZE - 10))
        

class Block:

    def __init__(self, distance_requirement, is_head=False):

        distance_requirement : int

        if is_head == True:
            self.image = pygame.image.load("images/kirby_head.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (BLOCK_SIZE,BLOCK_SIZE))
            self.is_moveable = True
            self.is_head = True


        else:
            self.image = pygame.image.load("images/kirby_head.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (BLOCK_SIZE,BLOCK_SIZE))
            self.is_moveable = False # block is not moveable until distance requirement is met
            self.is_head = False

        self.x = 0
        self.y = 0
        self.distance_requirement = int(distance_requirement)
        self.current_direction = ''
        self.previous_direction = ''
        self.direction_history = []
        self.item = "None"
        

    def update_direction_history(self):

        if len(self.direction_history) < self.distance_requirement:
            self.direction_history.insert(0,self.current_direction)

        else:
            # get rid of the last direction on the list
            self.direction_history.pop()

            # add the current direction to the front of the list
            self.direction_history.insert(0,self.current_direction)

            # save the last element as the previous direction
            self.previous_direction = self.direction_history[-1]

            self.is_moveable = True

    def add_item(self, item_name):
        '''
        Takes the current item that is on the board transforms the head of the snake to wear that item.
        '''

        image_path = KIRBY_DICT[item_name]
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (BLOCK_SIZE,BLOCK_SIZE))

        self.item = item_name


class Snake:

    def __init__(self, distance_requirement, parent_screen):

        self.distance_requirement : int
        self.body : list

        self.parent_screen = parent_screen
        # initialize the body of the snake where the first block is the head
        self.distance_requirement = distance_requirement
        self.body = [Block(self.distance_requirement, is_head = True)]
        self.length = len(self.body)
        self.collision = False

    def draw(self):

        for block in reversed(self.body):
            self.parent_screen.blit(block.image, (block.x, block.y))

    def add_length(self):

        self.length+=1
        self.body.append(Block(self.distance_requirement, is_head = False))

        # make the x, y coordinates of the new block equal to the x,y coordinates of the last block
        self.body[-1].x, self.body[-1].y = self.body[-2].x, self.body[-2].y


    # def update_snake(self, item):

    #     # each block wears the item of the block in front of it
    #     for i in range(self.length-1, -1,-1):

    #         current_block = self.body[i]

    #         if current_block.is_head is False:

    #             current_block.add_item(self.body[i - 1].item)

    #         else:
    #          self.body[i].add_item(item) 
    
    # def update_snake(self, item_name):

    #     # each block wears the item of the block in front of it
    #     self.body[-1].add_item(item_name)

    # Main function
    def update_snake(self, item_name):

        self.body[0].add_item(item_name)


    def change_direction(self, direction):
        
        self.body[0].current_direction = direction
        

    def move(self):

        # loop through each of the blocks and adjust their directions
        for i in range(self.length-1, -1,-1):

            current_block = self.body[i]

            if current_block.is_head is False:

                next_block = self.body[i-1]
                current_block.current_direction = next_block.previous_direction

            # then, update the current block's direction history
            current_block.update_direction_history()

            # now move the block towards it's current direction
            # only move moveable blocks, and the head
            if current_block.is_moveable or current_block.is_head:
                if current_block.current_direction == 'up':
                    current_block.y-=1
                elif current_block.current_direction == 'down':
                    current_block.y+=1
                elif current_block.current_direction == 'left':
                    current_block.x -=1
                elif current_block.current_direction == 'right':
                    current_block.x+=1

        # draw the body of the snake
        self.draw()

# button code from https://github.com/harsitbaral/ButtonPygame/blob/main/pygamebuttonyoutube.py
class Button():
    def __init__(self, surface, image, pos, text_input, font, base_color, hover_color):
        self.surface = surface
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hover_color = base_color, hover_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            self.surface.blit(self.image, self.rect)
        self.surface.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hover_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

class Game:
    def __init__(self):

        # initalize display module
        pygame.init()

        # initalize a window for display, size
        self.surface = pygame.display.set_mode(SURFACE_DIMENSIONS)
        self.paused = False

        # initialize pygame.mixer for music
        # pygame.mixer.init()
        # pygame.mixer.music.load(filename = "song.mp3")
        # pygame.mixer.music.play()

        # init the snake and item
        self.snake = Snake(DISTANCE_REQUIREMENT, self.surface)
        self.item = Item(self.surface)
        self.item.draw()
        self.score = 1
        self.current_sleep_time = INITIAL_SLEEP_TIME


    def display_score(self):
        font = pygame.font.SysFont('arial',30)
        score = font.render(f"Score: {self.snake.length}", True, (255,255,255))
        self.surface.blit(score, (SURFACE_DIMENSIONS[0] - 150, 15))

    def item_collision(self):

        snake_x = self.snake.body[0].x
        snake_y = self.snake.body[0].y

        if (snake_y <= self.item.y + BLOCK_SIZE/2) and (snake_y >= self.item.y - BLOCK_SIZE/2):
            if (snake_x <= self.item.x + BLOCK_SIZE/2) and (snake_x >= self.item.x - BLOCK_SIZE/2):
                return True
        return False
    
    def snake_collision(self):

        snake_x = self.snake.body[0].x
        snake_y = self.snake.body[0].y

        # Check to see if their was a collision after the movement (want to ommit the tail, because it will always collide)
        for i in range(3, self.snake.length - 1):
            #BLOCK_SIZE/2
            if (snake_y <= self.snake.body[i].y + BLOCK_SIZE/2) and (snake_y >= self.snake.body[i].y - BLOCK_SIZE/2):
                if (snake_x <= self.snake.body[i].x + BLOCK_SIZE/2) and (snake_x >= self.snake.body[i].x - BLOCK_SIZE/2):
                    return True
        return False
    
    def out_of_bounds(self):

        snake_x = self.snake.body[0].x
        snake_y = self.snake.body[0].y

        if (snake_y < 0 - BLOCK_SIZE/2) or (snake_y >= SURFACE_DIMENSIONS[1] - BLOCK_SIZE/2):
            return True
        
        elif (snake_x < 0 - BLOCK_SIZE/2) or (snake_x >= SURFACE_DIMENSIONS[0] - BLOCK_SIZE/2):
            return True
        
        else:
            return False

    def draw_board(self):

        # first clear the previous board
        self.surface.fill(BACKGROUND_COLOR)

        self.display_score()
        self.snake.move()
        self.item.draw()
        
        #update the parent screen
        pygame.display.flip()

    def decrease_sleep_time(self):
        if self.score < 10:
            multiplier = 9/10
        elif (self.score >= 10) and (self.score < 20):
            multiplier = 8/10
        elif (self.score >= 20) and (self.score <30):
            multiplier = 7/10
        elif (self.score >= 30) and (self.score < 40):
            multiplier = 6/10
        elif (self.score >= 40) and (self.score < 50):
            multiplier = 5/10
        else:
            multiplier = 4/10

        self.current_sleep_time = self.current_sleep_time *  multiplier
        
    def play(self):

        # play the game in each loop
        if self.item_collision():
            self.snake.add_length()
            self.snake.update_snake(self.item.name)
            self.item.respawn()
            self.score+=1
            self.decrease_sleep_time()

        if self.snake_collision():
            raise "Game Over"
        
        elif self.out_of_bounds():
            raise "Game Over"

        self.draw_board()

    def game_over(self):

        header_text1 = pygame.font.Font("images/font.ttf", 60).render("GAME OVER!", True, "#b68f40")
        header_rect1 = header_text1.get_rect(center = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*.75))

        header_text2 = pygame.font.Font("images/font.ttf", 60).render(f"Score: {self.snake.length}", True, "#b68f40")
        header_rect2 = header_text2.get_rect(center = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*1.5))

        # (self, surface, image, pos, text_input, font, base_color, hovering_color)
        play_button = Button(self.surface, 
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*3),
                            text_input = "PLAY",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")
        
        options_button = Button(self.surface,
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*4),
                            text_input = "OPTIONS",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")
        
        quit_button = Button(self.surface,
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*5),
                            text_input = "QUIT",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")


        # reset the snake, item, and score
        self.reset()

        
        while True:
            # first clear the previous board
            pygame.display.set_caption("Princess Gabi's Snake Game")
            self.surface.fill(BACKGROUND_COLOR)
            menu_mouse_pos = pygame.mouse.get_pos()

            self.surface.blit(header_text1, header_rect1)
            self.surface.blit(header_text2, header_rect2)

            for button in [play_button, options_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.run_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        self.run_game()
                    if options_button.checkForInput(menu_mouse_pos):
                        self.options()
                    if quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()

    def reset(self):
        # re-init the snake and item
        self.snake = Snake(DISTANCE_REQUIREMENT, self.surface)
        self.item = Item(self.surface)
        self.item.draw()
        self.score = 1
        self.current_sleep_time = INITIAL_SLEEP_TIME

    def options(self):
        self.paused = True
        # first clear the previous board
        self.surface.fill(BACKGROUND_COLOR)
        font = pygame.font.Font("images/font.ttf", 30)
        game_over_message = font.render(f"GAME OVER! Score: {self.snake.length}\nPress Enter to Play Again.", True, (255,255,255))
        self.surface.blit(game_over_message, (100, SURFACE_DIMENSIONS[1]/2))
        #update the parent screen
        pygame.display.flip()


    def run_game(self):
    
        running = 1
        while running:
            for event in pygame.event.get():
                # keydown is when the key is pressed -> keyup is when the key is released
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction('up')
                    if event.key == pygame.K_DOWN:
                        self.snake.change_direction('down')
                    if event.key == pygame.K_RIGHT:
                        self.snake.change_direction('right')
                    if event.key == pygame.K_LEFT:
                        self.snake.change_direction('left')

                    if event.key == pygame.K_ESCAPE:
                        running = 0

                    if event.key == pygame.K_SPACE:
                        if self.paused == True:
                            self.paused = False
                        elif self.paused == False:
                            self.paused = True

                elif event.type == pygame.QUIT:
                    sys.exit()

            if not self.paused:
                try:
                    self.play()
                except Exception as e:
                    self.game_over()

            time.sleep(self.current_sleep_time)

    def main_menu(self):

        header_text1 = pygame.font.Font("images/font.ttf", 45).render("Princess Gabi's", True, "#b68f40")
        header_rect1 = header_text1.get_rect(center = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*.75))

        header_text2 = pygame.font.Font("images/font.ttf", 60).render("Snake Game", True, "#b68f40")
        header_rect2 = header_text2.get_rect(center = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*1.5))

        # (self, surface, image, pos, text_input, font, base_color, hovering_color)
        play_button = Button(self.surface,
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*3),
                            text_input = "PLAY",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")
        
        options_button = Button(self.surface,
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*4),
                            text_input = "OPTIONS",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")
        
        quit_button = Button(self.surface,
                            image = pygame.image.load("images/play_rectangle.png"),
                            pos = (SURFACE_DIMENSIONS[0]/2, SURFACE_DIMENSIONS[1]/6*5),
                            text_input = "QUIT",
                            font = pygame.font.Font("images/font.ttf", 40),
                            base_color="#d7fcd4", hover_color="White")

        while True:
            # first clear the previous board
            pygame.display.set_caption("Princess Gabi's Snake Game")
            self.surface.fill(BACKGROUND_COLOR)
            menu_mouse_pos = pygame.mouse.get_pos()

            self.surface.blit(header_text1, header_rect1)
            self.surface.blit(header_text2, header_rect2)

            for button in [play_button, options_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.surface)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.run_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        self.run_game()
                    if options_button.checkForInput(menu_mouse_pos):
                        self.options()
                    if quit_button.checkForInput(menu_mouse_pos):
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()


if __name__ == "__main__":

    game = Game()
    game.main_menu()
