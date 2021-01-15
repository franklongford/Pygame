import os

import numpy as np
import pygame
from pygame import SYSTEM_CURSOR_ARROW, SYSTEM_CURSOR_HAND

from .world import World
from .colors import WHITE, BLACK


def run_game(world, gnum, param, speed=1, visual=False):

    FPS = 30
    time = 0
    total_resource = world.resources_left
    print("Running Game {}\nVisual = {} Total Resources = {}".format(gnum, visual, total_resource))
    print("PARAMETERS USED:\nCarry = {:.2f}  "
          "Scent = {:.2f}  Stamina = {:.2f}   "
          "P(turn) = {:.2f}\n".format(param[0], param[1], param[2], param[3])
          )

    if visual:
        pygame.init()

        screen_size = world.scaled_rect.size
        screen_size = (screen_size[0], screen_size[1] + int(20 * world.scale))
        main_surface = pygame.display.set_mode(screen_size)

        basicfont = pygame.font.SysFont(None, 12 * world.scale)
        clock = pygame.time.Clock()

    running = True
    build_hive = False
    resource_left = (world.resources_left / float(total_resource)) * 100.
    while running:

        world.update()

        if world.n_workers == 0:
            running = False

        resource_left = (world.resources_left / float(total_resource)) * 100.
        if len(world.resources) == 0 or resource_left <= 20:
            running = False

        if visual:

            main_surface.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        build_hive = True
                        pygame.mouse.set_system_cursor(SYSTEM_CURSOR_HAND)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if build_hive:
                        x_pos, y_pos = pygame.mouse.get_pos()
                        x_pos = int(x_pos / world.scale)
                        y_pos = int(y_pos / world.scale)
                        world.spawn_hive((x_pos, y_pos), param)
                        build_hive = False
                        pygame.mouse.set_system_cursor(SYSTEM_CURSOR_ARROW)

            if time % speed == 0:
                world.draw(main_surface)

            worker_text = basicfont.render(
                'No. Workers = {:5d}'.format(world.n_workers), True, BLACK, WHITE)
            main_surface.blit(
                worker_text, (10 * world.scale, world.screen_rect[3] * world.scale))

            res_text = basicfont.render(
                'Stored Food = {:.1f}  Res left = {:.1f} ({:.2f}%)'.format(
                    world.collected_food,
                    world.resources_left, resource_left), True, BLACK, WHITE)
            main_surface.blit(
                res_text, (10 * world.scale, (world.screen_rect[3] + 10) * world.scale))

            pygame.display.update()
            pygame.display.flip()

            clock.tick(FPS)

        if time % 500 == 0:
            print("Time = {}  Collected Food = {:.1f}  Res left = {:.1f} ({:.2f}%)  N workers = {}".format(
                time,
                world.collected_food,
                world.resources_left,
                resource_left,
                world.n_workers))

        if time == 5000:
            running = False

        time += 1

    return resource_left, time


def assess_game(world, res_left, n_game, time, param):

    """
    nbins = 30
    hist_carry = make_histogram(tot_carry, nbins, 0, "Carry Value")
    hist_scent = make_histogram(tot_scent, nbins, 1, "Scent Value")
    hist_prob = make_histogram(tot_prob, nbins, 2, "Prob of Turning")
    hist_stamina = make_histogram(tot_stamina, nbins, 3, "Stamina")
    """
    index = np.argmax([
        hive.n_workers for hive in world.hives
    ])
    winner = world.hives.sprites()[index]
    world.calculate_totals()

    av_carry = np.mean(world.tot_carry)
    av_scent = np.mean(world.tot_scent)
    av_stamina = int(np.mean(world.tot_stamina) + 0.5)
    av_P_turn = np.mean(world.tot_p_turn)
    tot_workers = len(winner.history['carry'])

    result = ("GAME {}  WINNER = HIVE {}\n".format(n_game, index) +
              "TOTALS:\nFood = {} ({:.2f}%)  Time = {}  \nTotal Workers = {}\n".format(
                  winner.collected_food, (100 - res_left), time, tot_workers) +
              "AVERAGES:\n Carry = {:.2f}  Scent = {:.2f}  Stamina = {:.2f}  P(turn) = {:.2f}\n".format(
                  av_carry, av_scent, av_stamina, av_P_turn))

    return result, tot_workers, (av_carry, av_scent, av_stamina, av_P_turn)


def main():
    visual = True
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    n_resources = 20
    res_spawn_rate = 0.1
    n_hives = 2
    L = 250
    ngames = 1
    n_maps = 1
    speed = 1
    scale = 3

    start_carry = 3
    start_scent = 1.0
    start_stamina = 400
    start_P_turn = 0.3
    av_tot_workers = 0

    try:
        param = np.loadtxt('Parameters.txt')
    except Exception:
        param = [start_carry, start_scent, start_stamina, start_P_turn]

    for n in range(ngames):
        tot_workers = []
        for m in range(n_maps):

            world = World(
                L, scale=scale, n_resources=n_resources, n_hives=n_hives,
                res_spawn_rate=res_spawn_rate, param=param
            )

            res_left, time = run_game(world, n, param, speed, visual)

            if world.n_hives > 0:
                result, new_tot_workers, param = assess_game(
                    world, res_left, n, time, param
                )

                print(result)

                tot_workers.append(new_tot_workers)

        if np.mean(new_tot_workers) > av_tot_workers:
            av_tot_workers = np.mean(new_tot_workers)
            av_carry = param[0]
            av_scent = param[1]
            av_stamina = param[2]
            av_P_turn = param[3]
            result = ("NEW PARAMETERS:\nCarry = {:.2f}  "
                      "Scent = {:.2f}  Stamina = {:.2f}  "
                      "P(turn) = {:.2f}\n".format(
                av_carry, av_scent, av_stamina, av_P_turn))
        else:
            result = "HIVE FAILED TO PRODUCE MORE WORKERS - OLD PARAMETERS RETAINED\n"

        print(result)

        np.savetxt('Parameters.txt', param)


if __name__ == "__main__":
    main()
