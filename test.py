import json


amount_d = 2
base = {}

for i in range(amount_d):
    base[str(i)] = {"name": "Имя", "surname": "Фамилия", "rating": 1400}


with open("models.json", "w", encoding="UTF-8") as database:
    json.dump(base, database, indent=1, ensure_ascii=False, separators=(',', ':'))
