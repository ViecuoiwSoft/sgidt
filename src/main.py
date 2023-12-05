from display import *

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Car")
    track = Track(None, 40.)
    track.generate_preset_1()
    player = Car()
    player.set(track)
    player.reset()
    process1 = Process(player, screen)
    end = False
    clock = pygame.time.Clock()
    f = 60.
    while not end:
        end = process1.update(f)
        screen.fill("white")
        process1.draw_track(track)
        process1.draw_car()
        pygame.display.flip()
        clock.tick(f)
    pygame.quit()
