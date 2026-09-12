import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Find combined classes: same teacher, same day/slot, same room
combos = defaultdict(list)
for s in d['schedule']:
    key = (s['day'], s['slot'], s['teacher'], s['classroom'])
    combos[key].append(s)

print("=== ОБЪЕДИНЕНИЯ (2 группы у одного препода) ===\n")
for (day, slot, teacher, room), entries in sorted(combos.items()):
    if len(entries) >= 2:
        groups = [e['group'] for e in entries]
        weeks = set()
        for e in entries:
            weeks.update(e['weeks'])
        print(f"{day} п{slot} | {teacher:12} | {room:12} | Группы: {', '.join(groups)} | Недели: {sorted(weeks)}")
