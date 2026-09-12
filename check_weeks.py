import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))
for s in d['schedule'][:5]:
    print(f"{s['group']:8} | course: {s['course'][:20]:20} | weeks: {s['weeks']}")
print()
# Check course_weeks
print("course_weeks:")
for k,v in d['course_weeks'].items():
    print(f"  {k}: {v}")
