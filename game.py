import pygame
import numpy as np
import tcod
import random
from enum import Enum

class Direction(Enum):
    DOWN = -90
    RIGHT = 0
    UP = 90
    LEFT = 180
    NONE = 360

def translate_screen_to_maze(in_coords, in_size=32):
    return int(in_coords[0] / in_size), int(in_coords[1] / in_size)

def translate_maze_to_screen(in_coords, in_size=32):
    return in_coords[0] * in_size, in_coords[1] * in_size

class GameObject:
    def __init__(self, in_surface, x, y,
                 in_size: int, in_color=(125, 25, 30),
                 is_circle: bool = False):
        self._size = in_size
        self._renderer: GameRenderer = in_surface
        self._surface = in_surface._screen
        self.y = y
        self.x = x
        self._color = in_color
        self._circle = is_circle
        self._shape = pygame.Rect(self.x, self.y, in_size, in_size)

    def draw(self):
        if self._circle:
            pygame.draw.circle(self._surface,
                               self._color,
                               (self.x, self.y),
                               self._size)
        else:
            rect_object = pygame.Rect(self.x, self.y, self._size, self._size)
            pygame.draw.rect(self._surface,
                             self._color,
                             rect_object,
                             border_radius=1)

    def tick(self):
        pass

    def get_shape(self):
        return pygame.Rect(self.x, self.y, self._size, self._size)

    def set_position(self, in_x, in_y):
        self.x = in_x
        self.y = in_y

    def get_position(self):
        return (self.x, self.y)

class Wall(GameObject):
    def __init__(self, in_surface, x, y, in_size: int, in_color=(183,176,156)):
        super().__init__(in_surface, x * in_size, y * in_size, in_size, in_color)

class FinishLine(GameObject):
    def __init__(self, in_surface, x, y, in_size: int, in_color=(0, 255, 0)):
        super().__init__(in_surface, x * in_size, y * in_size, in_size, in_color)

class GameRenderer:
    def __init__(self, in_width: int, in_height: int, lives: int):
        pygame.init()
        self._width = in_width
        self._height = in_height
        self._screen = pygame.display.set_mode((in_width, in_height))
        pygame.display.set_caption('Takeshi-Maze')
        self._clock = pygame.time.Clock()
        self._done = False
        self._won = False
        self._game_objects = []
        self._walls = []
        self._ghosts = []
        self._hero: Hero = None
        self._lives = lives
        self._score = 0
        self._finish_line = None
        self._pakupaku_event = pygame.USEREVENT + 3


    def tick(self, in_fps: int):
        black = (59, 69, 43)

        #self.handle_mode_switch()
        pygame.time.set_timer(self._pakupaku_event, 200) # open close mouth
        while not self._done:
            for game_object in self._game_objects:
                game_object.tick()
                game_object.draw()

            self.display_text(f"[Lives: {self._lives}]")

            if self._hero is None: 
                self._done = True
            if self.get_won(): 
                self._done = True
            pygame.display.flip()
            self._clock.tick(in_fps)
            self._screen.fill(black)
            self._handle_events()

    def add_game_object(self, obj: GameObject):
        self._game_objects.append(obj)

    def add_ghost(self, obj: GameObject):
        self._game_objects.append(obj)
        self._ghosts.append(obj)

    def set_won(self):
        self._won = True

    def get_won(self):
        return self._won

    def get_hero_position(self):
        return self._hero.get_position() if self._hero != None else (0, 0)

    def end_game(self):
        if self._hero in self._game_objects:
            self._game_objects.remove(self._hero)
        self._hero = None

    def kill_pacman(self):
        self.end_game()

    def display_text(self, text, in_position=(32, 0), in_size=30):
        font = pygame.font.SysFont('Arial', in_size)
        text_surface = font.render(text, False, (255, 255, 255))
        self._screen.blit(text_surface, in_position)

    def add_wall(self, obj: Wall):
        self.add_game_object(obj)
        self._walls.append(obj)

    def get_walls(self):
        return self._walls

    def get_ghosts(self):
        return self._ghosts

    def get_game_objects(self):
        return self._game_objects

    def add_hero(self, in_hero):
        self.add_game_object(in_hero)
        self._hero = in_hero

    def add_finish_line(self, obj: FinishLine):
        self.add_game_object(obj)
        self._finish_line = obj

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pressed = pygame.key.get_pressed()
        if self._hero is None: return
        if pressed[pygame.K_UP]:
            self._hero.set_direction(Direction.UP)
        elif pressed[pygame.K_LEFT]:
            self._hero.set_direction(Direction.LEFT)
        elif pressed[pygame.K_DOWN]:
            self._hero.set_direction(Direction.DOWN)
        elif pressed[pygame.K_RIGHT]:
            self._hero.set_direction(Direction.RIGHT)

class MovableObject(GameObject):
    def __init__(self, in_surface, x, y, in_size: int, in_color=(255, 0, 0), is_circle: bool = False):
        super().__init__(in_surface, x, y, in_size, in_color, is_circle)
        self.current_direction = Direction.NONE
        self.direction_buffer = Direction.NONE
        self.last_working_direction = Direction.NONE
        self.location_queue = []
        self.next_target = None
        self.image = pygame.image.load('graphics/monster/blue1.png')

    def get_next_location(self):
        return None if len(self.location_queue) == 0 else self.location_queue.pop(0)

    def set_direction(self, in_direction):
        self.current_direction = in_direction
        self.direction_buffer = in_direction

    def collides_with_wall(self, in_position):
        collision_rect = pygame.Rect(in_position[0], in_position[1], self._size, self._size)
        collides = False
        walls = self._renderer.get_walls()
        for wall in walls:
            collides = collision_rect.colliderect(wall.get_shape())
            if collides: break
        return collides

    def check_collision_in_direction(self, in_direction: Direction):
        desired_position = (0, 0)
        if in_direction == Direction.NONE: return False, desired_position
        if in_direction == Direction.UP:
            desired_position = (self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            desired_position = (self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            desired_position = (self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            desired_position = (self.x + 1, self.y)

        return self.collides_with_wall(desired_position), desired_position

    def automatic_move(self, in_direction: Direction):
        pass

    def tick(self):
        self.reached_target()
        self.automatic_move(self.current_direction)

    def reached_target(self):
        pass
    
    def draw(self):
        self.image = pygame.transform.scale(self.image, (32, 32))
        self._surface.blit(self.image, self.get_shape())

class Hero(MovableObject):
    def __init__(self, in_surface, x, y, in_size: int,):
        super().__init__(in_surface, x, y, in_size, (255, 255, 0), False)
        self.last_non_colliding_position = (0, 0)
        self.open = pygame.image.load("graphics/hero/hero_intro.png")
        self.image = self.open
        self.mouth_open = True

    def tick(self):
        # TELEPORT
        if self.x < 0:
            self.x = self._renderer._width

        if self.x > self._renderer._width:
            self.x = 0

        self.last_non_colliding_position = self.get_position()

        if self.check_collision_in_direction(self.direction_buffer)[0]:
            self.automatic_move(self.current_direction)
        else:
            self.automatic_move(self.direction_buffer)
            self.current_direction = self.direction_buffer

        if self.collides_with_wall((self.x, self.y)):
            self.set_position(self.last_non_colliding_position[0], self.last_non_colliding_position[1])

        if self._renderer._finish_line is not None and self.collides_with_finish_line():
            self._renderer.set_won()

        self.handle_ghosts()

    def automatic_move(self, in_direction: Direction):
        collision_result = self.check_collision_in_direction(in_direction)

        desired_position_collides = collision_result[0]
        if not desired_position_collides:
            self.last_working_direction = self.current_direction
            desired_position = collision_result[1]
            self.set_position(desired_position[0], desired_position[1])
        else:
            self.current_direction = self.last_working_direction

    def handle_ghosts(self):
        collision_rect = pygame.Rect(self.x, self.y, self._size, self._size)
        ghosts = self._renderer.get_ghosts()
        game_objects = self._renderer.get_game_objects()
        for ghost in ghosts:
            collides = collision_rect.colliderect(ghost.get_shape())
            if collides and ghost in game_objects:
                self._renderer.kill_pacman()

    def collides_with_finish_line(self):
        collision_rect = pygame.Rect(self.x, self.y, self._size, self._size)
        return collision_rect.colliderect(self._renderer._finish_line.get_shape())


    def draw(self):
        half_size = self._size / 2
        self.image = self.open
        super(Hero, self).draw()

class Ghost(MovableObject):
    def __init__(self, in_surface, x, y, in_size: int, in_game_controller, sprite_path="graphics/monster/blue2.blue2.png"):
        super().__init__(in_surface, x, y, in_size)
        self.game_controller = in_game_controller
        self.sprite_normal = pygame.image.load(sprite_path)

    def reached_target(self):
        if (self.x, self.y) == self.next_target:
            self.next_target = self.get_next_location()
        self.current_direction = self.calculate_direction_to_next_target()

    def set_new_path(self, in_path):
        for item in in_path:
            self.location_queue.append(item)
        self.next_target = self.get_next_location()

    def calculate_direction_to_next_target(self) -> Direction:
        if self.next_target is None:
            self.request_path_to_player(self)
            return Direction.NONE
        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return Direction.DOWN if diff_y > 0 else Direction.UP
        if diff_y == 0:
            return Direction.LEFT if diff_x < 0 else Direction.RIGHT

        self.game_controller.request_new_random_path(self)
        return Direction.NONE

    def request_path_to_player(self, in_ghost):
        player_position = translate_screen_to_maze(in_ghost._renderer.get_hero_position())
        current_maze_coord = translate_screen_to_maze(in_ghost.get_position())
        path = self.game_controller.p.get_path(current_maze_coord[1], current_maze_coord[0], player_position[1],
                                               player_position[0])

        new_path = [translate_maze_to_screen(item) for item in path]
        in_ghost.set_new_path(new_path)

    def automatic_move(self, in_direction: Direction):
        if in_direction == Direction.UP:
            self.set_position(self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            self.set_position(self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            self.set_position(self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            self.set_position(self.x + 1, self.y)
    def draw(self):
        self.image = self.sprite_normal
        super(Ghost, self).draw()

class Pathfinder:
    def __init__(self, in_arr):
        cost = np.array(in_arr, dtype=np.bool_).tolist()
        self.pf = tcod.path.AStar(cost=cost, diagonal=0)

    def get_path(self, from_x, from_y, to_x, to_y) -> object:
        res = self.pf.get_path(from_x, from_y, to_x, to_y)
        return [(sub[1], sub[0]) for sub in res]

class PacmanGameController:
    def __init__(self, x ):
        self.ascii_maze = []
        self.ascii_maze1 = [
            "X XXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP           XX       G    X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X         G                X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X      XX    XX    XX      X",
            "XXXXXX XXXXX XX XXXXX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXX  XXX XX XXXXXX",
            "XXXXXX XX X      X XX XXXXXX",
            "          X      X          ",
            "XXXXXX XX X      X XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "XXXXXX XX          XX XXXXXX",
            "XXXXXX XX XXXXXXXX XX XXXXXX",
            "X            XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X   XX                XX   X",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "X      XX    XX    XX      X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X                          X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXX X",
        ]
        self.ascii_maze2 = [
            "X XXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP     XX          XX      X",
            "X XXXX XX XXXXXXXX XX XXXX X",
            "X                          X",
            "XXX XX XXXXX XX XXXXX XX XXX",
            "    XXG      XX      GXX    ",
            "XXX XXXXX XXXXXXXX XXXXX XXX",
            "X                          X",
            "X XXXXXXX XXXXXXXX XXXXXXX X",
            "X   XX       XX       XX   X",
            "XXX XX XXXXX XX XXXXX XX XXX",
            "XXX XX XX          XX XX XXX",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "XXX XX XX          XX XX XXX",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "     G       XX       G     ",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X   XX                XX   X",
            "XXX XX XX XXXXXXXX XX XX XXX",
            "X      XX    XX    XX      X",
            "X XXXXXXXXXX XX XXXXXXXXXX X",
            "X                          X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXX X",
        ]
        self.ascii_maze3 = [
            "X XXXXXXXXXXXXXXXXXXXXXXXXXX",
            "XP      X          X       X",
            "  XXXXX X XXXXXXXX X XXXXX  ",
            "X            XX            X",
            "X XXXX XXXXX XX XXXXX XXXX X",
            "X X    XXXXX XX XXXXX    X X",
            "X X XXG  XXX    XXX  GXX X X",
            "X X XXXX XXXXXXXXXX XXXX X X",
            "X      X X        X X      X",
            "XXXXXX X X XXXXXX X X XXXXXX",
            "X            XX            X",
            "X XXX XXXXXX XX XXXXXX XXX X",
            "XG  X        XX        X  GX",
            "XXX XXXX XXXXXXXXXX XXXX XXX",
            "XXX X    XXXXXXXXXX    X XXX",
            "XXX X XX            XX X XXX",
            "XXX X XX XXXXXXXXXX XX X XXX",
            "             XX             ",
            "XXXXX XXXX XXXXXX XXXXXXXXXX",
            "XG    XXX   XXXX   XXX    GX",
            "X XXX XXX X XXXX X XXX XXX X",
            "X         X      X         X",
            "XXXXXXXXXXXXXXXXXXXXXXXXXX X",
        ]
        if x == 1: self.ascii_maze = self.ascii_maze1
        elif x == 2: self.ascii_maze = self.ascii_maze2
        elif x ==3 :self.ascii_maze = self.ascii_maze3
        self.numpy_maze = []
        self.reachable_spaces = []
        self.ghost_spawns = []
        self.ghost_colors = [
            "graphics/monster/pink1.png",
            "graphics/monster/pink2.png",
            "graphics/monster/red1.png",
            "graphics/monster/red2.png"
        ]
        self.size = (0, 0)
        self.convert_maze_to_numpy()
        self.p = Pathfinder(self.numpy_maze)

    def request_new_random_path(self, in_ghost: Ghost):
        random_space = random.choice(self.reachable_spaces)
        current_maze_coord = translate_screen_to_maze(in_ghost.get_position())

        path = self.p.get_path(current_maze_coord[1], current_maze_coord[0], random_space[1],
                               random_space[0])
        test_path = [translate_maze_to_screen(item) for item in path]
        in_ghost.set_new_path(test_path)

    def convert_maze_to_numpy(self):
        for x, row in enumerate(self.ascii_maze):
            self.size = (len(row), x + 1)
            binary_row = []
            for y, column in enumerate(row):
                if column == "G":
                    self.ghost_spawns.append((y, x))

                if column == "X":
                    binary_row.append(0)
                else:
                    binary_row.append(1)
                    self.reachable_spaces.append((y, x))

            self.numpy_maze.append(binary_row)
