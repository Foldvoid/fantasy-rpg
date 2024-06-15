import copy
from random import choice as chs
from random import randint as r_int

import pygame_gui
from pygame_gui.core import ObjectID
from data.gfx.paths.sprite_paths import *
from lib.render_tools import *

import source.mapgen as play_map
from source.environment import player

SCREEN_WIDTH, SCREEN_HEIGHT = play_map.WIDTH,  play_map.HEIGHT
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# top
TOP_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT / 25)
TOP_POS = (0, 0)
surface_top = pygame.Surface(TOP_SIZE)
# left
LEFT_SIZE = (SCREEN_WIDTH * 5 / 16, SCREEN_HEIGHT - TOP_SIZE[1])
LEFT_POS = (0, TOP_SIZE[1])
surface_left = pygame.Surface(LEFT_SIZE)
# right
RIGHT_SIZE = (SCREEN_WIDTH * 5 / 16, SCREEN_HEIGHT - TOP_SIZE[1])
RIGHT_POS = (TOP_SIZE[0] - LEFT_SIZE[0], TOP_SIZE[1])
surface_right = pygame.Surface(RIGHT_SIZE)
# bottom
BOTTOM_SIZE = (TOP_SIZE[0] - (LEFT_SIZE[0] + RIGHT_SIZE[0]), SCREEN_HEIGHT / 2)
BOTTOM_POS = (RIGHT_SIZE[0], SCREEN_HEIGHT - BOTTOM_SIZE[1])
surface_bottom = pygame.Surface(BOTTOM_SIZE)
# center
CENTER_SIZE = (SCREEN_WIDTH - (LEFT_SIZE[0] + RIGHT_SIZE[0]), SCREEN_HEIGHT - (TOP_SIZE[1] + BOTTOM_SIZE[1]))
CENTER_POS = (LEFT_SIZE[0], TOP_SIZE[1])
surface_center = pygame.Surface(CENTER_SIZE)

surface_bottom.fill(pygame.Color("#AA4466"))
surface_left.fill(pygame.Color("#7766AA"))
surface_right.fill(pygame.Color("#77AA76"))
surface_top.fill(pygame.Color("#4466AA"))
surface_center.fill(pygame.Color("#201976"))

# gui
rect_left = [
    pygame.Rect((LEFT_POS[0], LEFT_POS[1]), (LEFT_SIZE[0], 35)),  # player name
    pygame.Rect((LEFT_POS[0], LEFT_POS[1] + 42), (LEFT_SIZE[0] - 4, 35)),  # level
    pygame.Rect((LEFT_POS[0], LEFT_POS[1] + 42 * 2), (LEFT_SIZE[0] - 4, 35)),  # class
    pygame.Rect((LEFT_POS[0], LEFT_POS[1] + 42 * 3), (LEFT_SIZE[0] - 4, 35)),  # stats
    pygame.Rect((LEFT_POS[0], LEFT_POS[1] + 42 * 3), (LEFT_SIZE[0] - 4, 335)),  # stats text window
]

rect_right = [
    pygame.Rect((RIGHT_POS[0] + 2, RIGHT_POS[1] + 2), (RIGHT_SIZE[0] - 4, 35))  # zone name
]

surface_center_window = pygame.Surface((CENTER_SIZE[0] - 30, CENTER_SIZE[1] - 50))
surface_center_window.fill(pygame.Color("#123abc"))
center_rect = pygame.Rect((265, 140), (CENTER_SIZE[0] - 30, CENTER_SIZE[1] - 50))
center_label = [
    pygame.Rect((265, 140), (CENTER_SIZE[0] - 30, CENTER_SIZE[1] - 500)),
    pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1]), (LEFT_SIZE[0], 35)),  # player healthbar
    pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1] + 40), (LEFT_SIZE[0], 35)),  # player manaBar
    pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1] + 80), (LEFT_SIZE[0], 35)),  # player spiritBar

    pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1]), (LEFT_SIZE[0], 35)),  # monster healthbar
    pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1] + 40), (LEFT_SIZE[0], 35)),  # monster manaBar
    pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1] + 80), (LEFT_SIZE[0], 35)),  # monster spiritBar
]

# strong -(against)-> weak: Achlys -> Hephaestus  -> Gaia -> Αether -> Achlys (Key -> Value)
AstralSign = {"Achlys": "Hephaestus", "Αether": "Achlys", "Gaia": "Αether", "Hephaestus": "Gaia"}

# every value list has 4 parameters - offense, crit, defense, dodge | (1 = 10%)
BattleStance = {"Balanced": [0, 0, 0, 0], "Hit & Absorb": [2, 0, 2, 0], "Total Balance": [3, 3, 3, 3],
               "Offensive": [2, 1, -2, -1], "Assault": [2, 2, -2, -2], "Heavy Assault": [5, 5, -5, -5],
               "Defensive": [-1, -2, 2, 1], "Tower": [-3, -3, 3, 3], "Fortress": [-5, -5, 5, 5],
                "Critical": [1, 3, -3, -1], "Corner & Strike": [2, 5, -2, -5], "Into the fray": [5, 10, -10, -5]}

# Boost/Hinder status list of values - name, description, affects core stats, affects state, turns active
#       name: [description, core affect, state affect, wait turns]
Boost = {"Invigorate": ["Raises life points by 10 per level and adds 10% of that amount", "Life", "None", 3],
         "Second wind": ["Once out of stamina restores max stamina with 10% more", "Stamina", "None", -1],
         "Third eye": ["Increase Damage of all spells in the next 3 turns", "Arcana", "None", 3],
         "Belligerence": ["Increases your highest stat by 10% until battle ends", "Power", "None", -1],
         "Equilibrium": ["Adds 1 to all stance points until battle ends", "None", "Balanced", -1],
         "Gladiator code": ["Adds 4 in damage and 2 in crit and defence", "None", "Offensive", 3],
         "Last stand": ["In the next 2 turns: "
                        "Deal bonus damage that equals to your missing health and double that damage"
                        " every time you get hit.", "None", "Defensive", 2],
         "Impromptu": ["In the next 2 turns add 50% chance to crit", "None", "Critical", 2]}

Hinder = {"Discourage": ["Deduct life points by 10 per level and adds 10% of that amount", "Life", "None", 3],
          "Exhaustion": ["Once out of stamina lose 2 turns recovering", "Stamina", "None", 2],
          "Benightedness": ["Decreases Damage of all spells in the next 3 turns", "Arcana", "None", 3],
          "Pacifism": ["Decreases your highest stat by 10% until battle ends", "Power", "State affect", -1],
          "Imbalance": ["Decreases 1 to all stance points until battle ends", "None", "Balanced", -1],
          "Achilles heel": ["Deducts  4 in damage and 2 in crit and defence", "None", "Offensive", 3],
          "Meekness": ["In the next 2 turns: "
                        "Descrease damage that equals to your missing health and double that"
                        " every time you get hit.", "None", "Deffensive", 2],
          "Unprepared": ["In the next 2 turns subtract 50% chance to crit", "Core affect", "State affect", 2]}

# basic arts (physical/supernatural abilities) that can be used by any character
BattleArt = {
    "Warlord": {
        "Valiant slash": ["Damage ignores armour"],
        "Aura cleave": ["Damage ignores evasion"],
        "Astral shred": ["Damage using opponent's mana"],
        "Spectral Duel": ["Damage twice using phsycal and magical damage"],
        "Vanguard's stance": ["Adds health for 3 turns that later will be deducted"],
        "Ancestors Protection": ["Adds health for 3 turns that later will be deducted"],
    },
    "Sourcerer": {

    },
    "Hunter": {

    },
}

# In-game items
equip_path = './data/gfx/GUI/pics/equipment/v3/'
Equipment = {
    'Armour Of The Ancients': {
        'description': 'Used to belong to a legendary protector who was known for his '
                       'benevolence and courage and is remembered to this day as the demigod of the sun.',
        'value': 780060,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Armour Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 3]  # con, wis, fai, str, int, cun
    },
    'Blue Scale Armour': {
        'description': 'A ocean blue scaled armour made of hardened mana a symbol of clarity, '
                       'brings health and wisdom to the wearer as well as a little bit of hope.',
        'value': 216683,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Blue Scale Armour.png',
        'stats': [3, 3, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Chainmail': {
        'description': 'Chainmail armour but despite the common looks adds a great amount of constitution.',
        'value': 154773,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Chainmail.png',
        'stats': [4, 1, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Demon Armour': {
        'description': 'Although it is shunned upon nowadays, this artifact hold a great deal of historical '
                       'meaning in the practical summoning arts of the ancient Magus and brings power to the wearer',
        'value': 371457,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Demon Armour.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Leather Armour': {
        'description': "Imbued with all three of the empowering properties the Leather Armour "
                       "suits the interests of adventurers of all kinds and gives it's wearer the upper hand in battle",
        'value': 81256,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Leather Armour.png',
        'stats': [2, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plate Armour': {
        'description': 'The Plate Armour designed to increase the fortitude of the wearer '
                       'by a greater margin thus making it an empowering artifact piece unlike any other',
        'value': 154773,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Plate Armour.png',
        'stats': [4, 0, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plate Of Hardening': {
        'description': 'A piece that every mercenary can only dream of, a plate made of hardened '
                       'steel gives a great deal of fortitude, it\'s shine brings up the moral in the heat of battle',
        'value': 162512,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Plate Of Hardening.png',
        'stats': [4, 0, 2, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Robe Of Knowledge': {
        'description': 'Only a true battle mage knows the importance of his own competence in battle, '
                       'this battle robe not only does it give the needed fortitude to withstand an attack '
                       'but is imbued with the sacral knowledge of all the battle incantations a mage may forget.',
        'value': 154773,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Robe Of Knowledge.png',
        'stats': [1, 4, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Royal Plate Armour': {
        'description': 'When it comes to royal privilege, it always means quality above quantity, '
                       'and this plate armour says it all with the elegance and the generous amount of steel on it.',
        'value': 309547,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Royal Plate Armour.png',
        'stats': [4, 2, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Savior Robe': {
        'description': 'So you discovered that the rumors are true about the savior and his followers '
                       'they all forged a path to hold the human kind above all the chaos and last to lose it\'s hope.',
        'value': 1238189,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Savior Robe.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Scales Of Life': {
        'description': 'Just as the name of this artifact suggests it is the most durable armour of all and '
                       'grants the wearer the greatest amount of constitution to hold against the hardest of hits.',
        'value': 123818,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Scales Of Life.png',
        'stats': [5, 0, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Shadow Cloak': {
        'description': 'From the deps of the assassins guild comes the secret garnet that swallows the light '
                       'and with it the hope of the one on that opposes the guild.',
        'value': 183221,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Armours/Shadow Cloak.png',
        'stats': [1, 0, 4, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Axe Of Varyaga': {
        'description': 'Varyaga was a legendery warrior of the Northen tribes, known for their might, '
                       'the way they drink and how they fight Varyaga died a symbol of power to all people.',
        'value': 871717,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Axes/Axe Of Varyaga.png',
        'stats': [3, 0, 3, 3, 0, 3]  # con, wis, fai, str, int, cun
    },
    'Gael The Red': {
        'description': 'Nobody knows who he was and where he came from but the fear and pain he brought '
                       'Gael the red bandit knew that leaving anyone alive will bring more after him '
                       'and so wealding his axe, he worked alone and spared no one.',
        'value': 288712,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Axes/Gael The Red.png',
        'stats': [4, 1, 4, 4, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Bludgeoner': {
        'description': 'Increadably heavy and spiked with sharp edges not even the demon lord can recover '
                       'after a blow to the head with the Bludgeoner.',
        'value': 233312,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Axes/Bludgeoner.png',
        'stats': [0, 0, 2, 5, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Holy Spear Of The Ancient': {
        'description': 'Used to belong to a legendary protector who was known for his '
                       'benevolence and courage and is remembered to this day as the demigod of the sun.',
        'value': 33131,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Axes/Holy Spear Of The Ancient.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Alchemist Kit': {
        'description': 'The alchemists can concoct the most illustrious of potions but their talent lies '
                       'in the manipulation of natures laws and the materials this belt was made of is something '
                       'to behold.',
        'value': 53312,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Alchemist Kit.png',
        'stats': [2, 2, 2, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Belt Of Cold': {
        'description': 'A belt that was made of the fabric of Ymir and while it\'s cold embrace is not something '
                       'to be desired of the power of fortitude is still something anyone would want to get a hold of.',
        'value': 35541,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of Cold.png',
        'stats': [2, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Belt Of Knowledge': {
        'description': 'A belt that holds on to the knowledge of the ancients and gives away a strong aura of mana.',
        'value': 43415,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of Knowledge.png',
        'stats': [0, 3, 1, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Belt Of Power': {
        'description': 'A belt powerful enough to make any mortal surpass his physical bonds.',
        'value': 54151,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of Power.png',
        'stats': [2, 0, 1, 2, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Belt Of The Ancients': {
        'description': 'Belt made by the ancients imbued with their power made durable to stand the test of time.',
        'value': 51441,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 3]  # con, wis, fai, str, int, cun
    },
    'Belt Of The Believer': {
        'description': 'While strength and mind can be put to practice, so does faith and will, '
                       'this belt grants you an enigmatic feeling of salvation.',
        'value': 34155,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of The Believer.png',
        'stats': [2, 1, 2, 0, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Belt Of The Savior': {
        'description': 'Soaked in blood from all the enemies the guardians fought as well as the strength and courage '
                       'looks ragged hiding it\'s true power from the sight of evil',
        'value': 65731,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Belt Of The Savior.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Demon Belt': {
        'description': 'Practitioners of the occult did not sleep because of the frightening power surrounding them '
                       'as they summoned the beasts from the shadows, this belt was stolen by a demon.',
        'value': 65636,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Demon Belt.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Leather Belt': {
        'description': 'A belt that will give enough protection if equipped on, looks nothing special but arguably '
                       'can replace an armour in battle and will be much safer with it then without.',
        'value': 32436,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Leather Belt.png',
        'stats': [2, 1, 2, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Silver Belt': {
        'description': 'Mages who craved to find the tip of their magical powers used this belt to '
                       'unfold their potentials in battle or in their path to wisdom.',
        'value': 22124,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Silver Belt.png',
        'stats': [0, 2, 0, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'String Belt': {
        'description': 'More of an accessory then a belt but gives you more of each aspect of power '
                       'that might be useful to you in battle.',
        'value': 54761,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Belts/String Belt.png',
        'stats': [0, 0, 0, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Thorns': {
        'description': 'Like the stem of a rose it bites into your skin until it bleeds, '
                       'but it also boosts up your metabolism and feeds yor body with it\'s supernatural power.',
        'value': 47511,
        'equipped_on': 'Torso',
        'image_path': equip_path + 'Belts/Thorns.png',
        'stats': [2, 0, 0, 1, 1, 0]  # con, wis, fai, str, int, cun
    },
    'Blue Scale Boots': {
        'description': 'Made of the ocean purls shaved down like scales but durable against any type of damage.',
        'value': 7165,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Blue Scale Boots.png',
        'stats': [2, 2, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Boots Of Haste': {
        'description': 'If you are looking to gain the upper hand in battle and fast, look no more.',
        'value': 15765,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Boots Of Haste.png',
        'stats': [1, 1, 1, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Boots Of The Ancients': {
        'description': 'Engraved with the runes of protection speed and wisdom these boots can accompany '
                       'any adventurer in his travels for they have belonged to the ancient ones and protected them too',
        'value': 55361,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Boots Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 3]  # con, wis, fai, str, int, cun
    },
    'Demon Boots': {
        'description': 'Demonologists say that these are probably cursed, '
                       'but are yet to find the reason for that suspicion.',
        'value': 56155,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Demon Boots.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Greaves': {
        'description': 'Some of the incantations on those boots may come from some kind of'
                       ' late found religion in the south regions of the world but it\'s hard to tell nowadays',
        'value': 6155,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Greaves.png',
        'stats': [2, 2, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Hardening Boots': {
        'description': 'Boots forged by dwarves no other explanation can come to mind when you wear them.',
        'value': 8615,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Hardening Boots.png',
        'stats': [3, 0, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Leather Boots': {
        'description': 'Some say this leather can only be found in the north because of it\'s hardness, '
                       'but it\'s also good for keeping your feet protected',
        'value': 4674,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Leather Boots.png',
        'stats': [2, 0, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plated Boots': {
        'description': 'Can\'t find better steel than this one these are Freisorian steel boots!',
        'value': 6130,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Plated Boots.png',
        'stats': [3, 0, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Savior Boots': {
        'description': 'Grant the vigor of an ox, the wisdom of the moon and the courage of the lion.',
        'value': 63561,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Savior Boots.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Scale Boots': {
        'description': 'Scaled not by plate but by Wyvern\'s scales! they no harm can come to your feet with these on.',
        'value': 56513,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Scale Boots.png',
        'stats': [3, 3, 3, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Shadow Boots': {
        'description': 'The assassin guild made these for the best of their elite but can be worn only by a few chosen.',
        'value': 32543,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/Shadow Boots.png',
        'stats': [1, 0, 3, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'The Hermit': {
        'description': 'Belonged to a wise sage and a hermit of the six paths, '
                       'a long forgoten way of wisdom and solitude',
        'value': 50243,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Boots/The Hermit.png',
        'stats': [1, 3, 1, 0, 2, 1]  # con, wis, fai, str, int, cun
    },
    'Blue Scale Gloves': {
        'description': 'Made of the ocean purls shaved down like scales but durable against any type of damage.',
        'value': 24503,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Blue Scale Gloves.png',
        'stats': [2, 1, 1, 1, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Demon Gloves': {
        'description': 'A trade off was made between the summoner and the demon to enchant these with demonic '
                       'power, blood was given in exchange and a portion of the spirit',
        'value': 20345,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Demon Gloves.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Glovemail': {
        'description': 'An old generation gloves-mail in which your hands fell cold if you don\'t wear atleast '
                       'a sheet of cloth underneath it, but still gives good protection and momentum to your swings',
        'value': 13343,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Glovemail.png',
        'stats': [2, 0, 0, 2, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Glover Of Power': {
        'description': 'These are by nature can make anyone wearing these the '
                       'strongest man that can stop an elephant charge.',
        'value': 33343,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Glover Of Power.png',
        'stats': [2, 0, 1, 3, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Gloves Of The Ancients': {
        'description': 'Left from ancient times by the guardians, the protectors of the land '
                       'their power is all that is left protecting us from the chaos now.',
        'value': 83432,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Gloves Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 3]  # con, wis, fai, str, int, cun
    },
    'Gloves Of the Savior': {
        'description': 'Many ballads were sang about the savior and his followers, the legends of '
                       'the saviors feats holds to this day as a reminder of hope to humanity.',
        'value': 817472,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Gloves Of the Savior.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Gloves Lacrimo': {
        'description': 'We are bent but not broken, we are maybe spent but can still go on. '
                       'it is in our mind last we give up. Gloves for those who have not lost their way.',
        'value': 11230,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Gloves Lacrimo.png',
        'stats': [1, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Hardening Gloves': {
        'description': 'Suddenly chaos seems not so tough anymore, the bigger they are the harder they fall.',
        'value': 53012,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Hardening Gloves.png',
        'stats': [3, 0, 0, 2, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Hermit Gloves': {
        'description': 'Heritage from the dark wanderer the wise one and the sage. Those who spend the entirety '
                       'of their existence to find out the answers others may need.',
        'value': 125723,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Hermit Gloves.png',
        'stats': [1, 3, 1, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Leather Gloves': {
        'description': 'Strangely this leather is not from around here as it feels quite comfortable to wear '
                       'and quite durable not to wear off.',
        'value': 23057,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Leather Gloves.png',
        'stats': [1, 0, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plate Gloves': {
        'description': 'Heavy the burden carries the soldier, what counts in war most is the thought and preparation '
                       'these gloves are hard and plated but you get used to their weight in exchange for protection.',
        'value': 40527,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Plate Gloves.png',
        'stats': [2, 0, 1, 1, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Shadow Gloves': {
        'description': 'Light casts a shadow be it a sun or moon but as long as it goes unnoticed '
                       'that is all what matters in the end.',
        'value': 64275,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Gloves/Shadow Gloves.png',
        'stats': [1, 0, 3, 1, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Cap Of Aim': {
        'description': 'The further the target, the higher you aim. The closer the target, the faster you run.',
        'value': 230460,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Cap Of Aim.png',
        'stats': [1, 1, 1, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Chainmet': {
        'description': 'With the protection of scale armour you get all what there is to get against '
                       'even the formidable of opponents.',
        'value': 423060,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Chainmet.png',
        'stats': [2, 1, 2, 3, 1, 2]  # con, wis, fai, str, int, cun
    },
    'Demon Helmet': {
        'description': 'Try not to look too hard through it you may see some afterimages of your loved ones.',
        'value': 654566,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Demon Helmet.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Helm Of The Ancients': {
        'description': 'During the time of the ancients war meant nothing to anyone when everyone was fighting '
                       'for what they believed in and no ideals were berated by a demon.',
        'value': 843562,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Helm Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 3]  # con, wis, fai, str, int, cun
    },
    'Helm Of The Savior': {
        'description': 'Helm that hold the wisdom strength and courage of the savior to this day is the most '
                       'precious artifact you can stumble upon.',
        'value': 1843562,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Helm Of The Savior.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Iron Helmet': {
        'description': 'A mixture of iron and Sprigan\'s ichor is what make\'s this piece of equipment a unique.',
        'value': 70356,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Iron Helmet.png',
        'stats': [1, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Juggernaut': {
        'description': 'If strength in what you need then how about the brawn brute\'s helm that showed no mercy.',
        'value': 68273,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Juggernaut.png',
        'stats': [2, 0, 1, 1, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Leather Cap': {
        'description': 'Made with flexible leather with protective properties, serving as helmet made not to break of '
                       'even the most vicious of attacks while protection the wearer\'s head. '
                       'It\'s a perfect wear for any type of adventuring.',
        'value': 43162,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Leather Cap.png',
        'stats': [1, 0, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plated Helmet': {
        'description': 'A glorious shiny plated helmet with an unknown origin but legends speak of some sort of '
                       'slayer that traveled from village to village and exterminated all the goblins in his path.',
        'value': 12273,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Plated Helmet.png',
        'stats': [2, 0, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Royal Helmet': {
        'description': 'As far as nobility goes leading an army under a banner takes more skill '
                       'than the ordinary can imagine but to distinguish your loyalty from one lord to another '
                       'is by the shape of their helmet.',
        'value': 227273,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Royal Helmet.png',
        'stats': [2, 0, 2, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Scale Helmet': {
        'description': 'This helmet is made out of dragon scales or so they say, but truthfully no one knows fo sure. '
                       'What can confirm this claim is that you can hardly see any dents on it.',
        'value': 476289,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Scale Helmet.png',
        'stats': [2, 2, 4, 2, 2, 3]  # con, wis, fai, str, int, cun
    },
    'Shadow Crown': {
        'description': 'From the chosen amongst the shadow assassins wears the Shadow crown, '
                       'as a claim to a title that obviously dismisses any doubts about what his is capable of',
        'value': 1476289,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Helmets/Shadow Crown.png',
        'stats': [4, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Copper Chain': {
        'description': 'This copper chain has an engraved stone that serves as a talisman to ward of '
                       'any kind of evil and also acts as a charm that grants protection against physical harm.',
        'value': 291613,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Copper Chain.png',
        'stats': [1, 0, 0, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Demon Choker': {
        'description': 'Who knows where this came from but some unholy aura is felt surging through it, '
                       'this item will bring no harm to it\'s keeper but who knows what if it\'s owners finds out.',
        'value': 93416,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Demon Choker.png',
        'stats': [2, 0, 1, 2, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Iron Chain': {
        'description': 'Iron chain made of Yule\'s powder and iron for protection but also empowers the wearer',
        'value': 321364,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Iron Chain.png',
        'stats': [1, 0, 1, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Leafs Of Liberation': {
        'description': 'This is the very neckless that belonged to Afernisia the liberator of the land, '
                       'once the corruption started to swallow people with greed and lust for power it was Afernisia '
                       'the priestess who used her beliefs and astral ascend to revoke the power from from the '
                       'corrupted and restore back the order to the land.',
        'value': 651321,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Leafs Of Liberation.png',
        'stats': [1, 0, 2, 0, 1, 0]  # con, wis, fai, str, int, cun
    },
    'Leather Scarf': {
        'description': 'We call it the Sky Leather which comes from the Northern part of the world where '
                       'they cook the leather of Hullabafu for hours to dry it oil it and create these'
                       'pretty necklesses of protection.',
        'value': 435461,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Leather Scarf.png',
        'stats': [1, 4, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Pearl Head': {
        'description': 'Beautiful neckless made of silver chain with a pearl strapped to it. It\'s enchanted '
                       'with powerful ancient elven magic and gives you all the strength that nature can offer.',
        'value': 714615,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Pearl Head.png',
        'stats': [1, 2, 3, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Prayer Beads': {
        'description': 'Every man needs something to hold on to. Prayer keeps the devil at bay and the demons away, '
                       'this item also puts some magic strength to the arsenal.',
        'value': 76311,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Prayer Beads.png',
        'stats': [0, 0, 5, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Rabbits Foot': {
        'description': 'A neckless that brings luck to his wearer along with all the perks that you may think of.',
        'value': 32781,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Rabbits Foot.png',
        'stats': [1, 1, 1, 1, 1, 1]  # con, wis, fai, str, int, cun
    },
    'Relic Of Life': {
        'description': 'Grants the health perks to hold you though the tough battles to come.',
        'value': 17134,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Relic Of Life.png',
        'stats': [3, 0, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Ruby Of Strength': {
        'description': 'Gives strength to your hits and abilities.',
        'value': 17433,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Ruby Of Strength.png',
        'stats': [0, 0, 0, 3, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Shadow Claw': {
        'description': 'Another piece of the assassin\'s guild that was made purely for revenge. '
                       'It\'s holder will be granted the qualities of a true assassin.',
        'value': 433781,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Shadow Claw.png',
        'stats': [1, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Stone Of Knowledge': {
        'description': 'Sourcerer\'s stone of knowledge as simple as it looks it still gives out '
                       'a great amount of energy and wisdom.',
        'value': 23374,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Neckless/Stone Of Knowledge.png',
        'stats': [0, 1, 0, 0, 3, 0]  # con, wis, fai, str, int, cun
    },
    'Demon Ring': {
        'description': 'Once the demon portal was open little did they know of the deal they made with the devil. '
                       'Now all lands have fallen to the chaos and little hope remains to reclaim them.',
        'value': 86741,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Demon Ring.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'HellFire': {
        'description': 'You can feel the fire burning within you, like you\'ve gained '
                       'the weight and the strength of a bear.',
        'value': 54641,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/HellFire.png',
        'stats': [2, 0, 0, 2, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Iron Ring': {
        'description': 'Made of a prime iron, it rust\'s easily but it holds the power '
                       'anyone could use some of which.',
        'value': 33221,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Iron Ring.png',
        'stats': [1, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Protection Ring': {
        'description': 'It is something you will fancy for the generous amount of protection it gives you.',
        'value': 24507,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Protection Ring.png',
        'stats': [3, 0, 2, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Ring Of Life': {
        'description': 'In the old days mages were using black magic in their every day lives '
                       'unaware of the malice it may bring them in the future that is how the Ring of life '
                       'was made. Harvested with the life force of it\'s surroundings',
        'value': 36734,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Ring Of Life.png',
        'stats': [5, 0, 0, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Ring Of Power': {
        'description': 'Not the one from "Middle Earth" but it is what it says it is.',
        'value': 53474,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Ring Of Power.png',
        'stats': [1, 0, 0, 5, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Scale Ring': {
        'description': 'When the great war begun, all kings went in search of forging protection spells '
                       'even tried them on their own cities but the furthest they could manage to come with '
                       'that idea is this ring.',
        'value': 16124,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Scale Ring.png',
        'stats': [2, 3, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Tangled': {
        'description': 'When the kings decided to move on in the creation of the rings of power, '
                       'they conjured the walking library. It\'s a ring that the mages may use to '
                       'aid them in the research they conducted.',
        'value': 34635,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Tangled.png',
        'stats': [1, 2, 1, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Topaz Lotus': {
        'description': 'As the mages came to possess such grand knowledge, they started to experiment '
                       'with different combination of sacred plant until they made the Topaz Lotus ring.',
        'value': 52112,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Rings/Topaz Lotus.png',
        'stats': [1, 1, 2, 0, 0, 3]  # con, wis, fai, str, int, cun
    },
    'Bow Of Sight': {
        'description': 'Not many bows are of this sort, it\'s strong and beautiful in it\'s own way.',
        'value': 21262,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Bows/Bow Of Sight.png',
        'stats': [2, 2, 3, 0, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Long Bow': {
        'description': 'The long bow normally they used it to raid fortresses, nowadays.. not so much.',
        'value': 11262,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Bows/Long Bow.png',
        'stats': [0, 1, 2, 0, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Short Bow': {
        'description': 'Short war bow with not much to offer except it\'s practical use',
        'value': 4262,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Bows/Short Bow.png',
        'stats': [1, 0, 1, 0, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Cuttler': {
        'description': 'Those who wield the art of war, can use any weapon but to master them all '
                       'takes more than just swinging them.',
        'value': 24262,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Cuttler.png',
        'stats': [1, 0, 2, 0, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Holy Sword': {
        'description': 'The sword that was blessed by god and by the temple and by the priest.',
        'value': 123344,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Holy Sword.png',
        'stats': [4, 4, 5, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Iron Sword': {
        'description': 'Battle iron sword belonged to knight notabilities. great for keeping up the '
                       'pace of battle.',
        'value': 11124,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Iron Sword.png',
        'stats': [1, 1, 1, 2, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Quick Hand': {
        'description': 'Feels light in hand, and sharp enough to slice through pretty much anything.',
        'value': 12312,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Quick Hand.png',
        'stats': [1, 0, 1, 2, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Rapier': {
        'description': 'Long thin flexable and sharp! very light in hand can piece anything.',
        'value': 53212,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Rapier.png',
        'stats': [1, 0, 2, 0, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Scimitar': {
        'description': 'Heavy darkened steel curved sword can deal tremendous blows.',
        'value': 324532,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Scimitar.png',
        'stats': [0, 1, 0, 3, 4, 2]  # con, wis, fai, str, int, cun
    },
    'Scorpion': {
        'description': 'Belonged to a slayer or giant scorpions, it is much powerful than any other sword.',
        'value': 46632,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Scorpion.png',
        'stats': [0, 1, 0, 4, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Stabber': {
        'description': 'Out matched with almost any sword there is to be out there, is a bit heavy on the tilt '
                       'but when put to use is a very powerful weapon.',
        'value': 45652,
        'equipped_on': 'Hand',
        'image_path': equip_path + 'Swords/Stabber.png',
        'stats': [1, 1, 0, 4, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Arm Guard': {
        'description': 'Made of Eler wood strong and light to carry it has no dents to speak of, the wood can '
                       'hold against any attack without breaking.',
        'value': 16735,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Arm Guard.png',
        'stats': [1, 0, 2, 0, 0, 2]  # con, wis, fai, str, int, cun
    },
    'Buckler': {
        'description': 'Light and strong this lucky buckler was brought recently with not many of those '
                       'known of, it brings out out the best of a warrior',
        'value': 57312,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Buckler.png',
        'stats': [1, 1, 2, 2, 0, 1]  # con, wis, fai, str, int, cun
    },
    'Demon Shield': {
        'description': 'Having this shield may increase your chance of survival by big margin, but be aware '
                       'if it\'s origin, for we fight with those who made these.',
        'value': 62222,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Demon Shield.png',
        'stats': [3, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Holy Shield': {
        'description': 'Brings up hope, how can you not feel more confident with this holy shied in your hand.',
        'value': 123456,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Holy Shield.png',
        'stats': [5, 4, 4, 4, 4, 4]  # con, wis, fai, str, int, cun
    },
    'Iron Buckler': {
        'description': 'Iron is the metal of war and this buckler is a tool to encourage to partake in it.',
        'value': 22533,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Iron Buckler.png',
        'stats': [2, 1, 1, 0, 0, 0]  # con, wis, fai, str, int, cun
    },
    'Plated Shield': {
        'description': 'Plated with steel mixed with colored coal is not the only thing that makes this '
                       'shield unique but the generous qualities that it adds up to yours is as much as amazing.',
        'value': 41112,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Plated Shield.png',
        'stats': [3, 1, 2, 0, 2, 0]  # con, wis, fai, str, int, cun
    },
    'Royal Shield': {
        'description': 'Belong to the great Aetholemir - king of kings. there is not much left of his legacy but '
                       'a few of those high quality items such as this.',
        'value': 1245634,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Royal Shield.png',
        'stats': [5, 4, 2, 3, 4, 2]  # con, wis, fai, str, int, cun
    },
    'Shadow Shield': {
        'description': 'A product of the assassins guild made for the elite of units '
                       'but with less taste for looks though.',
        'value': 453345,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Shadow Shield.png',
        'stats': [2, 2, 2, 2, 2, 2]  # con, wis, fai, str, int, cun
    },
    'Shield Of The Savior': {
        'description': 'The human kind was left little choice but to go to war with the creatures of chaos. '
                       'When the creatures emerged from the portals connecting their world and the human one, '
                       'that\'s when the savior was found amongst the broken one\'s and saved humans from their doom.',
        'value': 2453345,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Shield Of The Savior.png',
        'stats': [5, 5, 5, 5, 5, 5]  # con, wis, fai, str, int, cun
    },
    'Shied Rojo': {
        'description': 'He was a famous bard and a warrior that lifted everyone\'s spirits. At the time of his '
                       'death they named this patterned shield in his name, never to forget that "Life is a waste of '
                       'time, time is a waste of life, get drunk all the time and you\'ll have the time of your life."',
        'value': 132142,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Shied Rojo.png',
        'stats': [1, 1, 2, 2, 1, 2]  # con, wis, fai, str, int, cun
    },
    'Shield Of The Ancients': {
        'description': 'Ancients knew the propertirs of all living things trees inclueded '
                       'so they knew how to make the best of it all and made this shield '
                       'that gives you every little bit of strength in your journey.',
        'value': 142313,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Shield Of The Ancients.png',
        'stats': [3, 3, 3, 3, 3, 2]  # con, wis, fai, str, int, cun
    },
    'Spike Lord': {
        'description': 'This idea was coined by a demon lord, one of the first came crossed the portal. '
                       'the idea of impaling your enemy of your shield is a very vicious one.',
        'value': 312314,
        'equipped_on': 'Accessory',
        'image_path': equip_path + 'Shields/Spike Lord.png',
        'stats': [2, 0, 2, 2, 0, 2]  # con, wis, fai, str, int, cun
    },
}

def updateCenterLabel():
    global center_label

    TOP_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT / 25)
    LEFT_SIZE = (SCREEN_WIDTH * 5 / 16, SCREEN_HEIGHT - TOP_SIZE[1])
    LEFT_POS = (0, TOP_SIZE[1])
    RIGHT_POS = (TOP_SIZE[0] - LEFT_SIZE[0], TOP_SIZE[1])

    center_label = [
        pygame.Rect(265, 140, SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1]), (LEFT_SIZE[0], 35)),  # player healthbar
        pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1] + 40), (LEFT_SIZE[0], 35)),  # player manaBar
        pygame.Rect((LEFT_POS[0] + 35, LEFT_POS[1] + 80), (LEFT_SIZE[0], 35)),  # player spiritBar

        pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1]), (LEFT_SIZE[0], 35)),  # monster healthbar
        pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1] + 40), (LEFT_SIZE[0], 35)),  # monster manaBar
        pygame.Rect((RIGHT_POS[0] - 35, LEFT_POS[1] + 80), (LEFT_SIZE[0], 35)),  # monster spiritBar
    ]

class Inventory:
    def __init__(self):
        self.size = 30
        self.items = []

    def addItem(self, name, desc, value, image_path, equipped_on=None, stats: list=[]):
        if len(self.items) < self.size:
            inv_item = {
                'slot_id': len(self.items) + 1,
                'name': name,
                'description': desc,
                'value': value,
                'equipped_on': equipped_on,
                'image_path': image_path,
                # adding stats
                'stats': stats
            }
            self.items.append(inv_item)

    def getItem(self, item_id):
        for item in self.items:
            if item['slot_id'] <= self.size and item['slot_id'] == item_id:
                return item
        return False

    def insertItem(self, item, insert_id=None):
        slot_id = insert_id if insert_id else item.slot_id
        inv_item = {
            'slot_id': slot_id,
            'name': item.name,
            'description': item.desc,
            'value': item.value,
            'equipped_on': item.equipped_on,
            'image_path': item.image_path,
            'stats': item.stats
        }
        self.items.append(inv_item)

    def delItem(self, item_id):
        if item_id <= self.size:
            for item in self.items:
                if item['slot_id'] == item_id:
                    self.items.remove(item)


class Mind(pygame.sprite.Sprite):
    def __init__(self, amount):
        super(Mind, self).__init__()
        self.health_capacity = amount
        self.current_health = self.health_capacity

    def setCapacity(self, capacity):
        self.health_capacity = capacity

    def addCapacity(self, addition):
        self.health_capacity += addition

    def subCapacity(self, subtraction):
        self.health_capacity -= subtraction

    def fillUp(self):
        self.current_health = self.health_capacity

    def setCurrent(self, mana):
        self.current_health = mana

    def addCurrent(self, mana):
        if self.current_health + mana > self.health_capacity:
            self.current_health = self.health_capacity
        else:
            self.current_health += mana

    def subCurrent(self, mana):
        self.current_health -= mana
        if self.current_health < 0:
            self.current_health = 0


class Spirit(Mind):
    def __init__(self, amount):
        super().__init__(amount)
        self.health_capacity = amount
        self.current_health = self.health_capacity


class Character(pygame.sprite.Sprite):
    def __init__(self, data, manager, is_bad=False, is_player=False, stats=None):  # add sprite group | object
        super(Character, self).__init__()

        # constantly displayed parameters (pre battle)
        self.level = 1
        self.exp, self.exp_needed = 0, 10
        self.name = "None"

        self.ar_max = 0
        self.ev_max = 0
        self.hit_max = 1

        self.ar = self.ar_max  # armour
        self.ev = self.ev_max  # evasion
        self.hit = self.hit_max  # hit chance

        self.con_max, self.wis_max, self.fai_max = 1, 1, 1
        self.str_max, self.int_max, self.cun_max = 1, 1, 1
        self.end_max, self.wil_max, self.fin_max = 0, 0, 0

        # passive
        self.con = self.con_max  # constitution
        self.wis = self.wis_max  # wisdom
        self.fai = self.fai_max  # faith

        # offensive
        self.str = self.str_max  # strength
        self.int = self.int_max  # intelligence
        self.cun = self.cun_max  # cunning

        # bonus
        self.end = self.end_max  # endurance
        self.wil = self.wil_max  # willpower
        self.fin = self.fin_max  # finesse

        if stats:
            self.con, self.wis, self.fai = stats[0], stats[1], stats[2]
            self.str, self.int, self.cun = stats[3], stats[4], stats[5]
            self.level = stats[6]
            self.end = self.level

        self.bonus_name = 'bonus'
        self.bonus_value = 'none'
        self.bonus_value_max = 'none'

        self.dmg_offset = 15
        self.hit_offset = 50

        self.hp_offset = 15 + self.dmg_offset
        self.mp_offset = 15 + self.hp_offset // 2
        self.sp_offset = 15 + self.mp_offset // 2

        self.ev_offset = 15

        # state stats
        self.stance = "None"
        # boosts and hinders both have tuple (name, turns_left)
        self.boosts = []
        self.hinders = []

        self.hp_max = self.calcHP()  # health points
        self.mp_max = self.calcMP()  # mind points
        self.sp_max = self.calcSP()  # spirit points

        match self.bonus_name:
            case 'Endurance':
                self.hp_max += 20
            case 'Willpower':
                self.mp_max += 20
            case 'Finesse':
                self.sp_max += 20

        # battle
        self.health_capacity = self.hp_max if self.hp_max > 0 else 1
        self.current_health = self.health_capacity

        self.mind_capacity = self.mp_max if self.mp_max > 0 else 1
        self.mind = Mind(self.mind_capacity)

        self.spirit_capacity = self.sp_max if self.sp_max > 0 else 1
        self.spirit = Spirit(self.spirit_capacity)

        self.state = "Idle"
        self.frame = 0
        self.used_skill = None
        self.hits_left = -1
        self.is_miss = False

        sprites = loadSprites()
        if is_player:
            self.sprite_sheet = sprites[0]
        else:
            self.sprite_sheet = sprites[1]

        if isinstance(data, str):
            self.kind = data
        elif isinstance(data, Character):
            self.kind = data.kind
            self.level = data.level
            self.exp, self.exp_needed = data.exp, data.exp_needed
            self.name = data.name

            self.health_capacity = data.health_capacity if data.current_health > 0 else 1
            self.current_health = data.current_health

            self.mind_capacity = data.mind_capacity if data.mind_capacity > 0 else 1
            self.mind = Mind(self.mind_capacity)
            self.mind.current_health = data.mind.health_capacity

            self.spirit_capacity = data.spirit_capacity if data.spirit.health_capacity > 0 else 1
            self.spirit = Spirit(self.spirit_capacity)
            self.spirit.current_health = data.spirit.health_capacity

            # passive
            self.con = data.con  # constitution
            self.wis = data.wis  # wisdom
            self.fai = data.fai  # faith

            # offensive
            self.str = data.str  # strength
            self.int = data.int  # intelligence
            self.cun = data.cun  # cunning

            # bonus
            self.bonus_name = data.bonus_name
            self.bonus_value = data.bonus_value

            self.stance = data.stance
            self.boosts = data.boosts
            self.hinders = data.hinders

            self.state = data.state
            self.frame = 0
            self.can_attack = True
            self.can_defend = True

        match self.kind:
            case 'Warlord':
                self.end = 1
                self.bonus_name = 'End'
                self.bonus_fullname = 'Endurance'
                self.bonus_value = self.end
                self.bonus_value_max = self.end
            case 'Sourcerer':
                self.wil = 1
                self.bonus_name = 'Wil'
                self.bonus_fullname = 'Willpower'
                self.bonus_value = self.wil
                self.bonus_value_max = self.wil
            case 'Hunter':
                self.fin = 1
                self.bonus_name = 'Fin'
                self.bonus_fullname = 'Finesse'
                self.bonus_value = self.fin
                self.bonus_value_max = self.fin

        self.animation = self.sprite_sheet[self.kind][self.state]
        # GUI - HP/AP Bars
        self.rect_health = center_label[1]
        self.rect_mana = center_label[2]
        self.rect_spirit = center_label[3]
        health_id = "#health_bar"
        if is_bad:
            self.rect_health = center_label[4]
            self.rect_mana = center_label[5]
            self.rect_spirit = center_label[6]
            health_id = "#monster_health_bar"

        self.is_dead = False

        self.HealthBar = pygame_gui.elements.UIScreenSpaceHealthBar(relative_rect=self.rect_health,
                                                                    manager=manager, sprite_to_monitor=self,
                                                                    object_id=ObjectID(object_id="#health_bar"))
        self.MagicBar = pygame_gui.elements.UIScreenSpaceHealthBar(relative_rect=self.rect_mana, manager=manager,
                                                                   sprite_to_monitor=self.mind,
                                                                   object_id=ObjectID(object_id="#arcana_bar"))
        self.SpiritBar = pygame_gui.elements.UIScreenSpaceHealthBar(relative_rect=self.rect_spirit, manager=manager,
                                                                   sprite_to_monitor=self.spirit,
                                                                   object_id=ObjectID(object_id="#spirit_bar"))

        self.HealthBar.hide()
        self.MagicBar.hide()
        self.SpiritBar.hide()

        self.inventory = Inventory()
        self.hand, self.torso, self.accessory = None, None, None

        self.is_transcended = False
        self.ult_turn = 0
        self.ult_limit = 5

        self.is_aggressive = False


    # General methods
    def displayInfo(self):
        print("Statistics:")
        print(f"General: "
              f"{self.name} | lvl: {self.level} | kind: {self.kind}")
        print(f"Battle:"
              f"LP: {self.current_health} | AP: {self.mind.current_health}"
              f"(Stance: {self.stance})")

    # Battle methods
    def changeStance(self, stance):
        try:
            if stance not in BattleStance:
                raise ValueError("Value Error: No such stance.")
            if type(stance) != str:
                raise TypeError("Type Error: Type incorrect, not string.")
            self.stance = stance
        except ValueError as e:
            print(type(e), ':', e)
        except TypeError as e:
            print(type(e), ':', e)
        except Exception as e:
            print(type(e), ':', e)

    def animate(self):
        self.animation = self.sprite_sheet[self.kind][self.state]
        return self.animation

    def getAnimationFrames(self, frame_width):
        return self.animation.get_width() // frame_width

    # Animations
    def getIdle(self):
        self.state = "Idle"

    def getAttacking(self):
        self.state = "Attack"

    def getHit(self):
        self.state = "Take Hit"
        self.hits_left -= 1
        if self.hits_left <= 0:
            self.hits_left = -1

    def getCast(self, used_skill, pos):
        self.state = "Cast"
        self.used_skill = used_skill
        self.used_skill["effect"].pos = pos

    def getCastedOn(self, skill):
        self.skill = skill  # name of effect

    def getDead(self):
        self.state = "Die"

    def getFinished(self):
        self.is_dead = True

    # calculations
    def levelUp(self):
        # Stat effects
        self.current_health = self.health_capacity
        self.mind.setCurrent(self.mind_capacity)
        self.spirit.setCurrent(self.spirit_capacity)
        self.level += 1
        self.exp = self.exp_needed - self.exp
        self.exp_needed = int(self.exp_needed * 1.5)

    def getStatsFromItem(self, item):
        for i in range(len(item.stats)):
            match i:
                case 0:
                    self.con += item.stats[i]
                case 1:
                    self.wis += item.stats[i]
                case 2:
                    self.fai += item.stats[i]
                case 3:
                    self.str += item.stats[i]
                case 4:
                    self.int += item.stats[i]
                case 5:
                    self.cun += item.stats[i]

    def updateStats(self, is_effect=False):
        self.con, self.wis, self.fai = self.con_max, self.wis_max, self.fai_max
        self.str, self.int, self.cun = self.str_max, self.int_max, self.cun_max
        self.bonus_value = self.bonus_value_max

        if self.hand:
            self.getStatsFromItem(self.hand)
        if self.torso:
            self.getStatsFromItem(self.torso)
        if self.accessory:
            self.getStatsFromItem(self.accessory)

        bonus = self.bonus_value if self.bonus_name == "End" else 0
        stats = (self.con * 0.4 + self.str * 0.3 + bonus * 0.2 + self.level * 0.1)

        bonus = self.bonus_value if self.bonus_name == "Wil" else 0
        stats = (self.wis * 0.4 + self.int * 0.3 + bonus * 0.2 + self.level * 0.1)

        if not is_effect:
            self.health_capacity = self.calcHP()
            self.mind_capacity = self.calcMP()
            self.spirit_capacity = self.calcSP()
            self.current_health = self.health_capacity

            self.mind.setCapacity(self.mind_capacity)
            self.spirit.setCapacity(self.spirit_capacity)

            self.mind.setCurrent(self.mind_capacity)
            self.spirit.setCurrent(self.spirit_capacity)

            self.ar = self.ar_max
            self.ev = self.ev_max
            self.hit = self.hit_max
        else:
            self.enableBoosts()
            self.enableHinders()

    def pAttack(self):
        self.is_miss = False
        dmg = self.str ** 2 + self.con * self.level
        if dmg < 0:
            dmg = 0
        crit = r_int(dmg // 2, dmg * 3 // 4) if (self.hit * 4/3 - 20 + r_int(0, 20)) > self.hit_offset else r_int(-dmg, dmg)

        if self.spirit.current_health == 0:
            crit *= 2

        if dmg + crit <= 0:
            self.is_miss = True
        total_dmg = dmg + crit

        if self.is_transcended:
            return total_dmg * 3
        return total_dmg * 2 if self.is_aggressive else total_dmg

    def mAttack(self):
        self.is_miss = False
        dmg = self.int ** 2 + self.wis * self.level
        if dmg < 0:
            dmg = 0
        crit = r_int(dmg // 2, dmg * 3 // 4) if (self.hit * 4 / 3 - 20 + r_int(0, 20)) > self.hit_offset else r_int(-dmg, dmg)

        if self.spirit.current_health == 0:
            crit *= 2

        if dmg + crit <= 0:
            self.is_miss = True

        total_dmg = dmg + crit
        if self.is_transcended:
            return total_dmg * 3
        return total_dmg * 2 if self.is_aggressive else total_dmg

    def aAttack(self, effect):
        match effect:
            case "ignore armour":
                # Warlord
                # Valiant slash
                return effect, self.pAttack()
            case "ignore evasion":
                # Warlord
                # Aura cleave
                return effect, self.pAttack()
            case "use opp mana":
                # Warlord
                # Astral shred
                return effect, self.pAttack()
            case "damage n times":
                # Warlord
                # Spectral Duel
                times = 2 if self.kind == "Warlord" else 15
                return effect, self.pAttack(), times

                # Sourcerer
                # Arcane frenzy
                pass
            case "damage over time":
                # Hunter
                # Deadly composition

                # Sourcerer
                # Tear's ripple
                if self.kind == "Sourcerer":
                    return effect, self.used_skill["name"]
            case "add health":
                # Warlord
                # Vanguard's stance
                turns_active = 2
                return effect, self.health_capacity * 2, turns_active
            case "add mana regen":
                # Sourcerer
                # Third eye
                pass
            case "tradeoff":
                # Warlord
                # Ancestors Protection
                if self.used_skill["name"] == "ancestors-protection":
                    return effect, self.health_capacity * 2
                # Aggression (Toggable)

                # Hunter
                # Rose Thorn
                # Intimidate
                # Perception
                # Arcane barrier
                if self.used_skill["name"] == "arcane-barrier":
                    return effect, self.mind.health_capacity
                # Aegis shield
                if self.used_skill["name"] == "aegis-shield":
                    return effect, self.mind.health_capacity

                # Blood magic
                pass
            case "ignore damage":
                # Warlord
                # Turtle reflex (Passive)
                pass
            case "absorb damage":
                # Hunter
                # Better position
                if self.used_skill["name"] == "better-position":
                    return effect, self.mind.health_capacity
            case "use opp health":
                # Warlord
                # Blood thirst(Stack max 5)
                pass
            case "weaken opp":
                # Sourcerer
                # Psychic Storm
                if self.used_skill["name"] == "psychic-storm":
                    turns_active = 2
                    return effect, self.mAttack(), self.used_skill["name"], turns_active + 1
                elif self.used_skill["name"] == "diamond-dust":  # Diamond dust
                    return effect, self.mAttack(), self.used_skill["name"]
            case "boost stats":
                # Warlord
                # True Vigor(Unlock 5 locks)
                boosts = {}
                count = 0
                if self.used_skill["lock_idx"] <= 5:
                    boosts = self.used_skill["lock"][f'{self.used_skill["lock_idx"]}']

                    if self.kind == "Warlord":
                        for key, val in boosts.items():
                            match key:
                                case "ar":
                                    self.ar = self.ar_max + val
                                    count += 1
                                case "con":
                                    self.con = self.con_max + val
                                    count += 1
                                case "str":
                                    self.str = self.str_max + val
                                    count += 1
                                case "ev":
                                    self.ev = self.ev_offset + val
                                    count += 1
                                case "end":
                                    self.end = self.end_max + val
                                    count += 1
                    elif self.kind == "Sourcerer":
                        for key, val in boosts.items():
                            match key:
                                case "ar":
                                    self.ar = self.ar_max + val
                                    count += 1
                                case "wis":
                                    self.con = self.con_max + val
                                    count += 1
                                case "int":
                                    self.str = self.str_max + val
                                    count += 1
                                case "ev":
                                    self.ev = self.ev_offset + val
                                    count += 1
                                case "wil":
                                    self.end = self.end_max + val
                                    count += 1
                    elif self.kind == "Hunter":
                        for key, val in boosts.items():
                            match key:
                                case "ar":
                                    self.ar = self.ar_max + val
                                    count += 1
                                case "fai":
                                    self.fai = self.fai + val
                                    count += 1
                                case "cun":
                                    self.cun = self.cun_max + val
                                    count += 1
                                case "ev":
                                    self.ev = self.ev_offset + val
                                    count += 1
                                case "fin":
                                    self.fin = self.fin_max + val
                                    count += 1
                return effect, 0 < len(boosts) == count

                # Hunter
                # True Speed

                # Sourcerer
                # True Spirit
                pass
            case "battle boost":
                # Hunter
                # Snake eyes
                pass
            case "hunter skill":
                # Hunter
                return effect, self.pAttack() * 3 // 2
                pass
            case "cancel":
                # Hunter
                # Disarm
                pass
            case "con damage":
                # Sourcerer
                # Cloud mind
                if self.used_skill["name"] == "cloud-mind":
                    turns_active = 1
                    return effect, self.used_skill["name"], turns_active
                pass
            case "countdown":
                # Warlord
                # Blood Thirst
                if self.used_skill["count"] <= 5:
                    self.used_skill["count"] += 1
                if self.used_skill["count"] < 5:
                    return effect, self.pAttack() + r_int(50, 100) * self.used_skill["count"]
                elif self.used_skill["count"] == 5:
                    return effect, self.pAttack() + 500
                return effect, self.pAttack() - 100
            case "transcendence":
                return effect, self.is_transcended

    def aDefense(self, effect):
        match effect[0]:
            case "ignore armour":
                dmg = effect[1]
                # Warlord
                # Valiant slash
                return self.pDefend(dmg + self.ar, pure_dmg=5, skill_dmg=6)
            case "ignore evasion":
                dmg = effect[1]
                # Warlord
                # Aura cleave
                return self.pDefend(dmg + self.ar, pure_dmg=7, skill_dmg=15)
            case "use opp mana":
                dmg_mind = 0
                if self.mind.current_health > self.mind.health_capacity / 10:
                    dmg_mind = self.mind.health_capacity // 10
                    self.mind.setCurrent(self.mind.current_health - dmg_mind)
                elif self.mind.current_health > 0:
                    dmg_mind = self.mind.current_health
                    self.mind.setCurrent(0)
                dmg = effect[1] + dmg_mind
                # Warlord
                # Astral shred
                return self.pDefend(dmg, pure_dmg=15, skill_dmg=24)
            case "damage n times":
                # Warlord
                # Spectral Duel
                dmg = effect[1]
                self.hits_left = effect[2]
                return self.mDefend(dmg, pure_dmg=24, skill_dmg=48)

                # Sourcerer
                # Arcane frenzy
                pass
            case "damage over time":
                # Hunter
                # Deadly composition

                # Sourcerer
                # Tear's ripple
                if effect[1] == "tears-ripple":
                    hinder = {
                        "type": effect[0],
                        "name": effect[1],
                        "turns_active": 3,
                        "turn": 0
                    }
                    self.hinders.append(hinder)
                    dmg = r_int(0, abs(self.pAttack()))
                    return dmg
            case "add health":
                # Warlord
                # Vanguard's stance
                boost = {
                    "type": effect[0],
                    "amount": effect[1],
                    "turns_active": effect[2],
                    "turn": 0
                }
                self.boosts.append(boost)
                return
            case "add mana regen":
                # Sourcerer
                # Third eye
                pass
            case "tradeoff":
                # Warlord
                # Ancestors Protection
                if self.used_skill["name"] == "ancestors-protection":
                    boost = {
                        "type": effect[0],
                        "amount": effect[1],
                        "name": self.used_skill["name"]
                    }
                    self.boosts.append(boost)
                # Aggression (Toggable)

                # Hunter
                # Rose Thorn
                # Intimidate
                # Perception
                # Arcane barrier
                if self.used_skill["name"] == "arcane-barrier":
                    boost = {
                        "type": effect[0],
                        "amount": effect[1],
                        "name": self.used_skill["name"],
                        "turns_active": 3,
                        "turn": 0
                    }
                    self.boosts.append(boost)

                elif self.used_skill["name"] == "aegis-shield":  # Aegis shield
                    boost = {
                        "type": effect[0],
                        "amount": effect[1],
                        "name": self.used_skill["name"],
                        "turns_active": 3,
                        "turn": 0
                    }
                    self.boosts.append(boost)
                # Blood magic
                pass
            case "ignore damage":
                # Warlord
                # Turtle reflex (Passive)
                pass
            case "absorb damage":
                # Hunter
                if self.used_skill["name"] == "better-position":
                    boost = {
                        "type": effect[0],
                        "amount": effect[1],
                        "name": self.used_skill["name"],
                        "turns_active": 3,
                        "turn": 0
                    }
                    self.boosts.append(boost)
                # Better position
                pass
            case "use opp health":
                # Warlord
                # Blood thirst(Stack max 5)
                pass
            case "weaken opp":
                # Sourcerer
                # Psychic Storm
                if effect[2] == "psychic-storm":
                    dmg = effect[1]
                    hinder = {
                        "type": effect[0],
                        "amount": 4,
                        "name": effect[2],
                        "turns_active": effect[3],
                        "turn": 0
                    }
                    self.hinders.append(hinder)
                    self.hits_left = 5
                    return self.mDefend(dmg)
                elif effect[2] == "diamond-dust":  # Diamond dust
                    dmg = effect[1]
                    return self.mDefend(dmg)
            case "boost stats":
                # Warlord
                # True Vigor(Unlock 5 locks)
                self.updateStats(is_effect=True)
                self.used_skill["lock_idx"] += 1

                return True
                # Hunter
                # True Speed

                # Sourcerer
                # True Spirit
                pass
            case "battle boost":
                # Hunter
                # Snake eyes
                pass
            case "hunter skill":
                # Hunter
                return self.mDefend(effect[1])
            case "cancel":
                # Hunter
                # Disarm
                pass
            case "con damage":
                # Sourcerer
                # Cloud mind
                if effect[1] == "cloud-mind":
                    hinder = {
                        "type": effect[0],
                        "name": effect[1],
                        "turns_active": effect[2],
                        "turn": 0
                    }
                    self.hinders.append(hinder)
                    return 1
                pass
            case "countdown":
                # Warlord
                # Blood Thirst
                dmg = effect[1]
                return self.pDefend(dmg)
            case "transcendence":
                if effect[1]:
                    return True
                return False

    def calcHP(self):
        hp = self.hp_max = (self.end * 2 + self.level) * (self.level + self.con)
        for boost in self.boosts:
            if boost["type"] == "add health":
                hp += boost["amount"]
            elif boost["type"] == "tradeoff":
                if self.kind == "Warlord":
                    hp += boost["amount"]
        return hp

    def calcMP(self):
        mp = self.mp_max = (self.wil * 2 + self.level) * (self.level + self.wis)
        return mp

    def calcSP(self):
        sp = self.sp_max = (self.fin * 2 + self.level) * (self.level + self.fai)
        return sp

    def pDefend(self, dmg, ev=-1, pure_dmg=0, skill_dmg=0):
        if ev == -1:
            ev = self.ev
        dmg -= self.ar
        if dmg < 0:
            dmg = 0
            crit = 0
        else:
            crit = r_int(0, dmg) if (ev * 4 / 3 - 20 + r_int(0, 20)) > self.ev_offset else r_int(abs(dmg) * 3 // 4, abs(dmg) * 5 // 4)
        # physical damage

        if pure_dmg > 0:
            self.current_health -= pure_dmg
        if skill_dmg > 0:
            skill_dmg = r_int(pure_dmg, skill_dmg) if skill_dmg > pure_dmg else r_int(1, skill_dmg)
            self.current_health -= skill_dmg
        total_dmg = dmg + crit
        self.current_health -= total_dmg
        # spiritual damage
        self.spirit.current_health = self.spirit.current_health - self.sp_max // 10 or 1 if self.current_health > self.hp_max // 2 else self.spirit.current_health - self.sp_max // 5 or 2
        if self.spirit.current_health < 0:
            self.spirit.current_health = 0
        return total_dmg + pure_dmg + skill_dmg

    def mDefend(self, dmg, pure_dmg=0, skill_dmg=0):
        dmg -= self.wil
        if dmg < 0:
            dmg = 0
            crit = 0
        else:
            crit = r_int(0, dmg) if (self.ev * 4 / 3 - 20 + r_int(0, 20)) > self.ev_offset else r_int(abs(dmg) * 3 // 4, abs(dmg) * 5 // 4)
        # magical damage
        if pure_dmg > 0:
            self.current_health -= pure_dmg
        if skill_dmg > 0:
            skill_dmg = r_int(pure_dmg, skill_dmg) if skill_dmg > pure_dmg else r_int(1, skill_dmg)
            self.current_health -= skill_dmg
        total_dmg = dmg + crit
        self.current_health -= total_dmg
        # spiritual damage
        self.spirit.current_health = self.spirit.current_health - self.sp_max // 10 or 1 if self.current_health > self.hp_max // 2 else self.spirit.current_health - self.sp_max // 5 or 2
        if self.spirit.current_health < 0:
            self.spirit.current_health = 0
        return total_dmg + pure_dmg + skill_dmg

    def findBoost(self, type=None, name=None):
        for boost in self.boosts:
            if boost["type"] == type:
                return boost
            elif "name" in boost and boost["name"] == name:
                return boost
        return False

    def findHinder(self, name):
        for hinder in self.hinders:
            if hinder["type"] == name:
                return hinder
            return False

    def enableBoosts(self):
        for boost in self.boosts:
            if boost["type"] == "add health":
                if boost["turn"] >= boost["turns_active"]:
                    difference = self.health_capacity - self.current_health
                    self.boosts.remove(boost)
                    self.health_capacity = self.calcHP()
                    self.current_health = self.health_capacity - difference
                    if self.current_health <= 0:
                        self.current_health = 0
                        self.getDead()
            elif boost["type"] == "tradeoff" and boost["name"] == "arcane-barrier":
                if boost["turn"] >= boost["turns_active"]:
                    self.boosts.remove(boost)
            elif boost["type"] == "tradeoff" and boost["name"] == "aegis-shield":
                if boost["turn"] >= boost["turns_active"]:
                    self.boosts.remove(boost)
            elif boost["type"] == "absorb damage" and boost["name"] == "better-position":
                if boost["turn"] >= boost["turns_active"]:
                    self.boosts.remove(boost)


        #self.boosts = list(filter(lambda x: True if x is not None else False, self.boosts))

        for boost in self.boosts:
            match boost["type"]:
                case "add health":
                    difference = self.health_capacity - self.current_health
                    health_cost = self.health_capacity // 10
                    self.health_capacity = self.calcHP()
                    self.current_health = self.health_capacity - difference - health_cost
                    boost["turn"] += 1
                case "tradeoff":
                    if boost["name"] == "ancestors-protection":
                        difference = self.health_capacity - self.current_health
                        self.health_capacity = self.calcHP()
                        self.current_health = self.health_capacity - difference - 1
                        self.ar = self.ar_max - 1
                    elif boost["name"] == "arcane-barrier":
                        boost["turn"] += 1

    def enableHinders(self):
        for hinder in self.hinders:
            if hinder["type"] == "weaken opp":
                if hinder["turn"] >= hinder["turns_active"]:
                    self.str = self.str_max
                    self.end = self.end_max
                    self.hinders.remove(hinder)
            if hinder["type"] == "con damage":
                if hinder["name"] == "cloud-mind":
                    if hinder["turn"] >= hinder["turns_active"]:
                        self.hinders.remove(hinder)
                    elif self.is_miss:
                        self.hinders.remove(hinder)
                        self.getHit()
                        self.updateStats(is_effect=True)
                        dmg = self.calcHP() // 2
                        return self.pDefend(dmg)
            if hinder["type"] == "damage over time":
                if hinder["name"] == "tears-ripple":
                    if hinder["turn"] >= hinder["turns_active"]:
                        self.hinders.remove(hinder)


        #self.hinders = list(filter(lambda x: True if x is not None else False, self.hinders))

        for hinder in self.hinders:
            match hinder["type"]:
                case "weaken opp":
                    self.str -= hinder["amount"]
                    self.end -= hinder["amount"]
                    hinder["turn"] += 1
                case "damage over time":
                    if hinder["name"] == "tears-ripple":
                        dmg = r_int(0, abs(self.pAttack()))
                        self.pDefend(dmg)
                    hinder["turn"] += 1

        return -1

    def isPassiveOn(self, turn=-1):
        if self.level >= 18:
            match self.kind:
                case "Warlord":
                    if turn % 3 == 0:
                        return True
                case "Hunter":
                    if turn % 3 == 0:
                        return True
                case "Sourcerer":
                    return True
        return False


class PlayerHero(Character):
    def __init__(self, data, manager):
        super().__init__(data, manager, is_bad=False, is_player=True)


class Monster(Character):
    def __init__(self, data, manager, exp: int, gold: int, stats: list=None):
        super().__init__(data, manager, is_bad=True, is_player=False, stats=stats)

        self.exp = exp
        self.gold = gold

    def die(self):
        self.state = "Idle"
        self.is_dead = False
        return self.exp, self.gold


class WeakMonster:
    def __init__(self):
        # combat stats
        self.lvl = 1
        self.name = "Monster - goblin"
        self.arts = {"bite": 2, "launch attack": 3}

        # combat stats
        self.life = 10*(self.lvl+2)**2
        self.stamina = 5*(-2*self.lvl-1)**2 + 10*(self.lvl+1)
        self.arcana = 5*(-2*self.lvl-1)**2 + 10*(self.lvl+1)
        self.power = 10*(self.lvl+2)**2

        # combat mechanics
        self.state = "attack"
        print(self.name+" is created.")
        self.display_info()

    def display_info(self):
        print("statistics:")
        print("life:", self.life)
        print("stamina:", self.stamina)
        print("arcana:", self.arcana)
        print("power:", self.power)
        print("arts:", self.arts)

    def changeState(self):
        states = ["attack", "art", "defend"]
        self.state = chs(states)

    def act(self):
        match self.state:
            case "attack":
                return self.power
            case "art":
                return self.power * chs([a for a in self.arts.values()])
