import sys
import os
import json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

import xlrd

path = r'C:\Users\XAKEP\Downloads\AyuGram Desktop\проба пера\проба пера'
output_json = r'C:\Users\XAKEP\Downloads\ii\schedule_data.json'

DAYS = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота']
TIME_SLOTS = [('07:40','09:15',1),('10:10','11:45',2),('12:45','14:20',3),('15:15','16:50',4)]
WEEK_DATES = {
    1:('01.09','06.09'),2:('07.09','13.09'),3:('14.09','20.09'),4:('21.09','27.09'),
    5:('28.09','04.10'),6:('05.10','11.10'),7:('12.10','18.10'),8:('19.10','25.10'),
    9:('26.10','01.11'),10:('02.11','08.11'),11:('09.11','15.11'),12:('16.11','22.11'),
    13:('23.11','29.11'),14:('30.11','06.12'),15:('07.12','13.12'),16:('14.12','20.12'),
}

TEACHERS = [
    {'name':'Акбалаева','preferred_days':['Вторник','Суббота'],'max_time_other_days':'12:00','can_teach_21z':True},
    {'name':'Туратбек к','preferred_days':[],'min_time':'10:00','max_time':'15:00','can_teach_21z':True},
    {'name':'Ысламов','preferred_days':['Понедельник','Среда','Пятница'],'can_teach_21z':True},
    {'name':'Полотова','preferred_days':[],'min_time_tt':'10:00','max_time_sat':'12:00','can_teach_21z':True},
    {'name':'Маманова','max_time':'14:00','can_teach_21z':True},
    {'name':'Апазбекова','preferred_days':['Вторник','Четверг','Суббота'],'can_teach_21z':True},
]
CLASSROOMS = ['Ук104','Ук105','Ук108','Ук109','Ук.313']

def time_to_min(t):
    h,m = map(int,t.split(':'))
    return h*60+m

def can_teach(t, day, slot):
    if t.get('preferred_days') and day not in t['preferred_days']: return False
    s = TIME_SLOTS[slot-1][0]
    if t.get('min_time') and time_to_min(s) < time_to_min(t['min_time']): return False
    if t.get('max_time') and time_to_min(s) >= time_to_min(t['max_time']): return False
    if t.get('max_time_other_days') and day not in t.get('preferred_days',[]):
        if time_to_min(s) >= time_to_min(t['max_time_other_days']): return False
    if t.get('max_time_sat') and day=='Суббота':
        if time_to_min(s) >= time_to_min(t['max_time_sat']): return False
    if t.get('min_time_tt') and day in ['Вторник','Четверг']:
        if time_to_min(s) < time_to_min(t['min_time_tt']): return False
    return True

def parse_kp_weeks():
    files = [f for f in os.listdir(path) if f.endswith('.xls') and f.startswith('КП')]
    cw = {}
    for fname in files:
        wb = xlrd.open_workbook(os.path.join(path,fname))
        parts = fname.replace('.xls','').replace('КП','').strip().split()
        key = f"{parts[0]}_{parts[1]}к" if len(parts)>=2 else fname
        sh = wb.sheet_by_index(0)
        for r in range(sh.nrows):
            code = str(sh.cell_value(r,2)).strip() if sh.cell_value(r,2) else ''
            if '21z' in code:
                wks = [c-3 for c in range(4,20) if sh.cell_value(r,c)]
                if key not in cw: cw[key]=set()
                cw[key].update(wks)
    return {k:sorted(list(v)) for k,v in cw.items()}

def parse_ras():
    files = [f for f in os.listdir(path) if f.endswith('.xls') and f.startswith('РАС')]
    entries = []
    for fname in files:
        wb = xlrd.open_workbook(os.path.join(path,fname))
        cn = fname.replace('.xls','').replace('РАС','').strip()
        for si in range(wb.nsheets):
            sh = wb.sheet_by_index(si)
            grps = [(c,str(sh.cell_value(6,c)).strip()) for c in range(6,sh.ncols) if sh.cell_value(6,c)]
            cd = ''
            for r in range(8,sh.nrows):
                dv = sh.cell_value(r,0)
                if dv and str(dv).strip(): cd = str(dv).strip()
                tv = sh.cell_value(r,1)
                if not tv: continue
                ts = str(tv).strip()
                sn = next((n for s,e,n in TIME_SLOTS if s in ts),0)
                for c,gn in grps:
                    cv = sh.cell_value(r,c)
                    if cv and '21z' in str(cv).lower():
                        cs = str(cv)
                        room = ''
                        if 'Ук' in cs:
                            p=cs.find('Ук'); e=cs.find(';',p)
                            room=cs[p:e if e>0 else len(cs)].strip()
                        elif 'Лз' in cs or 'лз' in cs: room='Лз-РДЛЦ'
                        elif 'ЗБВ' in cs: room='ЗБВ'
                        entries.append({'day':cd,'time':ts,'slot':sn,'group':gn,'classroom':room,'course':cn})
    return entries

def main():
    kp_weeks = parse_kp_weeks()
    raw = parse_ras()

    group_course = {}
    for e in raw:
        if e['group'] not in group_course:
            group_course[e['group']] = e['course']

    # Attach weeks to each entry
    for e in raw:
        for k,w in kp_weeks.items():
            if k.split('_')[0] in e['course']:
                e['weeks'] = w; break
        else:
            e['weeks'] = list(range(1,17))

    # Available teachers per (day, slot)
    avail = {}
    for d in DAYS:
        for s in range(1,5):
            avail[(d,s)] = [t['name'] for t in TEACHERS if t['can_teach_21z'] and can_teach(t,d,s)]

    # ============================================================
    # Check 1: classroom conflicts per (day, slot, week)
    # Two groups in same room at same time = conflict UNLESS КП matches
    # ============================================================
    # Group by (day, slot, week)
    week_slot_entries = defaultdict(lambda: defaultdict(list))
    for e in raw:
        for w in e['weeks']:
            week_slot_entries[w][(e['day'],e['slot'])].append(e)

    # For each entry, track issues
    for e in raw:
        e['issues'] = []

    for week_num, slots in week_slot_entries.items():
        for (day,slot), entries in slots.items():
            # Check classroom conflicts
            room_groups = defaultdict(list)
            for e in entries:
                if e['classroom']:
                    room_groups[e['classroom']].append(e)

            for room, groups in room_groups.items():
                if len(groups) > 1:
                    # Multiple groups in same room - check if КП matches
                    # КП matches = same weeks
                    week_sets = [set(g['weeks']) for g in groups]
                    all_match = all(ws == week_sets[0] for ws in week_sets)

                    if not all_match:
                        # КП doesn't match - conflict for ALL groups in this room
                        group_names = [g['group'] for g in groups]
                        for g in groups:
                            g['issues'].append({
                                'weeks': [week_num],
                                'reason': f'Конфликт аудитории: {room} занята группами {", ".join(group_names)} с разным КП'
                            })
                    # If КП matches - OK, they can share (combined class)

            # Check >3 classrooms
            unique_rooms = set(e['classroom'] for e in entries if e['classroom'])
            if len(unique_rooms) > 3:
                for e in entries:
                    e['issues'].append({
                        'weeks': [week_num],
                        'reason': f'Более 3 аудиторий одновременно ({len(unique_rooms)}: {", ".join(sorted(unique_rooms))})'
                    })

    # ============================================================
    # Check 2: assign teachers, no teacher in two places same week
    # ============================================================
    entry_week_teacher = defaultdict(dict)  # id(e) -> {week: teacher}

    for week_num, slots in week_slot_entries.items():
        for (day,slot), entries in slots.items():
            available = avail[(day,slot)]

            # Check which groups can share a teacher (same room, КП matches)
            # Group by room
            room_groups = defaultdict(list)
            for e in entries:
                room_groups[e['classroom']].append(e)

            # Build "teaching units": either single group or combined
            units = []
            assigned_rooms = set()
            for room, groups in room_groups.items():
                if len(groups) > 1:
                    week_sets = [set(g['weeks']) for g in groups]
                    all_match = all(ws == week_sets[0] for ws in week_sets)
                    if all_match and len(groups) <= 2:
                        # Can combine - one teacher for both
                        units.append({'groups': groups, 'combined': True, 'room': room})
                        assigned_rooms.add(room)
                    else:
                        for g in groups:
                            units.append({'groups': [g], 'combined': False, 'room': room})
                else:
                    units.append({'groups': groups, 'combined': False, 'room': room})

            # Assign teachers to units
            used = set()
            for unit in units:
                for tname in available:
                    if tname not in used:
                        for g in unit['groups']:
                            entry_week_teacher[id(g)][week_num] = tname
                        used.add(tname)
                        break

    # Merge teacher assignments
    for e in raw:
        eid = id(e)
        week_teachers = entry_week_teacher.get(eid, {})
        teacher_count = defaultdict(int)
        for w,t in week_teachers.items():
            teacher_count[t] += 1
        if teacher_count:
            e['teacher'] = max(teacher_count, key=teacher_count.get)
        else:
            e['teacher'] = avail[(e['day'],e['slot'])][0] if avail[(e['day'],e['slot'])] else 'Не назначен'

        # Check teacher conflicts
        unassigned_weeks = [w for w in e['weeks'] if w not in week_teachers]
        if unassigned_weeks:
            e['issues'].append({
                'weeks': unassigned_weeks,
                'reason': f'Нет преподавателя на {e["day"]} п{e["slot"]} (нед. {", ".join(map(str,unassigned_weeks))})'
            })

    # Deduplicate issues
    for e in raw:
        merged = {}
        for iss in e['issues']:
            key = iss['reason']
            if key not in merged:
                merged[key] = {'weeks': set(), 'reason': iss['reason']}
            merged[key]['weeks'].update(iss['weeks'])
        e['issues'] = [{'weeks':sorted(list(v['weeks'])),'reason':v['reason']} for v in merged.values()]

    # Stats
    print("=== НАЗНАЧЕНИЯ ===")
    ts = defaultdict(lambda:{'h':0,'d':set(),'g':set()})
    for e in raw:
        t=e['teacher']
        ts[t]['h']+=1.5; ts[t]['d'].add(e['day']); ts[t]['g'].add(e['group'])
    for tn,s in sorted(ts.items(),key=lambda x:-x[1]['h']):
        ds=', '.join(sorted(s['d'],key=lambda d:DAYS.index(d)))
        print(f"  {tn}: {s['h']:.1f}ч | {len(s['d'])} дн | {len(s['g'])} групп")

    flagged=[e for e in raw if e['issues']]
    print(f"\n=== ПОМЕТКИ: {len(flagged)} из {len(raw)} ===")
    for e in flagged:
        print(f"  {e['group']:8} | {e['day']:12} п{e['slot']} | {e['classroom']:16} | {e['teacher']}")
        for i in e['issues']:
            print(f"    → {i['reason']}")

    data = {
        'meta': {'semester':'Осений 2026/2027','department':'Кафедра лучевой диагностики','weeks':16,
                 'week_dates':{str(k):{'start':v[0],'end':v[1]} for k,v in WEEK_DATES.items()},
                 'sem_start':'01.09.2026','sem_end':'20.12.2026'},
        'teachers':TEACHERS,'classrooms':CLASSROOMS,'days':DAYS,
        'time_slots':[{'start':t[0],'end':t[1],'num':t[2]} for t in TIME_SLOTS],
        'course_weeks':kp_weeks,'group_course':group_course,'schedule':raw,
    }
    with open(output_json,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    print(f"\nJSON: {output_json}")

if __name__=='__main__':
    main()
