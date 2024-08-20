from selenium import webdriver
from selenium.webdriver.common.by import By
from os.path import getsize
from requests import get
from json import dumps, loads
from pathlib import Path


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
    CNY_TO_RUB = req_json["rates"][
        "RUB"
    ]  # if steam will continue prices in USD change it to USD
    return CNY_TO_RUB


def show(items):
    # in case i need it
    for keys, values in items.items():
        print(keys, values)


def next_page(
    driver, page_number
):  # Может быть просто по ссылке переходить, вместо нажатия кнопки next page?
    # на 7 странице XPATH кнопки next page меняется на /html/body/div[5]/div[1]/div[4]/div[2]/ul/li[13]/a
    # с 8 XPATH становится таким /html/body/div[5]/div[1]/div[4]/div[2]/ul/li[14]/a и остается таким
    xpath = ""
    if page_number < 6:
        xpath = "/html/body/div[5]/div[1]/div[4]/div[2]/ul/li[12]/a"
    elif page_number == 6:
        xpath = "/html/body/div[5]/div[1]/div[4]/div[2]/ul/li[13]/a"
    else:
        xpath = "/html/body/div[5]/div[1]/div[4]/div[2]/ul/li[14]/a"
    try:
        v = driver.find_element(By.XPATH, xpath)
        driver.find_element(By.XPATH, xpath).click()
    except Exception as er:
        if (
            er.msg
            == "Unable to locate element: /html/body/div[5]/div[1]/div[4]/div[2]/ul/li[14]/a; For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception"
        ):
            # Use global variable instead of wasted loops?
            return


def find(driver, element_XPATH):
    try:
        v = driver.find_element(By.XPATH, element_XPATH).text
        if v is not None:
            return v
    except:
        driver.implicitly_wait(1)
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

    # logging in by hand (for now)
    steam_login_link = "https://steamcommunity.com/login/home/"
    driver.get(steam_login_link)
    for cookie in loads(Path("cookies.json").read_text()):
        driver.add_cookie(cookie)
    driver.refresh()
    driver.implicitly_wait(3)
    login_link = "https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.realm=https%3A%2F%2Fbuff.163.com%2F&openid.sreg.required=nickname%2Cemail%2Cfullname&openid.assoc_handle=None&openid.return_to=https%3A%2F%2Fbuff.163.com%2Faccount%2Flogin%2Fsteam%2Fverification%3Fback_url%3D%252Faccount%252Fsteam_bind%252Ffinish&openid.ns.sreg=http%3A%2F%2Fopenid.net%2Fextensions%2Fsreg%2F1.1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select"
    driver.get(login_link)
    driver.find_element(By.XPATH, '//*[@id="imageLogin"]').click()
    # Manual generation of cookies for further automatization
    # Get cookies to a json file:
    # generate_cookies(driver)
    # driver.close()
    return driver


def save_items(items):
    open('file.txt', 'w').close() #for clearing file
    f = open("items.txt", "a")
    for item, value in items.items():
        f.write(item + " | " + value + "\n")
    f.close()


def get_items(number_of_pages):
    driver = setup()
    link = "https://buff.163.com/market/csgo#game=csgo&page_num=1&category_group=rifle&tab=top-bookmarked"
    driver.get(link)
    XPATH_list = {}
    items = {}
    for i in range(1, 21):
        # name of a weapon = price (in XPATH values)
        XPATH_list[f"html/body/div[5]/div[1]/div[4]/div[1]/ul/li[{i}]/h3/a"] = (
            f"/html/body/div[5]/div[1]/div[4]/div[1]/ul/li[{i}]/p/strong"
        )

    for i in range(0, number_of_pages):
        for xpath_name in XPATH_list:
            t = find(driver, xpath_name)
            if t not in items:
                watch = find(driver, XPATH_list[xpath_name])
                items[t] = watch
            else:  # As items come with stickers already installed, they doesnt matter to me as i want minimal price for given weapon (item) so does the float value
                price = find(driver, XPATH_list[xpath_name])
                b = float(price[2:])
                c = float(items[t][2:])
                if b < c:
                    items[t] = price
        next_page(driver, i)
    save_items(items)
    driver.close()
    return items


if __name__ == "__main__":
    get_items(25)
