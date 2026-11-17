"""Row-wise vs grouped vs LOGO CV for five model families (Table 3, Figures 3-4) and
per-group errors used for the group-level paired tests."""
import numpy as np, pandas as pd, json, sys
from common import load_tasks, models, splits, oof, score
tasks = load_tasks()
ONLY = set(sys.argv[1:])      # optional: recompute only these model names and merge
rows, pergroup, preds = [], [], []
for name, t in tasks.items():
    if ONLY and t['cls']: continue
    for mname in models(t['cls']):
        if ONLY and mname not in ONLY: continue
        fac = lambda: models(t['cls'])[mname]
        for proto in ('row', 'grouped'):
            for rep in range(t['reps']):
                p = oof(fac, t, splits(proto, t, seed=rep))
                rows.append(dict(task=name, model=mname, protocol=proto, rep=rep, **score(t, p)))
                preds.append(dict(task=name, model=mname, protocol=proto, rep=rep, pred=p.tolist()))
        p = oof(fac, t, splits('logo', t, 0))
        rows.append(dict(task=name, model=mname, protocol='logo', rep=0, **score(t, p)))
        preds.append(dict(task=name, model=mname, protocol='logo', rep=0, pred=p.tolist()))
        print(name, mname, flush=True)
new = pd.DataFrame(rows)
if ONLY:
    old = pd.read_csv('results/cv_runs.csv'); keep = ~old.model.isin(ONLY) | old.task.str.startswith('D3')
    new = pd.concat([old[keep], new], ignore_index=True)
    oldp = [p for p in json.load(open('results/cv_predictions.json')) if p['model'] not in ONLY or p['task'].startswith('D3')]
    preds = oldp + preds
new.to_csv('results/cv_runs.csv', index=False)
json.dump(preds, open('results/cv_predictions.json', 'w'))
