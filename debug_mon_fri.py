import sys
sys.stdout.reconfigure(encoding='utf-8')
import xlrd, os

path = r'C:\Users\XAKEP\Downloads\AyuGram Desktop\проба пера\проба пера'
files = [f for f in os.listdir(path) if f.endswith('.xls') and f.startswith('РАС')]

print("=== ПОНЕДЕЛЬНИК 1-я пара (07:40) — все ячейки с 21z ===\n")
for fname in files:
    wb = xlrd.open_workbook(os.path.join(path,fname))
    cn = fname[:40]
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
            if '07:40' not in ts: continue
            if cd != 'Понедельник': continue
            for c,gn in grps:
                cv = sh.cell_value(r,c)
                if cv and '21z' in str(cv).lower():
                    print(f'  [{cn}]  {gn:8}  →  {str(cv)[:60]}')

print("\n=== ПЯТНИЦА 1-я пара (07:40) — все ячейки с 21z ===\n")
for fname in files:
    wb = xlrd.open_workbook(os.path.join(path,fname))
    cn = fname[:40]
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
            if '07:40' not in ts: continue
            if cd != 'Пятница': continue
            for c,gn in grps:
                cv = sh.cell_value(r,c)
                if cv and '21z' in str(cv).lower():
                    print(f'  [{cn}]  {gn:8}  →  {str(cv)[:60]}')
