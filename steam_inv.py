import re
import requests
from bs4 import BeautifulSoup
import random
import time
import os
import pandas as pd
import json

#76561198273710960
# LOAD DO INVENTÁRIO QUANDO O JSON ESTIVER DESATUALIZADO
def update_inventory(steam_id):
    steam_id = int(steam_id)
    json_inventory = requests.get(f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=5000%22")
    print("Updating Inventory")
    time.sleep(random.uniform(1, 3))
    inventory_file = open("inventory.json", "w")
    json.dump(json_inventory.json(), inventory_file, indent = 4)
    inventory_file.close()


def filterCases(inventory: dict):
    cases: dict = {}
    for invDes in inventory["descriptions"]:
        if "Case" in invDes["name"]:
            cases[invDes["classid"]] = invDes["name"]
            case_url[invDes["name"]] = "https://steamcommunity.com/market/listings/730/" + invDes["name"].replace(" ", "%20")
    return cases

def getCasesAmmount(inventory: dict, casesId: dict):
    inv = {}
    for asset in inventory["assets"]:
        if asset["classid"] in casesId.keys():
            if casesId[asset["classid"]] not in inv.keys():
                inv[casesId[asset["classid"]]] = 1
            else:
                ammount = inv[casesId[asset["classid"]]] + 1
                inv[casesId[asset["classid"]]] = ammount
    return inv



def get_id(s):
    id = None
    for script in s.find_all('script'):
        id_regex = re.search('Market_LoadOrderSpread\(([ 0-9]+)\)', script.text)
        if id_regex:
            id = id_regex.groups()[0].strip()
            print(id)
            break
    return id



def get_price(id, table, error, headers):
    if id:
        id_url = f"https://steamcommunity.com/market/itemordershistogram?country=PT&language=english&currency=3&item_nameid={id}&two_factor=0" 
        html = requests.get(id_url, headers=headers).json()
        x = random.uniform(2, 5)
        time.sleep(x)
        try:
            soup = BeautifulSoup(html['sell_order_summary'], 'lxml')
            price = soup.select_one('span:last-child').text
            price = price.replace('--','00')
            print(f"Price: {price}")
            table['Sell Price'][table['Case'].index(steam_item_id_dict[id])] = price[:-1]
            error = 0
                
        except:
            error = error + 1
            print("Error")
            x = random.uniform(1, 3)
            get_price(id, table, error, headers)
            if error == 5:
                exit()


    else:
        print("Could not get ID")
        exit()


def abstract_load(name_file):
    with open(name_file) as f:
        raw = f.read()
    file = json.loads(raw)
    return file

def update_cases(case_url, steam_item_id_dict, table, cases_amount):
    for case in case_url:
        if case not in steam_item_id_dict.values():
            html = requests.get(case_url[case], headers=headers).text
            time.sleep(random.uniform(2, 4))
            soup = BeautifulSoup(html, 'lxml')
            id = get_id(soup)
            steam_item_id_dict[id]=case
        if case not in table['Case']:
            table['Case'].append(case)
            table['Qt'].append(cases_amount[case])
            table['Buy Price'].append(0.0)
            table['Sell Price'].append(0.0)
            table['Sell Price w tax'].append(0.0)
            table['Profit per Case'].append(0.0)
            table['Profit'].append(0.0)

def update_cases_price(table, buy_prices):
    for case in buy_prices:
        if case in table['Case']:
            table['Buy Price'][table['Case'].index(case)] = buy_prices[case]

def get_cases_price(steam_item_id_dict, table, error, headers):
    for id in steam_item_id_dict:
        print(f"Request To {steam_item_id_dict[id]}")
        time.sleep(random.uniform(1, 4))
        get_price(id, table,error,headers)
        time.sleep(random.uniform(2, 3))

def compute_table(df):
    for x in range(len(df['Case'])):
        df['Sell Price w tax'][x] = float(df['Sell Price'][x]) * 0.85

    for x in range(len(df['Case'])):
        df['Profit per Case'][x] = float(df['Sell Price w tax'][x]) - float(df['Buy Price'][x])

    for x in range(len(df['Case'])):
        df['Profit'][x] = int(df['Qt'][x]) * float(df['Profit per Case'][x])

if __name__ == "__main__":
    error = 0
    case_url = {}
    headers = {'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
           'Accept-Encoding' : "gzip, deflate, br",
           'Upgrade-Insecure-Requests' : "1",
           'Referer' : 'https://www.google.com/',
           'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0"}
    
    steam_item_id_dict = abstract_load('steam_item_id_dict.json')

    table = abstract_load('table_cases.json')

    buy_prices = abstract_load('buy_prices.json')

    answer = input('Update Inventory - 1\nNew Player - 2\nJust Get Profit - 3\n')
    if answer == "1":
        tfile = open('steam_id_file.txt', 'r')
        steam_id = tfile.readline()
        update_inventory(steam_id.replace('\n', ''))

    elif answer == "2":
        answer2 = input('Enter Steam ID (Number):')
        tfile = open('steam_id_file.txt', 'w')
        tfile.write(answer2)
        tfile.close()

        tfile = open('steam_id_file.txt', 'r')
        steam_id = tfile.readline()
        tfile.close()
        update_inventory(steam_id.replace('\n', ''))
    else:
        pass

    inventory = abstract_load('inventory.json')

    cases_filtered = filterCases(inventory)

    cases_amount = getCasesAmmount(inventory,cases_filtered)

    update_cases(case_url, steam_item_id_dict, table, cases_amount)

    update_cases_price(table, buy_prices)

    get_cases_price(steam_item_id_dict, table, error, headers)

    df = pd.DataFrame(data=table)
    pd.set_option('mode.chained_assignment', None)
    df["Sell Price"]=df["Sell Price"].str.replace(',','.')

    compute_table(df)

    with pd.option_context('display.max_rows', None,
                        'display.max_columns', None,
                        'display.precision', 3,
                        ):
        print(df)
        total = df['Profit'].sum()
        print(f"\nYour Profit is {total:.3f}€")

    tfile = open('test.txt', 'w')
    tfile.write(df.to_string())
    tfile.write(f"\n\nYour Profit is {total:.3f}€")
    tfile.close()

    json.dump( table, open( "table_cases.json", 'w' ) )
    json.dump( steam_item_id_dict, open( "steam_item_id_dict.json", 'w' ) )
    # save it as a new file, the original file is untouched and here I am saving
    # it as xlsm(m here denotes macros).



