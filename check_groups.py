import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Check all entries for groups involved
groups = ['ИГВ29', 'ИГВ30', 'ИГП8']
for g in groups:
    print(f"\n=== {g} ===")
    for s in d['schedule']:
        if s['group'] == g:
            print(f"  {s['day']:12} п{s['slot']} | {s['teacher']:12} | {s['classroom']:12} | КП: {sorted(s['weeks'])}")
