import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Group course_weeks by tuple of weeks
kp_map = defaultdict(list)
for course, weeks in d['course_weeks'].items():
    key = tuple(sorted(weeks))
    kp_map[key].append(course)

print("=== КП по группам ===\n")
for weeks, courses in sorted(kp_map.items()):
    print(f"Недели {list(weeks)}:")
    for c in courses:
        # Find groups in this course
        groups = [g for g, crs in d['group_course'].items() if crs == c]
        print(f"  {c}: {', '.join(sorted(groups))}")
    print()

# Check per-group КП from raw data
print("\n=== Детали по КП (из extract_data) ===\n")
# Re-read from schedule entries
group_weeks = defaultdict(set)
for s in d['schedule']:
    g = s['group']
    kp = s.get('kp_weeks')
    if kp:
        for w in kp:
            group_weeks[g].add(w)

# Group by identical week sets
wk_groups = defaultdict(list)
for g, weeks in group_weeks.items():
    wk_groups[tuple(sorted(weeks))].append(g)

print("Группы с одинаковым КП:\n")
for weeks, groups in sorted(wk_groups.items(), key=lambda x: (-len(x[1]), x[0])):
    print(f"  Недели {list(weeks)}: {', '.join(sorted(groups))}")
