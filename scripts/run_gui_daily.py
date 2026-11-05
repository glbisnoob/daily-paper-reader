import json
import os
import re
import runpy
import sys
import tempfile
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
os.chdir(root)
sys.path.insert(0, str(root / 'src'))

with tempfile.TemporaryDirectory(prefix='dpr-arxiv-') as temp:
    config = yaml.safe_load((root / 'config.yaml').read_text())
    config['arxiv_paper_setting']['prefer_supabase_read'] = False
    path = Path(temp) / 'config.yaml'
    path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
    os.environ['DPR_CONFIG_FILE'] = str(path)
    os.environ['DPR_ENABLE_MULTI_SOURCE_RPC'] = '0'
    main = runpy.run_path(str(root / 'src/main.py'))
    run_step = main['run_step']

    def run_one(label, args, env=None):
        if label == 'Step 2.2 - Embedding':
            date = os.environ['DPR_RUN_DATE']
            archive = root / 'archive' / date
            bm25 = json.loads((archive / 'filtered' / f'arxiv_papers_{date}.bm25.json').read_text())
            ids = set()
            for query in bm25['queries']:
                scores = query['sim_scores']
                ids.update(sorted(scores, key=lambda pid: scores[pid]['rank'])[:12])
            papers = json.loads((archive / 'raw' / f'arxiv_papers_{date}.json').read_text())
            cue = re.compile(r'\b(?:gui (?:agents?|grounding|understanding)|computer[- ](?:using|use) agents?|graphical user interface agents?)\b', re.I)
            shortlist = [paper for paper in papers if paper['id'] in ids or cue.search(paper['title'] + ' ' + paper['abstract'])]
            if not shortlist:
                raise RuntimeError('No GUI agent candidates found for embedding.')
            source = Path(temp) / 'gui-arxiv.json'
            source.write_text(json.dumps(shortlist, ensure_ascii=False))
            destination = archive / 'filtered' / f'arxiv_papers_{date}.embedding.json'
            print(f'Embedding shortlist: {len(shortlist)} of {len(papers)} papers', flush=True)
            args = [*args, '--input', str(source), '--output', str(destination)]
        if label == 'Step 6 - Generate Docs':
            date = os.environ['DPR_RUN_DATE']
            selection = root / 'archive' / date / 'recommend' / f'arxiv_papers_{date}.standard.json'
            data = json.loads(selection.read_text())
            deep = data.get('deep_dive') or []
            quick = data.get('quick_skim') or []
            if not (deep or quick):
                raise RuntimeError('No paper passed selection. No report published.')
            data['deep_dive'] = deep[:1]
            data['quick_skim'] = [] if deep else quick[:1]
            data.get('stats', {}).update(deep_selected=len(data['deep_dive']), quick_selected=len(data['quick_skim']))
            pending = selection.with_suffix('.tmp')
            pending.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            pending.replace(selection)
            print('Publishing exactly one selected paper', flush=True)
        run_step(label, args, env=env)

    main['main'].__globals__['run_step'] = run_one
    sys.argv = ['main.py', '--profile-tag', 'gui-agents', '--no-skip-fetch', '--fetch-days', '5', '--fetch-mode', 'standard', '--fetch-ignore-seen']
    sys.argv += ['--embedding-batch-size', '8']
    main['main']()
