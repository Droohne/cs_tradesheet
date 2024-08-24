import json

def expression_parse_1(line):
    want_items = ["AK-47", "MP9", "MAC-10", "SSG-08", "Galil AR", "FAMAS", "M4A1-S", "M4A4", "USP-S", "Glock-18", "Desert-Eagle", "Case"]
    for item in want_items:
        if item in line:
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


if __name__ == "__main__":
    #write_only_needed()
    #delete_youpin_id()
    #After this i deleted inner {} (not contents inside of it) using ctrl + H.
    #Must be done by hand. Probably can be automated...
    pass