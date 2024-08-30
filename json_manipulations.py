import json
import os


def expression_parse_1(line):
    want_items = [
        "AK-47",
        "MP9",
        "MAC-10",
        "SSG 08",
        "Galil AR",
        "FAMAS",
        "M4A1-S",
        "M4A4",
        "USP-S",
        "Glock-18",
        "Desert-Eagle",
        "Case",
    ]
    for item in want_items:
        if item.lower() in line.lower():
            if (
                (item == "Case" and "Case Hardened")
                or "Sticker" in line
                or "Souvenir" in line
                or "Doppler" in line
            ):
                return False
            return True
    return False


def write_only_needed():
    with open("items_id.json", "w") as f:
        start_writing = False
        base_json = open("fixed_cs2_marketplaceids.json", "r").read().splitlines()
        f.write("{\n")
        f.write('"items": {\n')
        for line in base_json:
            if "}" in line and start_writing:
                f.write(line + "\n")
                start_writing = False
            elif start_writing or expression_parse_1(line):
                f.write(line + "\n")
                start_writing = True
    with open("items_id.json", "rb+") as filehandle:
        #remove last ,
        filehandle.seek(-2, os.SEEK_END)
        filehandle.truncate()
    with open("items_id.json", "a") as file:
        file.write("\n  }" + "\n")
        file.write("}")


def delete_inner_parenthesis():
    base_json = open("not_yet_fixed_items.json", "r").read().splitlines()
    with open("finally_fixed_items.json", "w") as file:
        file.write("{\n")
        pair = ["", ""]
        for line in base_json:
            if ":" in line and "items" not in line:
                if pair[0] == "":
                    pair[0] = line.split(":")[0]
                elif pair[1] == "":
                    pair[1] = line.split(":")[1][:-3]
                if pair[0] != "" and pair[1] != "":
                    file.write(pair[0] + " : " + pair[1] + ",")
                    pair[0] = ""
                    pair[1] = ""
    with open("finally_fixed_items.json", "rb+") as filehandle:
        #remove last ,
        filehandle.seek(-2, os.SEEK_END)
        filehandle.truncate()
    with open("finally_fixed_items.json", "a") as file:
        file.write("\n  }")


def delete_patterns():
    with open("fixed_cs2_marketplaceids.json", "w") as file:
        base_json = open("cs2_marketplaceids.json", "r").read().splitlines()
        i = 0
        for line in base_json:
            if "patterns" in base_json[i + 1]:
                break
            i += 1
            file.write(line + "\n")
        file.write("    }" + "\n")
        file.write("}")


def delete_youpin_id():
    with open("items_id.json", "r") as f:
        with open("not_yet_fixed_items.json", "w") as file:
            for line in f:
                if "youpin_id" in line:
                    continue
                elif "buff163_goods_id" in line:
                    file.write(line[:-2])  # trim line. Deleted charachers are ", "
                else:
                    file.write(line)


def write_json(dictionary, file_name):
    # doesnt autoformat. Write a 1-liner
    open(file_name, "w").close()
    with open(file_name, "a") as data_json:
        json.dump(dictionary, data_json)


if __name__ == "__main__":
    delete_patterns() # delete patterns at hte end of cs_marketplaceids
    write_only_needed() # write only items that i need
    delete_youpin_id() # remove unnecesary id
    delete_inner_parenthesis() # remove inner parenthesis
