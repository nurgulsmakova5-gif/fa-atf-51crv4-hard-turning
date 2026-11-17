"""Additional analyses requested in review:
 (1) group-level paired Wilcoxon tests of row-wise vs LOGO errors (Holm-adjusted);
 (2) D3 class composition of grouped folds, per-repetition variability, confusion matrices, per-experiment predictions;
 (3) prediction-task variants: D1 leave-one-factor-level-out, D2 leave-one-condition-out (new tool under an unseen condition)."""
import json, numpy as np, pandas as pd
from scipy.stats import wilcoxon
from sklearn.metrics import confusion_matrix, balanced_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold
from statsmodels.stats.multitest import multipletests
from common import load_tasks, models, oof, nrmse, splits

T = load_tasks()
P = pd.DataFrame(json.load(open('results/cv_predictions.json')))

# (1) group-level paired tests
rows = []
for (task, model), d in P.groupby(['task', 'model'], sort=False):
    t = T[task]; y, g = t['y'], t['g']; G = np.unique(g)
    row_preds = np.array(d[d.protocol == 'row'].pred.tolist()); logo = np.array(d[d.protocol == 'logo'].pred.iloc[0])
    if t['cls']:
        e_row = np.array([np.mean([(rp[g == k] == y[g == k]).mean() for rp in row_preds]) for k in G])
        e_logo = np.array([(logo[g == k] == y[g == k]).mean() for k in G])
        stat = wilcoxon(e_row, e_logo, alternative='two-sided', zero_method='pratt')
        rows.append(dict(task=task, model=model, n_groups=len(G), median_row=np.median(e_row), median_logo=np.median(e_logo),
                         groups_worse_under_logo=int((e_logo < e_row).sum()), p=stat.pvalue, metric='accuracy per experiment'))
    else:
        e_row = np.array([np.mean([np.sqrt(np.mean((y[g == k] - rp[g == k]) ** 2)) for rp in row_preds]) for k in G]) / y.std()
        e_logo = np.array([np.sqrt(np.mean((y[g == k] - logo[g == k]) ** 2)) for k in G]) / y.std()
        stat = wilcoxon(e_row, e_logo, alternative='two-sided')
        rows.append(dict(task=task, model=model, n_groups=len(G), median_row=np.median(e_row), median_logo=np.median(e_logo),
                         groups_worse_under_logo=int((e_logo > e_row).sum()), p=stat.pvalue, metric='NRMSE per group'))
W = pd.DataFrame(rows)
W['p_holm'] = W.groupby('task').p.transform(lambda p: multipletests(p, method='holm')[1])
W.to_csv('results/wilcoxon_group_level.csv', index=False); print(W.round(4))

# (2) D3 diagnostics
t = T['D3, wear']; y, g = t['y'], t['g']
comp = []
for rep in range(5):
    for i, (tr, te) in enumerate(splits('grouped', t, rep)):
        ge = np.unique(g[te]); gt = np.unique(g[tr])
        lab = lambda gs: [int(y[g == k][0]) for k in gs]
        comp.append(dict(rep=rep, fold=i, test_experiments=' '.join(map(str, ge)), test_worn=sum(lab(ge)),
                         test_unworn=len(ge) - sum(lab(ge)), train_worn=sum(lab(gt)), train_unworn=len(gt) - sum(lab(gt)),
                         train_frac_worn_rows=float(y[tr].mean())))
pd.DataFrame(comp).to_csv('results/d3_fold_composition.csv', index=False)
cm, per_exp, reps = [], [], []
d3 = P[P.task == 'D3, wear']
for model, d in d3.groupby('model', sort=False):
    logo = np.array(d[d.protocol == 'logo'].pred.iloc[0]).astype(int)
    rowp = np.array(d[d.protocol == 'row'].pred.iloc[0]).astype(int)
    for proto, p in (('row', rowp), ('logo', logo)):
        tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel()
        cm.append(dict(model=model, protocol=proto, TN=tn, FP=fp, FN=fn, TP=tp))
    for k in np.unique(g):
        per_exp.append(dict(model=model, experiment=int(k), worn=int(y[g == k][0]), n=int((g == k).sum()),
                            frac_pred_worn_logo=float(logo[g == k].mean()), frac_pred_worn_row=float(rowp[g == k].mean())))
    for proto in ('row', 'grouped'):
        b = [balanced_accuracy_score(y, np.array(p).astype(int)) for p in d[d.protocol == proto].pred]
        reps.append(dict(model=model, protocol=proto, mean=np.mean(b), sd=np.std(b, ddof=1), min=np.min(b), max=np.max(b)))
# training-majority baseline: predicts, for every held-out experiment, the class holding most rows in the training folds
from sklearn.dummy import DummyClassifier
for proto, folds in (('logo', splits('logo', t, 0)), ('grouped', splits('grouped', t, 0))):
    p = oof(lambda: DummyClassifier(strategy='most_frequent'), t, folds).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, p, labels=[0, 1]).ravel()
    cm.append(dict(model='Majority baseline', protocol=proto, TN=tn, FP=fp, FN=fn, TP=tp, bacc=balanced_accuracy_score(y, p)))
pd.DataFrame(cm).to_csv('results/d3_confusion.csv', index=False)
pd.DataFrame(per_exp).to_csv('results/d3_per_experiment.csv', index=False)
pd.DataFrame(reps).to_csv('results/d3_repetition_spread.csv', index=False)
# experiment-level majority vote under LOGO
pe = pd.DataFrame(per_exp); pe['vote_worn'] = (pe.frac_pred_worn_logo > 0.5).astype(int)
print(pe.groupby('model').apply(lambda d: pd.Series(dict(exp_correct=int((d.vote_worn == d.worn).sum())))))

# (3) prediction-task variants
var = []
d1 = pd.read_csv('processed/D1.csv')
for tname in ('D1, Ra', 'D1, HV30'):
    t = T[tname]
    for fac_col in ('HV_init', 'f', 'v_c'):
        lev = d1[fac_col].values
        folds = [(np.where(lev != L)[0], np.where(lev == L)[0]) for L in np.unique(lev)]
        for m in models(False):
            var.append(dict(task=tname, scheme=f'leave-one-level-out ({fac_col})', model=m,
                            nrmse=nrmse(t['y'], oof(lambda: models(False)[m], t, folds))))
d2 = pd.read_csv('processed/D2.csv'); t = T['D2, VB']
cond = d2.DOC.astype(str) + '_' + d2.feed.astype(str) + '_' + d2.material.astype(str)
folds = [(np.where(cond != c)[0], np.where(cond == c)[0]) for c in cond.unique()]
for m in models(False):
    var.append(dict(task='D2, VB', scheme='leave-one-condition-out', model=m,
                    nrmse=nrmse(t['y'], oof(lambda: models(False)[m], t, folds))))
pd.DataFrame(var).to_csv('results/task_variants.csv', index=False)
print(pd.DataFrame(var).pivot_table(index=['task', 'scheme'], columns='model', values='nrmse').round(3))
