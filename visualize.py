import json


with open("wiki_data.json", "r") as f:
    raw_data = json.load(f, encoding="utf-8")

if __name__ == '__main__':
    print(raw_data)
