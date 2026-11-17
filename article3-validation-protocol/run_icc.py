"""Unadjusted and conditional ICC from random-intercept models fitted by REML (Table 2)."""
import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings
warnings.filterwarnings('ignore')
d1 = pd.read_csv('processed/D1.csv'); d2 = pd.read_csv('processed/D2.csv')
d2 = d2[d2.groupby('case').case.transform('size') > 1]          # case 6 has a single measured run
specs = [('D1, Ra', d1, 'Ra', 'specimen', 'C(HV_init) + C(f) + C(v_c) + C(a_p)'),
         ('D1, HV30', d1, 'HV30', 'specimen', 'C(HV_init) + C(f) + C(v_c) + C(a_p)'),
         ('D2, VB', d2, 'VB', 'case', 'DOC + feed + C(material) + time')]
rows = []
for name, d, y, g, fx in specs:
    for label, f in (('Unadjusted', f'{y} ~ 1'), ('Conditional', f'{y} ~ {fx}')):
        r = smf.mixedlm(f, d, groups=d[g]).fit(reml=True)
        sb, se = float(r.cov_re.iloc[0, 0]), float(r.scale)
        rows.append(dict(task=name, model=label, sigma_b2=sb, sigma_e2=se, ICC=sb / (sb + se)))
out = pd.DataFrame(rows); out.to_csv('results/icc.csv', index=False); print(out.round(4))
