import math
import random

import pygame.display
pygame.display.init()

WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]  # 800, 600

# fortifications: f - fort, k - keep, c - city
# resources: @ - wood, # - stone, % - metal, & - gem
# camps: m - military, w - wood, s - stone, t - metal, g - gem
# other: v - stable/ '-' - unstable, e - entry
# Generates Region
#                                       N|W|E|S
def generateRegion(w=6, h=6, entrances=(3, 4, 1, 2)):
    arr = list()
    entrance_spots = ((entrances[0], 0), (0, entrances[1]), (w - 1, entrances[2]), (entrances[3], h - 1))
    stable_count = 1
    stable_spots = tuple()
    counter = 0
    while counter < stable_count:
        x = random.randrange(1, w - 1)
        y = random.randrange(1, h - 1)
        if (x, y) not in stable_spots:
            stable_spots += ((x, y),)
            counter += 1

    resource_count = 5
    resource_type = ('@', '#', '%', '&')
    resource_spots = tuple()
    counter = 0
    while counter < resource_count:
        x = random.randrange(0, w)
        y = random.randrange(0, h)
        if (x, y) not in stable_spots and (x, y) not in entrance_spots:
            resource_spots += ((x, y),)
            counter += 1

    for i in range(h):
        line = list()
        for j in range(w):
            # North entrance
            if i == 0 and j == entrances[0]:
                line.append('e')
            # West entrance
            elif i == entrances[1] and j == 0:
                line.append('e')
            # East entrance
            elif i == entrances[2] and j == w - 1:
                line.append('e')
            # South entrance
            elif i == h - 1 and j == entrances[3]:
                line.append('e')
            else:
                line.append('-')

        arr.append(line)

    for spot in stable_spots:
        arr[spot[1]][spot[0]] = 'v'
    for spot in resource_spots:
        arr[spot[1]][spot[0]] = random.choice(resource_type)

    return arr


def getDivisors(n, dmin=1, dmax=None):
    dmax = dmax or n
    result = list()
    for i in range(dmin, dmax + 1):
        if n % i == 0:
            result.append(i)
    return result

# Generates world map array
def generateMap(w=12, h=12, regions=9, region_names=('Eslavih', 'Tinquet', 'Lapier', 'Nowemet')):
    arr = list()
    if regions > w * h - 4:
        raise Exception("Too many areas for map")
    elif regions > len(region_names):
        raise Exception("Areas count need to match area names count!")
    else:
        for i in range(h):
            line = list()
            for j in range(w):
                line.append(str(regions))
            arr.append(line)
        # Total cells in the array and the fraction (cells in an area)
        t = w * h
        f = t / regions

        # Fraction must be a whole number
        if math.sqrt(f) != int(math.sqrt(f)) and f != int(f):
            print("divisors that you can use:")
            if len(getDivisors(t)) > 2:
                divisors = getDivisors(t)[1:-1]
            else:
                raise Exception("Can't create map, check your parameters")
            for i in range(len(divisors)):
                if w % divisors[i] == 0 and h % divisors[len(divisors) - i - 1] == 0:
                    print(divisors[i])
            raise Exception("You can't do that!\ndivisors: "+f"{getDivisors(t)[1:-1]}")
        else:
            d = int(f)  # Delta used to loop through cells in each area
            if math.sqrt(f) == int(math.sqrt(f)):
                # Steps used to loop through grid
                sx = math.ceil(math.sqrt(f))
                sy = int(f / sx)
            else:
                sx = math.ceil(w / regions)
                sy = int(f / sx)

        area_i = 0
        for i in range(0, h, sy):
            for j in range(0, w, sx):
                for k in range(d):
                    arr[i + k // sx][j + k % sx] = region_names[area_i]
                area_i += 1
    return arr


def createMap(width: int, height: int, regions: int, region_names: tuple):
    try:
        biome_names = (
            "Desert",
            "Forest",
            "Grassland",
            "Hills",
            "Lush",
            "Marsh",
            "Rocks",
            "Swamp"
        )

        world = generateMap(width, height, regions, region_names)
        world_region, world_region_info = list(), list()
        for i in range(len(world)):
            regions, info = list(), list()
            for j in range(len(world[0])):
                n, w, e, s = random.randint(1, 4), random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)

                if i == 0:
                    n = -1
                if i == len(world) - 1:
                    s = -1
                if j == 0:
                    w = -1
                if j == len(world[0]) - 1:
                    e = -1
                exits = (n, w, e, s)
                regions.append(generateRegion(entrances=exits))
                info.append({"Name": world[i][j], "Chaos": (i + 1) * (j + 1),
                             "Guardians": 0, "Biome": random.choice(biome_names)})
            world_region.append(regions)
            world_region_info.append(info)
        return world, world_region, world_region_info
    except Exception as e:
        print(e)
