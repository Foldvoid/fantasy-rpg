import math
import random
from functools import reduce

import pygame.image

import source.mapgen as mapgen

print("Loading environment...")

WIDTH, HEIGHT = mapgen.WIDTH, mapgen.HEIGHT

turn = 0
location_world = [0, 0]
location_region = [0, 0]
region_name = "None"
chaos_level = 1
chaos_offset = 100

encounter = 0  # 0 - 100(%)
building_type = "Outpost"
building_name = None
structure = {"count": 0, "forts": 0, "camps": 0, "Fort": {}, "Camp": {
    (0, 0): {  # World Location
        "Wood": [-1, None],  # Workers, Region Location
        "Stone": [-1, None],
        "Metal": [-1, None],
        "Gems": [-1, None]
        }
    }
}

men_power = {"Workers": 0, "Soldiers": 0, "Max Workers": 0, "Max Soldiers": 0,
             "Total Workers": 0, "Total Soldiers": 0}
military_camp = None

BuildTech = {
    "Outpost": {
        "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
        "BaseStats": {"Security": 10, "Control": 10, "Quality": 10,
                      "MaxWorkers": 10, "RecruitAllowed": 20, "RecruitCost": 1000}
    },
    "Fort": {
        "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
        "BaseStats": {"Security": 30, "Control": 30, "Quality": 30,
                      "MaxWorkers": 30, "RecruitAllowed": 48, "RecruitCost": 1200}
    },
    "Citadel": {
        "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
        "BaseStats": {"Security": 60, "Control": 60, "Quality": 60,
                      "MaxWorkers": 60, "RecruitAllowed": 100, "RecruitCost": 2000}
    },
    "Castle": {
        "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
        "BaseStats": {"Security": 20, "Control": 20, "Quality": 20,
                      "MaxWorkers": 20, "RecruitAllowed": 66, "RecruitCost": 2200}
    },
    "City": {
        "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
        "BaseStats": {"Security": 40, "Control": 40, "Quality": 40,
                      "MaxWorkers": 40, "RecruitAllowed": 120, "RecruitCost": 3000}
    },
    "SubBuildings": {
        "FirstTier": {
            "Tents": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": None,
                "Bonuses": {"MaxVillagers": 10, "RecruitAllowed": 10},
                "Unlocks": "Cottages"
            },
            "Cottages": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": "Tents",
                "Bonuses": {"MaxVillagers": 30, "RecruitAllowed": 50},
                "Unlocks": "Houses"
            },
            "Houses": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": "Cottages",
                "Bonuses": {"MaxVillagers": 80, "RecruitAllowed": 150}
            },
            "Palisade": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": None,
                "Bonuses": {"Security": 10},
                "Unlocks": "Stone Walls"
            },
            "Unique": {
                "TownHall": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Security": 10, "RecruitCost": 400, "MaxVillagers": 30},
                    "Unlocks": "Chambers, Castle"
                },
                "Castle": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "TownHall"
                },
                "Fortified Walls": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Security": 20},
                    "Unlocks": "Fort"
                },
                "Fort": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "Fortified Walls"
                },
            }
        },
        "SecondTier": {
            "Stone Walls": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": "Palisade",
                "Bonuses": {"Security": 100}
            },
            "Archer Towers": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": None,
                "Bonuses": {"Control": 100, "Quality": 100, "Garrison": 200},
                "Unlocks": "Crossbow Pillboxes"
            },
            "Crossbow Pillboxes": {
                "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                "Require": "Archer Towers",
                "Bonuses": {"Security": 50, "Control": 200, "Quality": 200}
            },
            "Castle": {
                "Chambers": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"MaxVillagers": 30, "RecruitCost": 200}
                },
                "Bazaar": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Income": 50},
                    "Unlocks": "Merchants Guild"
                },
                "Merchants Guild": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "Bazaar",
                    "Bonuses": {"Income": 150, "RecruitCost": 300},
                    "Unlocks": "City"
                },
                "City": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "Merchants Guild"
                }
            },
            "Fort": {
                "Ballistas": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Control": 300, "Quality": 300, "Garrison": 300}
                },
                "Catapults": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Control": 500, "Quality": 500}
                },
                "Workshop": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Quality": 800},
                    "Unlocks": "Artisans Guild"
                },
                "Artisans Guild": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "Workshop",
                    "Bonuses": {"Quality": 1200},
                    "Unlocks": "Citadel"
                },
                "Citadel": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": "Artisans Guild"
                }
            }
        },
        "ThirdTier": {
            "City": {
                "Trade Root": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Quality": 200}
                },
                "Royal Palace": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Security": 800}
                }
            },
            "Citadel": {
                "Manors": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Security": 400, "MaxVillagers": 200}
                },
                "WarHall": {
                    "Cost": {"Gold": 0, "Wood": 0, "Stone": 0, "Metal": 0, "Gems": 0},
                    "Require": None,
                    "Bonuses": {"Control": 200, "Quality": 200}
                }
            }
        }

    }
}

resource = {"Wood": 0, "Stone": 0, "Metal": 0, "Gem": 0}
total_men_power = {"Workers": 0, "Soldiers": 0}
artifacts = list()


def placeMilitaryCamp(amount: int, power: int):
    global military_camp, player
    military_camp = {"WorldLocation": tuple(location_world),
                        "RegionLocation": tuple(location_region),
                        "Amount": amount, "Power": power}

    (game_map.regions[location_world[1]][location_world[0]]
    [location_region[1]][location_region[0]]) = 'm'
    player.army_amount, player.army_power = 0, 0
    player.army_trained = False
    calcEnvData()


def disbandMilitaryCamp():
    global military_camp
    wld_loc, rgn_loc = military_camp["WorldLocation"], military_camp["RegionLocation"]
    (game_map.regions[wld_loc[1]][wld_loc[0]]
    [rgn_loc[1]][rgn_loc[0]]) = '-'
    military_camp = None


def addToMilitaryCamp(amount: int, power: int):
    military_camp["Amount"] += amount
    military_camp["Power"] += power
    player.army_trained = False


def printResources():
    print(" | ".join(map(lambda x, y: x + ": " + str(y), resource.keys(), resource.values())))


def printMenPower():
    print(" | ".join(map(lambda x, y: x + ": " + str(y), men_power.keys(), men_power.values())))


def countForts(world_loc: tuple):
    if len(world_loc) > 2:
        raise Exception("Need to have exactly 2 coordinates!")
    else:
        count = 0
        for item in structure["Fort"]:
            if structure["Fort"][item]["WorldLocation"] == world_loc:
                count += 1
        return count


def countInRegion(region: str):
    count = 0
    for item in structure["Fort"]:
        if structure["Fort"][item]["RegionName"] == region:
            count += 1
    return count


class GameMap:
    def __init__(self, width: int, height: int, regions: int, region_names: tuple):
        self.width = width
        self.height = height
        self.regions_num = regions
        self.region_names = region_names

        # lists of region names, region tile types and region info
        self.world, self.regions, self.region_info = mapgen.createMap(width, height, regions, region_names)

    def getAreaPositions(self):
        areas = {}
        for i in range(len(self.world)):
            for j in range(len(self.world[i])):
                if self.world[i][j] in areas:
                    if areas[self.world[i][j]][1] != (-1, -1):
                        x, y = areas[self.world[i][j]][1]
                        if j >= x and i >= y:
                            areas[self.world[i][j]][1] = (j, i)
                    else:
                        areas[self.world[i][j]][1] = (j, i)
                else:
                    areas[self.world[i][j]] = [(j, i), (-1, -1)]

        return areas


def initialize(width: int, height: int, regions: int):
    global game_map
    region_names = ('Eslavih', 'Tinquet', 'Lapier', 'Nowemet', 'Veirgn', 'Oequanil', 'Gowdarat', 'Hovtimber', 'Keprel')

    game_map = GameMap(width, height, regions, region_names)


game_map = None
initialize(3, 3, 3)

class Structure:
    def __init__(self):
        pass


def countWorkers():
    men_power["Total Workers"] = 0
    men_power["Workers"] = 0
    for camp in structure["Camp"]:
        for workers in structure["Camp"][camp]:
            if structure["Camp"][camp][workers][0] > 0:
                men_power["Total Workers"] += structure["Camp"][camp][workers][0]
            if camp == tuple(location_world):
                men_power["Workers"] += structure["Camp"][camp][workers][0]


def getWorkersInStructure():
    return structure["Fort"][building_name]["Workers"]


def setWorkersInStructure(workers):
    structure["Fort"][building_name]["Workers"] = workers


def getMaxWorkersInStructure():
    return structure["Fort"][building_name]["MaxWorkers"]


def setMaxWorkersInStructure(workers):
    structure["Fort"][building_name]["MaxWorkers"] = workers


def countSoldiers():
    men_power["Total Soldiers"] = 0
    men_power["Soldiers"] = 0
    for struc in structure["Fort"]:
        men_power["Total Soldiers"] += structure["Fort"][struc]["Garrison"]
        if structure["Fort"][struc]["WorldLocation"] == tuple(location_world):
            men_power["Soldiers"] += structure["Fort"][struc]["Garrison"]

    men_power["Workers"] = 0
    camp = structure["Camp"][tuple(location_world)]
    for struc in camp:
        if camp[struc][0] > -1:
            structure["count"] += 1
            structure["camps"] += 1
            men_power["Workers"] += camp[struc][0]


def campExists(area_type: str):
    camp = structure["Camp"][tuple(location_world)]
    if tuple(location_world) in structure["Camp"]:
        return camp[area_type][1] is None


def updateCamps():
    if tuple(location_world) not in structure["Camp"]:
        structure["Camp"][tuple(location_world)] = \
            {
                "Wood": [-1, None],
                "Stone": [-1, None],
                "Metal": [-1, None],
                "Gems": [-1, None]
            }


def countGarrison():
    for struc in structure["Fort"]:
        if (structure["Fort"][struc]["WorldLocation"] == tuple(location_world) and
                structure["Fort"][struc]["RegionLocation"] == tuple(location_region)):
            return structure["Fort"][struc]["Garrison"]


def getAllowedRecruit():
    return structure["Fort"][building_name]["RecruitAllowed"]


def addAllowedRecruit(recruit):
    structure["Fort"][building_name]["RecruitAllowed"] += recruit


def addGarrison(soldiers: int):
    if player.gold >= structure["Fort"][building_name]["RecruitCost"]:
        structure["Fort"][building_name]["Garrison"] += soldiers
        player.gold -= structure["Fort"][building_name]["RecruitCost"]
    else:
        print("Not enough gold to garrison!")
        print("Gold needed: " + str(structure["Fort"][building_name]["RecruitCost"] - player.gold))


def getRecruitCost():
    return structure["Fort"][building_name]["RecruitCost"]


def setRecruitCost(cost):
    structure["Fort"][building_name]["RecruitCost"] = cost


def getGarrisoned():
    return structure["Fort"][building_name]["Garrison"]


def setGarrisoned(amount: int):
    structure["Fort"][building_name]["Garrison"] = amount


def getSecurity():
    return structure["Fort"][building_name]["Security"]


def addSecurity(num):
    structure["Fort"][building_name]["Security"] += num


def getControl():
    return structure["Fort"][building_name]["Control"]


def addControl(num):
    structure["Fort"][building_name]["Control"] += num


def getQuality():
    return structure["Fort"][building_name]["Quality"]


def addQuality(num):
    structure["Fort"][building_name]["Quality"] += num


def countStructures():
    structure["count"] = 0
    structure["forts"] = 0
    structure["camps"] = 0
    for struc in structure["Fort"]:
        structure["count"] += 1
        structure["forts"] += 1


def calcEnvData():
    countStructures()
    updateCamps()
    countWorkers()
    countSoldiers()


def addStructure(area_type: str, stype: str):
    if stype in ("Fortification", "Encampment") and game_map:
        if not building_name and stype != "Encampment":
            raise Exception("Structure must have a name!")
        elif chaos_level > 1:
            raise Exception("Can't build in chaotic places")
        elif stype == "Fortification":
            if building_name in structure["Fort"]:
                raise Exception(f"Fortification name: {building_name} already exists!")
            elif area_type != "Stable":
                raise Exception("Area is unstable!")
            else:
                structure["Fort"][building_name] = {
                    "Grade": building_type,
                    "RegionName": region_name,
                    "WorldLocation": tuple(location_world),
                    "RegionLocation": tuple(location_region),
                    "Built": [],
                    "RecruitAllowed": BuildTech[building_type]["BaseStats"]["RecruitAllowed"],
                    "RecruitCost": BuildTech[building_type]["BaseStats"]["RecruitCost"],
                    "Garrison": 0,
                    "Workers": 0,
                    "MaxWorkers": BuildTech[building_type]["BaseStats"]["MaxWorkers"],
                    "Security": BuildTech[building_type]["BaseStats"]["Security"],
                    "Control": BuildTech[building_type]["BaseStats"]["Control"],
                    "Quality": BuildTech[building_type]["BaseStats"]["Quality"]
                }
                grades = {"Outpost": "o", "Fort": "f", "Castle": "c", "Citadel": "r", "City": "q"}
                (game_map.regions[location_world[1]][location_world[0]]
                    [location_region[1]][location_region[0]]) = grades[building_type]
                calcEnvData()
                return True

        elif stype == "Encampment":
            if area_type not in ("Wood", "Stone", "Metal", "Gems"):
                raise Exception("No such camp type!")
            else:
                resource_type = {"Wood": "w", "Stone": "s", "Metal": "t", "Gems": "g"}
                world, region = tuple(location_world), tuple(location_region)
                if world not in structure["Camp"]:
                    structure["Camp"][world] = {"Wood": [-1, None],
                                                "Stone": [-1, None],
                                                "Metal": [-1, None],
                                                "Gems": [-1, None]}
                if structure["Camp"][world][area_type][1] is None:
                    structure["Camp"][world][area_type] = [0, region]
                    (game_map.regions[location_world[1]][location_world[0]]
                        [location_region[1]][location_region[0]]) = resource_type[area_type]
                else:
                    print(f"Already have a {area_type} camp")
                    return False
                countStructures()
                return True
    else:
        raise Exception("No such structure type!")
    return False


def getStructureByLoc(loc: tuple):
    if len(loc) != 2:
        raise Exception("Invalid location, needs two arguments!")
    else:
        loc = tuple(loc)
        for item in structure["Fort"]:
            if structure["Fort"][item]["RegionLocation"] == loc:
                result = {"Name": item}
                for key, value in structure["Fort"][item].items():
                    result[key] = value
                return result
        for item in structure["Camp"]:
            if structure["Camp"][item]["RegionLocation"] == loc:
                result = {"Name": item}
                for key, value in structure["Camp"][item].items():
                    result[key] = value
                return result
        raise Exception("Structure not found!")


def getStructureName():
    for struc in structure["Fort"]:
        if structure["Fort"][struc]["WorldLocation"] == tuple(location_world) and \
                structure["Fort"][struc]["RegionLocation"] == tuple(location_region):
            return struc


def addGold(gold: int):
    player.gold += gold


def subGold(gold: int):
    if player.gold >= gold:
        player.gold -= gold
        return True
    return False


def subCost(gold: int, wood: int = 0, stone: int = 0, metal: int = 0, gems: int = 0):
    has_cost = True
    if player.gold < gold:
        has_cost = False

    if player.wood < wood:
        has_cost = False

    if player.stone < stone:
        has_cost = False

    if player.metal < metal:
        has_cost = False

    if player.gems < gems:
        has_cost = False

    if has_cost:
        player.gold -= gold
        player.wood -= wood
        player.stone -= stone
        player.metal -= metal
        player.gems -= gems
    return has_cost


def hasCost(gold: int, wood: int = 0, stone: int = 0, metal: int = 0, gems: int = 0):
    return player.gold > gold and \
            player.wood > wood and \
            player.stone > stone and \
            player.metal > metal and \
            player.gems > gems


def workResources():
    # Get workers income
    resources = ""
    for camps in structure['Camp'].values():
        for camp, value in camps.items():
            if value[1]:
                match camp:
                    case "Wood":
                        player.wood += value[0] * 0.5
                    case "Stone":
                        player.stone += value[0] * 0.3
                    case "Metal":
                        player.metal += value[0] * 0.2
                    case "Gems":
                        player.gems += value[0] * 0.1


def giveResource(resources=(0, 0, 0, 0)):
    str_resources = ""

    if resources[0] > 0:
        player.wood += resources[0]
        str_resources += "Wood: " + str(resources[0]) + "\n"
    if resources[1] > 0:
        player.stone += resources[1]
        str_resources = "Stone: " + str(resources[1]) + "\n"
    if resources[2] > 0:
        player.metal += resources[2]
        str_resources += "Metal: " + str(resources[2]) + "\n"
    if resources[3] > 0:
        player.gems += resources[3]
        str_resources += "Gems " + str(resources[3]) + "\n"

    return str_resources


def addBuilding(building):
    structure["Fort"][building_name]["Built"].append(building)


def getBuilt():
    return structure["Fort"][building_name]["Built"]


def getInfo():
    return structure["Fort"][building_name]["Security"], \
            structure["Fort"][building_name]["Control"], \
            structure["Fort"][building_name]["Quality"]


def upgradeStructure(grade):
    grades = {"Outpost": "o", "Fort": "f", "Castle": "c", "Citadel": "r", "City": "q"}
    if grade not in grades:
        raise Exception("Building Grade must be a valid fortification type!")
    else:
        grade_prev = structure["Fort"][building_name]["Grade"]
        structure["Fort"][building_name]["Grade"] = grade
        for stat in BuildTech[grade]["BaseStats"]:
            new_amount = BuildTech[grade]["BaseStats"][stat] - BuildTech[grade_prev]["BaseStats"][stat]
            structure["Fort"][building_name][stat] += new_amount

        (game_map.regions[location_world[1]][location_world[0]]
            [location_region[1]][location_region[0]]) = grades[grade]

        print(f"Grade updated to {grade}:{grades[grade]}")
        print(structure["Fort"][building_name]["Built"])
        calcEnvData()


class Item:
    def __init__(self, img_path, value, is_moving=False, amount=1):
        self.img = pygame.image.load(img_path)
        self.value = value
        self.is_moving = is_moving
        self.amount = amount


class InvSlot:
    def __init__(self, x, y, item=None):
        self.x, self.y = x, y
        self.size = (HEIGHT - (HEIGHT / 2 + HEIGHT / 3)) / 2
        # self.item = item


class PlayerMarker:
    def __init__(self, name, job):
        self.name = name
        self.job = job
        self.location = [location_world, location_region]
        self.destination = None
        self.income = 0
        self.ap = 3
        self.gold = 0
        self.wood = 0
        self.stone = 0
        self.metal = 0
        self.gems = 0

        size = (HEIGHT - (HEIGHT / 2 + HEIGHT / 3)) / 2 if HEIGHT <= 600 else 120
        space_y = size / 2
        space_x = space_y
        middle = WIDTH / 3 - WIDTH / 16 - 2 * space_y
        space_btw = (middle - 3 * size) / 2

        self.equipment_slots = [InvSlot(space_x, space_y),
                                InvSlot(space_x + space_btw + size, space_y),
                                InvSlot(space_x + (space_btw + size) * 2, space_y)]

        self.army_amount = 0
        self.army_trained = False
        self.army_armour = 0
        self.army_weapon = 0

        self.updateArmyPower()

    def addArmyAmount(self, amount: int):
        self.army_amount += amount
        self.updateArmyPower()

    def setArmyAmount(self, amount: int):
        self.army_amount = amount
        self.updateArmyPower()

    def updateArmyPower(self):
        self.army_power = self.army_amount * 2 if self.army_trained else self.army_amount
        self.army_power += self.army_weapon * self.army_amount + self.army_armour * self.army_amount

    def getStructureByName(self, name: str):
        if name in structure["Fort"]:
            result = {"Name": name}
            for key, value in structure["Fort"][name].items():
                result[key] = value
            return result
        elif name in structure["Camp"]:
            result = {"Name": name}
            for key, value in structure["Camp"][name].items():
                result[key] = value
            return result
        else:
            return str("Structure not found!")

    def updateLocation(self):
        self.location[0] = location_world
        self.location[1] = location_region

    def useAction(self, ap=1):
        if self.ap >= ap:
            self.ap -= ap
            return self.ap + 1
        return -1

    def resetAction(self, ap=3):
        self.ap = ap

player = PlayerMarker("Player", "Warlord")
