from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from requests import get
import json
import time
import random

# TODO if using API you can only get lowest buy order price (from skins to cash)
# see example https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=34306

# TODO see in network page (GET - requests) try to ask server to get items instead of using selenium

# TODO I want to using requests instead of selenium. Handling dynamic content will make it much faster (i guess?)


def convert_CNY_RUB():
    req_json = get("https://api.exchangerate-api.com/v4/latest/CNY").json()
    CNY_TO_RUB = req_json["rates"]["RUB"]
    return CNY_TO_RUB


def find(driver, element_XPATH):
    try:
        v = driver.find_element(By.XPATH, element_XPATH).text
        if v is not None:
            return v
    except:
        pass
    return find(driver, element_XPATH)


def setup():
    opts = webdriver.FirefoxOptions()
    #opts.add_argument("--headless")
    serv = webdriver.FirefoxService(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=opts, service=serv)
    driver.implicitly_wait(5)
    return driver


def save_items(items):
    js = json.dumps(items)
    with open("result.json", "w") as f:
        for c in js:
            f.write(c)


def get_quality_XPATH(item_name): # redo this later
    with open("amounts.json", "r") as aj:
        d = json.load(aj)
        amount = d[item_name] + 1
        xpath_list = []
        for i in range(1, amount):
            xpath_list.append(f"/html/body/div[6]/div/div[2]/div/a[{i}]")
    return xpath_list


def get_items():
    #fuck it. use this instead https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id=33811
    CNY_RUB_price = convert_CNY_RUB() * 1.02  # with site commision
    base_string = "https://buff.163.com/goods/"
    items = {}
    driver = setup()
    with open("ready_to_use_items.json", "r") as ready_json:
        d = json.load(ready_json)
        for name in d:
            items[name] = []
            xpath_quality_list = get_quality_XPATH(name)
            s = base_string + str(d[name])
            driver.get(s)
            time.sleep(random.random() + 1.5)
            for xpath in xpath_quality_list:
                #somewhere here i also need to store "amount of selled" from sell button.
                quality_value = find(driver, xpath).split(" ¥ ")
                if len(quality_value) == 1:
                    continue 
                    # no items variation (Which means no price) so len == 1             
                items[name].append(
                    (quality_value[0], float("{:.2f}".format(float(quality_value[1]) * CNY_RUB_price)))
                )
    save_items(items)
    driver.close()


if __name__ == "__main__":
    full_st = time.time()
    get_items()
    full_et = time.time()
    full_time = full_et - full_st
    print("full exec time is = ", full_time)
