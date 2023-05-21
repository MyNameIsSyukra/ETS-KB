import pygame
from sys import exit
from game import *

# Init
pygame.init()
screen = pygame.display.set_mode((896, 736))
title = pygame.display.set_caption('Takeshi-Maze')
game_font = pygame.font.Font('font/Pixeltype.ttf', 56)
game_font_little = pygame.font.Font('font/Pixeltype.ttf', 40)
clock = pygame.time.Clock()

# Game & Level Flag
game_active = False
game_level = [False, False, False, False]
game_outro = False
game_won = False

# Intro
title_surf = game_font.render('Takeshi-Maze', False, '#212121')
title_rect = title_surf.get_rect(center = (448, 110))

player_intro_surf = pygame.image.load('graphics/hero/hero_intro.png').convert_alpha()
player_intro_rect = player_intro_surf.get_rect(center = (448,368))

cmnd_surf = game_font.render('Press Space to Start', False, '#212121')
cmnd_rect = cmnd_surf.get_rect(center = (448, 620))

# Level 0
sky_surf = pygame.image.load('graphics/sky.png').convert_alpha()
ground_surf = pygame.image.load('graphics/ground.png').convert_alpha()

player0_surf = pygame.image.load('graphics/hero/hero1.png')
player0_surf = pygame.transform.scale2x(player0_surf)
player0_rect = player0_surf.get_rect(midbottom = (80, 410))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if game_active:
            if game_level[0]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player0_rect.left > 910:
                    game_level[1] = True
                    game_level[0] = False
            elif game_level[1]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_won = False
                    game_level[2] = True
                    game_level[1] = False
            elif game_level[2]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_won = False
                    game_level[3] = True
                    game_level[2] = False
            elif game_level[3]:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_won = False
                    game_level[3] = False
                    player0_rect.x = -50
                    game_outro = True
            elif game_outro and player0_rect.left > 910:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_outro = False
                    game_active = False
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                game_level[0] = True
                player0_rect.left = 80
    
    if game_active:
        # Game running
        if game_level[0]:
            command_surf = game_font.render('Hold "->" to go!', False, '#212121')
            command_rect = command_surf.get_rect(center = (448, 110))
            
            screen.blit(sky_surf, (0,0))
            screen.blit(ground_surf, (0, 410))
            screen.blit(player0_surf, player0_rect)
            screen.blit(command_surf, command_rect)

            rigt_key = pygame.key.get_pressed()
            if rigt_key[pygame.K_RIGHT]:
                player0_rect.x += 5

            if player0_rect.left > 910:
                screen.fill('white')
                level_surf = game_font.render('Level  1', False, '#212121')
                level_rect = level_surf.get_rect(center = (448, 110))

                screen.blit(level_surf, level_rect)
                screen.blit(player_intro_surf, player_intro_rect)
                screen.blit(cmnd_surf, cmnd_rect)
        
        if game_level[1]:
            if game_won == False:
                unified_size = 32
                pacman_game = PacmanGameController(1)
                size = pacman_game.size
                game_renderer = GameRenderer(size[0] * unified_size, size[1] * unified_size)

                for y, row in enumerate(pacman_game.numpy_maze):
                    for x, column in enumerate(row):
                        if column == 0:
                            game_renderer.add_wall(Wall(game_renderer, x, y, unified_size))

                for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
                    translated = translate_maze_to_screen(ghost_spawn)
                    ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                                pacman_game.ghost_colors[i % 4])
                    game_renderer.add_ghost(ghost)
                
                finish_line = FinishLine(game_renderer, size[0] - 2, size[1] - 2, unified_size)
                game_renderer.add_finish_line(finish_line)

                pacman = Hero(game_renderer, unified_size, unified_size, unified_size)
                game_renderer.add_hero(pacman)
                game_renderer.tick(120)
                
                if game_renderer._won == True and game_renderer._lives > 0:
                    game_won = True

                if game_renderer._lives == 0:
                    game_level[1] = False
                    game_active = False
            
            else:
                screen.fill('white')
                level_surf = game_font.render('Level  2', False, '#212121')
                level_rect = level_surf.get_rect(center = (448, 110))

                screen.blit(level_surf, level_rect)
                screen.blit(player_intro_surf, player_intro_rect)
                screen.blit(cmnd_surf, cmnd_rect)
        
        if game_level[2]:
            if game_won == False:
                unified_size = 32
                pacman_game = PacmanGameController(2)
                size = pacman_game.size
                game_renderer = GameRenderer(size[0] * unified_size, size[1] * unified_size)

                for y, row in enumerate(pacman_game.numpy_maze):
                    for x, column in enumerate(row):
                        if column == 0:
                            game_renderer.add_wall(Wall(game_renderer, x, y, unified_size))

                for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
                    translated = translate_maze_to_screen(ghost_spawn)
                    ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                                pacman_game.ghost_colors[i % 4])
                    game_renderer.add_ghost(ghost)
                
                finish_line = FinishLine(game_renderer, size[0] - 2, size[1] - 2, unified_size)
                game_renderer.add_finish_line(finish_line)

                pacman = Hero(game_renderer, unified_size, unified_size, unified_size)
                game_renderer.add_hero(pacman)
                game_renderer.tick(120)
                
                if game_renderer._won == True and game_renderer._lives > 0:
                    game_won = True

                if game_renderer._lives == 0:
                    game_level[2] = False
                    game_active = False
            
            else:
                screen.fill('white')
                level_surf = game_font.render('Level  3', False, '#212121')
                level_rect = level_surf.get_rect(center = (448, 110))

                screen.blit(level_surf, level_rect)
                screen.blit(player_intro_surf, player_intro_rect)
                screen.blit(cmnd_surf, cmnd_rect)
            
        if game_level[3]:
            if game_won == False:
                unified_size = 32
                pacman_game = PacmanGameController(3)
                size = pacman_game.size
                game_renderer = GameRenderer(size[0] * unified_size, size[1] * unified_size)

                for y, row in enumerate(pacman_game.numpy_maze):
                    for x, column in enumerate(row):
                        if column == 0:
                            game_renderer.add_wall(Wall(game_renderer, x, y, unified_size))

                for i, ghost_spawn in enumerate(pacman_game.ghost_spawns):
                    translated = translate_maze_to_screen(ghost_spawn)
                    ghost = Ghost(game_renderer, translated[0], translated[1], unified_size, pacman_game,
                                pacman_game.ghost_colors[i % 4])
                    game_renderer.add_ghost(ghost)
                
                finish_line = FinishLine(game_renderer, size[0] - 2, size[1] - 2, unified_size)
                game_renderer.add_finish_line(finish_line)

                pacman = Hero(game_renderer, unified_size, unified_size, unified_size)
                game_renderer.add_hero(pacman)
                game_renderer.tick(120)
                
                if game_renderer._won == True and game_renderer._lives > 0:
                    game_won = True

                if game_renderer._lives == 0:
                    game_level[3] = False
                    game_active = False
            
            else:
                screen.fill('#212121')
                level_surf = game_font.render('CONGRATULATION!!!', False, '#ffffff')
                level_rect = level_surf.get_rect(center = (448, 363))

                screen.blit(level_surf, level_rect)
                screen.blit(cmnd_surf, cmnd_rect)

        if game_outro:
            outro_surf = game_font.render('Thank You', False, '#212121')
            outro_rect = outro_surf.get_rect(center = (448, 110))
            outro_cmd_surf = game_font.render('Press space to continue!', False, '#212121')
            outro_cmd_rect = outro_cmd_surf.get_rect(center = (448, 360))

            name1_surf = game_font_little.render('- Dewangga Dika Darmawan (5025211109)', False, '#fafafa')
            name1_rect = name1_surf.get_rect(midleft = (50, 550))
            name2_surf = game_font_little.render('- Syukra Wahyu Ramadhan (5025211037)', False, '#fafafa')
            name2_rect = name2_surf.get_rect(midleft = (50, 600))
            name3_surf = game_font_little.render('- Javier Nararya Aqsa Setiyono (5025211245)', False, '#fafafa')
            name3_rect = name3_surf.get_rect(midleft = (50, 650))

            screen.blit(sky_surf, (0,0))
            screen.blit(ground_surf, (0, 410))
            screen.blit(outro_surf, outro_rect)
            screen.blit(name1_surf, name1_rect)
            screen.blit(name2_surf, name2_rect)
            screen.blit(name3_surf, name3_rect)

            screen.blit(player0_surf, player0_rect)
            if player0_rect.left < 910:
                player0_rect.x += 5
            else:
                screen.blit(outro_cmd_surf, outro_cmd_rect)    
            
    else:
        # Main Menu
        screen.fill('#fafafa')
        screen.blit(title_surf, title_rect)
        screen.blit(player_intro_surf, player_intro_rect)
        screen.blit(cmnd_surf, cmnd_rect)
    
    pygame.display.update()
    clock.tick(60)