import os
import pygame

from data.gfx.paths.sprite_paths import *


def get_frame(sheet, width, height, pos, is_color_key=True):
    image = pygame.Surface((width, height)).convert_alpha()
    image.blit(sheet, (0, 0), (pos[0] * width, pos[1] * height, width, height))
    if is_color_key:
        color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def imgload(dir, file, convert=2, colorkey=None):
    img = pygame.image.load(os.path.join(dir, file))

    if convert == 1:
        img = img.convert()
    elif convert == 2:
        img = img.convert_alpha()

    if colorkey is not None:
        img.set_colorkey(colorkey)
    return img


# load all sprites
def loadSprites():
    Player_Sprite = {}
    for name in Player_Sprite_Path:
        Player_Sprite[name] = {
            "Idle": imgload(Player_Sprite_Path[name]["Sprite"], Player_Sprite_Path[name]["Idle"]),
            "Attack": imgload(Player_Sprite_Path[name]["Sprite"], Player_Sprite_Path[name]["Attack"]),
            "Take Hit": imgload(Player_Sprite_Path[name]["Sprite"], Player_Sprite_Path[name]["Take Hit"]),
            "Cast": imgload(Player_Sprite_Path[name]["Sprite"], Player_Sprite_Path[name]["Cast"]),
            "Die": imgload(Player_Sprite_Path[name]["Sprite"], Player_Sprite_Path[name]["Die"])
        }

    Monster_Sprite = {}
    for name in Monster_Sprite_Path:
        Monster_Sprite[name] = {
            "Idle": imgload(Monster_Sprite_Path[name]["Sprite"], Monster_Sprite_Path[name]["Idle"]),
            "Attack": imgload(Monster_Sprite_Path[name]["Sprite"], Monster_Sprite_Path[name]["Attack"]),
            "Take Hit": imgload(Monster_Sprite_Path[name]["Sprite"], Monster_Sprite_Path[name]["Take Hit"]),
            "Die": imgload(Monster_Sprite_Path[name]["Sprite"], Monster_Sprite_Path[name]["Die"])
        }

    Skill_Sprite = {}
    for name in Skill_Sprite_Path:
        Skill_Sprite[name] = {
            "Sprite": imgload(Skill_Sprite_Path[name]["Sprite"], Skill_Sprite_Path[name]["Path"]),
            "Size": Skill_Sprite_Path[name]["Size"]
        }

    return Player_Sprite, Monster_Sprite, Skill_Sprite

