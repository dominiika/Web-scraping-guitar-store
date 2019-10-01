import requests
import pandas
from bs4 import BeautifulSoup
import re
from datetime import datetime

r = requests.get("https://www.thomann.de/pl/7_strunowe.html?ls=25")
c = r.content
soup = BeautifulSoup(c, "html.parser")

# FIRST PAGE
all_content = soup.find_all("div", {"class": "extensible-article list-view compare parent"})

l = []
for item in all_content:
    d = dict()
    d["Manufacturer"] = item.find("span", {"class": "manufacturer"}).text
    d["Model"] = item.find("span", {"class": "model"}).text
    d["Price in EUR"] = item.find("span", {"class": "article-basketlink"}).text
    d["Price in PLN"] = item.find("div", {"class": "secondary"}).text
    avail = item.find("span", {"class": "rs-layover-trigger-text"}).text
    if "Artykuł dostępny w magazynie" in avail:
        d["Available in stock"] = "Yes"
    else:
        d["Available in stock"] = "No"

    for key in d:
        d[key] = re.sub(r'zł', "", d[key])
        d[key] = re.sub(r'€', "", d[key])
        d[key] = re.sub(r',', ".", d[key])

        # DON'T HACK ME
        d[key] = re.sub(r'[\'\"\/\\*#=%<>]', "", d[key])

    l.append(d)

# FIND THE NUMBER OF PAGES
page_no = soup.find_all("div", {"class": "page"})[-1].text

base_url1 = "https://www.thomann.de/pl/7_strunowe.html?"
base_url2 = "ls=25"

# ALL THE OTHER PAGES
l2 = []
for page in range(2, int(page_no)+1):
    url = base_url1+"pg="+str(page)+"&"+base_url2
    # print(url)
    r = requests.get(url)
    c = r.content
    soup = BeautifulSoup(c, "html.parser")
    all_content = soup.find_all("div", {"class": "extensible-article list-view compare parent"})

    for item in all_content:
        d = dict()
        d["Manufacturer"] = item.find("span", {"class": "manufacturer"}).text
        d["Model"] = item.find("span", {"class": "model"}).text
        d["Price in EUR"] = item.find("span", {"class": "article-basketlink"}).text
        d["Price in PLN"] = item.find("div", {"class": "secondary"}).text
        avail = item.find("span", {"class": "rs-layover-trigger-text"}).text
        if "Artykuł dostępny w magazynie" in avail:
            d["Available in stock"] = "Yes"
        else:
            d["Available in stock"] = "No"

        for key in d:
            d[key] = re.sub(r'zł', "", d[key])
            d[key] = re.sub(r'€', "", d[key])
            d[key] = re.sub(r',', ".", d[key])

            # DON'T HACK ME
            d[key] = re.sub(r'[\'\"\/\\*#=%<>]', "", d[key])

        l2.append(d)

l += l2

df = pandas.DataFrame(l)
df.index = range(1, len(l)+1)
now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
df.to_csv("Guitars_" + now + ".csv")
