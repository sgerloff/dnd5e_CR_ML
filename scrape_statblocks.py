from selenium import webdriver
from PIL import Image
from utility.monster_features import MonsterFeatures
import os.path


def save_statblock(driver, name):
    element = driver.find_element_by_id("wrp-pagecontent")

    location = element.location
    size = element.size

    driver.save_screenshot("data/statblocks/_screenshot.png")

    x = location['x']
    y = location['y']
    w = size['width']
    h = size['height']
    width = x + w
    height = y + h

    im = Image.open('data/statblocks/_screenshot.png')
    im = im.crop((int(x), int(y), int(width), int(height)))
    im.save('data/statblocks/' + str(name).replace('"', '') + '.png')


def accept_cookies(driver):
    buttons = driver.find_elements_by_xpath(
        '//*[@class=" bg-gray-300 text-sm md:text-base hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded outline-none m-2 "]')
    for b in buttons:
        if b.text == "Zustimmen und fortfahren":
            b.click()
            break;


def allow_npcs(driver):
    filter = driver.find_elements_by_xpath('//*[@class="fltr__mini-pill  fltr__mini-pill--default-desel "]')
    for f in filter:
        if f.text == "Adventure NPC":
            f.click()
            break;


def add_source_books(driver):
    filter_names = driver.find_elements_by_xpath('//*[@class="btn btn-default "]')
    for n in filter_names:
        if n.text == "Filter":
            n.click()
            break;

    filters = driver.find_elements_by_xpath('//*[@class="fltr__pill"]')
    add_filters = ["Dragon Magazine", "Infernal Machine Rebuild", "Locathah Rising", "Lost Laboratory of Kwalish",
                   "Mordenkainen’s Fiendish Folio", "Sapphire Anniversary Dice Set", "The Tortle Package",
                   "Wayfinder’s Guide to Eberron", "PS: Amonkhet", "PS: Dominaria", "PS: Innistrad", "PS: Ixalan",
                   "PS: Kaladesh", "PS: Zendikar"]
    for f in filters:
        if f.text in add_filters:
            f.click()
    driver.find_elements_by_xpath('//*[@class="glyphicon glyphicon-ok"]')[0].click()


def get_driver():
    driver = webdriver.Chrome('data/chromedriver.exe')
    driver.implicitly_wait(10)
    driver.get('https://5e.tools/bestiary.html')

    accept_cookies(driver)
    allow_npcs(driver)
    add_source_books(driver)
    return driver


def fetch_missing_statblocks(missing):
    driver = get_driver()
    names = driver.find_elements_by_xpath('//*[@class="ecgen__name bold col-4-2 pl-0"]')
    for n in names:
        if n.text in missing:
            print(n.text)
            n.click()
            save_statblock(driver, n.text)


def get_missing_statblocks():
    mf = MonsterFeatures()
    mf.load("data/monster_features")
    name_list = mf.df["name"].tolist()

    missing = []
    for name in name_list:
        file_name = name.replace('"', '')
        if os.path.isfile("data/statblocks/" + file_name + ".png"):
            pass
        else:
            print("Missing statblock: ", name)
            missing.append(name)
    return missing


def fetch_all_statblocks():
    mf = MonsterFeatures()
    mf.load("data/monster_features")
    name_list = mf.df["name"].tolist()

    driver = get_driver()
    names = driver.find_elements_by_xpath('//*[@class="ecgen__name bold col-4-2 pl-0"]')
    for n in names:
        if n.text in name_list:
            print(n.text)
            n.click()
            save_statblock(driver, n.text)


missing = get_missing_statblocks()
if missing:
    fetch_missing_statblocks(missing)

# fetch_all_statblocks()
