import json
import main
def expression_parse_1(line):
    want_items = ["AK-47", "MP9", "MAC-10", "SSG 08", "Galil AR", "FAMAS", "M4A1-S", "M4A4", "USP-S", "Glock-18", "Desert-Eagle", "Case"]
    for item in want_items:
        if item.lower() in line.lower():
            if (item == "Case" and "Case Hardened") or "Sticker" in line or "Souvenir" in line:
                return False
            return True
    return False    


def write_only_needed():
    with open("items_id.json", "w") as f:
        start_writing = True
        base_json =  open("cs2_marketplaceids.json", "r").read().splitlines()
        for line in base_json:
            if "}," in line and start_writing:
                f.write(line + '\n')
                start_writing = False
            elif start_writing or expression_parse_1(line):
                f.write(line + '\n')
                start_writing = True


def delete_youpin_id():
    with open("items_id.json", "r") as f:
        with open("fixed_items.json", "w") as file:
            for line in f:
                if "youpin_id" in line:
                    continue
                elif "buff163_goods_id" in line:
                    file.write(line[:-2]) # trim line. Deleted charachers are ", "
                else:
                    file.write(line)  

def steam_web_api_test():
    #rewrite json file and delete useless info from it.
    USD_to_RUB = main.convert_to_RUB("USD")
    with open('prepared_json.json') as json_file:
        #prices stored in USD
        data = json.load(json_file)
        items = {}
        i = 0
        for item in data:
            for wear in data[item]:
                new_item = {
                "skinname": data[item][wear]['name'],
                "skin_wear":  wear,
                "pricelatest": round(data[item][wear]["pricelatest"]*USD_to_RUB,2),
                "pricelatestsell": round(data[item][wear]["pricelatestsell"]*USD_to_RUB,2),
                "priceupdatedat": data[item][wear]["priceupdatedat"],
                "pricemin": round(data[item][wear]["pricemin"]*USD_to_RUB,2),
                "pricereal": round(data[item][wear]["pricereal"]*USD_to_RUB,2),
                "pricereal24h": round(data[item][wear]["pricereal24h"]*USD_to_RUB,2),
                "offervolume": data[item][wear]["offervolume"],
                "sold24h": data[item][wear]["sold24h"],
                "sold7d": data[item][wear]["sold7d"],
                "updatedat": data[item][wear]["updatedat"],
                }          
                if item in items:
                    items[item][wear] = new_item
                else:
                    new_item = {
                        wear: new_item
                    }
                    items[item] = new_item
    return items

def prepare_steam_web_api():
    #yes you can directly ask for a given type of weapon but cmon, it isnt for us free plesbs (500 requests per month)
    with open('steam_api.json', 'r') as json_file:
        data = json.load(json_file)
        i=0
        items = {}
        for item in data:
            i+=1
            if item['itemtype'] is not None:
                if expression_parse_1(item['itemtype']):
                    name = item['itemtype'] + " | " + item["itemname"]
                    wear = item['wear']
                    only_required_fields = {
                        "name" : name,
                        'wear' : wear,
                        "pricelatest" : item['pricelatest'],
                        'pricelatestsell' : item['pricelatestsell'],
                        "priceupdatedat" : item['priceupdatedat'],
                        "pricemin": item["pricemin"],
                        'pricereal' : item['pricereal'],
                        "pricereal24h" : item["pricereal24h"],
                        "pricerealcreatedat" : item['pricerealcreatedat'],
                        'pricemedian' : item['pricemedian'], 
                        "priceavg" : item['priceavg'],
                        'offervolume': item["offervolume"],
                        'sold24h' : item['sold24h'],
                        "sold7d" : item['sold7d'],
                        'updatedat' : item['updatedat'],  
                    }
                    if name in items:
                        items[name][wear] = only_required_fields
                    else:
                        new_item = {
                            wear: only_required_fields
                        }
                        items[name] = new_item
        return items
    
def write_json(dictionary, file_name):
    #doesnt autoformat. Write a 1-liner
    open(file_name, 'w').close()
    with open(file_name, 'a') as data_json:
        json.dump(dictionary, data_json)
            

if __name__ == "__main__":
    #write_only_needed()
    #delete_youpin_id()
    #After this i deleted inner {} (not contents inside of it) using ctrl + H. #Must be done by hand.
    #Download file into steam_api_test.json first
    write_json(prepare_steam_web_api(), "prepared_json.json")
    write_json(steam_web_api_test(), "steam_result.json")