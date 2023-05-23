import pygame   # mengimpor modul pygame ( lib penyedia pengelolaan grafik ,sound, dll untuk pembuatan apliaksi dan game)
import numpy as np # mengimpor modul numpy dan memberikan aliasnya sebagai np #  lib yang menyediakan struktur data
import tcod # impor untuk modul tcod (lib untuk model  roguelike)
import random # mengimpor modul random yang menyediakan fungsi-fungsi untuk menghasilkan nomor acak dalam Python
from enum import Enum # mengimpor class Enum(lib untuk jenis enumerasi) dari modul enum

class Direction(Enum): # membuat arah  dari class direction dengan nilai tertentu
    DOWN = -90
    RIGHT = 0
    UP = 90
    LEFT = 180
    NONE = 360

def translate_screen_to_maze(in_coords, in_size=32): # mengubah koordinat layar menjadi koordinat di dalam labirin 
    return int(in_coords[0] / in_size), int(in_coords[1] / in_size)

def translate_maze_to_screen(in_coords, in_size=32): # mengubah koordinat dalam labirin menjadi koordinat layar
    return in_coords[0] * in_size, in_coords[1] * in_size

class GameObject: # membuat objek permainan dengan atribut-atribut seperti ukuran, warna, dan bentuk objek.
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

class Wall(GameObject): # membuat objek dinding dalam permainan 
    def __init__(self, in_surface, x, y, in_size: int, in_color=(183,176,156)): 
        super().__init__(in_surface, x * in_size, y * in_size, in_size, in_color) # panggil konstruktor Gameobject dengan super() lalu set ukuran dan set warna wall

class FinishLine(GameObject): # membuat garis finish game
    def __init__(self, in_surface, x, y, in_size: int, in_color=(0, 255, 0)):
        super().__init__(in_surface, x * in_size, y * in_size, in_size, in_color) # panggil konstruktor GameObject dengan super() lalu setting ukuran garis finis dan warnanya

class GameRenderer: # menginisialisasi py game dengan beberapa argumen
    def __init__(self, in_width: int, in_height: int, lives: int): # Konstruktor yg menerima 3 parameter in_width (lebar layar game), in_height (tinggi layar game), dan lives (jumlah nyawa char)
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


    def tick(self, in_fps: int): # menggerakkan permainan dengan kecepatan frame per detik (fps)
        black = (59, 69, 43)

        #self.handle_mode_switch()
        pygame.time.set_timer(self._pakupaku_event, 200) # open close mouth
        while not self._done:
            for game_object in self._game_objects:
                game_object.tick()
                game_object.draw() # setiap objek permainan akan digambar

            self.display_text(f"[Lives: {self._lives}]") # menampilkan nyawa char

            if self._hero is None: 
                self._done = True
            if self.get_won(): 
                self._done = True
            pygame.display.flip() # melakukan refresh screen
            self._clock.tick(in_fps) # mengatur waktu game
            self._screen.fill(black) # mewarnai screen dengan warna hitam
            self._handle_events() # menangani input yang diberikan dari player

    def add_game_object(self, obj: GameObject): # menambahkan objek permainan ke dalam daftar self._game_objects
        self._game_objects.append(obj)

    def add_ghost(self, obj: GameObject): # menambahkan objek hantu ke dalam daftar self._game_objects dan self._ghosts
        self._game_objects.append(obj)
        self._ghosts.append(obj)

    def set_won(self): # menandai bahwa pemain telah memenangkan permainan dengan mengatur nilai atribut self._won menjadi True
        self._won = True

    def get_won(self): # menentukan apakah permainan telah dimenangkan atau belum
        return self._won

    def get_hero_position(self):
        return self._hero.get_position() if self._hero != None else (0, 0) # mendapatkan posisi char dalam bentuk koordinat (x, y) jika char ada. Jika char tidak ada, akan dikembalikan koordinat (0, 0)

    def end_game(self): # mengakhiri permainan. Jika char (_hero) ada dalam daftar _game_objects, maka char tersebut dihapus dari daftar. Kemudian, variabel _hero diatur menjadi None
        if self._hero in self._game_objects:
            self._game_objects.remove(self._hero)
        self._hero = None

    def kill_pacman(self): # kill char dengan memanggil metode end_game()
        self.end_game()

    def display_text(self, text, in_position=(32, 0), in_size=30): # menampilkan teks pada layar permainan
        font = pygame.font.SysFont('Arial', in_size) # dirender menggunakan font Arial dengan bantuan modul pygame.font dan kemudian ditampilkan pada layar menggunakan self._screen.blit()
        text_surface = font.render(text, False, (255, 255, 255))
        self._screen.blit(text_surface, in_position) # ditampilkan di screen

    def add_wall(self, obj: Wall): # menambahkan objek Wall ke dalam permainan
        self.add_game_object(obj)
        self._walls.append(obj)

    def get_walls(self): # mendapatkan daftar objek Wall yang ada dalam permainan 
        return self._walls

    def get_ghosts(self): # mendapatkan daftar objek hantu (Ghost) yang ada dalam permainan
        return self._ghosts

    def get_game_objects(self): # mendapatkan daftar semua objek permainan
        return self._game_objects

    def add_hero(self, in_hero): # menambahkan objek char (Hero) ke dalam permainan
        self.add_game_object(in_hero)
        self._hero = in_hero

    def add_finish_line(self, obj: FinishLine): # menambahkan objek garis finish (FinishLine) ke dalam permainan
        self.add_game_object(obj)
        self._finish_line = obj

    def _handle_events(self): # menangani event yang terjadi dalam permainan
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # permainan akan dihentikan dengan memanggil pygame.quit() dan exit()
                pygame.quit()
                exit()

        pressed = pygame.key.get_pressed() # memeriksa tombol yang ditekan oleh player menggunakan pygame.key.get_pressed(). Jika objek pahlawan (_hero) tidak ada, maka pemrosesan tombol dihentikan
        if self._hero is None: return
        if pressed[pygame.K_UP]: # Jika tombol atas (pygame.K_UP) ditekan, arah char diatur menjadi Direction.UP
            self._hero.set_direction(Direction.UP)
        elif pressed[pygame.K_LEFT]: # Jika tombol kiri (pygame.K_LEFT) ditekan, arah char diatur menjadi Direction.LEFT
            self._hero.set_direction(Direction.LEFT)
        elif pressed[pygame.K_DOWN]: #  Jika tombol bawah (pygame.K_DOWN) ditekan, arah char diatur menjadi Direction.DOWN
            self._hero.set_direction(Direction.DOWN)
        elif pressed[pygame.K_RIGHT]: #  Jika tombol kanan (pygame.K_RIGHT) ditekan, arah char diatur menjadi Direction.RIGHT
            self._hero.set_direction(Direction.RIGHT)

class MovableObject(GameObject): # mewakili objek yang dapat bergerak dalam permainan
    def __init__(self, in_surface, x, y, in_size: int, in_color=(255, 0, 0), is_circle: bool = False):
        super().__init__(in_surface, x, y, in_size, in_color, is_circle)
        self.current_direction = Direction.NONE
        self.direction_buffer = Direction.NONE
        self.last_working_direction = Direction.NONE
        self.location_queue = []
        self.next_target = None
        self.image = pygame.image.load('graphics/monster/blue1.png')

    def get_next_location(self): # mendapatkan lokasi berikutnya dari objek yang dapat bergerak
        return None if len(self.location_queue) == 0 else self.location_queue.pop(0) # mengembalikan None jika location_queue kosong atau menghapus dan mengembalikan elemen pertama dari location_queue jika tidak kosong

    def set_direction(self, in_direction): # mengatur arah saat ini dan buffer arah dari objek yang dapat bergerak
        self.current_direction = in_direction # menerima argumen in_direction yang merupakan arah yang ingin diatur
        self.direction_buffer = in_direction

    def collides_with_wall(self, in_position): # memeriksa apakah objek yang dapat bergerak bertabrakan dengan dinding
        collision_rect = pygame.Rect(in_position[0], in_position[1], self._size, self._size) # memeriksa tabrakan dengan menggunakan metode colliderect() dari objek pygame.Rect untuk memeriksa tabrakan antara collision_rect dan bentuk dinding
        collides = False # mengembalikan nilai True jika terjadi tabrakan dengan dinding, dan False jika tidak terjadi tabrakan
        walls = self._renderer.get_walls()
        for wall in walls:
            collides = collision_rect.colliderect(wall.get_shape())
            if collides: break
        return collides

    def check_collision_in_direction(self, in_direction: Direction): # memeriksa tabrakan dalam suatu arah tertentu
        # menerima argumen in_direction yang merupakan arah yang ingin diperiksa. 
        desired_position = (0, 0)
        if in_direction == Direction.NONE: return False, desired_position # memeriksa apakah terjadi tabrakan dengan dinding dalam posisi yang diinginkan
        if in_direction == Direction.UP:
            desired_position = (self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            desired_position = (self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            desired_position = (self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            desired_position = (self.x + 1, self.y)

        return self.collides_with_wall(desired_position), desired_position # mengembalikan tuple yang terdiri dari nilai True jika terjadi tabrakan, dan desired_position yang merupakan posisi yang diinginkan

    def automatic_move(self, in_direction: Direction): # menggerakkan objek yang dapat bergerak secara otomatis
        pass

    def tick(self): #  mengatur tindakan yang dilakukan pada setiap iterasi permainan. Metode ini memanggil reached_target() dan automatic_move(self
        self.reached_target()
        self.automatic_move(self.current_direction)

    def reached_target(self): #  reached_target() digunakan untuk menangani saat objek mencapai target tertentu
        pass
    
    def draw(self): # menggambar objek pada layar permainan. Pertama, gambar objek diubah ukurannya menggunakan pygame.transform.scale(self.image, (32, 32)) agar sesuai dengan ukuran yang diinginkan
        self.image = pygame.transform.scale(self.image, (32, 32))
        self._surface.blit(self.image, self.get_shape()) # gambar tersebut ditampilkan pada permukaan objek menggunakan self._surface.blit(self.image, self.get_shape())

class Hero(MovableObject): # merupakan konstruktor untuk objek Hero
    def __init__(self, in_surface, x, y, in_size: int,):
        super().__init__(in_surface, x, y, in_size, (255, 255, 0), False) # melakukan inisialisasi objek dengan parameter yang diberikan
        self.last_non_colliding_position = (0, 0)
        self.open = pygame.image.load("graphics/hero/hero_intro.png")
        self.image = self.open
        self.mouth_open = True

    def tick(self): # mengatur tindakan yang dilakukan pada setiap iterasi permainan oleh objek Hero
        # TELEPORT
        if self.x < 0:
            self.x = self._renderer._width

        if self.x > self._renderer._width:
            self.x = 0

        self.last_non_colliding_position = self.get_position() # diatur sebagai posisi saat ini menggunakan self.get_position()

        if self.check_collision_in_direction(self.direction_buffer)[0]:
            self.automatic_move(self.current_direction) # menggerakkan objek sesuai dengan arah saat ini (current_direction)
        else: # Jika tidak terjadi tabrakan, automatic_move(self.direction_buffer) dipanggil untuk menggerakkan objek sesuai dengan arah yang diinginkan (direction_buffer), dan current_direction diatur sama dengan direction_buffer
            self.automatic_move(self.direction_buffer)
            self.current_direction = self.direction_buffer

        if self.collides_with_wall((self.x, self.y)):
            self.set_position(self.last_non_colliding_position[0], self.last_non_colliding_position[1])

        if self._renderer._finish_line is not None and self.collides_with_finish_line():
            self._renderer.set_won()

        self.handle_ghosts()

    def automatic_move(self, in_direction: Direction): # menggerakkan objek Hero secara otomatis dalam arah yang ditentukan
        collision_result = self.check_collision_in_direction(in_direction) # diinisialisasi dengan hasil dari pemanggilan check_collision_in_direction(in_direction)

        desired_position_collides = collision_result[0] # desired_position_collides diambil dari indeks 0 dari collision_result, yang menunjukkan apakah terjadi tabrakan dengan dinding dalam posisi yang diinginkan
        if not desired_position_collides:
            self.last_working_direction = self.current_direction
            desired_position = collision_result[1]
            self.set_position(desired_position[0], desired_position[1]) #  Jika tidak terjadi tabrakan, last_working_direction diatur sama dengan current_direction. desired_position diambil dari indeks 1 dari collision_result, yang merupakan posisi yang diinginkan
        else:
            self.current_direction = self.last_working_direction # Jika terjadi tabrakan, current_direction diatur sama dengan last_working_direction

    def handle_ghosts(self): # menangani tabrakan antara objek Hero dengan objek hantu (ghosts)
        collision_rect = pygame.Rect(self.x, self.y, self._size, self._size)
        ghosts = self._renderer.get_ghosts() #  objek-objek hantu (ghosts) diambil dari renderer 
        game_objects = self._renderer.get_game_objects()
        for ghost in ghosts:
            collides = collision_rect.colliderect(ghost.get_shape()) # untuk memeriksa tabrakan
            if collides and ghost in game_objects:
                self._renderer.kill_pacman()

    def collides_with_finish_line(self): # memeriksa tabrakan antara objek Hero dengan garis finish (_finish_line)
        collision_rect = pygame.Rect(self.x, self.y, self._size, self._size)
        return collision_rect.colliderect(self._renderer._finish_line.get_shape()) # memeriksa tabrakan


    def draw(self): # menggambar objek Hero pada permukaan (surface) dengan menggunakan gambar yang telah ditentukan (self.open)
        half_size = self._size / 2
        self.image = self.open
        super(Hero, self).draw()

class Ghost(MovableObject):
    def __init__(self, in_surface, x, y, in_size: int, in_game_controller, sprite_path="graphics/monster/blue2.blue2.png"): # konstruktor untuk objek Ghost
        super().__init__(in_surface, x, y, in_size)
        self.game_controller = in_game_controller
        self.sprite_normal = pygame.image.load(sprite_path)

    def reached_target(self): # menentukan tindakan yang dilakukan saat objek Ghost mencapai target
        if (self.x, self.y) == self.next_target:
            self.next_target = self.get_next_location()
        self.current_direction = self.calculate_direction_to_next_target()

    def set_new_path(self, in_path): # mengatur jalur baru (in_path) untuk objek Ghost
        for item in in_path:
            self.location_queue.append(item)
        self.next_target = self.get_next_location() # Jalur baru ditambahkan ke dalam location_queue, dan next_target diperbarui dengan memanggil self.get_next_location()

    def calculate_direction_to_next_target(self) -> Direction:# menghitung arah yang harus diambil oleh objek Ghost menuju target berikutnya
        if self.next_target is None:
            self.request_path_to_player(self) # meminta jalur menuju pemain kepada pengontrol permainan (game_controller)
            return Direction.NONE
        diff_x = self.next_target[0] - self.x
        diff_y = self.next_target[1] - self.y
        if diff_x == 0:
            return Direction.DOWN if diff_y > 0 else Direction.UP
        if diff_y == 0:
            return Direction.LEFT if diff_x < 0 else Direction.RIGHT

        self.game_controller.request_new_random_path(self) # pengontrol permainan
        return Direction.NONE

    def request_path_to_player(self, in_ghost): # meminta jalur menuju pemain kepada pengontrol permainan (game_controller)
        player_position = translate_screen_to_maze(in_ghost._renderer.get_hero_position())
        current_maze_coord = translate_screen_to_maze(in_ghost.get_position())
        path = self.game_controller.p.get_path(current_maze_coord[1], current_maze_coord[0], player_position[1],
                                               player_position[0])

        new_path = [translate_maze_to_screen(item) for item in path]
        in_ghost.set_new_path(new_path) # jalur baru

    def automatic_move(self, in_direction: Direction): # menggerakkan objek Ghost secara otomatis berdasarkan arah yang diberikan
        if in_direction == Direction.UP:
            self.set_position(self.x, self.y - 1)
        elif in_direction == Direction.DOWN:
            self.set_position(self.x, self.y + 1)
        elif in_direction == Direction.LEFT:
            self.set_position(self.x - 1, self.y)
        elif in_direction == Direction.RIGHT:
            self.set_position(self.x + 1, self.y)
    def draw(self): #  menggambar objek Ghost pada permukaan (surface) dengan menggunakan gambar normal (sprite_normal)
        self.image = self.sprite_normal # berisi gambar untuk objek Ghost
        super(Ghost, self).draw()

class Pathfinder: # konstruktor untuk objek Pathfinder. Pada konstruktor ini, dilakukan inisialisasi jalur dengan membangun objek tcod.path.AStar menggunakan cost yang diberikan
    def __init__(self, in_arr):
        cost = np.array(in_arr, dtype=np.bool_).tolist() # Nilai cost diubah menjadi tipe data np.array dan kemudian diubah menjadi daftar
        self.pf = tcod.path.AStar(cost=cost, diagonal=0) # A* untuk mencari jalur

    def get_path(self, from_x, from_y, to_x, to_y) -> object: # mendapatkan jalur dari titik awal (from_x, from_y) ke titik tujuan (to_x, to_y)
        res = self.pf.get_path(from_x, from_y, to_x, to_y) # dipanggil dengan parameter yang diberikan
        return [(sub[1], sub[0]) for sub in res]# . Hasil yang diperoleh kemudian diubah ke dalam format yang diharapkan, yaitu pasangan koordinat dalam bentuk (sub[1], sub[0]), dan kemudian dikembalikan sebagai objek jalur

class PacmanGameController: # class yang berisi representasi labirin dalam bentuk string yang menggunakan karakter ASCII.
    def __init__(self, x ): # digunakan untuk membangun labirin dalam permainan, dengan menggambar char ASCII tsb pada surface permainan.
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
        self.numpy_maze = [] #  menyimpan labirin dalam bentuk numpy array 
        self.reachable_spaces = [] # menyimpan daftar koordinat yang dapat dicapai di labirin. 
        self.ghost_spawns = [] # menyimpan posisi awal ghost dalam labirin. 
        self.ghost_colors = [ #  berisi jalur file gambar untuk warna hantu.
            "graphics/monster/pink1.png",
            "graphics/monster/pink2.png",
            "graphics/monster/red1.png",
            "graphics/monster/red2.png"
        ]
        self.size = (0, 0) # menyimpan ukuran labirin dalam bentuk tupel (lebar, tinggi).
        self.convert_maze_to_numpy()
        self.p = Pathfinder(self.numpy_maze)

    def request_new_random_path(self, in_ghost: Ghost): # meminta jalur acak baru bagi objek Ghost
        random_space = random.choice(self.reachable_spaces) # Mengambil secara acak sebuah titik yang dapat dicapai dari daftar reachable_spaces
        current_maze_coord = translate_screen_to_maze(in_ghost.get_position()) # Mengambil posisi saat ini dari objek Ghost dengan menggunakan metode get_position(). Kemudian, mengubah posisi tersebut dari koordinat layar menjadi koordinat labirin menggunakan fungsi translate_screen_to_maze()
# Menghitung jalur terpendek antara current_maze_coord (posisi saat ini) dan random_space (titik acak yang dapat dicapai) menggunakan objek Pathfinder yang disimpan dalam atribut p
        path = self.p.get_path(current_maze_coord[1], current_maze_coord[0], random_space[1],
                               random_space[0])# Jalur yang dihasilkan disimpan dalam test_path.
        test_path = [translate_maze_to_screen(item) for item in path]# Mengubah jalur yang ditemukan dalam koordinat labirin menjadi koordinat layar menggunakan fungsi translate_maze_to_screen() untuk setiap elemen dalam daftar jalur. 
        in_ghost.set_new_path(test_path) # Memanggil metode set_new_path() pada objek Ghost dengan test_path sebagai argumennya. Metode ini mengatur jalur baru untuk objek Ghost

    def convert_maze_to_numpy(self):#  untuk mengonversi labirin dalam bentuk ASCII menjadi numpy array.
        for x, row in enumerate(self.ascii_maze): # Melakukan iterasi pada setiap baris dalam ascii_maze, sambil melacak indeks baris dengan variabel x
            self.size = (len(row), x + 1) # Mengatur atribut size menjadi lebar dan tinggi labirin, dengan menggunakan panjang baris saat ini dan nilai x sebagai indeks terakhir baris.
            binary_row = [] # Membuat sebuah daftar kosong binary_row untuk menyimpan nilai biner setiap kolom dalam baris.
            for y, column in enumerate(row): # Melakukan iterasi pada setiap kolom dalam baris, sambil melacak indeks kolom dengan variabel y.
                if column == "G": #  menyimpan posisi awal hantu dalam labirin.
                    self.ghost_spawns.append((y, x))

                if column == "X": #  Jika kolom saat ini adalah "X" (menandakan dinding), nilai 0 ditambahkan ke dalam binary_row.
                    binary_row.append(0)
                else:
                    binary_row.append(1) #  Jika kolom saat ini bukan "X" (menandakan area yang dapat dicapai), nilai 1 ditambahkan ke dalam binary_row. 
                    self.reachable_spaces.append((y, x))

            self.numpy_maze.append(binary_row)# Menambahkan binary_row ke dalam numpy_maze, sehingga membentuk representasi labirin dalam bentuk numpy array.
