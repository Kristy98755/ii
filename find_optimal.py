import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

# Teacher constraints from docx
TEACHER_CONSTRAINTS = {
    'Акбалаева': {
        'preferred_days': ['Вторник', 'Суббота'],
        'max_time': '12:00',  # other days only until 12:00
        'role': 'lectures',
        'hours': 345
    },
    'Туратбек к': {
        'preferred_days': [],  # any day
        'time_window': ('10:00', '15:00'),
        'classroom': 'НГ',
        'hours': 275
    },
    'Ысламов': {
        'preferred_days': ['Понедельник', 'Среда', 'Пятница'],
        'hours': 170
    },
    'Полотова': {
        'preferred_days': ['Понедельник', 'Среда', 'Пятница'],
        'max_pairs_per_day': 1,  # Mon/Wed/Fri max 1 pair
        'time_window_other': ('10:00', None),  # Tue/Thu after 10:00
        'sat_max': '12:00',
        'hours': 275
    },
    'Маманова': {
        'max_time': '14:00',
        'hours': 340
    },
    'Апазбекова': {
        'preferred_days': ['Вторник', 'Четверг', 'Суббота'],
        'hours': 170
    }
}

SLOT_TIMES = {
    1: ('07:40', '09:15'),
    2: ('09:25', '11:00'),
    3: ('11:10', '12:45'),
    4: ('13:30', '15:05'),
}

def can_teach(teacher, day, slot):
    """Check if a teacher can teach on this day/slot."""
    c = TEACHER_CONSTRAINTS[teacher]
    start, end = SLOT_TIMES[slot]
    
    # Ысламов: only Mon/Wed/Fri
    if teacher == 'Ысламов' and day not in ['Понедельник', 'Среда', 'Пятница']:
        return False
    
    # Апазбекова: only Tue/Thu/Sat
    if teacher == 'Апазбекова' and day not in ['Вторник', 'Четверг', 'Суббота']:
        return False
    
    # Туратбек к: only 10:00-15:00
    if teacher == 'Туратбек к' and (start < '10:00' or start >= '15:00'):
        return False
    
    # Полотова: Mon/Wed/Fri only 1 pair; Tue/Thu after 10:00; Sat until 12:00
    if teacher == 'Полотова':
        if day in ['Понедельник', 'Среда', 'Пятница']:
            pass  # max 1 pair constraint checked elsewhere
        elif day in ['Вторник', 'Четверг']:
            if start < '10:00':
                return False
        elif day == 'Суббота':
            if start >= '12:00':
                return False
    
    # Акбалаева: preferred Tue/Sat; other days only until 12:00
    if teacher == 'Акбалаева':
        if day not in ['Вторник', 'Суббота']:
            if start >= '12:00':
                return False
    
    # Маманова: until 14:00
    if teacher == 'Маманова':
        if start >= '14:00':
            return False
    
    return True

def main():
    d = json.load(open(r'C:\Users\XAKEP\Downloads\ii\schedule_data.json', encoding='utf-8'))
    
    # Build group data
    group_data = {}
    for s in d['schedule']:
        g = s['group']
        if g not in group_data:
            group_data[g] = {
                'weeks': set(s['weeks']),
                'day': s['day'],
                'slot': s['slot'],
                'classroom': s['classroom'],
                'teacher': s['teacher'],
                'course': s['course'],
                'issues': s.get('issues', [])
            }
    
    # Find pairs with same day/slot and matching КП
    print("=== ВОЗМОЖНЫЕ ОБЪЕДИНЕНИЯ ===\n")
    
    slot_groups = defaultdict(list)
    for g, data in group_data.items():
        key = (data['day'], data['slot'])
        slot_groups[key].append((g, data))
    
    combinations = []
    
    for (day, slot), groups in sorted(slot_groups.items()):
        if len(groups) < 2:
            continue
        
        # Check all pairs
        for i in range(len(groups)):
            for j in range(i+1, len(groups)):
                g1, d1 = groups[i]
                g2, d2 = groups[j]
                
                # Check КП match
                if d1['weeks'] != d2['weeks']:
                    continue
                
                # Can we assign the same teacher?
                current_t1 = d1['teacher']
                current_t2 = d2['teacher']
                
                if current_t1 == current_t2:
                    # Already same teacher - just need to check room
                    print(f"УЖЕ ОБЪЕДИНЕНЫ: {g1} + {g2} ({current_t1}) на {day} п{slot}")
                    continue
                
                # Try assigning d1's teacher to g2
                if can_teach(current_t1, day, slot):
                    # Check if g1 and g2 are in different rooms
                    if d1['classroom'] != d2['classroom']:
                        # Need to move g2 to g1's room
                        print(f"{g1} ({current_t1}, {d1['classroom']}) + {g2} ({current_t2}→{current_t1}, {d2['classroom']}→{d1['classroom']}) | {day} п{slot} | КП: {sorted(d1['weeks'])}")
                        combinations.append({
                            'groups': [g1, g2],
                            'teacher': current_t1,
                            'room': d1['classroom'],
                            'day': day,
                            'slot': slot,
                            'weeks': sorted(d1['weeks'])
                        })
                    else:
                        print(f"УЖЕ В ОДНОЙ КОМНАТЕ: {g1} + {g2} ({current_t1}) | {day} п{slot}")
                
                # Try assigning d2's teacher to g1
                elif can_teach(current_t2, day, slot):
                    if d1['classroom'] != d2['classroom']:
                        print(f"{g1} ({current_t1}→{current_t2}, {d1['classroom']}→{d2['classroom']}) + {g2} ({current_t2}, {d2['classroom']}) | {day} п{slot} | КП: {sorted(d1['weeks'])}")
                        combinations.append({
                            'groups': [g1, g2],
                            'teacher': current_t2,
                            'room': d2['classroom'],
                            'day': day,
                            'slot': slot,
                            'weeks': sorted(d1['weeks'])
                        })
    
    print(f"\nВсего вариантов объединения: {len(combinations)}")
    
    # Check which combinations would fix the >3 classrooms issue
    print("\n=== КОМБИНАЦИИ, РЕШАЮЩИЕ ПРОБЛЕМУ >3 АУДИТОРИЙ ===\n")
    problem_slots = [('Вторник', 1), ('Среда', 2)]
    for (day, slot) in problem_slots:
        print(f"{day} п{slot}:")
        for c in combinations:
            if c['day'] == day and c['slot'] == slot:
                print(f"  Объединить {c['groups']} → {c['teacher']} в {c['room']}")
        print()

if __name__ == '__main__':
    main()
