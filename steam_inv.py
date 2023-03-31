import re
import requests
from bs4 import BeautifulSoup
import random
import time
import openpyxl
import os


###########################################################
# urls to find id of the product

# name_url = ["https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case", 
#             "https://steamcommunity.com/market/listings/730/Prisma%202%20Case",
#             "https://steamcommunity.com/market/listings/730/CS20%20Case",
#             "https://steamcommunity.com/market/listings/730/Falchion%20Case",
#             "https://steamcommunity.com/market/listings/730/Fracture%20Case",
#             "https://steamcommunity.com/market/listings/730/Shadow%20Case",
#             "https://steamcommunity.com/market/listings/730/Horizon%20Case",
#             "https://steamcommunity.com/market/listings/730/Gamma%202%20Case"]

# finds id of the product

# def get_id(s):
#     id = None
#     for script in s.find_all('script'):
#         id_regex = re.search('Market_LoadOrderSpread\(([ 0-9]+)\)', script.text)
#         if id_regex:
#             id = id_regex.groups()[0].strip()
#             print(id)
#             break
#     return id

# use function to get id

#html = requests.get(url, headers=headers).text
#soup = BeautifulSoup(html, 'lxml')
#id = get_id(soup)

###########################################################

headers = {'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
           'Accept-Encoding' : "gzip, deflate, br",
           'Upgrade-Insecure-Requests' : "1",
           'Referer' : 'https://www.google.com/',
           'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0"}

steam_item_id_dict = { 176024744 : "DangerZone Case" , 176118270 : "Prisma 2 Case" , 176091756 : "CSGO 20 Case" , 49359031 : "Falchion Case" , 176185874 : "Fracture Case" , 67060949 : "Shadow Case" , 175999886 : "Horizon Case" , 165027636 : "Gamma 2 Case" }



def get_price(id, sheetname, headers):
    if id:
        id_url = f"https://steamcommunity.com/market/itemordershistogram?country=PT&language=english&currency=3&item_nameid={id}&two_factor=0" 
        html = requests.get(id_url, headers=headers).json()
        x = random.uniform(3, 6)
        time.sleep(x)
        try:
            soup = BeautifulSoup(html['sell_order_summary'], 'lxml')
            price = soup.select_one('span:last-child').text
            print(f"Price: {price}")
            match steam_item_id_dict[id]:
                case "DangerZone Case":
                    sheetname['D2'] = price
                case "Prisma 2 Case":
                    sheetname['D9'] = price
                case "CSGO 20 Case":
                    sheetname['D4'] = price
                case "Falchion Case":
                    sheetname['D7'] = price
                case "Fracture Case":
                    sheetname['D5'] = price
                case "Shadow Case":
                    sheetname['D8'] = price
                case "Horizon Case":
                    sheetname['D3'] = price
                case "Gamma 2 Case":
                    sheetname['D6'] = price
                
        except:
            print("Error")
            x = random.uniform(5, 9)
            get_price(id, sheetname, headers)


    else:
        print("Could not get ID")
        exit()




# to open the excel sheet and if it has macros
print("Opening Excel Sheet")
os.rename("CasesCS.xls" , "CasesCS.xlsx")
srcfile = openpyxl.load_workbook('CasesCS.xlsx', read_only=False, keep_vba=True)

# get sheetname from the file
sheetname = srcfile['Folha1']

for id in steam_item_id_dict:
    print(f"Request To {steam_item_id_dict[id]}")
    x = random.uniform(5, 13)
    time.sleep(x)
    get_price(id, sheetname, headers)
    x = random.uniform(10, 15)
    time.sleep(x)


# save it as a new file, the original file is untouched and here I am saving
# it as xlsm(m here denotes macros).
srcfile.save('CasesCS.xlsx')
print("Excel Sheet Saved")

srcfile = openpyxl.load_workbook('CasesCS.xlsx', read_only=False, keep_vba=True)
sheetname = srcfile['Folha1']
print(f"Your Money in Cases: {sheetname['G10'].value}")
srcfile.close()
os.rename("CasesCS.xlsx" , "CasesCS.xls")
