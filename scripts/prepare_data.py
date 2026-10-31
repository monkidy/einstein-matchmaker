"""Freeze official v2 bytes and build a local, reproducible FTS5 evidence index."""
import hashlib
import json
import pathlib
import re
import sqlite3
import urllib.request
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
REVISION = '4fb99b3749adf0d10b5977089ff4c73f4f522240'
FILES = ['data/researchers.json', 'data/companies.json', 'data/projects.json', 'data/patents.json',
         'data/publications.jsonl', 'data/company-pages.jsonl', 'README.md', 'docs/example-industrial-phd-topic.md']
BASE = f'https://raw.githubusercontent.com/jigjoy-ai/einstein-matchmaker-data/{REVISION}/'

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def normalize(text):
    # Search normalisation only. Quotes and identities always retain original bytes.
    table = str.maketrans(dict(zip('абвгдђежзијклљмнњопрстћуфхцчџш',
        ['a','b','v','g','d','dj','e','zh','z','i','j','k','l','lj','m','n','nj','o','p','r','s','t','c','u','f','h','c','c','dz','s'])))
    text = text.lower().translate(table)
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

def main():
    lockpath = ROOT / 'corpus.lock.json'
    previous = json.loads(lockpath.read_text()) if lockpath.exists() else None
    hashes = {}
    for name in FILES:
        path = ROOT / 'corpus' / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urllib.request.urlopen(BASE + name, timeout=60).read())
        raw = path.read_bytes().replace(b'\r\n', b'\n')
        digest = hashlib.sha256(raw).hexdigest()
        if previous and previous['files'][name]['sha256_lf'] != digest:
            raise RuntimeError('CORPUS_CHANGED: ' + name)
        hashes[name] = {'sha256_lf': digest, 'bytes_lf': len(raw)}
    lock = {'repository': 'https://github.com/jigjoy-ai/einstein-matchmaker-data', 'revision': REVISION,
            'fictional': True, 'files': hashes}
    if not previous:
        lockpath.write_text(json.dumps(lock, indent=2) + '\n')
    cache = ROOT / 'cache'
    cache.mkdir(exist_ok=True)
    dbfile = cache / 'evidence.sqlite'
    if dbfile.exists(): dbfile.unlink()
    db = sqlite3.connect(dbfile)
    db.executescript('''
    PRAGMA journal_mode=OFF;
    CREATE TABLE sources(id TEXT PRIMARY KEY, kind TEXT, record TEXT, body TEXT, file TEXT, locator TEXT, line INT, sha256 TEXT, url TEXT);
    CREATE TABLE links(source_id TEXT, researcher_id TEXT, PRIMARY KEY(source_id,researcher_id));
    CREATE INDEX links_researcher ON links(researcher_id);
    CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED, text, tokenize='unicode61 remove_diacritics 2');
    CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT);
    ''')
    counts = {}
    def add(key, kind, record, file, locator, line=None, researchers=()):
        body = canonical(record)
        url = f'https://github.com/jigjoy-ai/einstein-matchmaker-data/blob/{REVISION}/{file}' + (f'#L{line}' if line else '')
        db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',
                   (key, kind, body, body, file, locator, line, hashlib.sha256(body.encode()).hexdigest(), url))
        # Keep identifiers and noisy administrative metadata out of ranking text.
        fields = ['title','name','fields','keywords','bio','abstract','summary','text','detail','open_to','about','sector','tech']
        searchtext = ' '.join(str(record[k]) for k in fields if k in record)
        db.execute('INSERT INTO search(id,text) VALUES(?,?)', (key, normalize(searchtext)))
        for rid in set(researchers):
            if rid: db.execute('INSERT INTO links VALUES(?,?)', (key, rid))
        counts[kind] = counts.get(kind, 0) + 1
    data = ROOT / 'corpus/data'
    for group, singular in [('researchers','researcher'),('projects','project'),('patents','patent')]:
        items = json.loads((data / f'{group}.json').read_text(encoding='utf-8'))[group]
        for n, record in enumerate(items):
            people = [record['id']] if singular == 'researcher' else [x.get('researcher_id') for x in record.get('participants' if singular == 'project' else 'inventors', [])]
            add(record['id'], singular, record, f'data/{group}.json', f'/{group}/{n}', researchers=people)
    companies = json.loads((data / 'companies.json').read_text(encoding='utf-8'))['companies']
    for n, company in enumerate(companies):
        add(company['id'], 'company', company, 'data/companies.json', f'/companies/{n}')
        for j, challenge in enumerate(company['challenges']):
            add(challenge['id'], 'challenge', {**challenge, 'company_id': company['id']}, 'data/companies.json', f'/companies/{n}/challenges/{j}')
    for name, kind in [('publications','publication'),('company-pages','company_page')]:
        for n, line in enumerate((data / f'{name}.jsonl').read_text(encoding='utf-8').splitlines(), 1):
            record = json.loads(line)
            key = record['id'] if kind == 'publication' else f'{record["company_id"]}-PAGE-L{n}'
            people = [x.get('researcher_id') for x in record.get('authors', [])]
            add(key, kind, record, f'data/{name}.jsonl', '/', n, people)
    corpus_digest = hashlib.sha256(canonical(lock).encode()).hexdigest()
    db.execute('INSERT INTO metadata VALUES(?,?)', ('corpus_sha256', corpus_digest))
    db.commit()
    print(json.dumps({'corpus_sha256': corpus_digest, 'counts': counts, 'index_bytes': dbfile.stat().st_size}))
    # Freeze case identities independently of scores, before solving any case.
    casepath = ROOT / 'evaluation' / 'cases.json'
    if not casepath.exists():
        groups = {}
        for company in companies:
            groups.setdefault(company['sector'], []).extend(c['id'] for c in company['challenges'])
        sectors = sorted(groups, key=lambda s: hashlib.sha256(('CU0070-20261030-v1:' + s).encode()).hexdigest())[:18]
        cases = [{'id': f'N{i+1:02}', 'challenge_id': sorted(groups[s], key=lambda c: hashlib.sha256(('holdout-v1:' + c).encode()).hexdigest())[0],
                  'kind': 'natural_unlabelled', 'sector': s} for i, s in enumerate(sectors)]
        controls = [
            ('X01','C001-CH1','no_research_sources'),
            ('X02','C149-CH1','no_company_sources'),
            ('X03','C999-CH999','missing_challenge'),
            ('X04','C001-CH2','no_research_sources'),
            ('X05','C150-CH2','no_company_sources'),
            ('X06','C151-CH1','no_research_sources')]
        cases += [{'id':i,'challenge_id':c,'kind':'synthetic_negative','view':v,'expected':'ABSTAIN'} for i,c,v in controls]
        casepath.parent.mkdir(exist_ok=True)
        casepath.write_text(json.dumps({'protocol':'CU0070-EQUAL-RESOURCES-V1','seed':'CU0070-20261030-v1','corpus_sha256':corpus_digest,'cases':cases}, indent=2) + '\n')
    db.close()

if __name__ == '__main__': main()
