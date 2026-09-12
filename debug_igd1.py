import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))

# Show all entries for ИГД-1
print("=== Все записи ИГД-1 ===\n")
for s in d['schedule']:
    if s['group'] == 'ИГД-1':
        print(f"{s['day']:12} п{s['slot']} | {s['classroom']:12} | {s['teacher']:12} | КП: {sorted(s['weeks'])}")

# Show all entries for Акбалаева on Вт п1
print("\n=== Всё у Акбалаевой Вт п1 ===\n")
for s in d['schedule']:
    if s['teacher'] == 'Акбалаева' and s['day'] == 'Вторник' and s['slot'] == 1:
        print(f"{s['group']:8} | {s['classroom']:12} | КП: {sorted(s['weeks'])}")

# Show all entries for Ысламов
print("\n=== Всё у Ысламова ===\n")
for s in d['schedule']:
    if s['teacher'] == 'Ысламов':
        print(f"{s['group']:8} | {s['day']:12} п{s['slot']} | {s['classroom']:12} | КП: {sorted(s['weeks'])}")
