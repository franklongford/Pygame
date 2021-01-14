from unittest import TestCase

from ants.agent import Agent


class TestAgent(TestCase):

    def setUp(self):
        self.screen_size = (100, 100)
        self.agent = Agent((1, 2))

    def test_init(self):
        self.assertEqual((1, 2, 1, 1), self.agent.rect)
        self.assertEqual((1, 2, 1, 1), self.agent.scaled_rect)
        self.assertIsNone(self.agent.screen_size)

    def test_scale(self):
        self.agent.scale = 2

        self.assertEqual((1, 2, 1, 1), self.agent.rect)
        self.assertEqual((2, 4, 2, 2), self.agent.scaled_rect)

    def test_screen_size(self):
        agent = Agent((1, 2),
                      screen_size=self.screen_size)
        self.assertEqual((100, 100), agent.screen_size)

