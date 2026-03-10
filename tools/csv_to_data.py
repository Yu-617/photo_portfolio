import csv, json, os
from pathlib import Path

ROOT = Path('.')  # run from project root (where content/ と data/ がある)
CONTENT_GALLERY = ROOT / 'content' / 'gallery'
OUT_DIR = ROOT / 'data' / 'albums'
OUT_DIR.mkdir(parents=True, exist_ok=True)

for dirpath, dirs, files in os.walk(CONTENT_GALLERY):
    dirp = Path(dirpath)
    if 'album.csv' in files:
        rel = dirp.relative_to(CONTENT_GALLERY)  # may be '.'
        slug = str(rel).replace(os.sep, '__') if str(rel) != '.' else 'root'
        mapping = {}
        csvpath = dirp / 'album.csv'
        with open(csvpath, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row.get('filename') or row.get('file') or row.get('name')
                if not fname:
                    continue
                weight = row.get('weight', '').strip()
                try:
                    weight = int(weight) if weight != '' else None
                except:
                    weight = None
                comment = row.get('comment', '').strip() or None
                mapping[fname] = {'weight': weight, 'comment': comment}
        out = OUT_DIR / f'{slug}.json'
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print('Wrote', out)