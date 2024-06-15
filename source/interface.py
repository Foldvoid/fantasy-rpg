import copy
import re
import math
import random
import sys
from random import choice as chs
from random import randint as r_int
from ast import literal_eval
from importlib import reload

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame.locals import *
import json
import source.mapgen as play_map
import source.environment as environment
import lib.characters as characters
import lib.effects as effects
from lib.render_tools import *
from data.gfx.paths.sprite_paths import *

print("Loading interface...")

pygame.init()
WIDTH, HEIGHT = play_map.WIDTH, play_map.HEIGHT
TITLE = "Free Of Defeat"
FPS = 60
MUSIC_PATH = "./data/sfx/SBG_MUSIC/"
BG_MUSIC = ("Medieval1.mp3", "Medieval2.mp3", "Medieval3.mp3", "Medieval4.mp3", "Medieval5.mp3", "Medieval6.mp3"
            , "Medieval7.mp3", "Medieval8.mp3", "Medieval9.ogg", "Medieval10.ogg", "Medieval11.ogg", "Medieval12.ogg"
            , "Medieval13.ogg", "Medieval14.ogg", "Medieval15.ogg", "Medieval16.ogg", "Medieval17.ogg")

state = "Start Menu"  # starting screen state
clicked = False  # mouse click check
refreshed = False  # screen variables update
clock = pygame.time.Clock()
time_delta = 0

# Takes the interface screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

# Pygame_gui screen manager and objects
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
manager.get_theme().load_theme("./env/themes/localarea_menu.json")
manager.get_theme().load_theme("./env/themes/label.json")
manager.get_theme().load_theme("data/gfx/GUI/char_ui.json")
manager.get_theme().load_theme("data/gfx/GUI/battle_ui.json")
manager.get_theme().load_theme("./env/themes/battle_gui.json")
manager.get_theme().load_theme("./env/themes/tbx_gui.json")
manager.get_theme().load_theme("./env/themes/tbx_army.json")
manager.get_theme().load_theme("./env/themes/panel_gui.json")
manager.get_theme().load_theme("./env/themes/start_job.json")
manager.get_theme().load_theme("./env/themes/main_gui.json")


sfx_click = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_click_normal_2.wav")
sfx_equip = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_equip.ogg")
sfx_sell = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_sell.ogg")
sfx_inventory = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_inventory.ogg")
sfx_upgrade = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_upgrade.ogg")
sfx_settings = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_settings.ogg")
sfx_hit = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_blow.ogg")
sfx_miss = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_miss.ogg")
sfx_map = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_map.ogg")
sfx_move = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_move.ogg")
sfx_save = pygame.mixer.Sound("./data/sfx/SFX_GUI/game_save.ogg")
sfx_load = pygame.mixer.Sound("./data/sfx/SFX_GUI/game_load.ogg")
sfx_skill = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_skill.ogg")
sfx_attack = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_attack.ogg")
sfx_gameover = pygame.mixer.Sound("./data/sfx/SFX_GUI/game_over.ogg")
sfx_defeat = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_defeat.ogg")
sfx_victory = pygame.mixer.Sound("./data/sfx/SFX_GUI/battle_victory.ogg")
sfx_levelup = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_levelup.ogg")
sfx_built = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_built.ogg")
sfx_construct = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_construct.ogg")
sfx_cleansed = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_cleansed.ogg")
sfx_failcleanse = pygame.mixer.Sound("./data/sfx/SFX_GUI/gui_failcleanse.ogg")


music_idx = 1
is_music = True
music_volume = 100
sfx_volume = 100

pygame.mixer_music.load(os.path.join(MUSIC_PATH, BG_MUSIC[music_idx]))

pygame.mixer_music.play(-1)


# Event handler
def eventHandle():
    global clicked, state, inventory, music_idx, reward_window, world_map, region_map

    if not pygame.mixer_music.get_busy() and is_music:
        music_idx += 1
        if music_idx >= len(BG_MUSIC):
            music_idx = 0

        pygame.mixer_music.load(os.path.join(MUSIC_PATH, BG_MUSIC[music_idx]))
        pygame.mixer_music.play(-1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == "Start Menu":
                if event.button == 1:
                    clicked = True
                    if start_menu_screen.btn_play.active:
                        start_menu_screen.btn_play.getClicked()
                    if start_menu_screen.btn_load.active:
                        start_menu_screen.btn_load.getClicked()
                    if start_menu_screen.btn_exit.active:
                        start_menu_screen.btn_exit.getClicked()

            elif state == "Region":
                if event.button == 1 and region_map.btn_wmap.was_clicked:
                    clicked = True
                    sfx_map.play()
                    for alert in region_map.alerts:
                        alert.kill()
                        del alert
                    region_map.alerts.clear()
                    pygame.display.set_caption("World Map")
                    region_map.hide()

                    if inventory:
                        inventory.kill()
                        inventory = None
                        region_map.btn_inventory.switch(0)

                    state = "World"
                elif event.button == 1 and region_map.btn_inventory.was_clicked:
                    clicked = True
                    sfx_inventory.play()
                    if inventory:
                        inventory.kill()
                        inventory = None
                        region_map.btn_inventory.switch(0)
                    else:
                        inventory = Inventory()
                        region_map.btn_inventory.switch(1)
                elif event.button == 1 and region_map.btn_settings.was_clicked:
                    if not region_map.game_settings:
                        sfx_settings.play()
                        region_map.game_settings = GameSettings()
                elif region_map.window_test.is_displayed:
                    clicked = True
                    if region_map.window_test.collidepoint(event.pos) and \
                            not region_map.window_test.is_dragged and \
                            region_map.window_test.is_movable:
                        window = region_map.window_test
                        mouse_x, mouse_y = event.pos
                        window.offset_x, window.offset_y = window.x - mouse_x, window.y - mouse_y
                        window.is_dragged = True
                elif event.button == 1 and inventory:
                    mouse = event.pos
                    if inventory.box.rect.collidepoint(mouse) and \
                            not inventory.scroller.vert_scroll_bar.rect.collidepoint(mouse):

                        inventory.title.set_text("")
                        inventory.description.set_text("")
                        for slot in inventory.slots:
                            slot.selected.hide()
                        for slot in inventory.slots:
                            if slot.image.rect.collidepoint(mouse):
                                slot.selected.show()
                                if slot.item:
                                    showen_txt = f"Value: {slot.item.value}\n"
                                    showen_txt += slot.item.desc + "\n"
                                    showen_txt += slot.getStatsStr()

                                    inventory.title.set_text(slot.item.name)
                                    inventory.description.set_text(showen_txt)
                                break
                elif event.button == 3 and inventory:
                    mouse = event.pos
                    if inventory.box.rect.collidepoint(mouse):
                        selected = None
                        for slot in inventory.slots:
                            if slot.selected.visible:
                                selected = slot
                                break
                        for slot in inventory.slots:
                            if selected and slot.image.rect.collidepoint(mouse):
                                temp = copy.copy(slot.item)

                                slot.delItem()
                                slot.setItem(copy.copy(selected.item))
                                selected.delItem()
                                selected.setItem(temp)

                                if selected.item:
                                    selected.item.slot_id = selected.slot_id
                                    main_character.inventory.delItem(selected.slot_id)
                                    main_character.inventory.insertItem(selected.item)
                                else:
                                    main_character.inventory.delItem(selected.slot_id)
                                if slot.item:
                                    slot.item.slot_id = slot.slot_id
                                    main_character.inventory.delItem(slot.slot_id)
                                    main_character.inventory.insertItem(slot.item)

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if not pygame.mixer.get_busy():
                sfx_click.play()

            if start_menu_screen.start_window.alive():
                window = start_menu_screen.start_window
                if event.ui_element == window.btn_Warlord:
                    environment.player.job = "Warlord"
                    window.btn_Warlord.select()
                    window.btn_Sourcerer.unselect()
                    window.btn_Hunter.unselect()
                elif event.ui_element == window.btn_Sourcerer:
                    environment.player.job = "Sourcerer"
                    window.btn_Warlord.unselect()
                    window.btn_Sourcerer.select()
                    window.btn_Hunter.unselect()
                elif event.ui_element == window.btn_Hunter:
                    environment.player.job = "Hunter"
                    window.btn_Warlord.unselect()
                    window.btn_Sourcerer.unselect()
                    window.btn_Hunter.select()

                elif event.ui_element == window.btn_done:
                    if window.btn_Warlord.is_selected or \
                            window.btn_Sourcerer.is_selected or \
                            window.btn_Hunter.is_selected:
                        initialize(window.drop_menu.selected_option)
                        window.kill()
                        state = "Region"

            elif inventory and event.ui_element == inventory.btn_sell:
                for slot in inventory.slots:
                    if slot.selected.visible and slot.item:
                        main_character.inventory.delItem(slot.slot_id)
                        slot.sell()
                        inventory.title.set_text("")
                        inventory.description.set_text("")
                        region_map.updateInfo()  # Check later
                        sfx_sell.play()

            elif inventory and event.ui_element == inventory.btn_equip:
                for slot in inventory.slots:
                    if slot.selected.visible and slot.item:
                        if slot.item.equipped_on:
                            match slot.item.equipped_on:
                                case "Hand":
                                    temp = main_character.hand
                                    main_character.hand = copy.copy(slot.item)
                                    main_character.inventory.delItem(slot.slot_id)
                                    slot.delItem()
                                    inventory.title.set_text("")
                                    inventory.description.set_text("")
                                    if temp:
                                        slot.setItem(temp)
                                        slot.item.slot_id = slot.slot_id
                                        main_character.inventory.insertItem(temp)

                                        showen_txt = f"Value: {temp.value}\n"
                                        showen_txt += temp.desc + "\n"
                                        showen_txt += slot.getStatsStr()

                                        inventory.title.set_text(slot.item.name)
                                        inventory.description.set_text(showen_txt)
                                    sfx_equip.play()
                                case "Torso":
                                    temp = main_character.torso
                                    main_character.torso = copy.copy(slot.item)
                                    main_character.inventory.delItem(slot.slot_id)
                                    slot.delItem()
                                    inventory.title.set_text("")
                                    inventory.description.set_text("")
                                    if temp:
                                        slot.setItem(temp)
                                        slot.item.slot_id = slot.slot_id
                                        main_character.inventory.insertItem(temp)

                                        showen_txt = f"Value: {temp.value}\n"
                                        showen_txt += temp.desc + "\n"
                                        showen_txt += slot.getStatsStr()

                                        inventory.title.set_text(slot.item.name)
                                        inventory.description.set_text(showen_txt)
                                    sfx_equip.play()
                                case "Accessory":
                                    temp = main_character.accessory
                                    main_character.accessory = copy.copy(slot.item)
                                    main_character.inventory.delItem(slot.slot_id)
                                    slot.delItem()
                                    inventory.title.set_text("")
                                    inventory.description.set_text("")
                                    if temp:
                                        slot.setItem(temp)
                                        slot.item.slot_id = slot.slot_id
                                        main_character.inventory.insertItem(temp)

                                        showen_txt = f"Value: {temp.value}\n"
                                        showen_txt += temp.desc + "\n"
                                        showen_txt += slot.getStatsStr()

                                        inventory.title.set_text(slot.item.name)
                                        inventory.description.set_text(showen_txt)
                                    sfx_equip.play()
                        main_character.updateStats()
                        region_map.updateInfo()

            elif reward_window and event.ui_element == reward_window.btn_confirm:
                reward_window.kill()
                reward_window = None

        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = False
            if state == "Region" and event.button == 1:
                region_map.window_test.is_dragged = False

        elif event.type == pygame.MOUSEMOTION:
            if state == "Region" and region_map.window_test.is_dragged:
                window = region_map.window_test
                mouse_x, mouse_y = event.pos
                window.x = mouse_x + window.offset_x
                window.y = mouse_y + window.offset_y

        # Separate events using screen states
        if state == "World":
            if event.type == KEYUP:
                if event.key == K_g:
                    world_map.is_show_borders = not world_map.is_show_borders
        elif state == "Region":
            if event.type == KEYUP:
                if event.key == K_g and not region_map.text_input.cursor_on:  # toggle gui
                    region_map.gui = not region_map.gui
                    region_map.setLocation(environment.location_world)
                elif event.key == K_h and not region_map.text_input.cursor_on:  # temporary for debug
                    if region_map.text_input.visible:
                        region_map.text_input.hide()
                    else:
                        region_map.text_input.show()
                elif event.key == K_j:
                    if pygame.mixer_music.get_busy():
                        pygame.mixer_music.fadeout(3000)
                elif event.key == K_i and not region_map.text_input.cursor_on:
                    if inventory:
                        inventory.kill()
                        inventory = None
                        region_map.btn_inventory.switch(0)
                    else:
                        inventory = Inventory()
                        region_map.btn_inventory.switch(1)
                elif event.key == K_k and not region_map.text_input.cursor_on:  # temporary for debug
                    if inventory:
                        inventory.findOpenSlot()
                elif event.key == K_s and not region_map.text_input.cursor_on:  # temporary for debug
                    saveGame()
                    pygame.quit()
                    sys.exit(0)
            # Text input used for debug
            elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == region_map.text_input:
                text = region_map.text_input.text
                if text.count(' ') == 1 and text.split()[0] == "Gold":
                    try:
                        environment.addGold(int(text.split()[1]))
                    except ValueError:
                        print("Accepts values only!")
                    except Exception as e:
                        print(type(e), ':', e)
                    region_map.updateInfo()
                elif text.count(' ') == 1 and text.split()[0] in ("Wood", "Stone", "Metal", "Gems"):
                    try:
                        type, amount = text.split()
                        match type:
                            case "Wood":
                                environment.player.wood += int(amount)
                            case "Stone":
                                environment.player.stone += int(amount)
                            case "Metal":
                                environment.player.metal += int(amount)
                            case "Gems":
                                environment.player.gems += int(amount)
                        region_map.updateInfo()

                    except ValueError as e:
                        print("Accepts values only!")
                    except Exception as e:
                        print(type(e), ':', e)
                elif text in ("Wood", "Stone", "Metal", "Gems"):
                    environment.building_type = text
                elif text.count(' ') == 1 and text.split()[0] in ("Outpost", "Fort", "Castle", "Citadel", "City"):
                    environment.building_type, environment.building_name = text.split()
                elif text.count(' ') == 1 and "Battle" in text:
                    battle, toggle = text.split()
                    if battle == "Battle":
                        if toggle == "On":
                            region_map.is_battle = True
                            print("Battle is now on")
                        elif toggle == "Off":
                            region_map.is_battle = False
                            print("Battle is now off")
                else:
                    print("No such command")
                region_map.text_input.clear()
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if not pygame.mixer.get_busy():
                    sfx_click.play()

                if event.ui_element == region_map.btn_army:
                    if not region_map.btn_army.is_selected:
                        region_map.btn_army.select()
                    else:
                        region_map.btn_army.unselect()

                for alert in region_map.alerts:
                    if alert.alert_type == "Entry":
                        if event.ui_element == alert.btn_confirm:
                            #alert.confirm()
                            region_map.travel()
                            region_map.alerts.remove(alert)
                            alert.kill()

                        elif event.ui_element == alert.btn_cancel:
                            region_map.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    else:
                        if event.ui_element == alert.btn_confirm:
                            alert.confirm()
                            region_map.alerts.remove(alert)
                            alert.kill()
                            exitLocal()

                        elif event.ui_element == alert.btn_cancel:
                            region_map.alerts.remove(alert)
                            alert.kill()

                    alert.handleEvent(event)

                if region_map.game_settings:
                    basic_setting = region_map.game_settings.handleEvent(event)
                    if basic_setting and event.ui_element == region_map.game_settings.btn_close:
                        region_map.game_settings.kill()
                        del region_map.game_settings
                        region_map.game_settings = None
                    elif basic_setting and event.ui_element == region_map.game_settings.btn_exit:
                        pygame.quit()
                        sys.exit(0)

                if region_map.alert_level_up:
                    alert = region_map.alert_level_up
                    if event.ui_element == alert.btn_confirm and alert.points == 0:
                        main_character.con_max += int(alert.lbl_con.text)
                        main_character.wis_max += int(alert.lbl_wis.text)
                        main_character.fai_max += int(alert.lbl_fai.text)
                        main_character.bonus_value_max += int(alert.lbl_bonus.text)
                        main_character.str_max += int(alert.lbl_str.text)
                        main_character.int_max += int(alert.lbl_int.text)
                        main_character.cun_max += int(alert.lbl_cun.text)

                        main_character.updateStats()
                        region_map.updateInfo()

                        alert.kill()
                        region_map.alert_level_up = None
                    elif event.ui_element == alert.btn_reset:
                        alert.points += int(alert.lbl_con.text)
                        alert.points += int(alert.lbl_wis.text)
                        alert.points += int(alert.lbl_fai.text)
                        alert.points += int(alert.lbl_bonus.text)
                        alert.points += int(alert.lbl_str.text)
                        alert.points += int(alert.lbl_int.text)
                        alert.points += int(alert.lbl_cun.text)

                        alert.lbl_con.set_text('0')
                        alert.lbl_wis.set_text('0')
                        alert.lbl_fai.set_text('0')
                        alert.lbl_bonus.set_text('0')
                        alert.lbl_str.set_text('0')
                        alert.lbl_int.set_text('0')
                        alert.lbl_cun.set_text('0')

                        alert.lbl_points.set_text(f"Points: {alert.points}")
                    else:
                        alert.pickStat(event.ui_element.text)

        elif state == "Local":
            # Action-Menu functionality
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if not pygame.mixer.get_busy():
                    sfx_click.play()

                for button in local_region.menu.btn_actions:
                    if event.ui_element == button:
                        if button.text == "Manage Workers":
                            local_region.menu.openSubmenu(button.text)
                        elif button.text == "Manage Army":
                            local_region.menu.openSubmenu(button.text)
                        elif button.text == "Merchants":
                            local_region.menu.openSubmenu(button.text)
                        elif button.text == "Blacksmith":
                            local_region.menu.openSubmenu(button.text)
                        elif button.text == "Outpost":
                            local_region.menu.openAlert("Stable")
                        elif button.text in ("Lumber camp", "Stone query", "Metal query", "Gems query"):
                            match button.text:
                                case "Lumber camp":
                                    local_region.menu.openAlert("Wood")
                                case "Stone query":
                                    local_region.menu.openAlert("Stone")
                                case "Metal query":
                                    local_region.menu.openAlert("Metal")
                                case "Gems query":
                                    local_region.menu.openAlert("Gems")
                        elif button.text == "Travel":
                            region_map.travel()
                        elif button.text == "Explore area":
                            if environment.player.useAction() > 0:
                                results = ("Monster", "Gold", "Resources", "Refuges", "Artifact")
                                probabilities = (45, 25, 17, 3)
                                roll = random.randint(1, 100)
                                result = "You found "
                                if roll >= probabilities[0]:
                                    # monster encounter
                                    exitLocal()
                                    region_map.hide()
                                    for alert in region_map.alerts:
                                        alert.kill()
                                    region_map.alerts.clear()
                                    battle_screen.startBattle()
                                    battle_screen.show()
                                    state = "Battle"
                                elif probabilities[0] > roll >= probabilities[1]:
                                    print(result + "gold!")
                                    reward_exp = 5
                                    reward_gold = r_int(20, 1000)
                                    if reward_window:
                                        reward_window.kill()
                                    getRewarded(reward_exp, reward_gold)
                                    reward_window = RewardWindow(reward_exp, reward_gold)
                                elif probabilities[1] > roll >= probabilities[2]:
                                    print(result + "resources!")
                                    local_region.menu.killAlerts()
                                    resources = ("Wood", "Stone", "Metal", "Gems")
                                    reward_resources = [0, 0, 0, 0]
                                    luck = r_int(1, 4)

                                    for i in range(luck):
                                        reward_resources[resources.index(chs(resources))] += r_int(2, 10)

                                    if reward_window:
                                        reward_window.kill()
                                    reward_window = RewardWindow(0, 0, resources=reward_resources)
                                elif probabilities[2] > roll >= probabilities[3]:
                                    amount = r_int(5, 15)
                                    print(result + str(amount) + " refuges!")
                                    local_region.menu.killAlerts()
                                    local_region.menu.openAlert("Rescued " + str(amount) + " refuges")
                                    environment.player.addArmyAmount(amount)

                                    region_map.updateTbx_Army()
                                else:
                                    print(result + "an artifact!")
                                    reward_itms = addItemsToInv(1)
                                    if reward_window:
                                        reward_window.kill()
                                    reward_window = RewardWindow(0, 0, reward_itms)

                                print("Roll: " + str(roll))
                            else:
                                print("Out of actions!")
                            local_region.updateAP()
                        elif button.text == "Train yourself":
                            local_region.menu.killAlerts()
                            local_region.menu.openAlert(button.text)
                            local_region.updateAP()
                        elif button.text == "Train units":
                            print("Training units...")
                            local_region.menu.killAlerts()
                            local_region.menu.openAlert(button.text)
                            local_region.updateAP()
                        elif button.text == "Break camp":
                            local_region.menu.killAlerts()
                            local_region.menu.openAlert(button.text)
                            main_character.current_health = main_character.health_capacity
                            main_character.mind.current_health = main_character.mind.health_capacity
                            local_region.updateAP()

                for button in local_region.menu.btn_upgrades:
                    if event.ui_element == button:
                        # Tier 1
                        if button.text in ("Tents", "Cottages", "Houses", "Palisade"):
                            local_region.menu.openAlert(button.text)
                        elif button.text in ("Fortified Walls", "TownHall", "Fort", "Castle"):
                            local_region.menu.openAlert(button.text)
                        # Tier 2
                        elif button.text in ("Stone Walls", "Archer Towers", "Crossbow Pillboxes"):
                            local_region.menu.openAlert(button.text)
                        # Castle
                        elif button.text in ("Chambers", "Bazaar", "Merchants Guild", "City"):
                            local_region.menu.openAlert(button.text)
                        # Fort
                        elif button.text in ("Ballistas", "Catapults", "Workshop", "Artisans Guild", "Citadel"):
                            local_region.menu.openAlert(button.text)
                        # Tier 3
                        # City
                        elif button.text in ("Trade Root", "Royal Palace"):
                            local_region.menu.openAlert(button.text)
                        # Citadel
                        elif button.text in ("Manors", "WarHall"):
                            local_region.menu.openAlert(button.text)

                # Action-Sub-Menu functionality
                for sub_menu in local_region.menu.sub_menus:
                    if sub_menu.menu_type == "Manage Workers":
                        if event.ui_element == sub_menu.btn_confirm:
                            sub_menu.confirm()
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        elif event.ui_element == sub_menu.btn_cancel:
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        sub_menu.handleEvent(event)

                        environment.calcEnvData()
                        sub_menu.updateMenu()
                    if sub_menu.menu_type == "Manage Army":
                        if event.ui_element == sub_menu.btn_confirm:
                            sub_menu.confirm()
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        elif event.ui_element == sub_menu.btn_cancel:
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        if event.ui_element == sub_menu.btn_recruit:
                            sub_menu.recruit()

                        sub_menu.handleEvent(event)

                        environment.calcEnvData()
                        sub_menu.updateMenu()
                    if sub_menu.menu_type == "Merchants":
                        if event.ui_element == sub_menu.btn_confirm:
                            sub_menu.confirm()
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        elif event.ui_element == sub_menu.btn_cancel:
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        sub_menu.handleEvent(event)

                        environment.calcEnvData()
                        sub_menu.updateMenu()
                    if sub_menu.menu_type == "Blacksmith":
                        if event.ui_element == sub_menu.btn_confirm:
                            sub_menu.confirm()
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        elif event.ui_element == sub_menu.btn_cancel:
                            local_region.menu.sub_menus.remove(sub_menu)
                            sub_menu.kill()

                        sub_menu.handleEvent(event)

                        environment.calcEnvData()
                        sub_menu.updateMenu()

                # Region alerts
                for alert in local_region.menu.alerts:
                    # Tier 1
                    # Basic
                    if alert.alert_type in ("Tents", "Cottages", "Houses", "Palisade"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False
                            match alert.alert_type:
                                case "Tents":
                                    enough_res = environment.hasCost(2000, 25, 5, 2)
                                case "Cottages":
                                    enough_res = environment.hasCost(10000, 150, 30, 14)
                                case "Houses":
                                    enough_res = environment.hasCost(100000, 2500, 400, 300)
                                case "Palisade":
                                    enough_res = environment.hasCost(22500, 2500, 40)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                local_region.refreshMenu()

                                local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Unique
                    elif alert.alert_type in ("TownHall", "Fortified Walls", "Castle", "Fort"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False
                            match alert.alert_type:
                                case "TownHall":
                                    enough_res = environment.hasCost(650500, 2500, 4000)
                                case "Fortified Walls":
                                    enough_res = environment.hasCost(22500, 2500, 275, 200)
                                case "Fort":
                                    enough_res = environment.hasCost(675500, 5000, 4000, 3000)
                                case "Castle":
                                    enough_res = environment.hasCost(997550, 5000, 4000, 2000, 1000)

                            if enough_res:
                                if alert.alert_type in ("Castle", "Fort"):
                                    region_map.setLocation(environment.location_world)
                                    exitLocal()
                                else:
                                    local_region.menu.alerts.remove(alert)
                                    alert.kill()

                                    local_region.refreshMenu()

                                    local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Tier 2
                    elif alert.alert_type in ("Stone Walls", "Archer Towers", "Crossbow Pillboxes"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False
                            match alert.alert_type:
                                case "Stone Walls":
                                    enough_res = environment.hasCost(52500, 2500, 2275, 80)
                                case "Archer Towers":
                                    enough_res = environment.hasCost(82500, 3500, 1275)
                                case "Crossbow Pillboxes":
                                    enough_res = environment.hasCost(82500, 1255, 2275, 80)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                local_region.refreshMenu()

                                local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Castle
                    elif alert.alert_type in ("Chambers", "Bazaar", "Merchants Guild", "City"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False

                            match alert.alert_type:
                                case "Chambers":
                                    enough_res = environment.hasCost(100000, 400, 115255, 2275)
                                case "Bazaar":
                                    enough_res = environment.hasCost(100000, 1152500, 0, 2275, 2550)
                                case "Merchants Guild":
                                    enough_res = environment.hasCost(100000, 400, 115255, 2575, 52550)
                                case "City":
                                    enough_res = environment.hasCost(20577500, 80000, 40000, 0, 1000)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                if alert.alert_type == "City":
                                    region_map.setLocation(environment.location_world)
                                    exitLocal()
                                else:
                                    local_region.menu.alerts.remove(alert)
                                    alert.kill()
                                    local_region.refreshMenu()

                                    local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Fort
                    elif alert.alert_type in ("Ballistas", "Catapults", "Workshop", "Artisans Guild", "Citadel"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False
                            match alert.alert_type:
                                case "Ballistas":
                                    enough_res = environment.hasCost(88500, 1255, 2275, 800)
                                case "Catapults":
                                    enough_res = environment.hasCost(85500, 7255, 2275, 80)
                                case "Workshop":
                                    enough_res = environment.hasCost(115255, 2255, 2275, 10000)
                                case "Artisans Guild":
                                    enough_res = environment.hasCost(115575, 2255, 2275, 0, 10000)
                                case "Citadel":
                                    enough_res = environment.hasCost(5957500, 8000, 40000, 2000, 2000)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                if alert.alert_type == "Citadel":
                                    region_map.setLocation(environment.location_world)
                                    exitLocal()
                                else:
                                    local_region.menu.alerts.remove(alert)
                                    alert.kill()
                                    local_region.refreshMenu()

                                    local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Tier 3
                    # City
                    elif alert.alert_type in ("Trade Root", "Royal Palace"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False

                            match alert.alert_type:
                                case "Trade Root":
                                    enough_res = environment.hasCost(100000, 40000, 1075255, 23575, 352550)
                                case "Royal Palace":
                                    enough_res = environment.hasCost(10000000, 400000, 10700255, 300575, 302550)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                local_region.refreshMenu()

                                local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Citadel
                    elif alert.alert_type in ("Manors", "WarHall"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            enough_res = False

                            match alert.alert_type:
                                case "Manors":
                                    enough_res = environment.hasCost(10000000, 140000, 500000, 120000)
                                case "WarHall":
                                    enough_res = environment.hasCost(10000000, 400000, 11150255, 450575)

                            if enough_res:
                                local_region.menu.alerts.remove(alert)
                                alert.kill()
                                local_region.refreshMenu()

                                local_region.updateFortInfo()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        environment.calcEnvData()
                    # Unstable area actions
                    elif alert.alert_type in ("Explore area", "Train yourself", "Train units", "Break camp"):
                        alert.handleEvent(event)
                        if event.ui_element == alert.btn_confirm:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()
                            local_region.refreshMenu()
                            if alert.alert_type == "Train yourself" and environment.player.useAction() > 0:
                                print("Training...")
                            elif alert.alert_type == "Train units" and environment.player.army_amount > 0:
                                if environment.player.useAction(2) > 0:
                                    print("Training units...")
                                    environment.player.army_trained = True
                                    region_map.updateTbx_Army()
                            elif alert.alert_type == "Break camp" and environment.player.useAction(3) > 0:
                                if environment.military_camp:
                                    print("Already have a camp!")
                                    environment.player.resetAction()
                                elif environment.player.army_amount == 0:
                                    print("You have no army to place in camp")
                                    environment.player.resetAction()
                                elif environment.chaos_level == 1:
                                    print("No need for camp here")
                                    environment.player.resetAction()
                                else:
                                    amount = environment.player.army_amount
                                    power = environment.player.army_power
                                    environment.placeMilitaryCamp(amount, power)
                                    region_map.updateTbx_Army()
                                    environment.countSoldiers()
                                    region_map.setLocation(environment.location_world)
                            else:
                                print("Out of actions!")
                            local_region.updateAP()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()
                    else:
                        if event.ui_element == alert.btn_confirm:
                            alert.confirm()
                            local_region.menu.alerts.remove(alert)
                            alert.kill()
                            exitLocal()

                        elif event.ui_element == alert.btn_cancel:
                            local_region.menu.alerts.remove(alert)
                            alert.kill()

                        alert.handleEvent(event)

                if local_region.war_panel:
                    if event.ui_element == local_region.war_panel.btn_claim:
                        local_region.war_panel.calcCasualties()
                        region_map.setLocation(environment.location_world)

        elif state == "Battle":
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                battle_screen.player.kind = battle_screen.ddMenu_start.selected_option

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if not pygame.mixer.get_busy():
                    sfx_click.play()

                if event.ui_element == battle_screen.btn_start:
                    battle_screen.btn_attack.show()
                    battle_screen.btn_passive.show()
                    for btn_skill in battle_screen.btn_skills:
                        btn_skill.show()
                    battle_screen.btn_die.show()
                    battle_screen.btn_restart.show()

                    battle_screen.player.HealthBar.show()
                    battle_screen.player.MagicBar.show()
                    battle_screen.player.SpiritBar.show()

                    battle_screen.monster.HealthBar.show()
                    battle_screen.monster.MagicBar.show()
                    battle_screen.monster.SpiritBar.show()
                    battle_screen.btn_start.hide()
                    print('Battle started!')

                elif event.ui_element == battle_screen.btn_attack:
                    battle_screen.player.frame = 0
                    battle_screen.player.getAttacking()
                    if battle_screen.player.mind.current_health < battle_screen.player.mind.health_capacity:
                        print(battle_screen.player.mind.current_health + battle_screen.player.mind.health_capacity // 50)
                        battle_screen.player.mind.addCurrent(main_character.mind.health_capacity // 50)

                    if not pygame.mixer.get_busy():
                        sfx_attack.play()

                    battle_screen.disableButtons()

                is_used_skill = False

                player = battle_screen.player
                match main_character.kind:
                    case "Warlord":
                        if event.ui_element == battle_screen.btn_skills[0]:
                            if player.mind.current_health >= battle_screen.skill_costs[0]:
                                player.mind.subCurrent(battle_screen.skill_costs[0])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("valiant-slash")
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[1]:
                            if player.mind.current_health >= battle_screen.skill_costs[1]:
                                player.mind.subCurrent(battle_screen.skill_costs[1])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("aura-cleave")
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[2]:
                            if player.mind.current_health >= battle_screen.skill_costs[2]:
                                player.mind.subCurrent(battle_screen.skill_costs[2])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("astral-shred")
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[3]:
                            if player.mind.current_health >= battle_screen.skill_costs[3]:
                                player.mind.subCurrent(battle_screen.skill_costs[3])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("spectral-duel")
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[4]:
                            if player.mind.current_health >= battle_screen.skill_costs[4]:
                                player.mind.subCurrent(battle_screen.skill_costs[4])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("vanguards-stance")
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[5]:
                            if player.mind.current_health >= battle_screen.skill_costs[5]:
                                player.mind.subCurrent(battle_screen.skill_costs[5])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("ancestors-protection")
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[6]:
                            aggression = battle_screen.skills.getSkill("aggression")
                            aggression["isOn"] = not aggression["isOn"]
                            if aggression["isOn"]:
                                battle_screen.btn_skills[10].show()
                            else:
                                battle_screen.btn_skills[10].hide()
                        elif event.ui_element == battle_screen.btn_skills[7]:
                            if player.mind.current_health >= battle_screen.skill_costs[6]:
                                player.mind.subCurrent(battle_screen.skill_costs[6])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("blood-thirst")
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[8]:
                            if player.mind.current_health >= battle_screen.skill_costs[7]:
                                player.mind.subCurrent(battle_screen.skill_costs[7])
                                battle_screen.disableButtons()
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("true-vigor")
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[9]:
                            battle_screen.disableButtons()
                            player.frame = 0
                            used_skill = battle_screen.skills.transcend(main_character.kind)
                            pos = battle_screen.plr_pos
                            player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                            is_used_skill = True

                    case "Sourcerer":
                        if event.ui_element == battle_screen.btn_skills[0]:
                            if player.mind.current_health >= battle_screen.skill_costs[0]:
                                player.mind.subCurrent(battle_screen.skill_costs[0])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("psychic-storm", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[1]:
                            if player.mind.current_health >= battle_screen.skill_costs[1]:
                                player.mind.subCurrent(battle_screen.skill_costs[1])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("cloud-mind", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[2]:
                            if player.mind.current_health >= battle_screen.skill_costs[2]:
                                player.mind.subCurrent(battle_screen.skill_costs[2])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("tears-ripple", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[3]:
                            if player.mind.current_health >= battle_screen.skill_costs[3]:
                                player.mind.subCurrent(battle_screen.skill_costs[3])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("diamond-dust", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[4]:
                            if player.mind.current_health >= battle_screen.skill_costs[4]:
                                player.mind.subCurrent(battle_screen.skill_costs[4])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("arcane-barrier", is_physical=False)
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[5]:
                            if player.mind.current_health >= battle_screen.skill_costs[5]:
                                player.mind.subCurrent(battle_screen.skill_costs[5])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("aegis-shield", is_physical=False)
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[6]:
                            aggression = battle_screen.skills.getSkill("aggression")
                            aggression["isOn"] = not aggression["isOn"]
                            if aggression["isOn"]:
                                battle_screen.btn_skills[10].show()
                            else:
                                battle_screen.btn_skills[10].hide()
                        elif event.ui_element == battle_screen.btn_skills[7]:
                            if player.mind.current_health >= battle_screen.skill_costs[6]:
                                player.mind.subCurrent(battle_screen.skill_costs[6])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("arcane-frenzy", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[8]:
                            if player.mind.current_health >= battle_screen.skill_costs[7]:
                                player.mind.subCurrent(battle_screen.skill_costs[7])
                                battle_screen.disableButtons()
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("true-spirit", is_physical=False)
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[9]:
                            battle_screen.disableButtons()
                            player.frame = 0
                            used_skill = battle_screen.skills.transcend(main_character.kind)
                            pos = battle_screen.plr_pos
                            player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                            is_used_skill = True

                    case "Hunter":
                        if event.ui_element == battle_screen.btn_skills[0]:
                            if player.mind.current_health >= battle_screen.skill_costs[0]:
                                player.mind.subCurrent(battle_screen.skill_costs[0])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("fire-shot", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[1]:
                            if player.mind.current_health >= battle_screen.skill_costs[1]:
                                player.mind.subCurrent(battle_screen.skill_costs[1])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("ice-shot", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[2]:
                            if player.mind.current_health >= battle_screen.skill_costs[2]:
                                player.mind.subCurrent(battle_screen.skill_costs[2])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("thunder-shot", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[3]:
                            if player.mind.current_health >= battle_screen.skill_costs[3]:
                                player.mind.subCurrent(battle_screen.skill_costs[3])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("rose-thorns", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[4]:
                            if player.mind.current_health >= battle_screen.skill_costs[4]:
                                player.mind.subCurrent(battle_screen.skill_costs[4])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("better-position")
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[5]:
                            if player.mind.current_health >= battle_screen.skill_costs[5]:
                                player.mind.subCurrent(battle_screen.skill_costs[5])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("lightning-shock", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[6]:
                            perception = battle_screen.skills.getSkill("perception")
                            perception["isOn"] = not perception["isOn"]
                            if perception["isOn"]:
                                battle_screen.btn_skills[10].show()
                            else:
                                battle_screen.btn_skills[10].hide()
                        elif event.ui_element == battle_screen.btn_skills[7]:
                            if player.mind.current_health >= battle_screen.skill_costs[6]:
                                player.mind.subCurrent(battle_screen.skill_costs[6])
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("dark-bolt", is_physical=False)
                                pos = battle_screen.mns_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                battle_screen.disableButtons()
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[8]:
                            if player.mind.current_health >= battle_screen.skill_costs[7]:
                                player.mind.subCurrent(battle_screen.skill_costs[7])
                                battle_screen.disableButtons()
                                player.frame = 0
                                used_skill = battle_screen.skills.getSkill("true-speed")
                                pos = battle_screen.plr_pos
                                player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                                is_used_skill = True
                        elif event.ui_element == battle_screen.btn_skills[9]:
                            battle_screen.disableButtons()
                            player.frame = 0
                            used_skill = battle_screen.skills.transcend(main_character.kind)
                            pos = battle_screen.plr_pos
                            player.getCast(used_skill, (pos[0], pos[1] * 3 / 2))
                            is_used_skill = True

                if is_used_skill:
                    if not pygame.mixer.get_busy():
                        sfx_skill.play()

                if event.ui_element == battle_screen.btn_die:
                    battle_screen.player.frame = 0
                    battle_screen.player.getDead()

                elif event.ui_element == battle_screen.btn_restart:
                    battle_screen.monster.current_health = battle_screen.monster.health_capacity
                    battle_screen.monster.getIdle()
                    battle_screen.monster.frame = 0

                    battle_screen.btn_attack.hide()
                    battle_screen.btn_passive.hide()
                    for btn_skill in battle_screen.btn_skills:
                        btn_skill.hide()
                    battle_screen.btn_die.hide()
                    battle_screen.btn_restart.hide()

                    player.HealthBar.hide()
                    player.MagicBar.hide()
                    player.SpiritBar.hide()

                    battle_screen.monster.HealthBar.hide()
                    battle_screen.monster.MagicBar.hide()
                    battle_screen.monster.SpiritBar.hide()

        manager.process_events(event)
    return True


#               H, M, S  MS
time_in_game = [0, 0, 0, 0]


def isMapCleared():
    global world_map
    if world_map:
        areas = len(list(world_map.areas_cleansed))
        cleansed = 0
        for val in world_map.areas_cleansed.values():
            if val:
                cleansed += 1

        return cleansed == areas


def endDemo():
    font = pygame.font.Font(None, 32)
    txt = font.render("Thank you for playing the demo", True, (250, 250, 250))
    screen.blit(txt, (WIDTH / 3, HEIGHT / 2 - 40))
    txt = font.render("Game was made by Dmitry Krasnopolsky", True, (250, 250, 250))
    screen.blit(txt, (WIDTH / 3, HEIGHT / 2 + 40))


def manageState():
    global state, time_delta
    screen.fill((0, 0, 0))

    if isMapCleared():
        if state != "End Demo":
            global is_music
            is_music = False
            pygame.mixer_music.stop()
            pygame.mixer.stop()
            sfx_gameover.play()
        state = "End Demo"

    match state:
        case "Start Menu":
            stateStartMenu()
        case "World":
            stateWorld()
        case "Region":
            stateRegion()
        case "Local":
            stateLocal()
        case "Battle":
            battle_screen.update()
        case "End Demo":
            endDemo()

    # pygame_gui update elements
    manager.update(time_delta)
    # pygame_gui draw
    manager.draw_ui(screen)
    pygame.display.flip()

    time_in_game[3] += 1
    if time_in_game[3] > FPS:
        time_in_game[3] = 0
        time_in_game[2] += 1

        if time_in_game[2] > 59:
            time_in_game[2] = 0
            time_in_game[1] += 1

        #print(f"Time: [{time_in_game[0]}:{time_in_game[1]}:{time_in_game[2]}]")

    if time_in_game[1] > 59:
        time_in_game[1] = 0
        time_in_game[0] += 1

    time_delta = clock.tick(FPS) / 1000


def saveData(data: dict, path: str):
    try:
        path += ".json"
        data = json.dumps(data)
        with open(path, 'w') as file_out:
            file_out.write(data)
    except IOError as e:
        print(type(e), ':', e)


def loadData(path: str):
    try:
        path += ".json"
        with open(path, 'r') as file_opn:
            data = json.load(file_opn)
        return data
    except FileNotFoundError:
        return False
    except IOError as e:
        print(type(e), ':', e)


def drawPlayerIco(rect: tuple):
    """pygame.draw.circle(screen, (10, 200, 20),
                       (rect[0] + rect[2] / 2, rect[1] + rect[3] / 2), 15, 3)"""
    icon = pygame.image.load("./data/gfx/GUI/pics/icons/PlayerMarker.png").convert_alpha()
    icon = pygame.transform.scale(icon, (50, 50))
    screen.blit(icon, (rect[0] + rect[2] / 2 - 25, rect[1] + rect[3] / 2 - 25))


def drawAreaMarker(item: dict):
    area, pos = item
    if world_map.areas_cleansed[area]:
        icon = pygame.transform.scale(pygame.image.load("./data/gfx/GUI/pics/icons/capture_flag2.png"),
                                      (50, 50)).convert_alpha()
    else:
        icon = pygame.transform.scale(pygame.image.load("./data/gfx/GUI/pics/icons/capture_flag1.png"),
                                      (50, 50)).convert_alpha()

    screen.blit(icon, (pos[0] - 25, pos[1] - 25))


def getRewarded(reward_exp, reward_gold):
    global main_character
    main_character.exp += reward_exp
    environment.player.gold += reward_gold
    if main_character.exp >= main_character.exp_needed:
        if region_map.alert_level_up:
            alert = region_map.alert_level_up
            alert.points += 2
            alert.lbl_points.set_text(f"Points: {alert.points}")
        else:
            region_map.alert_level_up = LevelAlert()
        main_character.levelUp()

        pygame.mixer.stop()
        sfx_levelup.play()

        if state == "Local":
            exitLocal()

    region_map.exp_bar.percent_full = main_character.exp / main_character.exp_needed


class ActionMenu(pygame_gui.elements.UIWindow):
    def __init__(self):
        super().__init__(pygame.Rect(WIDTH - WIDTH / 3, 0, WIDTH / 3, HEIGHT),
                         manager, window_display_title="Actions", object_id="#window")

        self.btn_size = (WIDTH / 3 - 70, 35)  # Button size
        self.lbl_size = (WIDTH / 3 - 70, 35)  # Label size

        # Lists of objects
        self.labels = list()
        self.btn_actions = list()
        self.btn_upgrades = list()

        # Alerts and sub menus
        self.sub_menus = list()
        self.alerts = list()

        self.disable()
        self.hide()

    def drawLabel(self, text, location):
        self.labels.append(pygame_gui.elements.UILabel(pygame.Rect((location, self.lbl_size)),
                                                            text, manager,
                                                            container=self, parent_element=self))

    def drawActionButton(self, text, location):
        self.btn_actions.append(pygame_gui.elements.UIButton(pygame.Rect((location, self.btn_size)),
                                                            text, manager,
                                                            object_id="#button",
                                                            container=self, parent_element=self))

    def drawUpgradeButton(self, text, location):
        self.btn_upgrades.append(pygame_gui.elements.UIButton(pygame.Rect((location, self.btn_size)),
                                                             text, manager,
                                                             object_id="#button",
                                                             container=self, parent_element=self))

    def openSubmenu(self, menu_type: str):
        cancel = False
        for sub_menu in self.sub_menus:
            if sub_menu.menu_type == menu_type:
                if menu_type in ("Manage Workers",
                                 "Manage Army",
                                 "Merchants",
                                 "Blacksmith"):
                    cancel = True
        if not cancel:
            match menu_type:
                case "Manage Workers":
                    self.sub_menus.append(WorkerManagement(menu_type))
                case "Manage Army":
                    self.sub_menus.append(ArmyManagement(menu_type))
                case "Merchants":
                    self.sub_menus.append(MarketManagement(menu_type))
                case "Blacksmith":
                    self.sub_menus.append(BlacksmithMenu(menu_type))

    def openAlert(self, alert_type: str, confirm_txt: str=None, cancel_txt: str=None):
        cancel = False
        for alert in self.alerts:
            if alert.alert_type == alert_type:
                cancel = True
        if not cancel:
            if alert_type == "no resources":
                alert = Alert(alert_type)
                alert.setText("Not enough resources!")
                alert.btn_cancel.hide()
                self.alerts.append(alert)
            elif "refuges" in alert_type:
                alert = Alert(alert_type)
                alert.btn_confirm.set_text("To Map")
                alert.btn_cancel.set_text("Close")
                alert.setText(alert_type)
                self.alerts.append(alert)
            match alert_type:
                case "Stable":
                    alert = Alert(alert_type)
                    alert.setText(
                        "Building: Outpost\n"
                        "Info: Your base of operations\n"
                        "Cost: 10000 gold\n"
                        "Name:                                ")
                    alert.text_input.show()
                    self.alerts.append(alert)
                case "Wood":
                    alert = Alert(alert_type)
                    alert.setText(
                        "Building: Wood Gathering Camp\n"
                        "Info: Wood gathered per worker: 0.5\n"
                        "Cost: 1000 gold")
                    self.alerts.append(alert)
                case "Stone":
                    alert = Alert(alert_type)
                    alert.setText(
                        "Building: Stone Gathering Camp\n"
                        "Info: Stone gathered per worker: 0.3\n"
                        "Cost: 1000 gold")
                    self.alerts.append(alert)
                case "Metal":
                    alert = Alert(alert_type)
                    alert.setText(
                        "Building: Metal Gathering Camp\n"
                        "Info: Metal gathered per worker: 0.2\n"
                        "Cost: 1000 gold")
                    self.alerts.append(alert)
                case "Gems":
                    alert = Alert(alert_type)
                    alert.setText(
                        "Building: Gems Gathering Camp\n"
                        "Info: Gems gathered per worker: 0.1\n"
                        "Cost: 1000 gold")
                    self.alerts.append(alert)
                case "Tents":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Tents"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases maximum villagers and number\n" +
                                  "of garrison bought on recruitment.\n" +
                                  f"Villagers: {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}\n" +
                                  f"Recruits: {str(environment.getAllowedRecruit())} => " +
                                  f"{str(environment.getAllowedRecruit() + bonuses['RecruitAllowed'])}"
                                  )

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 2000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 25 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 5 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Cottages":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Cottages"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases maximum villagers and number\n" +
                                  "of garrison bought on recruitment.\n" +
                                  f"Villagers: {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}\n" +
                                  f"Recruits: {str(environment.getAllowedRecruit())} => " +
                                  f"{str(environment.getAllowedRecruit() + bonuses['RecruitAllowed'])}"
                                  )

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 10000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 150 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 30 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 14 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Houses":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Houses"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases maximum villagers and number\n" +
                                  "of garrison bought on recruitment.\n" +
                                  f"Villagers: {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}\n" +
                                  f"Recruits: {str(environment.getAllowedRecruit())} => " +
                                  f"{str(environment.getAllowedRecruit() + bonuses['RecruitAllowed'])}"
                                  )

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 100000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 400 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 300 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Palisade":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Palisade"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Security (Durability)\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}"
                                  )

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 22500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 40 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "TownHall":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Unique"]["TownHall"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Villagers {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}\n" +
                                  f"Recruit Cost: {str(environment.getRecruitCost())} => " +
                                  f"{str(environment.getRecruitCost() - bonuses['RecruitCost'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 650500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 4000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Fortified Walls":
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Unique"]["Fortified Walls"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Security\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 22500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 200 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Castle":
                    alert = Alert(alert_type)
                    alert.setText("Upgrades Outpost to a Castle")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 997550 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 5000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 4000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2000 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 1000"
                                     )

                    self.alerts.append(alert)
                case "Fort":
                    alert = Alert(alert_type)
                    alert.setText("Upgrades Outpost to a Fort")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 675500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 5000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 4000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 3000 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Stone Walls":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Stone Walls"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Security\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 52500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 80 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Archer Towers":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Archer Towers"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Control: {str(environment.getControl())} => " +
                                  f"{str(environment.getControl() + bonuses['Control'])}\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}\n" +
                                  f"Garrison: {str(environment.countGarrison())} => " +
                                  f"{str(environment.countGarrison() + bonuses['Garrison'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 82500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 3500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 1275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Crossbow Pillboxes":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Crossbow Pillboxes"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}\n" +
                                  f"Control: {str(environment.getControl())} => " +
                                  f"{str(environment.getControl() + bonuses['Control'])}\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 82500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 1255 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 80 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Ballistas":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Ballistas"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Control: {str(environment.getControl())} => " +
                                  f"{str(environment.getControl() + bonuses['Control'])}\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}\n" +
                                  f"Garrison: {str(environment.countGarrison())} => " +
                                  f"{str(environment.countGarrison() + bonuses['Garrison'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 88500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 1255 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 800 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Catapults":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Catapults"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Control: {str(environment.getControl())} => " +
                                  f"{str(environment.getControl() + bonuses['Control'])}\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 85500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 7255 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 80 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Workshop":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Workshop"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Weapon Quality\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 115255 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2255 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 10000 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Artisans Guild":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Artisans Guild"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Weapon Quality\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 115575 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 2255 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 10000"
                                     )

                    self.alerts.append(alert)
                case "Citadel":
                    alert = Alert(alert_type)
                    alert.setText("Upgrades Fort to a Citadel")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 5957500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 8000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 40000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2000 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 2000"
                                     )

                    self.alerts.append(alert)
                case "Chambers":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Chambers"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Villagers {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}\n" +
                                  f"Recruit Cost: {str(environment.getRecruitCost())} => " +
                                  f"{str(environment.getRecruitCost() - bonuses['RecruitCost'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 100000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 400 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 115255 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Bazaar":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Bazaar"]["Bonuses"]
                    income = bonuses['Income'] if environment.player.income < bonuses['Income'] else \
                        environment.player.income
                    alert = Alert(alert_type)
                    if income == environment.player.income:
                        income_str = f"Income: {income} = {income}"
                    else:
                        income_str = f"Income: {environment.player.income} => {income}"
                    alert.setText("Increases the player income\n" + income_str)

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 100000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 1152500 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2275 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 2550"
                                     )

                    self.alerts.append(alert)
                case "Merchants Guild":
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Merchants Guild"]["Bonuses"]
                    income = bonuses['Income'] if environment.player.income < bonuses['Income'] else \
                        environment.player.income
                    if income == environment.player.income:
                        income_str = f"Income: {income} = {income}"
                    else:
                        income_str = f"Income: {environment.player.income} => {income}"
                    alert = Alert(alert_type)
                    alert.setText("Increases the player income\n" +
                                  income_str)

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 100000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 400 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 115255 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 2575 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 52550"
                                     )

                    self.alerts.append(alert)
                case "City":
                    alert = Alert(alert_type)
                    alert.setText("Upgrades Castle to a City")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 20577500 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 80000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 40000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 0 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 1000"
                                     )

                    self.alerts.append(alert)
                case "Trade Root":
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["City"]["Trade Root"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Quality\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 100000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 40000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 1075255 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 23575 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 352550"
                                     )

                    self.alerts.append(alert)
                case "Royal Palace":
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["City"]["Royal Palace"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the Security\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 10000000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 400000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 10700255 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 300575 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 302550"
                                     )

                    self.alerts.append(alert)
                case "Manors":
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["Citadel"]["Manors"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Increases the following:\n" +
                                  f"Security: {str(environment.getSecurity())} => " +
                                  f"{str(environment.getSecurity() + bonuses['Security'])}\n" +
                                  f"Villagers: {str(environment.getMaxWorkersInStructure())} => " +
                                  f"{str(environment.getMaxWorkersInStructure() + bonuses['MaxVillagers'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 10000000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 140000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 500000 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 120000 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "WarHall":
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["Citadel"]["WarHall"]["Bonuses"]
                    alert = Alert(alert_type)
                    alert.setText("Changes:\n" +
                                  f"Control: {str(environment.getControl())} => " +
                                  f"{str(environment.getControl() + bonuses['Control'])}\n" +
                                  f"Weapon Quality: {str(environment.getQuality())} => " +
                                  f"{str(environment.getQuality() + bonuses['Quality'])}")

                    alert.setTextBox("Cost: "
                                     "<img src='data/gfx/GUI/pics/icons/Gold.png'> 10000000 "
                                     "<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> 400000 "
                                     "<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> 11150255 "
                                     "<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> 450575 "
                                     "<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> 0"
                                     )

                    self.alerts.append(alert)
                case "Train yourself":
                    alert = Alert(alert_type, 'train')
                    alert.setText("Begin training yourself? (costs 1AP)")
                    self.alerts.append(alert)
                case "Train units":
                    alert = Alert(alert_type, 'train')
                    alert.setText("Begin training your units? (costs 2 AP)")
                    self.alerts.append(alert)
                case "Break camp":
                    alert = Alert(alert_type, 'rest')
                    alert.setText("Break camp? (costs 3 AP)")
                    self.alerts.append(alert)

    def killAlerts(self):
        for alert in self.alerts:
            alert.kill()

        self.alerts.clear()

    def updateGarrison(self):
        self.labels[2].set_text(f"Garrison: {environment.countGarrison()}")


class Button:
    def __init__(self, x, y, sx, sy, color=(55, 55, 55), font="Arial", fcolor=(230, 230, 230), text="Button"):
        self.x, self.y = x, y
        self.sx, self.sy = sx, sy
        self.color = color
        self.font = font
        self.fcolor = fcolor
        self.text = text

        self.font_size = 25
        self.font = pygame.font.SysFont(font, self.font_size)

        self.active = False
        self.was_clicked = False

    def draw(self):
        # Draw rectangle
        #pygame.draw.rect(screen, self.fcolor, (self.x, self.y, self.sx, self.sy))

        text_surface = self.font.render(self.text, False, self.color)

        # Centralize text
        screen.blit(text_surface,
                    ((self.x + (self.sx / 2) -
                      (self.font_size / 2) * (len(self.text) / 2) -
                      5, (self.y + (self.sy / 2) -
                          (self.font_size / 2) - 4))))

    # Check mouse hover on button
    def checkFocused(self):
        mouse_pos = pygame.mouse.get_pos()
        if (self.x <= mouse_pos[0] <= self.x + self.sx
                and self.y <= mouse_pos[1] <= self.y + self.sy):
            self.active = True
        else:
            self.active = False
            self.was_clicked = False

    def getClicked(self):
        if self.active:
            self.was_clicked = True
            self.active = False

    def getRect(self):
        return (self.x, self.y, self.sx, self.sy)


class ImgButton(Button):
    def __init__(self, x, y, sx, sy, color, img, font="Arial", fcolor=(230, 230, 230), text="Button", img2=None):
        super().__init__(x, y, sx, sy, color, font, fcolor, text)

        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (sx, sy)).convert_alpha()
        if img2:
            self.img2 = pygame.transform.scale(pygame.image.load(img2), (sx, sy)).convert_alpha()
        else:
            self.img2 = None
        self.switched = False
        self.img_active = self.img

    def draw(self):
        screen.blit(self.img_active, (self.x, self.y))

    def switch(self, mode=-1):
        if mode == -1:
            if self.img_active == self.img:
                self.img_active = self.img2
            else:
                self.img_active = self.img
        else:
            if mode == 0:
                self.img_active = self.img
            else:
                self.img_active = self.img2


# Intractable button used to display areas
class GridButton(Button):
    def __init__(self, x, y, sx, sy, color, font="Arial", fcolor=(230, 230, 230), text="Button", loc=(0, 0), biome=None):
        super().__init__(x, y, sx, sy, color, font, fcolor, text)

        self.image = None
        if biome:
            self.biome = biome
            self.image = pygame.image.load("./data/gfx/GUI/pics/Biomes/" + biome + ".png").convert_alpha()

        self.loc = loc

    # Return the location area/area-tile upon click
    def getClicked(self):
        if self.active:
            self.was_clicked = True
        return self.loc


# Every game state has a co-responding screen object
class WorldMap:
    def __init__(self, map_w, map_h, map_regions, areas_collection):
        # divides screen to borders
        temp = range(0, WIDTH, WIDTH // map_w)
        borders_x = list()
        for i in range(map_w):
            borders_x.append(temp[i])

        temp = range(0, HEIGHT, HEIGHT // map_h)
        borders_y = list()
        for i in range(map_h):
            borders_y.append(temp[i])

        # Generate random colors for each
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
        self.colors = list()
        self.biomes = list()

        for i in range(map_regions):
            red = random.randint(50, 255)
            green = random.randint(50, 255)
            blue = random.randint(50, 255)
            self.colors.append((red, green, blue))

        self.regions = list()
        # add all buttons to list of sectors
        margin = max(math.ceil(borders_x[1] / 100), math.ceil(borders_y[1] / 100))
        size_x = borders_x[1] - margin
        size_y = borders_y[1] - margin
        self.cell_size = (size_x, size_y)

        for i in range(map_h):
            for j in range(map_w):
                idx = areas_collection.index(play_map.world[i][j])
                grid_btn = GridButton((margin + size_x * 1.01) * j + margin,
                                               (margin + size_y) * i + margin, size_x, size_y,
                                               (20, 20, 30), "TimesNewRoman",
                                               self.colors[idx], play_map.world[i][j], (j, i),
                                               play_map.region_info[i][j]['Biome'])
                grid_btn.image = pygame.transform.scale(grid_btn.image, (size_x * 1.02, size_y * 1.2))

                self.regions.append(grid_btn)

        self.is_show_borders = False
        areas_raw = play_map.getAreaPositions()

        start, end = areas_raw[list(areas_raw)[0]]
        self.area_regions = (end[0] - start[0] + 1) * (end[1] - start[1] + 1)

        self.area_centers = {}
        self.area_borders = {}
        self.areas_cleansed = {}

        for area in areas_raw:
            start, end = areas_raw[area]
            sx, sy = (margin + size_x) * start[0] + margin, (margin + size_y) * start[1] + margin
            ex = (margin + size_x) * end[0] + margin + size_x
            ey = (margin + size_y) * end[1] + margin + size_y
            dx, dy = (ex - sx) / 2, (ey - sy) / 2
            self.area_centers[area] = (sx + dx, sy + dy)
            self.area_borders[area] = (sx, sy, ex, ey)
            self.areas_cleansed[area] = False


class CustomWindow(pygame.Rect):
    def __init__(self):
        pos, size = (WIDTH / 4 - 50, 10), (WIDTH / 3 + 80, HEIGHT * 3 / 5)
        super().__init__((pos, size))

        self.offset_x, self.offset_y = pos
        self.is_displayed = False
        self.is_dragged = False
        self.is_movable = False

    def show(self):
        self.is_displayed = True

    def hide(self):
        self.is_displayed = False


class RegionMap:
    def __init__(self, gui: bool):
        self.tiles = list()
        self.tiles_color = (60, 150, 80)
        self.gui = gui
        self.width, self.height = len(play_map.regions[0][0]), len(play_map.regions[0][0][0])

        # Gui elements
        bg_image = pygame.image.load("./data/gfx/GUI/pics/Biomes/Ground_BG.png").convert()
        self.bg_image = pygame.transform.scale(bg_image, screen.get_size())

        bg_img = pygame.image.load("./data/gfx/GUI/pics/wood_bg.png")
        self.bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

        color = (100, 120, 180)
        self.bottomGuiHolder = pygame.Surface((WIDTH, HEIGHT / 3))
        self.bottomGuiHolder.fill(color)
        self.rightGuiHolder = pygame.Surface((WIDTH / 6, HEIGHT))
        self.rightGuiHolder.fill(color)
        self.leftGuiHolder = pygame.Surface((WIDTH / 6, HEIGHT))
        self.leftGuiHolder.fill(color)

        self.showWalk = False

        # Bottom Gui

        self.btn_army = pygame_gui.elements.UIButton(
            pygame.Rect(10, HEIGHT - self.bottomGuiHolder.get_height() + 10,
                        50, 50),
            text="",
            manager=manager,
            object_id="#btn_army",
            visible=False
        )
        self.tbx_army = pygame_gui.elements.UITextBox(
            f"Army Size: {environment.player.army_amount}   Power: {environment.player.army_power}"
            f"   Armour Tier: {environment.player.army_armour}   Weapon Tier: {environment.player.army_weapon}"
            f"   Trained: {environment.player.army_trained}",
            pygame.Rect(60, HEIGHT - self.bottomGuiHolder.get_height() + 10,
                        WIDTH / 2, 50), manager, object_id="#tbx_army", visible=False)

        self.text_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(WIDTH * 3 / 8, HEIGHT - self.bottomGuiHolder.get_height(),
                        WIDTH / 4, 35), manager, visible=False)

        # Right Gui - Forts, Workers, Resources
        self.text_box = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect(WIDTH * 5 / 6, 0, WIDTH / 6, HEIGHT * 2 / 3 + 16),
            object_id="#tbx_window"
        )

        # map button proportions
        btn_wmap_size = 100 + WIDTH / 20
        self.btn_wmap = ImgButton(WIDTH - (btn_wmap_size + 10), HEIGHT - (btn_wmap_size + 10),
                                  btn_wmap_size, btn_wmap_size, (10, 80, 130),
                               "./data/gfx/GUI/pics/worldmap.jpg", "Arial", (20, 100, 160), "World")

        self.btn_inventory = ImgButton(WIDTH * 3 / 5, HEIGHT - (btn_wmap_size + 10),
                                  btn_wmap_size, btn_wmap_size, (10, 80, 130),
                               "./data/gfx/GUI/pics/inventory_bag.png",
                                       "Arial", (20, 100, 160), "World",
                               "./data/gfx/GUI/pics/inventory_bag_open.png",)

        self.btn_settings = ImgButton(WIDTH / 3, HEIGHT - (btn_wmap_size + 10),
                                  btn_wmap_size, btn_wmap_size, (10, 80, 130),
                               "./data/gfx/GUI/pics/settings.png",
                                       "Arial", (20, 100, 160), "World",)

        # Left Gui - Turn, Chaos, Encounter Chance
        path = "./data/gfx/Portraits/"
        self.portrait = pygame.image.load(os.path.join(path, main_character.kind + ".jpg")).convert_alpha()
        self.portrait = pygame.transform.scale(self.portrait, (self.leftGuiHolder.get_width() - 20,
                                                               self.leftGuiHolder.get_width() - 20))

        self.exp_bar = pygame_gui.elements.UIStatusBar(
            pygame.Rect(5, self.portrait.get_height() + 30 + 20, self.leftGuiHolder.get_width() - 10, HEIGHT / 40),
            manager,
            visible=False,
            object_id='#exp_bar',
        )

        self.exp_bar.percent_full = main_character.exp / main_character.exp_needed * 100

        stats_offset, stats_space = HEIGHT * 3 / 40 - 10, 20
        self.gui_player_lvl = pygame_gui.elements.UILabel(
                pygame.Rect(-30, self.portrait.get_height() + stats_space / 2, 200, 35),
                text="",
                manager=manager, object_id="#label_level", visible=False)

        self.txb_player_stats = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect(0, self.portrait.get_height() * 1.4,
                        WIDTH / 6, HEIGHT / 4 + int(6000 / HEIGHT) * 4),
            object_id="#tbx_window"
        )

        self.equipment_img = pygame.image.load('./data/gfx/GUI/pics/equipment/wood_inv_bg.png')
        size = (WIDTH / 3 - WIDTH / 16, HEIGHT - (HEIGHT / 2 + HEIGHT / 3))
        if size[0] > 320:
            size = (320, 120)
        self.equipment_img = pygame.transform.scale(self.equipment_img, size)
        self.equipment_surf = pygame.Surface(size)
        height = HEIGHT / 2 + HEIGHT / 3 - 10 if HEIGHT <= 600 else HEIGHT - (size[1] + 60)
        self.equipment_rect = self.equipment_surf.get_rect(x=10, y=height)

        # custom windows
        self.window_test = CustomWindow()
        #self.window_test.show()

        # alert windows
        self.alerts = list()
        self.game_sound = 1
        self.game_settings = None
        self.alert_level_up = None

        self.text_box.hide()

        self.updateInfo()

    def setLocation(self, loc):
        ratio = 2 / 3
        size_x = math.ceil(WIDTH / self.width * math.pow(ratio, int(self.gui)))
        size_y = math.ceil(HEIGHT / self.height * math.pow(ratio, int(self.gui)))
        margin_x = math.ceil(size_x / 500)
        margin_y = math.ceil(size_y / 500)

        size_x -= margin_x
        size_y -= margin_y
        left_gui = self.leftGuiHolder.get_width()

        self.tiles.clear()
        for i in range(self.width):
            for j in range(self.height):
                # idx = areas_collection.index(game_map["WorldMap"][i][j])
                self.tiles.append(GridButton((margin_x + size_x) * j + margin_x +
                                             int(self.gui) * (left_gui - math.floor(self.width / 4)),
                                             (margin_y + size_y) * i + margin_y, size_x, size_y,
                                             (20, 20, 30), "TimesNewRoman",
                                             self.tiles_color, play_map.regions[loc[1]][loc[0]][i][j], (j, i)))

    def drawRegionImg(self, tile, biome):
        image = pygame.image.load("./data/gfx/GUI/pics/Biomes/" + "Region_" + biome + ".png").convert_alpha()
        image = pygame.transform.scale(image, (tile.sx, tile.sy))

        screen.blit(image, (tile.x, tile.y))

        icon = None
        camp = None

        match tile.text:
            case '@':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Wood.png").convert_alpha()
            case '#':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Stone.png").convert_alpha()
            case '%':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Metal.png").convert_alpha()
            case '&':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Gems.png").convert_alpha()
            case 'v':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/StableGround.png").convert_alpha()
            case 'e':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Entry.png").convert_alpha()
            case 'o':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Outpost.png").convert_alpha()
            case 'f':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Fort.png").convert_alpha()
            case 'c':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Castle.png").convert_alpha()
            case 'r':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Citadel.png").convert_alpha()
            case 'q':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/City.png").convert_alpha()
            case 'w':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Wood.png").convert_alpha()
                camp = pygame.image.load("./data/gfx/GUI/pics/icons/Camp.png").convert_alpha()
            case 's':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Stone.png").convert_alpha()
                camp = pygame.image.load("./data/gfx/GUI/pics/icons/Camp.png").convert_alpha()
            case 't':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Metal.png").convert_alpha()
                camp = pygame.image.load("./data/gfx/GUI/pics/icons/Camp.png").convert_alpha()
            case 'g':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/Gems.png").convert_alpha()
                camp = pygame.image.load("./data/gfx/GUI/pics/icons/Camp.png").convert_alpha()
            case 'm':
                icon = pygame.image.load("./data/gfx/GUI/pics/icons/MCamp.png")

        if icon:
            icon = pygame.transform.scale(icon, (tile.sx - 10, tile.sy - 10))
            screen.blit(icon, (tile.x + 5, tile.y + 5))
            if camp:
                camp = pygame.transform.scale(camp, (tile.sx - 10, tile.sy - 10))
                screen.blit(camp, (tile.x + 5, tile.y + 5))

    def drawTiles(self):
        global clicked, state, local_region, region_map, refreshed, inventory
        x, y = environment.location_world[0], environment.location_world[1]
        biome = play_map.region_info[y][x]['Biome']
        environment.region_name = play_map.region_info[y][x]["Name"]
        environment.chaos_level = play_map.region_info[y][x]["Chaos"]

        for tile in self.tiles:
            tile.draw()
            self.drawRegionImg(tile, biome)

            tile.checkFocused()
            if tile.active and pygame.mouse.get_pressed()[0] and \
                    not clicked and \
                    not self.text_input.hovered and \
                    not self.alert_level_up and \
                    not self.game_settings:
                clicked = True

                w_loc = environment.location_world
                loc = environment.location_region = list(tile.getClicked())
                presence = environment.player.location[0] == w_loc and \
                        environment.player.location[1] == loc

                if presence and not self.window_test.is_displayed:
                    area_type = getAreaType(play_map.regions[y][x][tile.loc[1]][tile.loc[0]])

                    if area_type in ("Outpost", "Fort", "Castle", "Citadel", "City"):
                        environment.building_name = environment.getStructureName()
                    del local_region
                    local_region = LocalRegion(area_type)
                    local_region.showMenu()

                    self.hide()
                    for alert in self.alerts:
                        alert.kill()
                        del alert
                    self.alerts.clear()

                    if inventory:
                        inventory.kill()
                        inventory = None
                        region_map.btn_inventory.switch(0)

                    state = "Local"
                    pygame.display.set_caption(
                        f"Region: {play_map.world[y][x]} "
                        f"Area: {area_type} "
                        f"Biome: {biome}")
            elif tile.active and pygame.mouse.get_pressed()[1] and not clicked:
                clicked = True

                x, y = environment.location_world[0], environment.location_world[1]
                area_type = getAreaType(play_map.regions[y][x][tile.loc[1]][tile.loc[0]])
                del local_region
                local_region = LocalRegion(area_type)
                local_region.hideMenu()

                try:
                    environment.location_region = tile.loc
                    if environment.building_type in ("Outpost", "Fort", "Castle", "Citadel", "City"):
                        environment.addStructure(area_type, "Fortification")
                        pygame.mixer.stop()
                        sfx_built.play()
                    elif environment.building_type in ("Wood", "Stone", "Metal", "Gems"):
                        environment.addStructure(area_type, "Encampment")
                        pygame.mixer.stop()
                        sfx_built.play()

                except Exception as e:
                    print(type(e), ':', e)

                refreshed = True  # update area symbols
            elif tile.active and pygame.mouse.get_pressed()[2] and not clicked:
                clicked = True

                # Move player
                if environment.player.location[0] == environment.location_world:
                    if not pygame.mixer.get_busy():
                        sfx_move.play()

                    x, y = tile.getClicked()
                    wx, wy = environment.location_world[0], environment.location_world[1]
                    plr_x, plr_y = environment.player.location[1]

                    if abs(plr_x - x) + abs(plr_y - y) < 2 or abs(plr_x - x) == 1 and abs(plr_y - y) == 1:
                        environment.location_region = list(tile.getClicked())
                        environment.player.updateLocation()
                        area_type = getAreaType(play_map.regions[wy][wx][tile.loc[1]][tile.loc[0]])

                        self.is_battle = True

                        if not re.search('camp|outpost|fort|castle|citadel|city|entry', area_type.lower()):
                            environment.workResources()
                            if self.is_battle:
                                self.hide()
                                for alert in self.alerts:
                                    alert.kill()
                                self.alerts.clear()

                                battle_screen.startBattle()
                                battle_screen.show()

                                state = "Battle"

                        elif area_type == "Entry":
                            self.openAlert("Entry")

                environment.player.gold += environment.player.income

                environment.player.resetAction()
                region_map.updateInfo()

            if environment.player.location[0] == environment.location_world and \
                    list(tile.loc) == environment.player.location[1]:
                drawPlayerIco(tile.getRect())

        if refreshed:
            region_map.setLocation(environment.location_world)
            refreshed = False

        if self.window_test.is_displayed:
            pygame.draw.rect(screen, (60, 60, 60), self.window_test)

    def drawGUI(self):
        if self.gui:
            screen.blit(self.bottomGuiHolder, (0, HEIGHT * 2 / 3))
            screen.blit(self.rightGuiHolder, (0, 0))
            screen.blit(self.leftGuiHolder, (WIDTH * 5 / 6, 0))

            screen.blit(self.bg_img, (0, 0))

            screen.blit(self.portrait, (10, 10))

            self.exp_bar.show()


            self.gui_player_lvl.show()

            self.txb_player_stats.show()

            screen.blit(self.equipment_img, (10, HEIGHT / 2 + HEIGHT / 3 - 10))
            #pygame.draw.rect(screen, (200, 200, 200), self.equipment_rect)
            slots = environment.player.equipment_slots
            for slot in slots:
                slot_img = pygame.image.load("./data/gfx/GUI/pics/slot.png").convert_alpha()
                slot_img = pygame.transform.scale(slot_img, (50, 50))

                screen.blit(slot_img, (slot.x + self.equipment_rect.x,
                                         slot.y + self.equipment_rect.y))

                match slots.index(slot):
                    case 0:
                        if main_character.hand:
                            screen.blit(main_character.hand.image,
                                        (slot.x + self.equipment_rect.x,
                                         slot.y + self.equipment_rect.y))
                    case 1:
                        if main_character.torso:
                            screen.blit(main_character.torso.image,
                                        (slot.x + self.equipment_rect.x,
                                         slot.y + self.equipment_rect.y))
                    case 2:
                        if main_character.accessory:
                            screen.blit(main_character.accessory.image,
                                        (slot.x + self.equipment_rect.x,
                                         slot.y + self.equipment_rect.y))

            self.btn_army.show()
            if self.btn_army.is_selected:
                self.tbx_army.show()
            else:
                self.tbx_army.hide()
            self.text_box.show()
            self.btn_wmap.draw()
            self.btn_inventory.draw()
            self.btn_settings.draw()
            self.btn_wmap.checkFocused()
            self.btn_inventory.checkFocused()
            self.btn_settings.checkFocused()
            if self.btn_wmap.active and not self.alert_level_up and not self.game_settings:
                self.btn_wmap.getClicked()
            elif self.btn_inventory.active:
                self.btn_inventory.getClicked()
            elif self.btn_settings.active:
                self.btn_settings.getClicked()
        else:
            screen.blit(self.bg_image, (0, 0))
            self.text_input.hide()

            self.exp_bar.hide()

            self.gui_player_lvl.hide()
            self.txb_player_stats.hide()

            self.btn_army.hide()
            self.tbx_army.hide()
            self.text_box.hide()

    def updateInfo(self):
        fort_count = environment.countForts(tuple(environment.location_world))
        x, y = environment.location_world[0], environment.location_world[1]
        self.text_box.set_text(f"Region: {play_map.world[y][x]}\n"
                               f"Forts: {str(fort_count)}\n" +
                               f"Workers: {str(environment.men_power['Workers'])}\n" +
                               f"Soldiers: {str(environment.men_power['Soldiers'])}\n" +
                               f"Total workers: {str(environment.men_power['Total Workers'])}\n" +
                               f"Total soldiers: {str(environment.men_power['Total Soldiers'])}\n" +
                               f"<img src='data/gfx/GUI/pics/icons/Gold.png'> {str(environment.player.gold)}\n" +
                               f"<img src='data/gfx/GUI/pics/icons/Wood_Res.png'> {str(int(environment.player.wood))}\n" +
                               f"<img src='data/gfx/GUI/pics/icons/Stone_Res.png'> {str(int(environment.player.stone))}\n" +
                               f"<img src='data/gfx/GUI/pics/icons/Metal_Res.png'> {str(int(environment.player.metal))}\n" +
                               f"<img src='data/gfx/GUI/pics/icons/Gems_Res.png'> {str(int(environment.player.gems))}\n")

        self.gui_player_lvl.set_text(f"Lvl: {main_character.level}")
        self.txb_player_stats.set_text(f"Con: {main_character.con}\n"
                                       f"Wis: {main_character.wis}\n"
                                       f"Fai: {main_character.fai}\n"
                                       f"{main_character.bonus_name}: {main_character.bonus_value}\n"
                                       f"Str: {main_character.str}\n"
                                       f"Int: {main_character.int}\n"
                                       f"Cun: {main_character.cun}")

    def hide(self):
        if self.text_box.visible or self.exp_bar.visible:
            self.text_input.hide()

            self.gui_player_lvl.hide()

            self.btn_army.hide()
            self.tbx_army.hide()
            self.text_box.hide()

            self.exp_bar.hide()

            self.txb_player_stats.hide()

    def travel(self):
        if environment.player.destination is not None:
            environment.location_world = environment.player.destination[0]
            environment.location_region = environment.player.destination[1]
            self.setLocation(environment.location_world)
            environment.player.updateLocation()
            environment.calcEnvData()
            environment.player.destination = None
            if pygame.mixer_music.get_busy():
                pygame.mixer_music.fadeout(3000)

            exitLocal()

    def openAlert(self, alert_type: str):
        cancel = False
        for alert in self.alerts:
            if alert.alert_type == alert_type:
                cancel = True
        if not cancel:
            match alert_type:
                case "Entry":
                    x, y = environment.location_region
                    w_target = environment.location_world.copy()

                    count = 0
                    if x == 0:
                        w_target[0] -= 1
                        for tile in play_map.regions[w_target[1]][w_target[0]]:
                            if tile[-1] == 'e' and count != 0:
                                r_target = [len(play_map.regions[0][0]) - 1, count]
                                if environment.player.destination is None:
                                    environment.player.destination = [w_target, r_target]
                                break
                            count += 1
                    elif x == len(play_map.regions[0][0]) - 1:
                        w_target[0] += 1
                        for tile in play_map.regions[w_target[1]][w_target[0]]:
                            if tile[0] == 'e' and count != 0:
                                r_target = [0, count]
                                if environment.player.destination is None:
                                    environment.player.destination = [w_target, r_target]
                                break
                            count += 1
                    elif y == 0:
                        w_target[1] -= 1
                        for tile in play_map.regions[w_target[1]][w_target[0]][len(play_map.regions[0][0]) - 1]:
                            if tile == 'e':
                                r_target = [count, len(play_map.regions[0][0]) - 1]
                                if environment.player.destination is None:
                                    environment.player.destination = [w_target, r_target]
                                break
                            count += 1
                    elif y == len(play_map.regions[0][0]) - 1:
                        w_target[1] += 1
                        for tile in play_map.regions[w_target[1]][w_target[0]][0]:
                            if tile == 'e':
                                r_target = [count, 0]
                                if environment.player.destination is None:
                                    environment.player.destination = [w_target, r_target]
                                break
                            count += 1

                    alert = Alert(alert_type)
                    alert.setText(f"Travel to {play_map.world[w_target[1]][w_target[0]]} area?")
                    self.alerts.append(alert)

    def updateTbx_Army(self):
        environment.player.updateArmyPower()
        self.tbx_army.set_text(f"Army Size: {environment.player.army_amount}   Power: {environment.player.army_power}"
                               f"   Armour Tier: {environment.player.army_armour}"
                               f"   Weapon Tier: {environment.player.army_weapon}"
                               f"   Trained: {environment.player.army_trained}")

def getBGImg():
    x, y = environment.location_world[0], environment.location_world[1]
    biome = play_map.region_info[y][x]['Biome']
    path = "./data/gfx/Backgrounds/"
    match biome:
        case "Desert":
            bg_img = pygame.image.load(os.path.join(path, "Desert.png"))
        case "Forest":
            bg_img = pygame.image.load(os.path.join(path, "Forest.png"))
        case "Hills":
            bg_img = pygame.image.load(os.path.join(path, "Hills.png"))
        case "Swamp":
            bg_img = pygame.image.load(os.path.join(path, "Swamp.png"))
        case "Grassland":
            bg_img = pygame.image.load(os.path.join(path, "Grassland.png"))
        case "Lush":
            bg_img = pygame.image.load(os.path.join(path, "Lush.png"))
        case "Marsh":
            bg_img = pygame.image.load(os.path.join(path, "Marsh.png"))
        case "Rocks":
            bg_img = pygame.image.load(os.path.join(path, "Rocks.png"))
    return bg_img.convert()


# Translate the symbols of sector tiles to are types
class LocalRegion:
    def __init__(self, area_type):
        self.area_type = area_type
        self.title_bg = pygame.transform.scale(pygame.image.load("./data/gfx/GUI/pics/Title.png"), (WIDTH / 2, 64))
        self.font = pygame.font.SysFont("Ariel", 35)

        self.renderImage()

        self.textbox_info = None
        if re.search('camp|outpost|fort|castle|citadel|city|entry', self.area_type.lower()):
            if 'camp' not in self.area_type.lower() and self.area_type.lower() != 'entry':
                rect = (WIDTH / 10, 0, WIDTH / 2, 55)
                security, control, quality = environment.getInfo()
                textbox_info = f'Security: {security}  Control: {control}  Quality: {quality}  Recruit Cost: {environment.getRecruitCost()}'
                self.textbox_info = pygame_gui.elements.UITextBox(textbox_info, rect, manager=manager,
                                                                  object_id="#tbx_window")
                self.textbox_info.show()
        elif not self.area_type.lower() == 'stable':
            rect = (WIDTH / 10, 0, WIDTH / 2, 55)
            textbox_info = "Action points:      "
            for i in range(environment.player.ap):
                textbox_info += "<img src='data/gfx/GUI/pics/icons/action_points.png'>     "
            self.textbox_info = pygame_gui.elements.UITextBox(textbox_info, rect, manager=manager, object_id="#tbx_window")
            self.textbox_info.show()
        self.menu = ActionMenu()
        self.war_panel = None

    def drawTitle(self):
        text = self.area_type
        if text in environment.BuildTech:
            try:
                text += ": " + str(environment.getStructureName())
            except Exception as e:
                print(type(e), ':', e)

        text_surface = self.font.render(text, False, (10, 10, 10))
        screen.blit(self.title_bg, (WIDTH / 8, HEIGHT / 10))
        screen.blit(text_surface, (WIDTH / 3 - text_surface.get_width() / 2, HEIGHT / 8))

    def renderImage(self):
        background_image = getBGImg()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        screen.blit(background_image, (0, 0))
        struc = environment.getStructureName()
        if struc:
            grade = environment.structure["Fort"][struc]["Grade"]
            img_path = "./data/gfx/GUI/pics/" + grade + ".png"
            struc_img = pygame.transform.scale(pygame.image.load(img_path), (WIDTH*1.5, HEIGHT*1.5)).convert_alpha()
            screen.blit(struc_img, (-WIDTH/6, -HEIGHT/12))

    def showMenu(self):
        lbl_names = tuple()
        lbl_info = tuple()
        action_names = tuple()
        upgrade_names = tuple()

        if self.area_type == "Outpost":
            lbl_names = ("Outpost Management", "Outpost Upgrades")
            action_names = ("Manage Workers", "Manage Army")
            upgrades = environment.BuildTech["SubBuildings"]["FirstTier"]
            for upgrade in upgrades:
                if upgrade != "Unique" and upgrade not in environment.getBuilt():
                    # and has required building
                    if upgrades[upgrade]["Require"] is None or upgrades[upgrade]["Require"] in environment.getBuilt():
                        upgrade_names += (upgrade,)
                elif upgrade == "Unique":
                    for sub_upgrade in upgrades[upgrade]:
                        if upgrades[upgrade][sub_upgrade]["Require"] is None and \
                                not re.search("TownHall|Fortified Walls", " ".join(environment.getBuilt())):
                            upgrade_names += (sub_upgrade,)
                        elif upgrades[upgrade][sub_upgrade]["Require"] is not None and \
                                upgrades[upgrade][sub_upgrade]["Require"] in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)
        elif self.area_type == "Fort":
            lbl_names = ("Fort Management", "Fort Upgrades")
            action_names = ("Manage Workers", "Manage Army", "Blacksmith")

            # take all the remaining upgrades from first tier
            upgrades = environment.BuildTech["SubBuildings"]["FirstTier"]
            for upgrade in upgrades:
                if upgrade != "Unique" and upgrade not in environment.getBuilt():
                    if upgrades[upgrade]["Require"] is None or upgrades[upgrade]["Require"] in environment.getBuilt():
                        upgrade_names += (upgrade,)

            upgrades = environment.BuildTech["SubBuildings"]["SecondTier"]
            for upgrade in upgrades:
                if upgrade not in ("Castle", "Fort") and (upgrades[upgrade]["Require"] is None or
                        upgrades[upgrade]["Require"] in environment.getBuilt()) and \
                        upgrade not in environment.getBuilt():
                    upgrade_names += (upgrade,)
                elif upgrade == "Fort":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt() and \
                                upgrades[upgrade][sub_upgrade]["Require"] is None or \
                                upgrades[upgrade][sub_upgrade]["Require"] in environment.getBuilt() \
                                and sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)
        elif self.area_type == "Castle":
            lbl_names = ("Castle Management", "Castle Upgrades")
            action_names = ("Manage Workers", "Manage Army", "Merchants")

            # take all the remaining upgrades from first tier
            upgrades = environment.BuildTech["SubBuildings"]["FirstTier"]
            for upgrade in upgrades:
                if upgrade != "Unique" and upgrade not in environment.getBuilt():
                    if upgrades[upgrade]["Require"] is None or upgrades[upgrade]["Require"] in environment.getBuilt():
                        upgrade_names += (upgrade,)

            upgrades = environment.BuildTech["SubBuildings"]["SecondTier"]
            for upgrade in upgrades:
                if upgrade not in ("Castle", "Fort") and (upgrades[upgrade]["Require"] is None or
                                                          upgrades[upgrade]["Require"] in environment.getBuilt()) and \
                        upgrade not in environment.getBuilt():
                    upgrade_names += (upgrade,)
                elif upgrade == "Castle":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt() and \
                                upgrades[upgrade][sub_upgrade]["Require"] is None or \
                                upgrades[upgrade][sub_upgrade]["Require"] in environment.getBuilt() \
                                and sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)
        elif self.area_type == "Citadel":
            lbl_names = ("Castle Management", "Castle Upgrades")
            action_names = ("Manage Workers", "Manage Army", "Blacksmith")

            # take all the remaining upgrades from first tier
            upgrades = environment.BuildTech["SubBuildings"]["FirstTier"]
            for upgrade in upgrades:
                if upgrade != "Unique" and upgrade not in environment.getBuilt():
                    if upgrades[upgrade]["Require"] is None or upgrades[upgrade]["Require"] in environment.getBuilt():
                        upgrade_names += (upgrade,)

            # take all upgrades from second tier
            upgrades = environment.BuildTech["SubBuildings"]["SecondTier"]
            for upgrade in upgrades:
                if upgrade not in ("Castle", "Fort") and (upgrades[upgrade]["Require"] is None or
                                                          upgrades[upgrade]["Require"] in environment.getBuilt()) and \
                        upgrade not in environment.getBuilt():
                    upgrade_names += (upgrade,)
                elif upgrade == "Fort":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt() and \
                                upgrades[upgrade][sub_upgrade]["Require"] is None or \
                                upgrades[upgrade][sub_upgrade]["Require"] in environment.getBuilt() \
                                and sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)

            upgrades = environment.BuildTech["SubBuildings"]["ThirdTier"]
            for upgrade in upgrades:
                if upgrade == "Citadel":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)
        elif self.area_type == "City":
            lbl_names = ("Castle Management", "Castle Upgrades")
            action_names = ("Manage Workers", "Manage Army", "Merchants")

            # take all the remaining upgrades from first tier
            upgrades = environment.BuildTech["SubBuildings"]["FirstTier"]
            for upgrade in upgrades:
                if upgrade != "Unique" and upgrade not in environment.getBuilt():
                    if upgrades[upgrade]["Require"] is None or upgrades[upgrade]["Require"] in environment.getBuilt():
                        upgrade_names += (upgrade,)

            # take all upgrades from second tier
            upgrades = environment.BuildTech["SubBuildings"]["SecondTier"]
            for upgrade in upgrades:
                if upgrade not in ("Castle", "Fort") and (upgrades[upgrade]["Require"] is None or
                                                          upgrades[upgrade]["Require"] in environment.getBuilt()) and \
                        upgrade not in environment.getBuilt():
                    upgrade_names += (upgrade,)
                elif upgrade == "Castle":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt() and \
                                upgrades[upgrade][sub_upgrade]["Require"] is None or \
                                upgrades[upgrade][sub_upgrade]["Require"] in environment.getBuilt() \
                                and sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)

            upgrades = environment.BuildTech["SubBuildings"]["ThirdTier"]
            for upgrade in upgrades:
                if upgrade == "City":
                    for sub_upgrade in upgrades[upgrade]:
                        if sub_upgrade not in environment.getBuilt():
                            upgrade_names += (sub_upgrade,)
        elif self.area_type == "Stable":
            lbl_info = ("Stable area",)
            action_names = ("Outpost",)
        elif self.area_type in ("Wood", "Stone", "Metal", "Gems"):
            lbl_info = ("Area resource: " + self.area_type, )
            match self.area_type:
                case "Wood":
                    action_names = ("Lumber camp",)
                case "Stone":
                    action_names = ("Stone query",)
                case "Metal":
                    action_names = ("Metal query",)
                case "Gems":
                    action_names = ("Gems query",)
            action_names += ("Explore area", "Train yourself", "Train units")
        elif self.area_type == "Unstable":
            lbl_names = ("Unstable area", )
            action_names = ("Explore area", "Train yourself", "Train units", "Break camp")
        elif self.area_type == "Military Camp":
            if environment.player.army_amount > 0:
                amount, power = environment.player.army_amount, environment.player.army_power
                environment.addToMilitaryCamp(amount, power)
                environment.player.setArmyAmount(0)
                region_map.updateTbx_Army()
            self.war_panel = WarPanel()
        elif self.area_type == "Entry":
            # entries are to be connected
            # and so will have buttons to transition from map to map on to another entry point
            x, y = environment.location_region
            w_target = environment.location_world.copy()

            count = 0
            if x == 0:
                w_target[0] -= 1
                for tile in play_map.regions[w_target[1]][w_target[0]]:
                    if tile[-1] == 'e' and count != 0:
                        r_target = [len(play_map.regions[0][0]) - 1, count]
                        if environment.player.destination is None:
                            environment.player.destination = [w_target, r_target]
                        break
                    count += 1
            elif x == len(play_map.regions[0][0]) - 1:
                w_target[0] += 1
                for tile in play_map.regions[w_target[1]][w_target[0]]:
                    if tile[0] == 'e' and count != 0:
                        r_target = [0, count]
                        if environment.player.destination is None:
                            environment.player.destination = [w_target, r_target]
                        break
                    count += 1
            elif y == 0:
                w_target[1] -= 1
                for tile in play_map.regions[w_target[1]][w_target[0]][len(play_map.regions[0][0]) - 1]:
                    if tile == 'e':
                        r_target = [count, len(play_map.regions[0][0]) - 1]
                        if environment.player.destination is None:
                            environment.player.destination = [w_target, r_target]
                        break
                    count += 1
            elif y == len(play_map.regions[0][0]) - 1:
                w_target[1] += 1
                for tile in play_map.regions[w_target[1]][w_target[0]][0]:
                    if tile == 'e':
                        r_target = [count, 0]
                        if environment.player.destination is None:
                            environment.player.destination = [w_target, r_target]
                        break
                    count += 1
            lbl_names = (f"Travel to {play_map.world[w_target[1]][w_target[0]]}",)
            action_names = ("Travel",)

        self.menu.labels.clear()
        self.menu.btn_actions.clear()
        self.menu.btn_upgrades.clear()
        for i in range(len(lbl_names)):
            self.menu.drawLabel(lbl_names[i], (15, 15 + i * 220))

        for i in range(len(lbl_info)):
            self.menu.drawLabel(lbl_info[i], (15, 15 + i * 35))

        if self.area_type in ("Outpost", "Fort", "Castle", "Citadel", "City"):
            self.menu.drawLabel(f"Garrison: {environment.countGarrison()}", (15, 220))

        for i in range(len(action_names)):
            self.menu.drawActionButton(action_names[i], (15, 50 + i * 35))

        for i in range(len(upgrade_names)):
            self.menu.drawUpgradeButton(upgrade_names[i], (15, 50 + i * 35 + 220))

        if "Camp" not in self.area_type:
            self.menu.show()

    def hideMenu(self):
        if self.textbox_info:
            self.textbox_info.hide()

        self.menu.hide()

    def updateAP(self):
        textbox_info = "Action points:      "
        for i in range(environment.player.ap):
            textbox_info += "<img src='data/gfx/GUI/pics/icons/action_points.png'>     "

        self.textbox_info.set_text(textbox_info)

    def updateFortInfo(self):
        security, control, quality = environment.getInfo()
        textbox_info = f'Security: {security}  Control: {control}  Quality: {quality}  Recruit Cost: {environment.getRecruitCost()}'
        self.textbox_info.set_text(textbox_info)

    def refreshMenu(self):
        self.menu.kill()
        del self.menu
        self.menu = ActionMenu()
        self.showMenu()

        self.menu.alerts.clear()


def getAreaType(area_type):
    match area_type:
        case "-":
            return "Unstable"
        case "e":
            return "Entry"
        case "v":
            return "Stable"
        case "@":
            return "Wood"
        case "#":
            return "Stone"
        case "%":
            return "Metal"
        case "&":
            return "Gems"
        case "m":
            return "Military Camp"
        case "w":
            return "Wood Camp"
        case "s":
            return "Stone Camp"
        case "t":
            return "Metal Camp"
        case "g":
            return "Gems Camp"
        case "o":
            return "Outpost"
        case "f":
            return "Fort"
        case "c":
            return "Castle"
        case "r":
            return "Citadel"
        case "q":
            return "City"


# Change to battle screen that manages the battle and return the results to player possessions
class BattleScreen:
    def __init__(self, title):
        self.title = title
        self.turn = 1
        self.is_player_turn = False
        self.bg_color = pygame.Color('#121342')
        self.bg_img = getBGImg()
        self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))
        self.dmg_img = pygame.image.load("./data/gfx/GUI/Effects/DamageBubble.png").convert_alpha()
        self.miss_img = pygame.image.load("./data/gfx/GUI/Effects/MissBubble.png").convert_alpha()

        self.dmg_disp = -1

        # player object
        self.player = None
        print("Creating Battle Screen")

        self.monster_names = list(map(lambda x: x, Monster_Sprite_Path))

        # monster object
        self.monster = None
        self.monster_weak = characters.Monster(random.choice(self.monster_names), manager, 25, 60, [1, 1, 1, 1, 1, 1, 1])

        self.pEffect = None

        self.start_lbl = pygame_gui.elements.UILabel(pygame.Rect((350, 75), (125, 50)), "Choose Class", manager=manager)

        self.ddMenu_start = pygame_gui.elements.UIDropDownMenu(options_list=["Warlord", "Wizard", "Hunter"],
                                                          relative_rect=pygame.Rect((350, 125), (125, 50)),
                                                          starting_option="Warlord",
                                                          manager=manager)

        self.btn_start = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (125, 50)),
                                                 text='Start Battle',
                                                 manager=manager)

        self.btn_attack = None
        self.btn_passive = None
        self.btn_skills = None
        self.skills = effects.Skills(manager)
        self.skill_costs = (
            10 + main_character.level // 10, 22 + main_character.level // 10,
            34 + main_character.level // 10, 48 + main_character.level // 10,
            60 + main_character.level // 10, 84 + main_character.level // 10,
            112 + main_character.level // 10, 124 + main_character.level // 10
        )

        self.createUI()

        self.btn_die = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 475), (125, 50)),
                                               text='Die',
                                               manager=manager)

        self.btn_restart = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((400, 475), (125, 50)),
                                                   text='Restart',
                                                   manager=manager)

        self.RENDER_SPEED = 7
        self.WAIT_BEFORE_END = 5
        self.end_countdown = -1

        self.hide()

    def createUI(self):
        if self.btn_attack:
            self.btn_attack.kill()

        if self.btn_passive:
            self.btn_passive.kill()

        if self.btn_skills:
            for btn_skill in self.btn_skills:
                btn_skill.kill()

        self.btn_attack = None
        self.btn_passive = None
        self.btn_skills = None

        btn_size = (WIDTH / 16, WIDTH / 16)
        match main_character.kind:
            case "Warlord":
                self.btn_attack = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50, HEIGHT * 4 / 5),
                                              btn_size),
                    text="",
                    tool_tip_text="Attack",
                    manager=manager,
                    object_id="#skill_atk_warlord")

                self.btn_passive = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 2 - btn_size[0] * 2, HEIGHT * 1 / btn_size[1] / 2 + btn_size[1] / 2),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Turtle reflex (Passive) - Every 3rd incoming attack is absorbed",
                        manager=manager,
                        object_id="#skill_turtle-reflex_warlord")

                self.btn_skills = [
                    pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 2, HEIGHT * 4 / 5),
                                              btn_size),
                    text="",
                    tool_tip_text=f"Valiant slash({self.skill_costs[0]}MP) - Damage ignores armour",
                    manager=manager,
                    object_id="#skill_valiant-slash_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 3, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Valiant slash({self.skill_costs[1]}MP) - Damage ignores evasion",
                        manager=manager,
                        object_id="#skill_aura-cleave_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 4, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Astral shred({self.skill_costs[2]}MP) - Damage using opponent's mana",
                        manager=manager,
                        object_id="#skill_astral-shred_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 5, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Spectral Duel({self.skill_costs[3]}MP) - Damage twice using physical and magical damage",
                        manager=manager,
                        object_id="#skill_spectral-duel_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 6, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Vanguard's stance({self.skill_costs[4]}MP) - Adds health for 3 turns that later will be deducted",
                        manager=manager,
                        object_id="#skill_vanguards-stance_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 7, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Ancestors Protection({self.skill_costs[5]}MP) - Can use if hp is lower than 50%, "
                                      "adds 25% to max hp and fills hp to max "
                                      "and decrease ap by 1 until the end of the battle",
                        manager=manager,
                        object_id="#skill_ancestors-protection_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 8, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Aggression (Toggable) - Deal more damage but take more damage",
                        manager=manager,
                        object_id="#skill_aggression_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 9, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Blood thirst(Stack max 5) ({self.skill_costs[6]}MP)- "
                                      "Feed your sword with opponents blood "
                                      "by scaling damage up to 5 times can't be used after that",
                        manager=manager,
                        object_id="#skill_blood-thirst_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 10, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"True Vigor(Unlock 5 locks) ({self.skill_costs[7]}MP)- "
                                      "1: AP + 1, 2: Constitution + 10, 3: Strength + 10, "
                                      "4: EVA + 10, 5: Luck + 10, Constitution + 20",
                        manager=manager,
                        object_id="#skill_true-vigor_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 11, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Transcendence - For the 5 next turns: Triple normal damange, "
                                      "double skill damage, Ignore cost, cooldown and damage taken(Needs 5 locks)",
                        manager=manager,
                        object_id="#skill_transcendence_warlord"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + 48, HEIGHT * 1 / 5 + 24),
                                                  (24, 24)),
                        text="",
                        tool_tip_text="Aggression - Toggled on",
                        manager=manager,
                        object_id="#skill_aggression-boost_warlord",
                        visible=False
                    )
                ]

            case "Sourcerer":
                self.btn_attack = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50, HEIGHT * 4 / 5),
                                              btn_size),
                    text="",
                    tool_tip_text="Attack",
                    manager=manager,
                    object_id="#skill_atk_sourcerer")

                self.btn_passive = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 2 - btn_size[0] * 2, HEIGHT * 1 / btn_size[1] / 2 + btn_size[1] / 2),
                                                  btn_size),
                        text="",
                        tool_tip_text="Third eye (Passive) - recover 10% mana per turn",
                        manager=manager,
                        object_id="#skill_third-eye_sourcerer")

                self.btn_skills = [
                    pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 2, HEIGHT * 4 / 5),
                                              btn_size),
                    text="",
                    tool_tip_text=f"Psychic Wave ({self.skill_costs[0]}MP)- Deal damage weakening opponent's next attack",
                    manager=manager,
                    object_id="#skill_psychic-wave_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 3, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Cloud mind ({self.skill_costs[1]}MP)- Deal damage if oponent's next attack misses",
                        manager=manager,
                        object_id="#skill_cloud-mind_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 4, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Tear's ripple ({self.skill_costs[2]}MP)- Deal echoing damage each turn for 3 turns that is doubled the 3rd time",
                        manager=manager,
                        object_id="#skill_tears-ripple_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 5, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Diamond dust ({self.skill_costs[3]}MP)- Deal damage freeze oponent can't evade next attack",
                        manager=manager,
                        object_id="#skill_diamond-dust_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 6, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Arcane barrier ({self.skill_costs[4]}MP)- lose 5% of max mana per turn to absorb damage "
                                      "if lower than your own otherwise reduce by C",
                        manager=manager,
                        object_id="#skill_arcane-barrier_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 7, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Aegis shield ({self.skill_costs[5]}MP)- Use 10% of hp and 60% of oponent's mana "
                                      "to reflect 60% of enemy mana + 40% player matk damage of the next attack",
                        manager=manager,
                        object_id="#skill_aegis-shield_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 8, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Blood magic (Toggable) - Use your own blood to amplify magic damage",
                        manager=manager,
                        object_id="#skill_blood-magic_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 9, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Arcane frenzy(Stack max 5) ({self.skill_costs[6]}MP)- "
                                      "Cast last attack multiplying it by 5 up to 5 times can't be used after that",
                        manager=manager,
                        object_id="#skill_arcane-frenzy_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 10, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"True Spirit(Unlock 5 locks) ({self.skill_costs[7]}MP)- "
                                      "1: AP + 1, 2: Spirit + 10, 3: Magic + 10, "
                                      "4: EVA + 10, 5: Luck + 10, Spirit + 20",
                        manager=manager,
                        object_id="#skill_true-spirit_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 11, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Transcendence - For the 5 next turns: Triple normal damange, "
                                      "double skill damage, Ignore cost, cooldown and damage taken(Needs 5 locks)",
                        manager=manager,
                        object_id="#skill_transcendence_sourcerer"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + 48, HEIGHT * 1 / 5 + 24),
                                                  (24, 24)),
                        text="",
                        tool_tip_text="Blood magic - Toggled on",
                        manager=manager,
                        object_id="#skill_blood-magic-boost_sourcerer")
                ]

            case "Hunter":
                self.btn_attack = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50, HEIGHT * 4 / 5),
                                              btn_size),
                    text="",
                    tool_tip_text="Attack",
                    manager=manager,
                    object_id="#skill_atk_hunter")

                self.btn_passive = pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 2 - btn_size[0] * 2, HEIGHT * 1 / btn_size[1] / 2 + btn_size[1] / 2),
                                                  btn_size),
                        text="",
                        tool_tip_text="Snake eyes (Passive) - Every 3rd attack is critical",
                        manager=manager,
                        object_id="#skill_snake-eyes_hunter")

                self.btn_skills = [
                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 2, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Analize ({self.skill_costs[0]}MP)- expose oponent's next move",
                        manager=manager,
                        object_id="#skill_analize_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 3, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Disarm ({self.skill_costs[1]}MP)- cancel oponent's next move",
                        manager=manager,
                        object_id="#skill_disarm_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 4, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Recareate ({self.skill_costs[2]}MP)- use oponent's previos move",
                        manager=manager,
                        object_id="#skill_recreate_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 5, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Rose Thorn ({self.skill_costs[3]}MP)- Damage oponent if oponent hits",
                        manager=manager,
                        object_id="#skill_rose-thorn_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 6, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Better position ({self.skill_costs[4]}MP)- Take 20% of oponent's physical defense for 3 turns",
                        manager=manager,
                        object_id="#skill_better-position_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 7, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Intimidate ({self.skill_costs[5]}MP)- "
                                      "Reduce oponent's critical damage by 20% "
                                      "until the end of the battle in exchange for 1 turn",
                        manager=manager,
                        object_id="#skill_intimidate_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 8, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Perception (Togable) - Dodge more often but increase skills cooldown",
                        manager=manager,
                        object_id="#skill_perception_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 9, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"Deadly composition(Stack max 5) ({self.skill_costs[6]}MP)- "
                                      "Poison your weapon with aditional venom each time "
                                      "adding DOT damage up to 5 times can't be used after that",
                        manager=manager,
                        object_id="#skill_deadly-composition_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 10, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text=f"True Speed(Unlock 5 locks) ({self.skill_costs[7]}MP)- "
                                      "1: AP + 1, 2: Stamina + 10, 3: Agility + 10, "
                                      "4: EVA + 10, 5: Luck + 10, Stamina + 20",
                        manager=manager,
                        object_id="#skill_true-speed_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + btn_size[0] * 11, HEIGHT * 4 / 5),
                                                  btn_size),
                        text="",
                        tool_tip_text="Transcendence - For the 5 next turns: Triple normal damange, "
                                      "double skill damage, Ignore cost, cooldown and damage taken(Needs 5 locks)",
                        manager=manager,
                        object_id="#skill_transcendence_hunter"),

                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((WIDTH / 50 + 48, HEIGHT * 1 / 5 + 24),
                                                  (24, 24)),
                        text="",
                        tool_tip_text="Perception - Toggled on",
                        manager=manager,
                        object_id="#skill_perception-boost_hunter")
                ]

            case default:
                self.btn_attack = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((WIDTH / 50, HEIGHT * 4 / 5),
                                              btn_size),
                    text='Attack',
                    tool_tip_text="Attack",
                    manager=manager,
                    object_id="#skill_atk_warlord")

    def show(self):
        #self.btn_start.show()
        battle_screen.btn_attack.show()
        battle_screen.btn_passive.show()
        for i in range(len(self.btn_skills)):
            if main_character.level > i + int(i / 4) * 2 + 1:
                self.btn_skills[i].show()
            else:
                self.btn_skills[i].hide()

        battle_screen.player.HealthBar.show()
        battle_screen.player.MagicBar.show()
        battle_screen.player.SpiritBar.show()

        battle_screen.monster.HealthBar.show()
        battle_screen.monster.MagicBar.show()
        battle_screen.monster.SpiritBar.show()

    def hide(self):
        self.start_lbl.hide()
        self.ddMenu_start.hide()
        self.btn_start.hide()

        self.btn_attack.hide()
        self.btn_passive.hide()
        for btn_skill in self.btn_skills:
            btn_skill.hide()
        self.btn_die.hide()
        self.btn_restart.hide()

    def timerTick(self):
        global time_in_game

        if time_in_game[3] % self.RENDER_SPEED == 0:
            return True
        return False

    def disableButtons(self):
        self.is_player_turn = False
        if self.btn_attack.is_enabled:
            self.btn_attack.disable()
        for skill in self.btn_skills:
            if skill.is_enabled:
                skill.disable()
        self.monster.updateStats(is_effect=True)

    def enableButtons(self):
        if not self.btn_attack.is_enabled:
            self.btn_attack.enable()
        for i in range(len(self.btn_skills)):
            if main_character.level < i + int(i / 4) * 2 + 1:
                self.btn_skills[i].hide()

            if main_character.kind == "Warlord":
                match i:
                    case 4:
                        if self.player.findBoost("add health"):
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 5:
                        if self.player.findBoost("tradeoff"):
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 7:
                        count = self.skills.getSkill("blood-thirst")["count"]
                        if count >= 5:
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 8:
                        count = self.skills.getSkill("true-vigor")["lock_idx"]
                        if count > 5:
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 9:
                        if self.player.ult_turn == 0 and not self.player.is_transcended:
                            self.btn_skills[i].enable()
                        else:
                            self.btn_skills[i].disable()
                    case _:
                        self.btn_skills[i].enable()
            elif main_character.kind == "Sourcerer":
                match i:
                    case 8:
                        count = self.skills.getSkill("true-spirit", is_physical=False)["lock_idx"]
                        if count > 5:
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 9:
                        if self.player.ult_turn == 0 and not self.player.is_transcended:
                            self.btn_skills[i].enable()
                        else:
                            self.btn_skills[i].disable()
                    case _:
                        self.btn_skills[i].enable()
            elif main_character.kind == "Hunter":
                match i:
                    case 8:
                        count = self.skills.getSkill("true-speed")["lock_idx"]
                        if count > 5:
                            self.btn_skills[i].disable()
                        else:
                            self.btn_skills[i].enable()
                    case 9:
                        if self.player.ult_turn == 0 and not self.player.is_transcended:
                            self.btn_skills[i].enable()
                        else:
                            self.btn_skills[i].disable()
                    case _:
                        self.btn_skills[i].enable()

    def resetCounts(self):
        if main_character.kind == "Warlord":
            self.skills.getSkill("blood-thirst")["count"] = 0
            self.skills.getSkill("true-vigor")["lock_idx"] = 1
        elif main_character.kind == "Sourcerer":
            self.skills.getSkill("true-spirit", False)["lock_idx"] = 1
        elif main_character.kind == "Hunter":
            self.skills.getSkill("true-speed")["lock_idx"] = 1

    def update(self):
        #  screen.fill(self.bg_color)
        screen.blit(self.bg_img, (0, 0))
        font = pygame.font.Font(None, 32)
        txt = font.render(f"Turn: {self.turn}", True, (50, 250, 50))
        screen.blit(txt, (WIDTH / 2 - 20, 40))

        player_sprite_frame = pygame.transform.scale(get_frame(self.player.animation,
                                        Player_Sprite_Path[self.player.kind]["Size"][0],
                                        Player_Sprite_Path[self.player.kind]["Size"][1],
                                        [self.player.frame, 0]), (300, 300)).convert_alpha()

        player_frames = self.player.getAnimationFrames(Player_Sprite_Path[self.player.kind]["Size"][0])

        monster_sprite_frame = pygame.transform.scale(get_frame(self.monster.animation,
                                                               Monster_Sprite_Path[self.monster.kind]["Size"][0],
                                                               Monster_Sprite_Path[self.monster.kind]["Size"][1],
                                                               [self.monster.frame, 0]), (300, 300)).convert_alpha()

        monster_frames = self.monster.getAnimationFrames(Monster_Sprite_Path[self.monster.kind]["Size"][0])

        monster_sprite_frame = pygame.transform.flip(monster_sprite_frame, True, False)


        if self.timerTick():
            self.player.frame += 1
            self.monster.frame += 1
            self.lookForEffects()

        self.player.animate()
        self.monster.animate()

        if self.player.state == "Idle" and self.player.frame >= player_frames:
            self.player.frame = 0
        elif self.player.state == "Die" and self.player.frame >= player_frames:
            self.player.frame = player_frames
        elif self.player.state == "Attack" and self.player.frame >= player_frames:
            self.player.frame = 0
            self.monster.frame = 0
            self.player.getIdle()
            self.monster.getHit()
            self.dmg_disp = self.monster.pDefend(self.player.pAttack())
        elif self.player.state == "Take Hit" and self.player.frame >= player_frames:
            self.player.frame = 0
            if self.player.hits_left > 0:
                self.player.getHit()
            else:
                self.player.getIdle()
            if self.player.current_health <= 0:
                self.player.current_health = 0
                self.player.getDead()
            if self.dmg_disp != -1:
                self.dmg_disp = -1
            self.is_player_turn = True
            if self.player.isPassiveOn() and self.player.kind == "Sourcerer":
                add_mana = self.player.mind.health_capacity // 10
                self.player.mind.addCurrent(add_mana)

        elif self.player.state == "Cast" and self.player.frame >= player_frames:
            self.player.frame = 0
            self.player.getIdle()

            skill_type = self.player.used_skill["type"]
            skill = self.player.used_skill["effect"]

            if self.player.used_skill["type"] == "countdown" and self.player.used_skill["count"] == 4:
                skill = self.player.used_skill["effectu"]
                skill.pos = (self.mns_pos[0], self.mns_pos[1] * 3 / 2)

            skill.activate()
            self.player.enableBoosts()
            if skill_type == "add health":
                if not self.player.findBoost("add health"):
                    self.player.aDefense(self.player.aAttack(self.player.used_skill["type"]))
                else:
                    self.enableButtons()
            elif skill_type == "tradeoff" or skill_type == "absorb damage":
                if not self.player.findBoost("tradeoff"):
                    self.player.aDefense(self.player.aAttack(self.player.used_skill["type"]))
                    self.player.enableBoosts()
                else:
                    self.enableButtons()
            elif skill_type == "boost stats":
                self.player.aDefense(self.player.aAttack(self.player.used_skill["type"]))
            elif skill_type == "weaken opp":
                self.monster.frame = 0
                self.monster.getHit()
                self.dmg_disp = self.monster.aDefense(self.player.aAttack(self.player.used_skill["type"]))
            elif skill_type == "transcendence":
                self.player.is_transcended = True
            else:
                if skill_type != "con damage" and skill_type != "damage over time":
                    self.monster.frame = 0
                    self.monster.getHit()
                    self.dmg_disp = self.monster.aDefense(self.player.aAttack(self.player.used_skill["type"]))

            self.player.getIdle()

        self.monsterTurn(monster_frames)

        # turn on buttons on players turn, check if monster is dead end the battle
        if self.is_player_turn and not self.btn_attack.is_enabled:
            self.enableButtons()
            self.player.updateStats(is_effect=True)
        elif self.monster.is_dead or self.player.current_health <= 0:
            if self.timerTick():
                self.end_countdown += 1
            if self.end_countdown == self.WAIT_BEFORE_END:
                self.endBattle()

        # rendering of the battle
        if self.end_countdown == 0:
            screen.blit(player_sprite_frame, self.plr_pos)
            screen.blit(monster_sprite_frame, self.mns_pos)

            if self.player.used_skill:
                skill = self.player.used_skill["effect"]
                if self.player.used_skill["type"] == "countdown":
                    if self.player.used_skill["count"] == 5:
                        skill = self.player.used_skill["effectu"]
                        if skill.is_active:
                            screen.blit(skill.sprite_frame, skill.pos)
                    else:
                        skill = self.player.used_skill["effect"]
                        if skill.is_active:
                            screen.blit(skill.sprite_frame, skill.pos)
                if skill.is_active:
                    screen.blit(skill.sprite_frame, skill.pos)

            if self.player.state == "Take Hit":
                pos = (self.plr_pos[0] + 150, self.plr_pos[1] + 50)

                if self.dmg_disp > 0:
                    screen.blit(self.dmg_img, pos)
                    font = pygame.font.Font(None, 32)
                    txt = font.render(f"{self.dmg_disp}", True, (180, 190, 160))
                    screen.blit(txt, (pos[0] + 48, pos[1] + 60))

                    if not pygame.mixer.get_busy():
                        sfx_hit.play()
                else:
                    screen.blit(self.miss_img, pos)
                    font = pygame.font.Font(None, 32)
                    txt = font.render("Miss", True, (220, 220, 255))
                    screen.blit(txt, (pos[0] + 48, pos[1] + 60))

                    if not pygame.mixer.get_busy():
                        sfx_miss.play()

            elif self.monster.state == "Take Hit":
                pos = (self.mns_pos[0] + 50, self.mns_pos[1] + 50)

                if self.dmg_disp > 0:
                    screen.blit(self.dmg_img, pos)
                    font = pygame.font.Font(None, 32)
                    txt = font.render(f"{self.dmg_disp}", True, (180, 190, 160))
                    screen.blit(txt, (pos[0] + 48, pos[1] + 60))

                    if not pygame.mixer.get_busy():
                        sfx_hit.play()
                else:
                    screen.blit(self.miss_img, pos)
                    font = pygame.font.Font(None, 32)
                    txt = font.render("Miss", True, (220, 220, 255))
                    screen.blit(txt, (pos[0] + 48, pos[1] + 60))

                    if not pygame.mixer.get_busy():
                        sfx_miss.play()

    def lookForEffects(self):
        if self.player.used_skill:
            skill = self.player.used_skill["effect"]
            if self.player.used_skill["type"] == "countdown" and self.player.used_skill["count"] == 5:
                skill = self.player.used_skill["effectu"]

            if skill.is_active:
                skill.frame += 1
                skill_type = self.player.used_skill["type"]
                skill.animate()

                if skill.frame >= skill.getAnimationFrames():
                    if skill_type == "add health" or skill_type == "tradeoff" or skill_type == "boost stats" \
                            or skill_type == "absorb damage" or skill_type == "transcendence":
                        self.player.is_transcended = True
                        self.is_player_turn = True
                    elif skill_type == "con damage" or skill_type == "damage over time":
                        self.monster.frame = 0
                        self.monster.getHit()
                        self.dmg_disp = self.monster.aDefense(self.player.aAttack(self.player.used_skill["type"]))

                    skill.deactivate()

    def startBattle(self):
        global inventory
        self.turn = 1
        pygame.display.set_caption(self.title)


        # asigning monster and his stats to current monter
        #self.monster_weak = characters.Monster(random.choice(self.monster_names), manager, 25, 60, [5, 5, 5, 5, 5, 5])
        #self.monster = characters.Monster(self.monster_weak, manager, self.monster_weak.exp, self.monster_weak.gold)

        # randomize stats acording to character's level

        mc = main_character

        mc.boosts.clear()
        mc.updateStats()
        self.resetCounts()

        chaos = environment.chaos_level
        luck = main_character.level if main_character.level < 5 else 5
        r_stats = [
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            r_int(mc.level - luck, mc.level * chaos - luck) + r_int(-luck, luck),
            mc.level
                   ]
        r_exp = r_int(5, 5 * mc.level)
        r_gold = r_int(100, 300 * mc.level)

        self.player = characters.PlayerHero(main_character, manager)
        self.monster = characters.Monster(chs(self.monster_names), manager, r_exp, r_gold, r_stats)

        self.is_player_turn = True
        self.end_countdown = 0

        self.plr_pos = (WIDTH / 10, characters.LEFT_POS[1] + HEIGHT / 10)
        self.mns_pos = (
        WIDTH * 4 / 5 - Monster_Sprite_Path[self.monster.kind]["Size"][0] - 50, characters.RIGHT_POS[1] + HEIGHT / 10)

        x, y = environment.location_world[0], environment.location_world[1]
        biome = play_map.region_info[y][x]['Biome']
        self.bg_img = getBGImg()
        self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))
        print(f"Biome is: {biome}")

        if inventory:
            inventory.kill()
            inventory = None
            region_map.btn_inventory.switch(0)

        if pygame.mixer.get_busy():
            pygame.mixer.stop()

        if region_map.alert_level_up:
            region_map.alert_level_up.hide()

    def monsterTurn(self, monster_frames):
        if self.monster.state == "Idle" and self.monster.frame >= monster_frames:
            self.monster.frame = 0
        elif self.monster.state == "Die" and self.monster.frame >= monster_frames:
            self.monster.frame = monster_frames - 1
            self.monster.getFinished()
        elif self.monster.state == "Attack" and self.monster.frame >= monster_frames:
            self.monster.frame = 0
            self.player.frame = 0
            self.monster.getIdle()
            if self.player.findBoost(name="arcane-barrier") or self.player.findBoost(name="better-position"):
                self.player.enableBoosts()
                self.dmg_disp = -1
                boost = self.player.findBoost(name="better-position")
                if boost:
                    boost["turn"] += 1
                self.is_player_turn = True
                boost = self.player.findBoost("better-position")
            elif self.player.findBoost(name="aegis-shield"):
                self.player.enableBoosts()
                boost = self.player.findBoost(name="aegis-shield")
                boost["turn"] += 1
                self.dmg_disp = -1
                self.monster.getHit()
                self.dmg_disp = self.monster.pDefend(self.player.pAttack())
                self.is_player_turn = True
            else:
                self.player.getHit()
                self.dmg_disp = self.player.pDefend(self.monster.pAttack())

            if self.player.is_transcended:
                self.player.ult_turn += 1
                if self.player.ult_turn >= self.player.ult_limit:
                    self.player.is_transcended = False
            self.turn += 1
        elif self.monster.state == "Take Hit" and self.monster.frame >= monster_frames:
            self.monster.frame = 0
            # check multiple hits
            if self.monster.hits_left > 1:
                self.monster.getHit()
                match main_character.kind:
                    case "Warlord":
                        self.dmg_disp = self.monster.pDefend(self.player.pAttack())
                    case "Sourcerer":
                        self.dmg_disp = self.monster.mDefend(self.player.mAttack())
                    case "Hunter":
                        # flip a coin for damage type
                        coin = bool(r_int(0, 1))
                        if coin:
                            self.dmg_disp = self.monster.pDefend(self.player.aAttack)
                        else:
                            self.dmg_disp = self.monster.mDefend(self.player.mAttack)
                return
            elif self.monster.current_health <= 0:
                self.monster.current_health = 0
                self.monster.getDead()
            else:
                if not self.is_player_turn:
                    self.monster.getAttacking()

                    if not pygame.mixer.get_busy():
                        sfx_attack.play()
                else:
                    self.monster.getIdle()
            if self.dmg_disp != -1:
                self.dmg_disp = -1

            dot_effect = self.monster.enableHinders()
            if dot_effect != -1:
                self.dmg_disp = dot_effect

    def endBattle(self):
        global main_character, reward_window
        print("Battle Ended!")

        if self.player.current_health > 0:
            reward_exp, reward_gold = self.monster.die()

            roll = r_int(0, 100)
            if roll <= 2:
                reward_itms = addItemsToInv(1)
            else:
                reward_itms = []

            pygame.mixer.stop()
            sfx_victory.play()
        else:
            reward_exp, reward_gold, reward_itms = r_int(1, 10), 0, []

            pygame.mixer.stop()
            sfx_defeat.play()

        getRewarded(reward_exp, reward_gold)

        if reward_window:
            reward_window.kill()
        print(reward_itms)
        reward_window = RewardWindow(reward_exp, reward_gold, reward_itms)

        self.hide()
        self.player.HealthBar.hide()
        self.player.MagicBar.hide()
        self.player.SpiritBar.hide()

        self.monster.HealthBar.hide()
        self.monster.MagicBar.hide()
        self.monster.SpiritBar.hide()

        del self.player
        del self.monster

        self.end_countdown = -1

        if region_map.alert_level_up:
            region_map.alert_level_up.show()

        exitLocal()


class SubMenu(pygame_gui.elements.UIWindow):
    def __init__(self, menu_type):
        super().__init__(pygame.Rect(WIDTH / 4, HEIGHT / 4, 620, 340), manager,
                         object_id="#window")
        self.menu_type = menu_type

        self.btn_cancel = pygame_gui.elements.UIButton(
            pygame.Rect(25, 220, 150, 35),
            "Cancel",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )
        self.btn_confirm = pygame_gui.elements.UIButton(
            pygame.Rect(620 - 185 - 25, 220, 150, 35),
            "Confirm",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )


class WorkerManagement(SubMenu):
    def __init__(self, menu_type):
        super().__init__(menu_type)

        offset = (80, 15)
        label_size = (165, 35)
        button_size = (35, 35)
        environment.calcEnvData()

        self.workers, self.workers_max = environment.getWorkersInStructure(), environment.getMaxWorkersInStructure()

        camp = environment.structure["Camp"][tuple(environment.location_world)]
        self.resources = [
            camp["Wood"][0],
            camp["Stone"][0],
            camp["Metal"][0],
            camp["Gems"][0]
        ]
        self.amount_inc, self.amount_dec = 5, 5

        self.lbl_workers_info = pygame_gui.elements.UILabel(
            pygame.Rect(offset[0] + 140, offset[1], label_size[0] + 20, label_size[1]),
            "Workers amount: ",
            manager,
            container=self,
            parent_element=self
        )

        self.worker_job = "gathering "
        self.lbl_wood_info = pygame_gui.elements.UILabel(
            pygame.Rect(offset[0], offset[1] + 40, label_size[0], label_size[1]),
            self.worker_job + "wood: ",
            manager,
            container=self,
            parent_element=self
        )

        self.lbl_stone_info = pygame_gui.elements.UILabel(
            pygame.Rect(offset[0], offset[1] + 120, label_size[0], label_size[1]),
            self.worker_job + "stone: ",
            manager,
            container=self,
            parent_element=self
        )

        self.lbl_metal_info = pygame_gui.elements.UILabel(
            pygame.Rect(offset[0] + 270, offset[1] + 40, label_size[0], label_size[1]),
            self.worker_job + "metal: ",
            manager,
            container=self,
            parent_element=self
        )

        self.lbl_gems_info = pygame_gui.elements.UILabel(
            pygame.Rect(offset[0] + 270, offset[1] + 120, label_size[0], label_size[1]),
            self.worker_job + "gems: ",
            manager,
            container=self,
            parent_element=self
        )

        # Buttons
        button_dist = 50

        # Wood
        self.btn_wood_inc = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 50 + button_dist, offset[1] + 85, 35, 35),
            "+",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        self.btn_wood_dec = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 50 - button_dist, offset[1] + 85, 35, 35),
            "-",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        # Stone
        self.btn_stone_inc = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 50 + button_dist, offset[1] + 165, 35, 35),
            "+",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        self.btn_stone_dec = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 50 - button_dist, offset[1] + 165, 35, 35),
            "-",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        # Metal
        self.btn_metal_inc = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 325 + button_dist, offset[1] + 85, 35, 35),
            "+",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        self.btn_metal_dec = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 325 - button_dist, offset[1] + 85, 35, 35),
            "-",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        # Gems
        self.btn_gems_inc = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 325 + button_dist, offset[1] + 165, 35, 35),
            "+",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

        self.btn_gems_dec = pygame_gui.elements.UIButton(
            pygame.Rect(offset[0] + 325 - button_dist, offset[1] + 165, 35, 35),
            "-",
            manager,
            object_id= "#button",
            container=self,
            parent_element=self
        )

    def updateMenu(self):
        self.lbl_workers_info.set_text(
            "Workers amount: " + f"{self.workers}/{self.workers_max}"
        )

        self.lbl_wood_info.set_text(self.worker_job + "wood: " + str(
            self.resources[0] if self.resources[0] > -1 else "N/A"))
        self.lbl_stone_info.set_text(self.worker_job + "stone: " + str(
            self.resources[1] if self.resources[1] > -1 else "N/A"))
        self.lbl_metal_info.set_text(self.worker_job + "metal: " + str(
            self.resources[2] if self.resources[2] > -1 else "N/A"))
        self.lbl_gems_info.set_text(self.worker_job + "gems: " + str(
            self.resources[3] if self.resources[3] > -1 else "N/A"))

    def updateInfo(self):
        idx = 0
        camp = environment.structure["Camp"][tuple(environment.location_world)]
        for resource in camp:
            camp[resource][0] = self.resources[idx]
            idx += 1

    def confirm(self):
        self.updateInfo()
        environment.setWorkersInStructure(self.workers)

        idx = 0
        camp = environment.structure["Camp"][tuple(environment.location_world)]
        for resource in camp:
            camp[resource][0] = self.resources[idx]
            idx += 1

    def handleEvent(self, event):
        if event.ui_element == self.btn_wood_inc and \
                 (self.workers < self.workers_max):
            if self.resources[0] != -1:
                self.workers += self.amount_inc
                self.resources[0] += self.amount_inc

        elif event.ui_element == self.btn_wood_dec and \
                (self.workers > 0 and self.resources[0] > 0):
            if self.resources[0] != -1:
                self.workers -= self.amount_dec
                self.resources[0] -= self.amount_dec

        elif event.ui_element == self.btn_stone_inc and \
                (self.workers < self.workers_max):
            if self.resources[1] != -1:
                self.workers += self.amount_inc
                self.resources[1] += self.amount_inc

        elif event.ui_element == self.btn_stone_dec and \
                (self.workers > 0 and self.resources[1] > 0):
            if self.resources[1] != -1:
                self.workers -= self.amount_dec
                self.resources[1] -= self.amount_dec

        elif event.ui_element == self.btn_metal_inc and \
                (self.workers < self.workers_max):
            if self.resources[2] != -1:
                self.workers += self.amount_inc
                self.resources[2] += self.amount_inc

        elif event.ui_element == self.btn_metal_dec and \
                (self.workers > 0 and self.resources[2] > 0):
            if self.resources[2] != -1:
                self.workers -= self.amount_dec
                self.resources[2] -= self.amount_dec

        elif event.ui_element == self.btn_gems_inc and \
                (self.workers < self.workers_max):
            if self.resources[3] != -1:
                self.workers += self.amount_inc
                self.resources[3] += self.amount_inc

        elif event.ui_element == self.btn_gems_dec and \
                (self.workers > 0 and self.resources[3] > 0):
            if self.resources[3] != -1:
                self.workers -= self.amount_dec
                self.resources[3] -= self.amount_dec


class ArmyManagement(SubMenu):
    def __init__(self, menu_type):
        super().__init__(menu_type)

        self.btn_recruit = pygame_gui.elements.UIButton(
            pygame.Rect((200, 20, 175, 35)),
            f"Recruit ({environment.getAllowedRecruit()})", manager,
            object_id="#button",
            container=self, parent_element=self)

        self.amount = environment.player.army_amount + environment.getGarrisoned()
        self.amount_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(10, 170, 570, 50),
            0,
            (self.amount, 0),
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#main_scroll_bar"
        )

        self.lbl_left_title = pygame_gui.elements.UILabel(
            pygame.Rect(10, 70, 240, 50),
            "Army carrying",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_left = pygame_gui.elements.UILabel(
            pygame.Rect(10, 120, 240, 50),
            str(environment.player.army_amount + self.amount_slider.get_current_value()),
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_right_title = pygame_gui.elements.UILabel(
            pygame.Rect(620 - 260, 70, 240, 50),
            "Army garrisoned",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_right = pygame_gui.elements.UILabel(
            pygame.Rect(620 - 260, 120, 240, 50),
            str(environment.getGarrisoned() - self.amount_slider.get_current_value()),
            manager=manager,
            container=self,
            parent_element=self
        )

    def handleEvent(self, event):
        if self.amount_slider.has_moved_recently:
            self.lbl_left.set_text(str(self.amount_slider.get_current_value()))
            self.lbl_right.set_text(str(self.amount - self.amount_slider.get_current_value()))

        self.process_event(event)

    def updateMenu(self):
        pass

    def updateInfo(self):
        pass

    def recruit(self):
        environment.addGarrison(environment.getAllowedRecruit())
        environment.countSoldiers()
        local_region.menu.updateGarrison()
        self.amount = environment.player.army_amount + environment.getGarrisoned()
        self.amount_slider.value_range = (self.amount, 0)
        self.lbl_left.set_text(str(self.amount_slider.get_current_value()))
        self.lbl_right.set_text(str(self.amount - self.amount_slider.get_current_value()))

    def confirm(self):
        environment.player.setArmyAmount(int(self.lbl_left.text))
        environment.setGarrisoned(int(self.lbl_right.text))
        region_map.updateTbx_Army()
        environment.countSoldiers()
        local_region.menu.updateGarrison()


class MarketManagement(SubMenu):
    def __init__(self, menu_type):
        super().__init__(menu_type)

        self.amount = int(environment.player.gems)
        self.gem_worth = 100
        self.amount_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(10, 170, 570, 50),
            0,
            (self.amount, 0),
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#window"
        )

        self.lbl_left_title = pygame_gui.elements.UILabel(
            pygame.Rect(10, 70, 240, 50),
            "Gems carrying",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_left = pygame_gui.elements.UILabel(
            pygame.Rect(10, 120, 240, 50),
            str(self.amount_slider.get_current_value()),
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_right_title = pygame_gui.elements.UILabel(
            pygame.Rect(620 - 260, 70, 240, 50),
            "Gold Received",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_right = pygame_gui.elements.UILabel(
            pygame.Rect(620 - 260, 120, 240, 50),
            str((self.amount - self.amount_slider.get_current_value()) * self.gem_worth),
            manager=manager,
            container=self,
            parent_element=self
        )

    def handleEvent(self, event):
        if self.amount_slider.has_moved_recently:
            self.lbl_left.set_text(str(self.amount_slider.get_current_value()))
            self.lbl_right.set_text(str((self.amount - self.amount_slider.get_current_value()) * self.gem_worth))

        self.process_event(event)

    def updateMenu(self):
        pass

    def updateInfo(self):
        pass

    def confirm(self):
        environment.player.gems = int(self.lbl_left.text)
        environment.player.gold += int(self.lbl_right.text)


class BlacksmithMenu(SubMenu):
    def __init__(self, menu_type):
        super().__init__(menu_type)

        self.armour_tier = environment.player.army_armour
        self.weapon_tier = environment.player.army_weapon

        if self.armour_tier == 5:
            self.txt_armour = f"Armour Tier: {self.armour_tier} (Max)"
        else:
            self.txt_armour = f"Armour Tier: {self.armour_tier} -> {self.armour_tier + 1}"

        if self.weapon_tier == 5:
            self.txt_weapon = f"Weapon Tier: {self.armour_tier} (Max)"
        else:
            self.txt_weapon = f"Weapon Tier: {self.weapon_tier} -> {self.weapon_tier + 1}"

        self.lbl_armour_tier = pygame_gui.elements.UILabel(
            pygame.Rect((20, 20, 200, 35)),
            self.txt_armour,
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_weapon_tier = pygame_gui.elements.UILabel(
            pygame.Rect((20, 100, 200, 35)),
            self.txt_weapon,
            manager=manager,
            container=self,
            parent_element=self
        )

        self.btn_armour_up = pygame_gui.elements.UIButton(
            pygame.Rect((280, 20, 64, 64)),
            "",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#btn_armour"
        )

        self.btn_weapon_up = pygame_gui.elements.UIButton(
            pygame.Rect((280, 100, 64, 64)),
            "",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#btn_weapon"
        )

        self.armour_cost = 8 ** (environment.player.army_armour + 1) * 1000
        self.weapon_cost = 8 ** (environment.player.army_weapon + 1) * 1000

        self.lbl_armour_cost = pygame_gui.elements.UILabel(
            pygame.Rect((400, 20, 200, 35)),
            f"Cost: {self.armour_cost}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_weapon_cost = pygame_gui.elements.UILabel(
            pygame.Rect((400, 100, 200, 35)),
            f"Cost: {self.weapon_cost}",
            manager=manager,
            container=self,
            parent_element=self
        )

        if self.armour_tier == 5:
            self.btn_armour_up.disable()
            self.lbl_armour_cost.hide()

        if self.weapon_tier == 5:
            self.btn_weapon_up.disable()
            self.lbl_weapon_cost.hide()

        self.lbl_plr_gold = pygame_gui.elements.UILabel(
            pygame.Rect((20, 200, 200, 35)),
            f"Gold: {environment.player.gold}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.btn_cancel.hide()

    def handleEvent(self, event):
        if event.ui_element == self.btn_armour_up:
            if environment.player.gold >= self.armour_cost and self.armour_tier < 5:
                environment.player.army_armour += 1
                environment.player.gold -= self.armour_cost

                self.armour_tier = environment.player.army_armour

                if self.armour_tier == 5:
                    self.txt_armour = f"Armour Tier: {self.armour_tier} (Max)"
                else:
                    self.txt_armour = f"Armour Tier: {self.armour_tier} -> {self.armour_tier + 1}"

                self.lbl_armour_tier.set_text(self.txt_armour)

                self.armour_cost = 8 ** (environment.player.army_armour + 1) * 1000
                self.lbl_armour_cost.set_text(f"Cost: {self.armour_cost}")

                if self.armour_tier == 5:
                    self.btn_armour_up.disable()
                    self.lbl_armour_cost.hide()

                self.lbl_plr_gold.set_text(f"Gold: {environment.player.gold}")
                sfx_upgrade.play()

        elif event.ui_element == self.btn_weapon_up:
            if environment.player.gold >= self.weapon_cost and self.weapon_tier < 5:
                environment.player.army_weapon += 1
                environment.player.gold -= self.weapon_cost

                self.weapon_tier = environment.player.army_weapon

                if self.weapon_tier == 5:
                    self.txt_weapon = f"Weapon Tier: {self.armour_tier} (Max)"
                else:
                    self.txt_weapon = f"Weapon Tier: {self.weapon_tier} -> {self.weapon_tier + 1}"

                self.lbl_weapon_tier.set_text(self.txt_weapon)

                self.weapon_cost = 8 ** (environment.player.army_weapon + 1) * 1000
                self.lbl_weapon_cost.set_text(f"Cost: {self.weapon_cost}")

                if self.weapon_tier == 5:
                    self.btn_weapon_up.disable()
                    self.lbl_weapon_cost.hide()

                self.lbl_plr_gold.set_text(f"Gold: {environment.player.gold}")
                sfx_upgrade.play()
        region_map.updateTbx_Army()
        self.process_event(event)

    def updateMenu(self):
        pass

    def updateInfo(self):
        pass

    def confirm(self):
        pass


class Alert(pygame_gui.elements.UIWindow):
    def __init__(self, alert_type, used_img=""):
        super().__init__(pygame.Rect(150, 150, 400, 360), manager,
                         object_id="#window")

        self.alert_type = alert_type
        self.image_depict = None

        match used_img:
            case "train":
                self.image_size = (400 / 2 - 70, 320 / 2)

                rect = pygame.Rect((400 / 4, 320 / 8 + 10), self.image_size)
                img = pygame.transform.scale(pygame.image.load("./data/gfx/GUI/pics/Training.png"), self.image_size)
                self.image_depict = pygame_gui.elements.UIImage(
                    rect,
                    img,
                    parent_element=self,
                    container=self
                )
            case "rest":
                self.image_size = (400 / 2, 320 / 2)

                rect = pygame.Rect((400 / 4 - 20, 320 / 8 + 10), self.image_size)
                img = pygame.transform.scale(pygame.image.load("./data/gfx/GUI/pics/Camp.png"), self.image_size)
                self.image_depict = pygame_gui.elements.UIImage(
                    rect,
                    img,
                    parent_element=self,
                    container=self
                )

        if self.image_depict:
            self.image_depict.show()

        global world_map

        self.btn_cancel = pygame_gui.elements.UIButton(
            pygame.Rect(15, 260, 160, 35),
            "Cancel",
            manager,
            object_id="#button",
            container=self,
            parent_element=self,
        )
        self.btn_confirm = pygame_gui.elements.UIButton(
            pygame.Rect(185, 260, 160, 35),
            "Confirm",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.text_max_len = 42

        self.labels = [
            pygame_gui.elements.UILabel(
                pygame.Rect(5, 15, 330, 35),
                "",
                manager,
                container=self,
                parent_element=self,
            ),

            pygame_gui.elements.UILabel(
                pygame.Rect(15, 50, 330, 35),
                "",
                manager,
                container=self,
                parent_element=self
            ),

            pygame_gui.elements.UILabel(
                pygame.Rect(15, 85, 330, 35),
                "",
                manager,
                container=self,
                parent_element=self
            ),

            pygame_gui.elements.UILabel(
                pygame.Rect(15, 120, 330, 35),
                "",
                manager,
                container=self,
                parent_element=self
            ),

            pygame_gui.elements.UILabel(
                pygame.Rect(15, 155, 330, 35),
                "",
                manager,
                container=self,
                parent_element=self
            )
        ]

        self.text_input = pygame_gui.elements.UITextEntryLine(
            pygame.Rect(140, 120, 160, 35), manager, container=self, parent_element=self,
            visible=False, )

        self.txb_cost = pygame_gui.elements.UITextBox(
            "",
            pygame.Rect(15, 170, 335, 55), manager, container=self, parent_element=self,
            visible=False, object_id="#textbox")

    def handleEvent(self, event):
        if event.ui_element == self.btn_confirm:
            if self.alert_type != "Entry":
                pygame.mixer.stop()
                sfx_construct.play()
            if self.alert_type == "Tents":
                if environment.subCost(2000, 25, 5, 2):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Tents"]["Bonuses"]
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    environment.addAllowedRecruit(bonuses["RecruitAllowed"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Cottages":
                if environment.subCost(10000, 150, 30, 14):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Cottages"]["Bonuses"]
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    environment.addAllowedRecruit(bonuses["RecruitAllowed"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Houses":
                if environment.subCost(100000, 2500, 400, 300):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Houses"]["Bonuses"]
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    environment.addAllowedRecruit(bonuses["RecruitAllowed"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Palisade":
                if environment.subCost(22500, 2500, 40):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Palisade"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "TownHall":
                if environment.subCost(650500, 2500, 4000):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Unique"]["TownHall"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    recruit_cost = environment.getRecruitCost() - bonuses["RecruitCost"]
                    environment.setRecruitCost(recruit_cost)
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Fortified Walls":
                if environment.subCost(22500, 2500, 275, 200):
                    bonuses = environment.BuildTech["SubBuildings"]["FirstTier"]["Unique"]["TownHall"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Fort":
                if environment.subCost(675500, 5000, 4000, 3000):
                    environment.addBuilding(self.alert_type)
                    try:
                        environment.upgradeStructure("Fort")
                    except Exception as e:
                        print(f"{type(e)} {e} couldn't build the fort")
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Castle":
                if environment.subCost(997550, 5000, 4000, 2000, 1000):
                    environment.addSecurity(20)
                    environment.addBuilding(self.alert_type)
                    try:
                        environment.upgradeStructure("Castle")
                    except Exception as e:
                        print(type(e), ':', e)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Stone Walls":
                if environment.subCost(52500, 2500, 2275, 80):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Stone Walls"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Archer Towers":
                if environment.subCost(82500, 3500, 1275):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Archer Towers"]["Bonuses"]
                    environment.addControl(bonuses["Control"])
                    environment.addQuality(bonuses["Quality"])
                    environment.addGarrison(bonuses["Garrison"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Crossbow Pillboxes":
                if environment.subCost(82500, 1255, 2275, 80):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Crossbow Pillboxes"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    environment.addControl(bonuses["Control"])
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Ballistas":
                if environment.subCost(88500, 1255, 2275, 800):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Ballistas"]["Bonuses"]
                    environment.addControl(bonuses["Control"])
                    environment.addQuality(bonuses["Quality"])
                    environment.addGarrison(bonuses["Garrison"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Catapults":
                if environment.subCost(85500, 7255, 2275, 80):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Catapults"]["Bonuses"]
                    environment.addControl(bonuses["Control"])
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Workshop":
                if environment.subCost(115255, 2255, 2275, 10000):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Workshop"]["Bonuses"]
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Artisans Guild":
                if environment.subCost(115575, 2255, 2275, 0, 10000):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Fort"]["Artisans Guild"]["Bonuses"]
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Citadel":
                if environment.subCost(5957500, 8000, 40000, 2000, 2000):
                    environment.addSecurity(60)
                    environment.addBuilding(self.alert_type)
                    try:
                        environment.upgradeStructure("Citadel")
                    except Exception as e:
                        print(type(e), ':', e)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Chambers":
                if environment.subCost(100000, 400, 115255, 2275):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Chambers"]["Bonuses"]
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    recruit_cost = environment.getRecruitCost() - bonuses["RecruitCost"]
                    environment.setRecruitCost(recruit_cost)
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Bazaar":
                if environment.subCost(100000, 1152500, 0, 2275, 2550):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Bazaar"]["Bonuses"]
                    if environment.player.income < bonuses["Income"]:
                        environment.player.income = bonuses["Income"]
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Merchants Guild":
                if environment.subCost(100000, 400, 115255, 2575, 52550):
                    bonuses = environment.BuildTech["SubBuildings"]["SecondTier"]["Castle"]["Merchants Guild"]["Bonuses"]
                    if environment.player.income < bonuses["Income"]:
                        environment.player.income = bonuses["Income"]
                    recruit_cost = environment.getRecruitCost() - bonuses["RecruitCost"]
                    environment.setRecruitCost(recruit_cost)
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "City":
                if environment.subCost(20577500, 80000, 40000, 0, 1000):
                    environment.addSecurity(60)
                    environment.addBuilding(self.alert_type)
                    try:
                        environment.upgradeStructure("City")
                    except Exception as e:
                        print(type(e), ':', e)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Trade Root":
                if environment.subCost(100000, 40000, 1075255, 23575, 352550):
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["City"]["Trade Root"]["Bonuses"]
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Royal Palace":
                if environment.subCost(10000000, 400000, 10700255, 300575, 302550):
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["City"]["Royal Palace"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "Manors":
                if environment.subCost(10000000, 140000, 500000, 120000):
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["Citadel"]["Manors"]["Bonuses"]
                    environment.addSecurity(bonuses["Security"])
                    workers = environment.getMaxWorkersInStructure() + bonuses["MaxVillagers"]
                    environment.setMaxWorkersInStructure(workers)
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)
            elif self.alert_type == "WarHall":
                if environment.subCost(10000000, 400000, 11150255, 450575):
                    bonuses = environment.BuildTech["SubBuildings"]["ThirdTier"]["Citadel"]["WarHall"]["Bonuses"]
                    environment.addControl(bonuses["Control"])
                    environment.addQuality(bonuses["Quality"])
                    environment.addBuilding(self.alert_type)
                else:
                    alert = Alert("no resources")
                    alert.setText("Not enough resources!")
                    alert.btn_cancel.hide()
                    local_region.menu.alerts.append(alert)

    def setText(self, text: str):
        if text.count('\n') == 0 and len(text) > 0:
            self.labels[0].set_text(text)
        elif 0 < text.count('\n') < 5:
            lines = text.split('\n')
            idx = 0
            for line in lines:

                if 0 < len(line) <= self.text_max_len and line.count(' ') >= 0:
                    self.labels[idx].set_text(line)
                    idx += 1
                else:
                    raise Exception(f"Line {idx+1} is longer than allowed!")

    def setTextBox(self, text: str):
        self.txb_cost.set_text(text)
        self.txb_cost.show()

    def confirm(self):
        match self.alert_type:
            case "Stable":
                if environment.player.gold < 10000:
                    alert = Alert("Insufficient gold")
                    alert.setText("Insufficient gold!")
                    alert.btn_cancel.hide()
                    region_map.alerts.append(alert)
                else:
                    try:
                        environment.building_name = self.text_input.text
                        if environment.addStructure("Stable", "Fortification") and environment.subGold(10000):
                            region = environment.region_name
                            if environment.countInRegion(region) == world_map.area_regions:
                                if region in world_map.areas_cleansed:
                                    world_map.areas_cleansed[region] = True
                            print(f"{environment.building_name} has been built!")
                            region_map.setLocation(environment.location_world)
                    except Exception as e:
                        if str(e) == "Can't build in chaotic places":
                            alert = Alert("Can't build in chaotic places")
                            alert.setText("Can't build in chaotic places!")
                            alert.btn_cancel.hide()
                            region_map.alerts.append(alert)
                        print(type(e), ':', e)
            case "Wood":
                try:
                    if environment.subGold(1000):
                        environment.addStructure("Wood", "Encampment")
                        print("Gathering wood!")

                        x, y = environment.location_world[0], environment.location_world[1]
                        for line in play_map.world[y][x]:
                            print(line)

                        region_map.setLocation(environment.location_world)
                    else:
                        alert = Alert("Not enough gold")
                        alert.setText("Not enough gold!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
                except Exception as e:
                    if str(e) == "Can't build in chaotic places":
                        alert = Alert("Can't build in chaotic places")
                        alert.setText("Can't build in chaotic places!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
            case "Stone":
                try:
                    if environment.subGold(1000):
                        environment.addStructure("Stone", "Encampment")
                        print("Gathering stone!")

                        x, y = environment.location_world[0], environment.location_world[1]
                        for line in play_map.world[y][x]:
                            print(line)

                        region_map.setLocation(environment.location_world)
                    else:
                        alert = Alert("Not enough gold")
                        alert.setText("Not enough gold!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
                except Exception as e:
                    if str(e) == "Can't build in chaotic places":
                        alert = Alert("Can't build in chaotic places")
                        alert.setText("Can't build in chaotic places!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
            case "Metal":
                try:
                    if environment.subGold(1000):
                        environment.addStructure("Metal", "Encampment")
                        print("Gathering metal!")

                        x, y = environment.location_world[0], environment.location_world[1]
                        for line in play_map.world[y][x]:
                            print(line)

                        region_map.setLocation(environment.location_world)
                    else:
                        alert = Alert("Not enough gold")
                        alert.setText("Not enough gold!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
                except Exception as e:
                    if str(e) == "Can't build in chaotic places":
                        alert = Alert("Can't build in chaotic places")
                        alert.setText("Can't build in chaotic places!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
            case "Gems":
                try:
                    if environment.subGold(1000):
                        environment.addStructure("Gems", "Encampment")
                        print("Gathering gems!")

                        x, y = environment.location_world[0], environment.location_world[1]
                        for line in play_map.regions[y][x]:
                            print(line)

                        region_map.setLocation(environment.location_world)
                    else:
                        alert = Alert("Not enough gold")
                        alert.setText("Not enough gold!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)
                except Exception as e:
                    if str(e) == "Can't build in chaotic places":
                        alert = Alert("Can't build in chaotic places")
                        alert.setText("Can't build in chaotic places!")
                        alert.btn_cancel.hide()
                        region_map.alerts.append(alert)

class GameSettings(pygame_gui.elements.UIWindow):
    def __init__(self):
        super().__init__(pygame.Rect(WIDTH / 8, HEIGHT / 4, 640, 320), manager,
                         object_id="#window")

        self.checkbox = pygame_gui.elements.UIButton(
            pygame.Rect(250, 20, 32, 32),
            text="",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#checkbox"
        )

        if pygame.display.is_fullscreen():
            self.checkbox.select()

        self.lbl_fullscreen = pygame_gui.elements.UILabel(
            pygame.Rect(50, 20, 175, 35),
            text="Toggle fullscreen",
            manager=manager,
            container=self,
            parent_element=self
        )

        resolutions = {"(800, 600)", "(1536, 864)"}

        resolutions.add(str(pygame.display.get_desktop_sizes()[0]))
        self.resolution_ddMenu = pygame_gui.elements.UIDropDownMenu(
            list(resolutions),
            str((WIDTH, HEIGHT)),
            pygame.Rect(300, 20, 175, 35),
            manager=manager,
            container=self,
            parent_element=self
        )

        self.btn_resolution_change = pygame_gui.elements.UIButton(
            pygame.Rect(480, 20, 120, 35),
            text="Change",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#button"
        )

        self.current_sound = music_volume
        self.lbl_game_sound = pygame_gui.elements.UILabel(
            pygame.Rect(50, 70, 175, 35),
            text=f"Music volume: {self.current_sound}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.amount_slider = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(200, 62, 400, 50),
            self.current_sound,
            (0, 100),
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#window"
        )

        self.current_sound2 = sfx_volume
        self.lbl_game_sound2 = pygame_gui.elements.UILabel(
            pygame.Rect(50, 100, 175, 35),
            text=f"SFX volume: {self.current_sound2}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.amount_slider2 = pygame_gui.elements.UIHorizontalSlider(
            pygame.Rect(200, 92, 400, 50),
            self.current_sound2,
            (0, 100),
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#window"
        )

        self.btn_save_game = pygame_gui.elements.UIButton(
            pygame.Rect(80, 140, 120, 35),
            text="Save Game",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#button"
        )

        self.lbl_game_saved = pygame_gui.elements.UILabel(
            pygame.Rect(250, 140, 175, 35),
            text="Game Saved!",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#label",
            visible=False
        )

        self.btn_close = pygame_gui.elements.UIButton(
            pygame.Rect(350, 200, 120, 35),
            text="Close",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#button"
        )

        self.btn_exit = pygame_gui.elements.UIButton(
            pygame.Rect(80, 200, 120, 35),
            text="Exit Game",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#button"
        )

    def handleEvent(self, event):
        if event.ui_element == self.checkbox:
            pygame.display.toggle_fullscreen()
            if pygame.display.is_fullscreen():
                self.checkbox.select()
            else:
                self.checkbox.unselect()
        elif event.ui_element == self.btn_resolution_change:
            global WIDTH, HEIGHT, manager
            new_resolution = tuple(literal_eval(self.resolution_ddMenu.selected_option))
            play_map.WIDTH, play_map.HEIGHT = new_resolution
            WIDTH, HEIGHT = play_map.WIDTH, play_map.HEIGHT
            environment.WIDTH, environment.HEIGHT = WIDTH, HEIGHT
            characters.SCREEN_WIDTH, characters.SCREEN_HEIGHT = WIDTH, HEIGHT

            characters.updateCenterLabel()

            pygame.display.set_mode(new_resolution)
            manager.set_window_resolution(new_resolution)
            saveGame()
            updateRes()
            loadGame()
            return False
        elif self.amount_slider.has_moved_recently:
            global music_volume
            self.current_sound = self.amount_slider.get_current_value()
            music_volume = self.current_sound
            pygame.mixer_music.set_volume(self.current_sound / 100)

            self.lbl_game_sound.set_text(f"Music volume: {self.current_sound}")
        elif self.amount_slider2.has_moved_recently:
            global sfx_volume
            self.current_sound2 = self.amount_slider2.get_current_value()
            sfx_volume = self.current_sound2
            sfx_click.set_volume(self.current_sound2 / 100)
            sfx_equip.set_volume(self.current_sound2 / 100)
            sfx_sell.set_volume(self.current_sound2 / 100)
            sfx_inventory.set_volume(self.current_sound2 / 100)
            sfx_upgrade.set_volume(self.current_sound2 / 100)
            sfx_settings.set_volume(self.current_sound2 / 100)
            sfx_hit.set_volume(self.current_sound2 / 100)
            sfx_miss.set_volume(self.current_sound2 / 100)
            sfx_map.set_volume(self.current_sound2 / 100)
            sfx_move.set_volume(self.current_sound2 / 100)
            sfx_save.set_volume(self.current_sound2 / 100)
            sfx_load.set_volume(self.current_sound2 / 100)
            sfx_skill.set_volume(self.current_sound2 / 100)
            sfx_attack.set_volume(self.current_sound2 / 100)
            sfx_gameover.set_volume(self.current_sound2 / 100)
            sfx_defeat.set_volume(self.current_sound2 / 100)
            sfx_victory.set_volume(self.current_sound2 / 100)
            sfx_levelup.set_volume(self.current_sound2 / 100)
            sfx_built.set_volume(self.current_sound2 / 100)
            sfx_construct.set_volume(self.current_sound2 / 100)
            sfx_cleansed.set_volume(self.current_sound2 / 100)
            sfx_failcleanse.set_volume(self.current_sound2 / 100)

            self.lbl_game_sound2.set_text(f"SFX volume: {self.current_sound2}")
        elif event.ui_element == self.btn_save_game:
            pygame.mixer.stop()
            sfx_save.play()
            saveGame()
            self.lbl_game_saved.show()

        self.process_event(event)
        return True

class LevelAlert(pygame_gui.elements.UIWindow):
    def __init__(self):
        super().__init__(pygame.Rect(150, 150, 260, 340), manager,
                         object_id="#window")
        self.width, self.height = 260, 340

        self.lbl_top = pygame_gui.elements.UILabel(pygame.Rect(60, 10, 100, 35),
                                                   "Leveled up!",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        start_y, space_y = 60, 25
        self.points = 2

        self.lbl_points = pygame_gui.elements.UILabel(pygame.Rect(10, 35, 100, 35),
                                                   f"Points: {self.points}",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_con = pygame_gui.elements.UILabel(pygame.Rect(125, start_y, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_wis = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_fai = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y * 2, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_bonus = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y * 3, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_str = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y * 4, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_int = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y * 5, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        self.lbl_cun = pygame_gui.elements.UILabel(pygame.Rect(125, start_y + space_y * 6, 100, 35),
                                                   "0",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        start_y = 40
        self.btn_con = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y, 120, 25),
            "Constitution",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_wis = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 2, 120, 25),
            "Wisdom",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_fai = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 3, 120, 25),
            "Faith",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_bonus = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 4, 120, 25),
            main_character.bonus_fullname,
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_str = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 5, 120, 25),
            "Strength",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_int = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 6, 120, 25),
            "Intelligence",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_cun = pygame_gui.elements.UIButton(
            pygame.Rect(20, start_y + space_y * 7, 120, 25),
            "Cunning",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_confirm = pygame_gui.elements.UIButton(
            pygame.Rect(120, 250, 100, 35),
            "Confirm",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

        self.btn_reset = pygame_gui.elements.UIButton(
            pygame.Rect(5, 250, 100, 35),
            "Reset",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )

    def pickStat(self, name):
        if self.points > 0:
            match name:
                case "Constitution":
                    n = int(self.lbl_con.text)
                    n += 1
                    self.points -= 1
                    self.lbl_con.set_text(str(n))
                case "Wisdom":
                    n = int(self.lbl_wis.text)
                    n += 1
                    self.points -= 1
                    self.lbl_wis.set_text(str(n))
                case "Faith":
                    n = int(self.lbl_fai.text)
                    n += 1
                    self.points -= 1
                    self.lbl_fai.set_text(str(n))
                case main_character.bonus_fullname:
                    n = int(self.lbl_bonus.text)
                    n += 1
                    self.points -= 1
                    self.lbl_bonus.set_text(str(n))
                case "Strength":
                    n = int(self.lbl_str.text)
                    n += 1
                    self.points -= 1
                    self.lbl_str.set_text(str(n))
                case "Intelligence":
                    n = int(self.lbl_int.text)
                    n += 1
                    self.points -= 1
                    self.lbl_int.set_text(str(n))
                case "Cunning":
                    n = int(self.lbl_cun.text)
                    n += 1
                    self.points -= 1
                    self.lbl_cun.set_text(str(n))
            self.lbl_points.set_text(f"Points: {self.points}")


class RewardWindow(pygame_gui.elements.UIWindow):
    def __init__(self, reward_exp, reward_gold, reward_items: list=[], resources=[]):
        super().__init__(pygame.Rect(150, 150, 400, 320), manager,
                         object_id="#window")

        self.lbl_top = pygame_gui.elements.UILabel(pygame.Rect(120, 10, 130, 35),
                                                   "Your finds:",
                                                   container=self,
                                                   parent_element=self,
                                                   manager=manager)

        txt_reward = ""
        if reward_exp > 0:
            txt_reward += f"<img src='data/gfx/GUI/pics/icons/Exp.png'>(Exp): {reward_exp}\n"

        if reward_gold > 0:
            txt_reward += f"<img src='data/gfx/GUI/pics/icons/Gold.png'>(Gold): {reward_gold}\n"

        if len(reward_items) > 0:
            for itm in reward_items:
                txt_reward += f"<img src='{itm['image_path']}'>\t"

        if len(resources) > 0:
            txt_reward += environment.giveResource(resources)

        self.txb_gain = pygame_gui.elements.UITextBox(txt_reward,
                                                   pygame.Rect(55, 50, 260, 160),
                                                   container=self,
                                                   parent_element=self,
                                                   object_id="#tbx_window",
                                                   manager=manager)

        self.btn_confirm = pygame_gui.elements.UIButton(
            pygame.Rect(115, 220, 150, 35),
            "Confirm",
            manager,
            object_id="#button",
            container=self,
            parent_element=self
        )


def addItemsToInv(num: int):
    reward_itms = []
    for i in range(num):
        itm_name, itm_params = chs(list(characters.Equipment.items()))
        main_character.inventory.addItem(itm_name, itm_params['description'],
                                         itm_params['value'], itm_params['image_path'], itm_params['equipped_on'],
                                         itm_params['stats'])

        reward_itms.append(itm_params)
    return reward_itms


class StartChoice(pygame_gui.elements.UIWindow):
    def __init__(self):
        super().__init__(pygame.Rect(150, 150, 580, 420), manager,
                         object_id="#window")

        rect_top = pygame.Rect(175, 15, 185, 35)
        self.lbl_top = pygame_gui.elements.UILabel(rect_top, "Choose your class",
                                                   parent_element=self, container=self,
                                                   object_id="#label_start")

        self.btn_Warlord = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (40, 120),
                        (150, 150)),
                        text="",
                        tool_tip_text="Warlord",
                        manager=manager,
                        object_id="#job_warlord",
                        parent_element=self,
                        container=self
        )

        self.btn_Sourcerer = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(
                        (40 + 160 * 2, 120),
                        (150, 150)),
                        text="",
                        tool_tip_text="Sourcerer",
                        manager=manager,
                        object_id="#job_sourcerer",
                        parent_element=self,
                        container=self
        )

        self.btn_Hunter = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
            (40 + 160, 120),
            (150, 150)),
            text="",
            tool_tip_text="Hunter",
            manager=manager,
            object_id="#job_hunter",
            parent_element=self,
            container=self
        )

        self.btn_done = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (580 / 3, 275),
                (165, 85)),
            text="",
            manager=manager,
            object_id="#done",
            parent_element=self,
            container=self,
        )

        self.drop_menu = pygame_gui.elements.UIDropDownMenu(
            ["small-world", "medium-world", "large-world"],
            starting_option="small-world",
            relative_rect=pygame.Rect(
                (580 / 3 + 6, 50),
                (150, 50)
            ),
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#start_world_size"
        )

        self.btn_done.hide()


reward_window = None
start_window = None


class StartMenu:
    def __init__(self):
        self.TIME_FRAME = 7
        self.frame_i, self.frame_j = 0, 0
        self.frame_width = 800
        self.sprite_sheet = pygame.image.load(Title_Screen_BG_Path)
        self.bg_animation = pygame.transform.scale(get_frame(self.sprite_sheet, 800, 450,
                                                             [self.frame_i, self.frame_j], is_color_key=False),
                                                   (WIDTH, HEIGHT)).convert_alpha()

        self.menu_img = pygame.transform.scale(pygame.image.load(Title_Screen_Menu_Path), (WIDTH * 2 / 5, HEIGHT * 2 / 3)).convert_alpha()
        self.menu_size = self.menu_img.get_size()
        self.menu_pos = (WIDTH * 3 / 5, HEIGHT - self.menu_size[1])

        self.btn_play_size = (self.menu_size[0] * 4 / 32 * 3.5, self.menu_size[1] * 3 / 32)

        self.btn_play_pos = (self.menu_pos[0] + self.menu_size[0] * 9 / 32, self.menu_pos[1] + self.btn_play_size[1] * 6.4)
        self.btn_load_pos = (self.menu_pos[0] + self.menu_size[0] * 9 / 32, self.menu_pos[1] + self.btn_play_size[1] * 7.7)
        self.btn_exit_pos = (self.menu_pos[0] + self.menu_size[0] * 9 / 32, self.menu_pos[1] + self.btn_play_size[1] * 8.9)

        self.btn_play = ImgButton(self.btn_play_pos[0], self.btn_play_pos[1], self.btn_play_size[0],
                                  self.btn_play_size[1], (0, 0, 0), "./data/gfx/GUI/Buttons/btn_play.png")

        self.btn_load = ImgButton(self.btn_load_pos[0], self.btn_load_pos[1], self.btn_play_size[0],
                                  self.btn_play_size[1], (0, 0, 0), "./data/gfx/GUI/Buttons/btn_load.png")

        self.btn_exit = ImgButton(self.btn_exit_pos[0], self.btn_exit_pos[1], self.btn_play_size[0],
                                  self.btn_play_size[1], (0, 0, 0), "./data/gfx/GUI/Buttons/btn_exit.png")

        self.start_window = StartChoice()
        self.start_window.hide()

        screen.fill((0, 0, 0))

    def getAnimationFrames(self):
        return self.sprite_sheet.get_width() // self.frame_width - 111

    def tickClock(self):
        if time_in_game[3] % self.TIME_FRAME == 0:
            return True
        return False

    def animate(self):
        global state
        screen.blit(self.bg_animation, (0, 0))
        screen.blit(self.menu_img, self.menu_pos)
        #screen.blit(self.img_play, self.btn_play_pos)

        self.btn_play.checkFocused()
        self.btn_load.checkFocused()
        self.btn_exit.checkFocused()
        if not clicked or not self.btn_play.active:
            self.btn_play.draw()
        if not clicked or not self.btn_load.active:
            self.btn_load.draw()
        if not clicked or not self.btn_exit.active:
            self.btn_exit.draw()

        if self.btn_play.was_clicked:
            if not self.start_window.visible:
                self.start_window.show()
        elif clicked and self.btn_load.was_clicked:
            save_found = loadGame()
            if not pygame.mixer.get_busy():
                sfx_load.play()

            if save_found:
                self.start_window.kill()
                state = "Region"
        elif self.btn_exit.was_clicked:
            pygame.quit()
            sys.exit(0)

        if self.tickClock():
            self.frame_j += 1

            if self.frame_i > 2 and self.frame_j > 12:
                self.frame_i = 0
                self.frame_j = 0

            if self.frame_j >= 13:
                self.frame_i += 1
                self.frame_j = 0

        self.bg_animation = pygame.transform.scale(get_frame(self.sprite_sheet, 800, 450,
                                                             [self.frame_i, self.frame_j]),
                                                   (WIDTH, HEIGHT)).convert_alpha()


start_menu_screen = StartMenu()


def stateStartMenu():
    start_menu_screen.animate()


def stateWorld():
    global world_map, clicked, state

    # Render all sectors
    for region in world_map.regions:
        region.draw()

        # Checks mouse hover on button - button becomes active
        region.checkFocused()
        # Swtiches state on left button press
        if region.active and pygame.mouse.get_pressed()[0] and not clicked:
            clicked = True
            loc = environment.location_world = list(region.getClicked())

            region_map.setLocation(loc)
            environment.calcEnvData()
            region_map.updateInfo()

            state = "Region"
            pygame.display.set_caption(f"Region: {play_map.region_info[loc[1]][loc[0]]['Name']} Area: {loc} "
                                       f"Biome: {play_map.region_info[loc[1]][loc[0]]['Biome']}")

    pygame.draw.rect(screen, (40, 90, 250), pygame.Rect((0, 0, screen.get_width(), world_map.cell_size[1] / 3)))


    for region in world_map.regions:
        screen.blit(region.image, (region.x - 1, region.y))

        if list(region.loc) == environment.player.location[0]:
            drawPlayerIco(region.getRect())

    if world_map.is_show_borders:
        for area, border in world_map.area_borders.items():
            pygame.draw.rect(screen, (200, 200, 200), border, 5)

        for item in world_map.area_centers.items():
            drawAreaMarker(item)


def stateRegion():
    global clicked, state

    region_map.drawGUI()
    region_map.drawTiles()
"""
    if pygame.mouse.get_pressed()[2] and not clicked:
        clicked = True
        pygame.display.set_caption("World Map")
        if region_map.text_input.visible:
            region_map.lbl_txt_input.hide()
            region_map.text_input.hide()

            for element in region_map.right_gui:
                element.hide()
            for element in region_map.left_gui:
                element.hide()

            region_map.text_box.hide()

        state = "World"
        """


def exitLocal():
    global state
    x, y = environment.location_world
    rx, ry = environment.location_region

    local_region.hideMenu()

    for sub_menu in local_region.menu.sub_menus:
        sub_menu.kill()

    local_region.menu.killAlerts()
    if local_region.area_type == "Military Camp":
        local_region.war_panel.kill()

    region_map.updateInfo()
    pygame.display.set_caption(
        f"Region: {play_map.world[y][x]} "
        f"Area: {[rx, ry]} "
        f"Biome: {play_map.region_info[y][x]['Biome']}")
    state = "Region"


def stateLocal():
    global clicked, state
    local_region.renderImage()
    local_region.drawTitle()
    
    if pygame.mouse.get_pressed()[2] and not clicked:
        clicked = True
        exitLocal()


class Item:
    def __init__(self, slot_id, name, desc, value, image, equipped_on=None, stats: list=[]):
        self.slot_id = slot_id
        self.name = name
        self.desc = desc
        self.value = value
        self.equipped_on = equipped_on
        self.stats = stats

        size = 50
        self.image_path = image
        image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(image, (size, size))


class Slot:
    def __init__(self, slot_id, rect, container):
        self.slot_id = slot_id
        self.rect = rect

        size = 50
        slot_img = pygame.image.load("./data/gfx/GUI/pics/slot.png").convert_alpha()
        slot_img = pygame.transform.scale(slot_img, (size, size))
        slot_selected = pygame.image.load("./data/gfx/GUI/pics/slot_selected.png").convert_alpha()
        slot_selected = pygame.transform.scale(slot_selected, (size, size))

        self.image = pygame_gui.elements.UIImage(rect, slot_img, container=container)
        self.selected = pygame_gui.elements.UIImage(rect, slot_selected, container=container)
        self.container = container

        self.selected.hide()
        self.item = None
        self.item_img = None

    def setItem(self, item):
        if item:
            self.item = item
            self.item_img = pygame_gui.elements.UIImage(self.rect, item.image, container=self.container)

    def delItem(self):
        if self.item:
            self.item_img.kill()
            del self.item_img
            self.item_img = None
            del self.item.image
            del self.item
            self.item = None

    def sell(self):
        environment.addGold(self.item.value)
        self.delItem()

    def getStatsStr(self):
        if self.item:
            stats = self.item.stats
            txt = "stats:"
            for i in range(len(stats)):
                match i:
                    case 0:
                        if stats[i] > 0:
                            txt += "\ncon: " + str(stats[i])
                    case 1:
                        if stats[i] > 0:
                            txt += "\nwis: " + str(stats[i])
                    case 2:
                        if stats[i] > 0:
                            txt += "\nfai: " + str(stats[i])
                    case 3:
                        if stats[i] > 0:
                            txt += "\nstr: " + str(stats[i])
                    case 4:
                        if stats[i] > 0:
                            txt += "\nint: " + str(stats[i])
                    case 5:
                        if stats[i] > 0:
                            txt += "\ncun: " + str(stats[i])
            return txt


class Inventory(pygame_gui.elements.UIPanel):
    def __init__(self):
        super().__init__(pygame.Rect(WIDTH - 255, 5, 250, 540))

        self.box = pygame_gui.elements.UIPanel(pygame.Rect((5, 5, 235, 240)),
                                  parent_element=self,
                                  container=self)

        self.scroller = pygame_gui.elements.UIScrollingContainer(pygame.Rect(0, 0, 230, 235),
                                               manager=manager,
                                               container=self.box,
                                               object_id="#top_button")

        self.scroller.set_scrollable_area_dimensions((210, 680))

        self.btn_equip = pygame_gui.elements.UIButton(pygame.Rect(15, 255, 80, 25),
                                                      "Equip", manager=manager, container=self,
                                                      object_id="#main_button")

        self.btn_sell = pygame_gui.elements.UIButton(pygame.Rect(250 - 80 - 15, 255, 80, 25),
                                                     "Sell", manager=manager, container=self,
                                                     object_id="#main_button")

        self.title = pygame_gui.elements.UITextBox("", pygame.Rect(5, 290, 235, 35), container=self,
                                                         object_id="#tbx_window")

        self.description = pygame_gui.elements.UITextBox("", pygame.Rect(5, 330, 235, 180),
                                                         container=self,
                                                         object_id="#tbx_window")

        self.slots = []
        self.sort()

    def sort(self):
        count = 0
        offset_x, offset_y = 15, 15
        bspace = 15
        size = 50

        rect = pygame.Rect(0, 0, size, size)

        for i in range(10):
            rect.y = offset_y + (size + bspace) * i
            for j in range(3):
                rect.x = offset_x + (bspace + size) * j

                slot = Slot(count + 1, rect.copy(), self.scroller)
                item = main_character.inventory.getItem(count + 1)
                if item:
                    item = Item(item['slot_id'], item['name'], item['description'],
                                item['value'], item['image_path'], item['equipped_on'], item['stats'])
                    slot.setItem(item)
                self.slots.append(slot)
                count += 1

    def findOpenSlot(self):
        for slot in self.slots:
            if slot.item is None:
                return slot.slot_id

    def hide(self):
        for slot in self.slots:
            slot.delItem()
        self.box.kill()
        self.btn_sell.kill()
        self.btn_equip.kill()
        self.description.kill()
        self.kill()

    def swapSlots(self, slotA, slotB):
        itemA, itemB = slotA.item, None
        id_A, id_B = slotA.item
        if slotA.item:

            if slotB.item:
                itemB = slotB.item

            slotA.delItem()
            slotB.delItem()

            slotA.setItem(itemB)
            slotB.setItem(itemA)

            self.sort()


class WarPanel(pygame_gui.elements.UIPanel):
    def __init__(self):
        super().__init__(pygame.Rect(WIDTH / 4, HEIGHT / 4, WIDTH / 2, HEIGHT / 2))
        self.size =(WIDTH / 2, HEIGHT / 2)
        self.lbl_title = pygame_gui.elements.UILabel(
            pygame.Rect(self.size[0] / 4, 20, self.size[0] / 2, 50),
            "War Panel - Preparation",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.order_army = environment.military_camp['Amount']
        self.order_strength = environment.military_camp['Power']
        self.chaos_strength = environment.chaos_offset ** 2 + environment.chaos_level * 100

        self.lbl_army = pygame_gui.elements.UILabel(
            pygame.Rect(self.size[0] / 8, 70, self.size[0] / 2, 50),
            f"Order strength: {self.order_strength}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.lbl_chaos = pygame_gui.elements.UILabel(
            pygame.Rect(self.size[0] / 8, 120, self.size[0] / 2, 50),
            f"Chaos strength: {self.chaos_strength}",
            manager=manager,
            container=self,
            parent_element=self
        )

        self.btn_claim = pygame_gui.elements.UIButton(
            pygame.Rect(self.size[0] * 3 / 8, 180, self.size[0] / 4, 50),
            "Calim",
            manager=manager,
            container=self,
            parent_element=self,
            visible=False,
            object_id="#button"
        )

        if self.order_strength >= self.chaos_strength:
            self.btn_claim.show()

    def calcCasualties(self):
        luck_odds = list(range(-3, 3, 1))
        luck = 0
        survived_amount = 0

        if self.order_strength >= self.chaos_strength * 3:
            luck_odds = list(range(-2, 4, 1))
            luck = chs(luck_odds)

            if self.order_strength - self.chaos_strength > self.chaos_strength * 10:
                survived_amount = self.order_strength - self.chaos_strength // 2
            elif self.order_strength - self.order_army * luck > 0:
                survived_amount = self.order_army * 2 // 3
            else:
                survived_amount = self.order_army * 2 // 3 - self.chaos_strength
                if survived_amount < 0:
                    survived_amount = 0
        elif self.order_strength >= self.chaos_strength * 2:
            luck = chs(luck_odds)
            luck = 3 if luck + 1 > 3 else luck + 1

            if self.order_strength - self.order_army * luck > 0:
                survived_amount = self.order_army // 2
            else:
                survived_amount = self.order_army // 2 - self.chaos_strength
                if survived_amount < 0:
                    survived_amount = 0

        if survived_amount > 0:
            self.lbl_title.set_text("Victory!")
            self.lbl_army.set_text(f"Survived troops: {survived_amount}")

            x, y = environment.location_world[0], environment.location_world[1]
            play_map.region_info[y][x]["Chaos"] = 1

            self.lbl_chaos.set_text(f"Land is claimed!")
            self.btn_claim.hide()
            environment.player.setArmyAmount(int(survived_amount))
            region_map.updateTbx_Army()
            pygame.mixer.stop()
            sfx_cleansed.play()
        elif luck == 3:
            survived_amount = self.order_army // 8 + 3
            self.lbl_title.set_text("Defeat!")
            self.lbl_army.set_text(f"Survived troops: {survived_amount}")
            self.btn_claim.hide()
            environment.player.setArmyAmount(int(survived_amount))
            region_map.updateTbx_Army()
            pygame.mixer.stop()
            sfx_failcleanse.play()
        else:
            self.lbl_title.set_text("Defeat!")
            self.lbl_army.set_text("No survivors!")
            self.btn_claim.hide()
            pygame.mixer.stop()
            sfx_failcleanse.play()

        environment.disbandMilitaryCamp()



"""
for i in range(2):
    main_character.inventory.addItem('Armour', 'Great armour to wear anywhere',
                                     5500, f'./data/gfx/GUI/pics/equipment/armour/Armour{i + 1}.png', "Torso")

for i in range(1):
    main_character.inventory.addItem('Potion', 'Great potion you can use anywhere',
                                     5500, f'./data/gfx/GUI/pics/items/potions/Potion{i + 1}.png')

    if i < 4:
        main_character.inventory.addItem('Potion', 'Great potion you can use anywhere',
                                         5500, f'./data/gfx/GUI/pics/items/potions/HpPotion{i + 1}.png')

    if i < 3:
        main_character.inventory.addItem('Potion', 'Great potion you can use anywhere',
                                         5500, f'./data/gfx/GUI/pics/items/potions/MpPotion{i + 1}.png')

for i in range(2):
    main_character.inventory.addItem('Sword', 'Great sword to get anywhere',
                                     5500, f'./data/gfx/GUI/pics/equipment/swords/Sword{i + 1}.png', "Hand")

for i in range(16):
    main_character.inventory.addItem('Wand', 'Great sword to get anywhere',
                                     5500, f'./data/gfx/GUI/pics/equipment/wands/Wand{i+1}.png', "Accessory")
"""


def initialize(size: str, job: str=""):
    global play_map, main_character, world_map, \
        region_map, local_region, battle_screen
    if size == "medium-world":
        environment.initialize(6, 6, 4)
    elif size == "large-world":
        environment.initialize(9, 9, 9)

    play_map = environment.game_map

    if job == "Sourcerer":
        environment.player.job = job
    elif job == "Hunter":
        environment.player.job = job

    main_character = characters.Character(environment.player.job, manager, is_player=True)

    world_map = WorldMap(play_map.width, play_map.height, play_map.regions_num, play_map.region_names)
    region_map = RegionMap(True)
    region_map.setLocation(environment.location_world)
    local_region = LocalRegion(getAreaType('-'))
    local_region.hideMenu()

    battle_screen = BattleScreen("Battling Monster")

    #item = characters.Equipment['Armour Of The Ancients']
    #main_character.inventory.addItem('Armour Of The Ancients', item['description'], item['value'], item['image_path'], item['equipped_on'], item['stats'])

def saveGame():
    global main_character

    save_path = "data/saves/save"

    structure = environment.structure
    envi = environment
    save_data = {
        'Environment': {
            'location_world': envi.location_world,
            'location_region': envi.location_region,
            'region_name': envi.region_name,
            'chaos_level': envi.chaos_level,
            'building_type': envi.building_type,
            'building_name': envi.building_name
        },

        'Structure': {
            'count': structure['count'],
            'forts': structure['forts'],
            'camps': structure['camps'],
            'Camp': {},
            'Fort': {}
        }
    }

    for key, val in structure['Camp'].items():
        save_data['Structure']['Camp'][f'{list(key)}'] = val

    for key, val in structure['Fort'].items():
        save_data['Structure']['Fort'][key] = val

    game_map = environment.game_map
    save_data['GameMap'] = {
        'width': game_map.width,
        'height': game_map.height,
        'regions_num': game_map.regions_num,
        'region_names': game_map.region_names,
        'world': game_map.world,
        'regions': game_map.regions,
        'region_info': game_map.region_info,
    }

    player = environment.player
    save_data['Player'] = {
        'name': player.name,
        'job': player.job,
        'location': player.location,
        'destination': player.destination,
        'income': player.income,
        'ap': player.ap,
        'gold': player.gold,
        'wood': player.wood,
        'stone': player.stone,
        'metal': player.metal,
        'gems': player.gems,
        'army_amount': player.army_amount,
        'army_trained': player.army_trained,
        'army_armour': player.army_armour,
        'army_weapon': player.army_weapon,
        'army_power': player.army_power,
    }

    character = main_character
    save_data['Character'] = {
        'kind': character.kind,
        'level': character.level,
        'exp': character.exp,
        'exp_needed': character.exp_needed,
        'con_max': character.con_max,
        'wis_max': character.wis_max,
        'fai_max': character.fai_max,
        'str_max': character.str_max,
        'int_max': character.int_max,
        'end_max': character.end_max,
        'wil_max': character.wil_max,
        'fin_max': character.fin_max,
        'bonus_value_max': character.bonus_value_max
    }

    save_data['Inventory'] = main_character.inventory.items
    save_data['Equipped'] = {}

    if character.hand:
        save_data['Equipped']['Hand'] = {
            'slot_id': character.hand.slot_id,
            'name': character.hand.name,
            'desc': character.hand.desc,
            'value': character.hand.value,
            'equipped_on': character.hand.equipped_on,
            'stats': character.hand.stats,
            'image_path': character.hand.image_path,
        }
    else:
        save_data['Equipped']['Hand'] = None

    if character.torso:
        save_data['Equipped']['Torso'] = {
            'slot_id': character.torso.slot_id,
            'name': character.torso.name,
            'desc': character.torso.desc,
            'value': character.torso.value,
            'equipped_on': character.torso.equipped_on,
            'stats': character.torso.stats,
            'image_path': character.torso.image_path
        }
    else:
        save_data['Equipped']['Torso'] = None

    if character.accessory:
        save_data['Equipped']['Accessory'] = {
            'slot_id': character.accessory.slot_id,
            'name': character.accessory.name,
            'desc': character.accessory.desc,
            'value': character.accessory.value,
            'equipped_on': character.accessory.equipped_on,
            'stats': character.accessory.stats,
            'image_path': character.accessory.image_path,
        }
    else:
        save_data['Equipped']['Accessory'] = None

    save_data['Cleansed'] = world_map.areas_cleansed

    save_data['MusicVolume'] = music_volume
    save_data['SFXVolume'] = sfx_volume

    saveData(save_data, save_path)


def loadGame():
    global play_map, main_character, world_map, \
        region_map, local_region, battle_screen, \
        inventory, music_volume, sfx_volume

    load_data = loadData("data/saves/save")

    if load_data:
        envi = environment

        envi.location_world = load_data['Environment']['location_world']
        envi.location_region = load_data['Environment']['location_region']
        envi.region_name = load_data['Environment']['region_name']
        envi.chaos_level = load_data['Environment']['chaos_level']
        envi.building_type = load_data['Environment']['building_type']
        envi.building_name = load_data['Environment']['building_name']

        structure = environment.structure
        structure['count'] = load_data['Structure']['count']
        structure['forts'] = load_data['Structure']['forts']
        structure['camps'] = load_data['Structure']['camps']

        for key, val in load_data['Structure']['Camp'].items():

            structure['Camp'].update({tuple(literal_eval(key)): val})

        for key, val in load_data['Structure']['Fort'].items():
            structure['Fort'][key] = val
            structure['Fort'][key]['WorldLocation'] = tuple(structure['Fort'][key]['WorldLocation'])
            structure['Fort'][key]['RegionLocation'] = tuple(structure['Fort'][key]['RegionLocation'])

        #environment.game_map = load_data['GameMap']
        game_map = environment.game_map
        game_map.width = load_data['GameMap']['width']
        game_map.height = load_data['GameMap']['height']
        game_map.regions_num = load_data['GameMap']['regions_num']
        game_map.region_names = load_data['GameMap']['region_names']
        game_map.world = load_data['GameMap']['world']
        game_map.regions = load_data['GameMap']['regions']
        game_map.region_info = load_data['GameMap']['region_info']

        if environment.player:
            del environment.player
            environment.player = environment.PlayerMarker("Player", load_data['Player']['job'])

        player = environment.player
        player.name = load_data['Player']['name']
        player.job = load_data['Player']['job']
        player.location = load_data['Player']['location']
        player.destination = load_data['Player']['destination']
        player.income = load_data['Player']['income']
        player.ap = load_data['Player']['ap']
        player.gold = load_data['Player']['gold']
        player.wood = load_data['Player']['wood']
        player.stone = load_data['Player']['stone']
        player.metal = load_data['Player']['metal']
        player.gems = load_data['Player']['gems']
        player.army_amount = load_data['Player']['army_amount']
        player.army_trained = load_data['Player']['army_trained']
        player.army_armour = load_data['Player']['army_armour']
        player.army_weapon = load_data['Player']['army_weapon']
        player.army_power = load_data['Player']['army_power']

        main_character = characters.Character(player.job, manager, is_player=True)
        character = main_character

        character.kind = load_data['Character']['kind']
        character.level = load_data['Character']['level']
        character.exp = load_data['Character']['exp']
        character.exp_needed = load_data['Character']['exp_needed']
        character.con_max = load_data['Character']['con_max']
        character.wis_max = load_data['Character']['wis_max']
        character.fai_max = load_data['Character']['fai_max']
        character.str_max = load_data['Character']['str_max']
        character.int_max = load_data['Character']['int_max']
        character.end_max = load_data['Character']['end_max']
        character.wil_max = load_data['Character']['wil_max']
        character.fin_max = load_data['Character']['fin_max']
        character.bonus_value_max = load_data['Character']['bonus_value_max']
        character.bonus_value = character.bonus_value_max

        play_map = environment.game_map

        character.inventory.items = load_data['Inventory']

        if load_data['Equipped']['Hand']:
            load_hand = load_data['Equipped']['Hand']
            item_hand = Item(load_hand['slot_id'], load_hand['name'],
                             load_hand['desc'], load_hand['value'],
                             load_hand['image_path'], load_hand['equipped_on'],
                             load_hand['stats'])
            character.hand = item_hand

        if load_data['Equipped']['Torso']:
            load_torso = load_data['Equipped']['Torso']
            item_torso = Item(load_torso['slot_id'], load_torso['name'],
                              load_torso['desc'], load_torso['value'],
                              load_torso['image_path'], load_torso['equipped_on'],
                              load_torso['stats'])
            character.torso = item_torso

        if load_data['Equipped']['Accessory']:
            load_accessory = load_data['Equipped']['Accessory']
            item_accessory = Item(load_accessory['slot_id'], load_accessory['name'],
                                  load_accessory['desc'], load_accessory['value'],
                                  load_accessory['image_path'], load_accessory['equipped_on'],
                                  load_accessory['stats'])
            character.accessory = item_accessory

        music_volume = load_data["MusicVolume"]
        sfx_volume = load_data["SFXVolume"]

        if pygame.mixer_music.get_busy():
            pygame.mixer_music.set_volume(music_volume / 100)

        character.updateStats()

        world_map = WorldMap(play_map.width, play_map.height, play_map.regions_num, play_map.region_names)
        world_map.areas_cleansed = load_data['Cleansed']
        region_map = RegionMap(True)
        region_map.setLocation(environment.location_world)
        local_region = LocalRegion(getAreaType('-'))
        local_region.hideMenu()

        if battle_screen:
            del battle_screen

        battle_screen = BattleScreen("Battling Monster")
        return True
    return False


def updateRes():
    global region_map, battle_screen, main_character
    region_map.btn_army.kill()
    region_map.tbx_army.kill()
    region_map.text_input.kill()
    region_map.text_box.kill()
    region_map.exp_bar.kill()
    region_map.game_settings.kill()
    region_map.gui_player_lvl.kill()
    region_map.txb_player_stats.kill()

# Game map object
play_map = None

# Interface character object
main_character = None

# Game state objects
world_map = None
region_map = None
local_region = None
battle_screen = None

inventory = None

