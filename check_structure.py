import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))
print(list(d['schedule'][0].keys()))
print()
print(d['schedule'][0])
