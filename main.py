from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from os.path import getsize
from requests import get
from json import dumps, loads
from pathlib import Path
import time
import decimal


# TODO if using API you can only get lowest buy order price (from skins to cash)
# see example https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id=34306

# TODO see in network page (GET - запросы) try to ask server to get items instead of using selenium

# TODO I want to using requests instead of selenium. Handling dynamic content will make it much faster (i guess?)
# Проеблема блять в том, что получаемый текст не соответствует тексту из html
# Сайт выполняет GET запрос к бдшке поэтому пока так


def generate_cookies(driver):
    open('cookies.json', 'w').close()
    Path("cookies.json").write_text(dumps(driver.get_cookies(), indent=2))


def convert_CNY_RUB():
    # in case i will need it
    # hide it later
    # API_KEY = fc58b1da2479d5493a749550 # i dont need id xd
    req_json = get("https://api.exchangerate-api.com/v4/latest/CNY").json()
    CNY_TO_RUB = req_json["rates"]["RUB"]
    return CNY_TO_RUB


def show(items):
    # in case i need it
    for keys, values in items.items():
        print(keys, values)


def next_page(driver, amount_of_tries = 0):
    try:
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.LINK_TEXT, "Next page"))).click()
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
    try:
        if getsize("cookies.json") == 0:
            print("generate cookies first")
    except:
        print("generate cookies first")
        quit()
    opts = webdriver.FirefoxOptions()
    #opts.add_argument("--headless")
    serv = webdriver.FirefoxService(executable_path="/snap/bin/geckodriver")
    driver = webdriver.Firefox(options=opts, service=serv)
    driver
    # logging in by hand (for now). Make a throw away aсcount without 2FA and use its data (login/pass) in env var if coockies not valid
    steam_login_link = "https://steamcommunity.com/login/home/"  
    driver.get(steam_login_link)
    # Manual generation of cookies for further automatization
    # Get cookies to a json file:
    # generate_cookies(driver)
    # driver.close()
    for cookie in loads(Path("cookies.json").read_text()):
        driver.add_cookie(cookie)
    driver.refresh()
    driver.implicitly_wait(5)
    login_link = "https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.realm=https%3A%2F%2Fbuff.163.com%2F&openid.sreg.required=nickname%2Cemail%2Cfullname&openid.assoc_handle=None&openid.return_to=https%3A%2F%2Fbuff.163.com%2Faccount%2Flogin%2Fsteam%2Fverification%3Fback_url%3D%252Faccount%252Fsteam_bind%252Ffinish&openid.ns.sreg=http%3A%2F%2Fopenid.net%2Fextensions%2Fsreg%2F1.1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select"
    driver.get(login_link)
    driver.find_element(By.XPATH, '//*[@id="imageLogin"]').click()
    return driver

def save_items(items):
    open('file.txt', 'w').close() #for clearing file
    f = open("items.txt", "a")
    for item, value in items.items():
        f.write(item + " | " + str(value) + "\n")
    f.close()


def get_links(weapon_names_list):
    links = []
    for name in weapon_names_list:
        links.append(f"https://buff.163.com/market/csgo#game=csgo&page_num=1&category=weapon_{name}&tab=selling")
    return links

def get_items():
    weapon_list = ["ak47","awp","m4a1","m4a1_silencer","famas","galilar","ssg08","usp_silencer","glock","geagle","mp9"]
    full_st = time.time()
    CNY_RUB_price = convert_CNY_RUB() * 1.02 # with site commision
    driver = setup()
    links = get_links(weapon_list)
    XPATH_list = {}
    items = {} # until no db this will stay as it is. When db it will be imported from it
    for i in range(1, 21):
        # name of a weapon = price (in XPATH values)
        XPATH_list[f"html/body/div[5]/div[1]/div[4]/div[1]/ul/li[{i}]/h3/a"] = (
            f"/html/body/div[5]/div[1]/div[4]/div[1]/ul/li[{i}]/p/strong"
        )

    for link in links:
        driver.get(link)
        last_page_xpath = "/html/body/div[5]/div[1]/div[4]/div[2]/ul/li[13]/a"
        n = int(find(driver, last_page_xpath))
        time.sleep(0.001)
        for i in range(1, n):
            #st = time.time()
            for xpath_name in XPATH_list:
                t = find(driver, xpath_name)
                watch = find(driver, XPATH_list[xpath_name])
                items[t] = "{:.2f}".format(float(watch[2:]) * CNY_RUB_price)
            next_page(driver)
            #et = time.time()
            #print("Elapsed time in seconds for 1 iteration = ", et-st )
    save_items(items)
    driver.close()
    full_et = time.time()
    full_time = full_et - full_st
    print("full exec time is = " , full_time)
    return items


if __name__ == "__main__":
    get_items()
