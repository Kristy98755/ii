import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Each group has КП weeks from the schedule
group_weeks = {}
for s in d['schedule']:
    g = s['group']
    if g not in group_weeks:
        group_weeks[g] = set(s['weeks'])

# Group by identical week sets
wk_groups = defaultdict(list)
for g, weeks in sorted(group_weeks.items()):
    wk_groups[tuple(sorted(weeks))].append(g)

print("=== Группы с одинаковым КП ===\n")
for weeks, groups in sorted(wk_groups.items(), key=lambda x: (-len(x[1]), x[0])):
    print(f"Недели {list(weeks)} ({len(groups)} групп):")
    for g in sorted(groups):
        crs = d['group_course'].get(g, '?')
        print(f"  {g:8} ({crs})")
    print()

# Now check which pairs share the same day/slot (can be combined)
print("=== Возможные объединения (один день + слот + КП) ===\n")
slot_groups = defaultdict(list)
for s in d['schedule']:
    if not s.get('issues'):
        key = (s['day'], s['slot'], tuple(sorted(group_weeks.get(s['group'], set()))))
        slot_groups[key].append(s)

for key, entries in sorted(slot_groups.items()):
    day, slot, weeks = key
    groups = [e['group'] for e in entries]
    if len(groups) > 1:
        print(f"{day} п{slot} | Недели {list(weeks)}:")
        for e in entries:
            print(f"  {e['group']:8} → {e['classroom']} ({e['teacher']})")
        print()
