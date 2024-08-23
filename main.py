from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from requests import get
import time
import random

# TODO if using API you can only get lowest buy order price (from skins to cash)
# see example https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=34306

# TODO see in network page (GET - requests) try to ask server to get items instead of using selenium

# TODO I want to using requests instead of selenium. Handling dynamic content will make it much faster (i guess?)


def convert_USD_RUB():
    req_json = get("https://api.exchangerate-api.com/v4/latest/USD").json()
    USD_TO_RUB = req_json["rates"]["RUB"]
    return USD_TO_RUB


def show(items):
    # in case i need it
    for keys, values in items.items():
        print(keys, values)


def next_page(driver, amount_of_tries=0):
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Next page"))
        ).click()
    except:
        time.sleep(0.1)
        if amount_of_tries > 1:
            driver.get(driver.current_ulr)
        next_page(driver, amount_of_tries + 1)


def find(driver, element_XPATH):
    try:
        v = driver.find_element(By.XPATH, element_XPATH).text
        if v is not None:
            return v
    except:
        pass
    return find(driver, element_XPATH)


def setup():
    # login in with steam is redundant. Items can be seen by ids
    opts = webdriver.FirefoxOptions()
    opts.add_argument("--headless")
    serv = webdriver.FirefoxService(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=opts, service=serv)
    driver.implicitly_wait(5)
    return driver


def save_items(items):
    open("file.txt", "w").close()  # for clearing file
    f = open("items.txt", "a")
    for item, value in items.items():
        f.write(item + " | " + str(value) + "\n")
    f.close()


def get_links(file_name):
    with open(file_name, "r") as f:
        links = []
        for link in f:
            links.append(link)
    return links


def get_items():
    USD_RUB_price = convert_USD_RUB() * 1.05  # with site commision
    driver = setup()
    links = get_links("links.txt")
    items = {}

    name = f"/html/body/div[2]/div[4]/div/div/div[1]/div/div/div[1]/div[2]/div[1]/p[1]"
    XPATH_list = {
        name: (
            (
                f"/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[1]/span[1]",
                "/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[1]/span[3]",
            ),
            (
                f"/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[2]/span[1]",
                "/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[2]/span[3]",
            ),
            (
                f"/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[3]/span[1]",
                "/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[3]/span[3]",
            ),
            (
                f"/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[4]/span[1]",
                "/html/body/div[2]/div[4]/div/div/div[1]/div/div/ul/li[4]/span[3]",
            ),
        )
    }

    for link in links:
        # If they dont ban by IP how can they stop me?
        bot_evasion = random.random()
        driver.get(link)
        time.sleep(bot_evasion)
        base_name = find(driver, name)
        for pair in XPATH_list[name]:
            quality = find(driver, pair[0])
            value_USD = find(driver, pair[1])
            skin_name = base_name + " | " + quality
            items[skin_name] = float(
                "{:.2f}".format(float(value_USD[1:]) * USD_RUB_price)
            )
    save_items(items)
    driver.close()
    return items


if __name__ == "__main__":
    full_st = time.time()
    get_items()
    full_et = time.time()
    full_time = full_et - full_st
    print("full exec time is = ", full_time)
