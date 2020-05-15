import requests
import json
import settings
from datetime import date, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict
if settings.wikipedia_language == "en":
    wikipedia_root = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/{}"
else:
    wikipedia_root = "https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report/{}"


def wiki_format(d1: date, d2: date) -> str:
    if d1.year != d2.year:
        return "{}_to_{}".format(d1.strftime("%B_%-d,_%Y"), d2.strftime("%B_%-d,_%Y"))
    elif d1.month == d2.month:
        return "{}_to_{}".format(d1.strftime("%B_%-d"), d2.strftime("%-d,_%Y"))
    else:
        return "{}_to_{}".format(d1.strftime("%B_%-d"), d2.strftime("%B_%-d,_%Y"))


def to_wiki_week(d: date) -> str:
    current = d
    while current < date.today() - timedelta(days=7):
        yield wiki_format(current, current + timedelta(days=6))
        current = current + timedelta(days=7)


def request_wiki(datestring: str) -> str:
    r = requests.get(wikipedia_root.format(datestring))
    if r.status_code != 200:
        raise requests.exceptions.RequestException(
            "The page you requested does not exist. {}".format(r.url))
    else:
        return r.text


def parse_page(datestring: str) -> List[Dict]:
    soup = BeautifulSoup(request_wiki(datestring), "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    results: List = list()
    for row in table.find_all("tr")[1:]:
        info: Dict = dict()
        cells = row.find_all("td")
        try:
            info["article"] = cells[1].text.strip()
            info["views"] = cells[3].text.strip()
        except IndexError:
            continue
        results.append(info)
    return results


if __name__ == '__main__':
    day_zero = date(2013, 1, 6)
    # day_zero = date(2018, 12, 23)
    datestrings = to_wiki_week(day_zero)
    data: List[Dict] = list()
    while True:
        try:
            datestr: str = next(datestrings)
            info: Dict = parse_page(datestr)
            data.append({datestr: info})
        except requests.exceptions.RequestException as e:
            print("An error occured: {}".format(e))
            continue
        except StopIteration:
            print("Finished the program")
            break
    with open("wiki_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
