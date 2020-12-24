import json


names = ["Алика", "Лиза", "Даша", "Даша", "Полина", "Лиза", "Саша", "Катя", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
surnames = ["Станкевич", "Дианова", "Васильева", "Сушинская", "Марчукевич", "Арташкевич", "Кордик", "Масалова", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
data = {}
i = 0
for name, surname in zip(names, surnames):
   data[str(i)]["name"] = name
   data[str(i)]["surname"] = surname
   data[str(i)]["rating"] = 1400
   i += 1

# for i in range(amount_d):
#     base[str(i)] = {"name": "Имя", "surname": "Фамилия", "rating": 1400}


with open("models.json", "w", encoding="UTF-8") as database:
    json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))
