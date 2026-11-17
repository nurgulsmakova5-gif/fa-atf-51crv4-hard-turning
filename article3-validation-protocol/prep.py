"""Data preparation for D1 (hard turning 51CrV4), D2 (NASA milling), D3 (UMich CNC mill).
Usage: python prep.py <D1_csv> <mill.mat> <cnc_mill_dir> <outdir>"""
import sys, numpy as np, pandas as pd, scipy.io as sio
from pathlib import Path

def prep_d1(path):
    d = pd.read_csv(path, sep=';', skiprows=[1, 2], header=0)
    d.columns = ['specimen', 'section', 'HV_init', 'v_c', 'f', 'a_p', 'HV30', 'Ra', 'Rz']
    d = d.dropna(subset=['specimen'])
    return d[['specimen', 'section', 'HV_init', 'v_c', 'f', 'a_p', 'Ra', 'HV30']]

SIG = ['smcAC', 'smcDC', 'vib_table', 'vib_spindle', 'AE_table', 'AE_spindle']

def prep_d2(path):
    m = sio.loadmat(path, struct_as_record=True)['mill'][0]
    rows = []
    for i, r in enumerate(m):
        vb = np.squeeze(r['VB'])
        if np.size(vb) == 0 or np.isnan(float(vb)):
            continue
        row = dict(record=i, case=int(np.squeeze(r['case'])), run=int(np.squeeze(r['run'])), VB=float(vb),
                   time=float(np.squeeze(r['time'])), DOC=float(np.squeeze(r['DOC'])),
                   feed=float(np.squeeze(r['feed'])), material=int(np.squeeze(r['material'])))
        bad = False
        for s in SIG:
            x = np.squeeze(r[s]).astype(float)
            if not np.all(np.isfinite(x)) or np.abs(x).max() > 1e6:
                bad = True                                 # corrupted recording
            n = len(x); x = x[n // 4: 3 * n // 4]          # middle half of the run
            row[f'{s}_rms'] = np.sqrt(np.mean(x ** 2)); row[f'{s}_std'] = x.std(); row[f'{s}_p2p'] = np.ptp(x)
        if bad:                                            # record 17 (case 2) contains corrupted values
            continue
        rows.append(row)
    return pd.DataFrame(rows)

def prep_d3(folder):
    folder = Path(folder)
    meta = pd.read_csv(folder / 'train.csv')
    out = []
    for _, mrow in meta.iterrows():
        e = int(mrow['No'])
        d = pd.read_csv(folder / f'experiment_{e:02d}.csv')
        d = d[d['Machining_Process'].str.startswith('Layer')].iloc[::4].copy()   # cutting stages, every 4th sample
        d['experiment'] = e; d['worn'] = int(mrow['tool_condition'] == 'worn')
        out.append(d)
    a = pd.concat(out, ignore_index=True)
    drop = [c for c in a.columns if 'Position' in c] + ['M1_CURRENT_PROGRAM_NUMBER', 'M1_sequence_number',
                                                         'M1_CURRENT_FEEDRATE', 'Machining_Process']
    a = a.drop(columns=drop)
    feats = [c for c in a.columns if c not in ('experiment', 'worn')]
    const = [c for c in feats if a[c].std() == 0]
    return a.drop(columns=const)

if __name__ == '__main__':
    d1p, d2p, d3p, out = sys.argv[1:5]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    d1 = prep_d1(d1p); d1.to_csv(out / 'D1.csv', index=False)
    d2 = prep_d2(d2p); d2.to_csv(out / 'D2.csv', index=False)
    d3 = prep_d3(d3p); d3.to_csv(out / 'D3.csv', index=False)
    pd.read_csv(Path(d3p) / 'train.csv').to_csv(out / 'D3_experiments.csv', index=False)
    print('D1', d1.shape, d1.specimen.nunique(), '| D2', d2.shape, d2.case.nunique(),
          '| D3', d3.shape, d3.experiment.nunique(), 'features', d3.shape[1] - 2)
