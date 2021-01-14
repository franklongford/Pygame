import numpy as np

from skimage.transform import rescale

from .colors import (
    GRASS, VERY_LIGHT_SCENT, LIGHT_SCENT, MID_SCENT,
    HEAVY_SCENT, VERY_HEAVY_SCENT)


def random_number(low=-1.0, high=1.0):
    range = high - low
    return (np.random.rand() - 0.5) * range


def mutate(parameter, threshold_p=0.2, size=0.1):
    will_mutate = np.random.rand() <= threshold_p

    if will_mutate:
        size *= parameter / 2
        if isinstance(parameter, float):
            parameter += random_number(low=-size, high=size)
        elif isinstance(parameter, int):
            size = int(size)
            parameter += int(random_number(low=-size, high=size))
    return parameter

def create_background(scent_map, scale=1):

    transpose = scent_map
    rgb_map = np.zeros(scent_map.shape + (3,))

    def get_mask(array, lower, upper):
        return np.where((lower < array) * (array <= upper))

    rgb_map[np.where(transpose <= 1E-2)] = GRASS
    rgb_map[get_mask(transpose, 1E-2, 1.0)] = VERY_LIGHT_SCENT
    rgb_map[get_mask(transpose, 1.0, 2.0)] = LIGHT_SCENT
    rgb_map[get_mask(transpose, 2.0, 5.0)] = MID_SCENT
    rgb_map[get_mask(transpose, 5.0, 15.0)] = HEAVY_SCENT
    rgb_map[np.where(transpose > 15.0)] = VERY_HEAVY_SCENT

    return rescale(rgb_map, scale, multichannel=True)
