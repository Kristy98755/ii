import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

print("=== 1. ПРОВЕРКА: одна группа — один преподаватель в неделю ===\n")

# Group by (group, week) → set of teachers
gw_teachers = defaultdict(lambda: defaultdict(set))
for s in d['schedule']:
    g = s['group']
    t = s['teacher']
    for w in s['weeks']:
        gw_teachers[g][w].add(t)

issues1 = []
for g, weeks in sorted(gw_teachers.items()):
    for w, teachers in sorted(weeks.items()):
        if len(teachers) > 1:
            issues1.append((g, w, teachers))

if issues1:
    print(f"Найдено {len(issues1)} расхождений:")
    for g, w, teachers in issues1:
        print(f"  {g} нед.{w}: {', '.join(sorted(teachers))}")
else:
    print("Все ок — у каждой группы один преподаватель в неделю")

print("\n=== 2. ПРОВЕРКА: не более 2 групп на одно занятие ===\n")

# Group by (day, slot, week, teacher) → list of groups
stwg_groups = defaultdict(list)
for s in d['schedule']:
    g = s['group']
    t = s['teacher']
    day = s['day']
    slot = s['slot']
    for w in s['weeks']:
        stwg_groups[(day, slot, w, t)].append(g)

# Group by (day, slot, week, classroom) → list of groups
swcg_groups = defaultdict(list)
for s in d['schedule']:
    g = s['group']
    room = s['classroom']
    day = s['day']
    slot = s['slot']
    for w in s['weeks']:
        swcg_groups[(day, slot, w, room)].append(g)

issues2a = []
for key, groups in stwg_groups.items():
    day, slot, w, t = key
    if len(groups) > 2:
        issues2a.append((day, slot, w, t, groups))

issues2b = []
for key, groups in swcg_groups.items():
    day, slot, w, room = key
    if len(groups) > 2:
        issues2b.append((day, slot, w, room, groups))

if issues2a:
    print(f"Преподаватель: {len(issues2a)} нарушений (>2 групп):")
    for day, slot, w, t, groups in issues2a:
        print(f"  {day} п{slot} нед.{w} | {t}: {', '.join(sorted(groups))}")
else:
    print("Преподаватель: все ок (≤2 групп)")

if issues2b:
    print(f"\nАудитория: {len(issues2b)} нарушений (>2 групп):")
    for day, slot, w, room, groups in issues2b:
        print(f"  {day} п{slot} нед.{w} | {room}: {', '.join(sorted(groups))}")
else:
    print("\nАудитория: все ок (≤2 групп)")
