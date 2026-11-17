"""Shared definitions: tasks, model families, fold generators, metrics."""
import numpy as np, pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.svm import SVR, SVC
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, \
    HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.model_selection import KFold, StratifiedKFold, GroupKFold, StratifiedGroupKFold, LeaveOneGroupOut
from sklearn.compose import TransformedTargetRegressor
from sklearn.metrics import balanced_accuracy_score, matthews_corrcoef

D2_FEATS = ['time', 'DOC', 'feed', 'material'] + [f'{s}_{k}' for s in
            ['smcAC', 'smcDC', 'vib_table', 'vib_spindle', 'AE_table', 'AE_spindle'] for k in ('rms', 'std', 'p2p')]

def load_tasks(folder='processed'):
    d1 = pd.read_csv(f'{folder}/D1.csv'); d2 = pd.read_csv(f'{folder}/D2.csv'); d3 = pd.read_csv(f'{folder}/D3.csv')
    f1 = ['HV_init', 'v_c', 'f', 'a_p']
    f3 = [c for c in d3.columns if c not in ('experiment', 'worn')]
    return {
        'D1, Ra':   dict(X=d1[f1].values, y=d1.Ra.values, g=d1.specimen.values, k=9, reps=20, cls=False),
        'D1, HV30': dict(X=d1[f1].values, y=d1.HV30.values, g=d1.specimen.values, k=9, reps=20, cls=False),
        'D2, VB':   dict(X=d2[D2_FEATS].values, y=d2.VB.values, g=d2.case.values, k=8, reps=20, cls=False),
        'D3, wear': dict(X=d3[f3].values, y=d3.worn.values, g=d3.experiment.values, k=6, reps=5, cls=True),
    }

# Fixed hyperparameters of the five model families (Section 2.3, Table A1)
def models(cls, seed=0):
    sc = StandardScaler
    if not cls:
        return {
            'Ridge': make_pipeline(sc(), Ridge(alpha=1.0)),
            'kNN':   make_pipeline(sc(), KNeighborsRegressor(n_neighbors=5)),
            'SVR':   TransformedTargetRegressor(make_pipeline(sc(), SVR(kernel='rbf', C=1.0, epsilon=0.1, gamma='scale')),
                                            transformer=sc()),   # epsilon acts on the standardized target
            'RF':    RandomForestRegressor(n_estimators=200, min_samples_leaf=1, max_features=1.0, random_state=seed, n_jobs=-1),
            'GBM':   HistGradientBoostingRegressor(learning_rate=0.1, max_iter=100, max_leaf_nodes=31, min_samples_leaf=20, random_state=seed),
        }
    return {
        'Logistic': make_pipeline(sc(), LogisticRegression(C=1.0, max_iter=2000)),
        'kNN':      make_pipeline(sc(), KNeighborsClassifier(n_neighbors=5)),
        'SVC':      make_pipeline(sc(), SVC(kernel='rbf', C=1.0, gamma='scale')),
        'RF':       RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=-1),
        'GBM':      HistGradientBoostingClassifier(learning_rate=0.1, max_iter=100, random_state=seed),
    }

def splits(protocol, t, seed):
    X, y, g, k = t['X'], t['y'], t['g'], t['k']
    if protocol == 'row':
        cv = StratifiedKFold(k, shuffle=True, random_state=seed) if t['cls'] else KFold(k, shuffle=True, random_state=seed)
        return list(cv.split(X, y))
    if protocol == 'grouped':
        cv = StratifiedGroupKFold(k, shuffle=True, random_state=seed) if t['cls'] else GroupKFold(k, shuffle=True, random_state=seed)
        return list(cv.split(X, y, g))
    if protocol == 'logo':
        return list(LeaveOneGroupOut().split(X, y, g))
    raise ValueError(protocol)

def oof(model_factory, t, folds):
    X, y = t['X'], t['y']
    p = np.empty(len(y), dtype=float)
    for tr, te in folds:
        m = model_factory(); m.fit(X[tr], y[tr]); p[te] = m.predict(X[te])
    return p

def nrmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)) / np.std(y))

def score(t, p):
    if t['cls']:
        return dict(bacc=balanced_accuracy_score(t['y'], p), mcc=matthews_corrcoef(t['y'], p))
    return dict(nrmse=nrmse(t['y'], p))
