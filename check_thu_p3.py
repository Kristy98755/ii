import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))
for s in d['schedule']:
    if s['day'] == 'Четверг' and s['slot'] == 3:
        print(f"{s['group']:8} | {s['teacher']:12} | {s['classroom']:12} | КП: {sorted(s['weeks'])}")
