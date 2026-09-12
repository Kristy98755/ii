import sys
sys.stdout.reconfigure(encoding='utf-8')
import xlrd, os
from collections import defaultdict

path = r'C:\Users\XAKEP\Downloads\AyuGram Desktop\проба пера\проба пера'
files = [f for f in os.listdir(path) if f.endswith('.xls') and f.startswith('РАС')]

TIME_SLOTS = [('07:40','09:15',1),('10:10','11:45',2),('12:45','14:20',3),('15:15','16:50',4)]
DAYS = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота']

day_slot_groups = defaultdict(lambda: defaultdict(set))

for fname in files:
    full_path = os.path.join(path, fname)
    wb = xlrd.open_workbook(full_path)
    for si in range(wb.nsheets):
        sheet = wb.sheet_by_index(si)
        groups = []
        for col in range(6, sheet.ncols):
            val = sheet.cell_value(6, col)
            if val:
                groups.append((col, str(val).strip()))
        current_day = ''
        for row in range(8, sheet.nrows):
            day_val = sheet.cell_value(row, 0)
            if day_val and str(day_val).strip():
                current_day = str(day_val).strip()
            time_val = sheet.cell_value(row, 1)
            if not time_val:
                continue
            time_str = str(time_val).strip()
            slot_num = 0
            for start, end, num in TIME_SLOTS:
                if start in time_str:
                    slot_num = num
                    break
            for col, group_name in groups:
                cell_val = sheet.cell_value(row, col)
                if cell_val and '21z' in str(cell_val).lower():
                    day_slot_groups[current_day][slot_num].add(group_name)

print('День | Пара | Кол-во групп')
print('-' * 40)
for day in DAYS:
    for slot in range(1, 5):
        if day_slot_groups[day][slot]:
            grs = sorted(day_slot_groups[day][slot])
            print(f'{day:12} | п{slot} | {len(grs)} групп: {grs}')
