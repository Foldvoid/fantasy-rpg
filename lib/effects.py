from lib.render_tools import *


class GEffect(pygame.sprite.Sprite):
    def __init__(self, manager, name):  # add sprite group | object
        super(GEffect, self).__init__()

        self.manager = manager
        self.name = name
        self.frame = 0
        self.pos = (0, 0)

        sprites = loadSprites()
        self.sprite_sheet = sprites[2]
        self.animation = self.sprite_sheet[self.name]["Sprite"]
        self.sprite_frame = pygame.transform.scale(get_frame(self.animation, self.sprite_sheet[self.name]["Size"][0],
                                                             self.sprite_sheet[self.name]["Size"][0],
                                                             [self.frame, 0]), (300, 300)).convert_alpha()

        self.is_active = False

    def animate(self):
        self.animation = self.sprite_sheet[self.name]["Sprite"]
        self.sprite_frame = pygame.transform.scale(get_frame(self.animation, self.sprite_sheet[self.name]["Size"][0],
                                                             self.sprite_sheet[self.name]["Size"][1],
                                                             [self.frame, 0]), (300, 300)).convert_alpha()
        return self.sprite_frame

    def getAnimationFrames(self):
        frame_width = self.sprite_sheet[self.name]["Size"][0]
        return self.animation.get_width() // frame_width

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.frame = 0
        self.is_active = False
        return self.name


class Skills:
    def __init__(self, manager):
        self.Physical = {
            "valiant-slash": {"effect": GEffect(manager, "valiant-slash"), "name": "valiant-slash", "type": "ignore armour"},
            "aura-cleave": {"effect": GEffect(manager, "aura-cleave"), "name": "aura-cleave", "type": "ignore evasion"},
            "astral-shred": {"effect": GEffect(manager, "astral-shred"), "name": "astral-shred",
                             "type": "use opp mana"},
            "spectral-duel": {"effect": GEffect(manager, "spectral-duel"), "name": "spectral-duel",
                              "type": "damage n times"},
            "vanguards-stance": {"effect": GEffect(manager, "vanguards-stance"), "name": "vanguards-stance",
                                 "type": "add health"},
            "ancestors-protection": {"effect": GEffect(manager, "ancestors-protection"), "name": "ancestors-protection",
                                     "type": "tradeoff"},
            "aggression": {"name": "aggression", "type": "tradeoff", "isOn": False},
            "blood-thirst": {"effect": GEffect(manager, "blood-thirst"), "effectu": GEffect(manager, "blood-thirstu"),
                             "name": "blood-thirst", "type": "countdown", "count": 0},
            "true-vigor": {"effect": GEffect(manager, "true-strength"), "name": "true-vigor", "type": "boost stats",
                           "lock": {
                               "1": {"ar": 1}, "2": {"ar": 1, "con": 10}, "3": {"ar": 1, "con": 10, "str": 10},
                               "4": {"ar": 1, "con": 10, "str": 10, "ev": 10},
                               "5": {"ar": 1, "con": 20, "str": 10, "ev": 10, "end": 10}
                           }, "lock_idx": 1
                           },
            # Hunter skills
            "better-position": {"effect": GEffect(manager, "better-position"), "type": "absorb damage",
                                "name": "better-position"},
            "perception": {"name": "perception", "type": "tradeoff", "isOn": False},
            "true-speed": {"effect": GEffect(manager, "true-speed"), "name": "true-speed", "type": "boost stats",
                           "lock": {
                               "1": {"ar": 1}, "2": {"ar": 1, "fai": 10}, "3": {"ar": 1, "fai": 10, "cun": 10},
                               "4": {"ar": 1, "fai": 10, "cun": 10, "ev": 10},
                               "5": {"ar": 1, "fai": 20, "cun": 10, "ev": 10, "fin": 10}
                           }, "lock_idx": 1
                           }
        }

        self.Magical = {
            "psychic-storm": {"effect": GEffect(manager, "psychic-storm"), "type": "weaken opp",
                              "name": "psychic-storm"},
            "cloud-mind": {"effect": GEffect(manager, "cloud-mind"), "type": "con damage", "name": "cloud-mind"},
            "tears-ripple": {"effect": GEffect(manager, "tears-ripple"), "type": "damage over time",
                             "name": "tears-ripple"},
            "diamond-dust": {"effect": GEffect(manager, "diamond-dust"), "type": "weaken opp", "name": "diamond-dust"},
            "arcane-barrier": {"effect": GEffect(manager, "arcane-barrier"), "type": "tradeoff",
                               "name": "arcane-barrier"},
            "aegis-shield": {"effect": GEffect(manager, "aegis-shield"), "type": "tradeoff", "name": "aegis-shield"},
            "blood-magic": {"name": "aggression", "type": "tradeoff", "isOn": False},
            "arcane-frenzy": {"effect": GEffect(manager, "arcane-frenzy"), "type": "damage n times",
                              "name": "arcane-frenzy"},
            "true-spirit": {"effect": GEffect(manager, "true-spirit"), "name": "true-spirit", "type": "boost stats",
                            "lock": {
                                "1": {"ar": 1}, "2": {"ar": 1, "wis": 10}, "3": {"ar": 1, "wis": 10, "int": 10},
                                "4": {"ar": 1, "wis": 10, "int": 10, "ev": 10},
                                "5": {"ar": 1, "wis": 20, "int": 10, "ev": 10, "wil": 10}
                            }, "lock_idx": 1
            },
            # Hunter skills
            "fire-shot": {"effect": GEffect(manager, "fire-shot"), "type": "hunter skill", "name": "fire-shot"},
            "ice-shot": {"effect": GEffect(manager, "ice-shot"), "type": "hunter skill", "name": "ice-shot"},
            "thunder-shot": {"effect": GEffect(manager, "thunder-shot"), "type": "hunter skill",
                             "name": "thunder-shot"},
            "rose-thorns": {"effect": GEffect(manager, "rose-thorns"), "type": "hunter skill", "name": "rose-thorns"},
            "lightning-shock": {"effect": GEffect(manager, "lightning-shock"), "type": "hunter skill",
                                "name": "lightning-shock"},
            "dark-bolt": {"effect": GEffect(manager, "dark-bolt"), "type": "hunter skill", "name": "dark-bolt"},
        }

        self.Transcendence = {
            "Warlord": {"effect": GEffect(manager, "warlord_transcendence"), "type": "transcendence", "locks_needed": 5},
            "Sourcerer": {"effect": GEffect(manager, "sourcerer_transcendence"), "type": "transcendence", "locks_needed": 5},
            "Hunter": {"effect": GEffect(manager, "hunter_transcendence"), "type": "transcendence", "locks_needed": 5}
        }

    def getSkill(self, name, is_physical=True):
        if is_physical and name in self.Physical:
            return self.Physical[name]
        elif not is_physical and name in self.Magical:
            return self.Magical[name]

    def transcend(self, kind):
        return self.Transcendence[kind]

    def getEffect(self, name, is_physical=True):
        if is_physical and name in self.Physical:
            return self.Physical[name]["effect"]
        elif not is_physical and name in self.Magical:
            return self.Magical[name]["effect"]

    def getType(self, name, is_physical=True):
        if is_physical and name in self.Physical:
            return self.Physical[name]["type"]
        elif not is_physical and name in self.Magical:
            return self.Magical[name]["type"]
