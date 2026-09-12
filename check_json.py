import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Check ИГП1 and ИГП11
for s in d['schedule']:
    g = s.get('group','')
    if g in ['ИГП1','ИГП11']:
        issues = s.get('issues', [])
        print(f"{g:8} | {s['day']:12} | {s.get('time',''):12} | slot={s['slot']} | {s['classroom']:12} | {issues}")

print("\n--- All groups ---")
groups = sorted(set(s['group'] for s in d['schedule']))
for g in groups:
    print(g)
