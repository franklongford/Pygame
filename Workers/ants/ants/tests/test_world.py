from unittest import TestCase

import pygame as pg

from ants.world import World


class TestWorld(TestCase):

    def setUp(self):
        self.world = World(
            100, diffusion_rate=0.4, decay_rate=0.01)

    def test_init(self):
        self.assertEqual(10, self.world.n_resources)
        self.assertEqual(1, self.world.n_hives)
        self.assertEqual(10, self.world.n_workers)
        self.assertEqual((100, 100), self.world.scent_map.shape)

    def test_assess_collisions(self):
        #self.world.assess_collisions()

        self.assertEqual(10, self.world.n_workers)
        self.world.spawn_resource(
            (2, 2), 10
        )
        self.assertEqual(11, self.world.n_resources)
        self.world.assess_collisions()

    def test_update(self):
        # Given
        self.world.scent_map[20, 20] = 5
        self.world.update()

        self.assertAlmostEqual(
            4.182559803, self.world.scent_map[20, 20])

        self.world.diffusion_rate = 0
        self.world.update()

        self.assertAlmostEqual(
            4.140734205, self.world.scent_map[20, 20])

        self.world.decay_rate = 0
        self.world.update()

        self.assertAlmostEqual(
            4.140734205, self.world.scent_map[20, 20])

    def _test_visual(self):
        world = World(200, scale=4, n_hives=1, diffusion_rate=0.35)

        pg.init()
        screen_size = world.scaled_rect.size
        main_surface = pg.display.set_mode(screen_size)

        running = True
        play = True
        while running:

            if play:
                world.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        play = not play

            world.draw(main_surface)

            pg.display.update()
