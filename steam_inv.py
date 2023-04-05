import re
import requests
from bs4 import BeautifulSoup
import random
import time
import os
import pandas as pd
import json
import discord
###################################################################################################
#### DISCORD PART
# 76561198273710960 - top
 
def sendMessage(token, channel_id, message):
    url = 'https://discord.com/api/v8/channels/{}/messages'.format(channel_id)
    data = {"content": message}
    header = {"authorization": token}
    
    files = {'file': open('Report.txt', 'rb')}
    r = requests.post(url, data=data, headers=header, files=files)
    print(r.status_code)
 
 
def createDmChannel(token, user_id):
    data = {"recipient_id": user_id}
    headers = {"authorization": token}
    data2 = {"nicks" : {255766528635437056: "Mercao", 299201969300570113: "Top"}, "access_token": [token],  "recipients": [
        "255766528635437056","299201969300570113"
    ]}
    r1 = requests.post('https://discord.com/api/v9/users/@me/channels',json=data2, headers=headers)
    print(r1.status_code)
    print(r1.json())
    r = requests.post(f'https://discord.com/api/v9/users/@me/channels', json=data, headers=headers)
    print(r.status_code)
    
    print(r.json())
    channel_id = r.json()['id']
    
    return channel_id

 
# #Change these variables
token = 'Mjk5MjAxOTY5MzAwNTcwMTEz.GwFdIS.Jp1uItS5DBxLhkeUUt9OkY6Fg_9LLtn53er0dY'
user_id = '255766528635437056'
message = 'Report'

###################################################################################################
def update_inventory(steam_id, headers):
    steam_id = int(steam_id)
    json_inventory = requests.get(f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=5000%22", headers=headers)
    print("Updating Inventory")
    time.sleep(random.uniform(1, 2))
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
            break
    return id



def get_price(id, table, error, headers):
    if id:
        id_url = f"https://steamcommunity.com/market/itemordershistogram?country=PT&language=english&currency=3&item_nameid={id}&two_factor=0" 
        html = requests.get(id_url, headers=headers).json()
        x = random.uniform(2, 3)
        time.sleep(x)
        try:
            #soup = BeautifulSoup(html['sell_order_summary'], 'lxml')
            soup = BeautifulSoup(html['sell_order_table'], 'lxml')
            price_tags = soup.find_all('td', {'align': 'right'})
            price = price_tags[2].text.strip()
            price = price.replace('--','00')
            print(f"Price: {price}")
            table['Sell Price'][table['Case'].index(steam_item_id_dict[id])] = price[:-1]
                
        except:
            error = error + 1
            print("Error")
            x = random.uniform(2, 3)
            get_price(id, table, error, headers)
            if error == 5:
                exit()
        error = 0
    else:
        print("Could not get ID")
        exit()


def abstract_load(name_file):
    try:
        with open(name_file) as f:
            raw = f.read()
        file = json.loads(raw)
        return file
    except:
        f = open(name_file, 'w+') 
        f.write('{}')
        f.close()
        with open(name_file) as f:
            raw = f.read()
        file = json.loads(raw)
        return file

def add_case_to_table(case):
    table['Case'].append(case)
    table['Qt'].append(cases_amount[case])
    table['Buy Price'].append(0.0)
    table['Sell Price'].append(0.0)
    table['Sell Price w tax'].append(0.0)
    table['Profit per Case'].append(0.0)
    table['Profit'].append(0.0)

def get_case_id(case_url, case):
    html = requests.get(case_url[case], headers=headers).text
    time.sleep(random.uniform(1, 2))
    soup = BeautifulSoup(html, 'lxml')
    id = get_id(soup)
    return id


def update_cases(case_url, steam_item_id_dict, table, cases_amount):
    for case in case_url:
        if case not in steam_item_id_dict.values():
            id = get_case_id(case_url,case)
            steam_item_id_dict[id]=case
        if case not in table['Case']:
            add_case_to_table(case)

def update_cases_price(table, buy_prices):
    for case in buy_prices:
        if case in table['Case']:
            table['Buy Price'][table['Case'].index(case)] = buy_prices[case]
    
    for case in table['Case']:
        if case not in buy_prices:
            buy_prices[case] = 0.0
            table['Buy Price'][table['Case'].index(case)] = 0.0

def get_cases_price(steam_item_id_dict, table, error, headers):
    for id in steam_item_id_dict:
        print(f"Request To {steam_item_id_dict[id]}")
        time.sleep(random.uniform(1, 4))
        get_price(id, table,error,headers)
        time.sleep(random.uniform(1, 2))

def compute_table(table):
    df = pd.DataFrame(data=table)
    pd.set_option('mode.chained_assignment', None)
    df["Sell Price"]=df["Sell Price"].str.replace(',','.')

    for x in range(len(df['Case'])):
        df['Sell Price w tax'][x] = float(df['Sell Price'][x]) * 0.85

    for x in range(len(df['Case'])):
        df['Profit per Case'][x] = float(df['Sell Price w tax'][x]) - float(df['Buy Price'][x])

    for x in range(len(df['Case'])):
        df['Profit'][x] = int(df['Qt'][x]) * float(df['Profit per Case'][x])

    return df

def get_steam_id():
    tfile = open('steam_id_file.txt', 'r')
    steam_id = tfile.readline()
    steam_id = steam_id.replace('\n', '')
    tfile.close()
    return steam_id

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


    answer = input('Update Inventory - 1\nNew Player - 2\nJust Get Profit - Other Key\n')
    if answer == "1":
        steam_id = get_steam_id()
        update_inventory(steam_id, headers)

    elif answer == "2":
        print("Please set your buy prices in the \"buy_prices.txt\" file")
        answer2 = input('Enter Steam ID (Number):')
        tfile = open('steam_id_file.txt', 'w')
        tfile.write(answer2)
        tfile.close()

        steam_id = get_steam_id()

        update_inventory(steam_id, headers)
        table['Case']= []
        table['Qt']=[]
        table['Buy Price']=[]
        table['Sell Price']=[]
        table['Sell Price w tax']=[]
        table['Profit per Case']=[]
        table['Profit']=[]
        steam_item_id_dict = {}
    else:
        pass

    steam_id = get_steam_id()

    buy_prices = abstract_load(f'{steam_id}_buy_prices.json')
    inventory = abstract_load('inventory.json')

    cases_filtered = filterCases(inventory)

    cases_amount = getCasesAmmount(inventory,cases_filtered)

    update_cases(case_url, steam_item_id_dict, table, cases_amount)

    update_cases_price(table, buy_prices)

    get_cases_price(steam_item_id_dict, table, error, headers)


    df = compute_table(table)

    with pd.option_context('display.max_rows', None,
                        'display.max_columns', None,
                        'display.precision', 3,
                        ):
        print(df)
        total = df['Profit'].sum()
        print(f"\nYour Profit is {total:.3f}€")

    tfile = open('Report.txt', 'w')
    tfile.write(df.to_string())
    tfile.write(f"\n\nYour Profit is {total:.3f}€")
    tfile.close()

    steam_id = get_steam_id()

    json.dump( buy_prices, open( f"{steam_id}_buy_prices.json", 'w' ) )
    json.dump( table, open( "table_cases.json", 'w' ) )
    json.dump( steam_item_id_dict, open( "steam_item_id_dict.json", 'w' ) )

    answer = input('Send to Merc - 1\nNo - 2\n')
    if answer == "1":
        channel_id = 1092817113795792997
        sendMessage(token, channel_id, message)
    # save it as a new file, the original file is untouched and here I am saving
    # it as xlsm(m here denotes macros).



