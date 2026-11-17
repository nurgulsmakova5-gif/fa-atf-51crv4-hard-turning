"""Figures 1, 3-7 of the revised manuscript (Figure 2 is the protocol schematic)."""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 7, 'axes.linewidth': 0.6,
                     'xtick.major.width': 0.6, 'ytick.major.width': 0.6, 'savefig.dpi': 600, 'axes.grid': True,
                     'grid.linewidth': 0.3, 'grid.alpha': 0.5, 'axes.axisbelow': True})
W = 17 / 2.54
C_ROW, C_GRP, C_LOGO = '#c0392b', '#1f5fa8', '#111111'
MODELS = {'reg': ['Ridge', 'kNN', 'SVR', 'RF', 'GBM'], 'cls': ['Logistic', 'kNN', 'SVC', 'RF', 'GBM']}
def tag(ax, s): ax.text(-0.20, 1.02, s, transform=ax.transAxes, fontsize=10, fontweight='bold', va='bottom')

def fig1():
    d1 = pd.read_csv('processed/D1.csv'); d2 = pd.read_csv('processed/D2.csv'); d3 = pd.read_csv('processed/D3.csv')
    fig, ax = plt.subplots(1, 3, figsize=(W, 2.5), gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
    order = d1.groupby('specimen').Ra.mean().sort_values().index
    for i, s in enumerate(order):
        r = d1[d1.specimen == s]
        ax[0].plot([i] * 3, r.Ra, 'o', ms=2.6, color=plt.cm.viridis(r.HV_init.iloc[0] / 700 - 0.3), mec='none')
        ax[0].plot([i, i], [r.Ra.min(), r.Ra.max()], lw=0.6, color='0.4')
    ax[0].set_xlabel('Specimen (sorted by mean $R_a$)'); ax[0].set_ylabel('$R_a$ (µm)'); ax[0].set_xticks([])
    ax[0].set_title('D1: 27 specimens × 3 sections')
    h = [Line2D([], [], marker='o', ls='', ms=3, color=plt.cm.viridis(v / 700 - 0.3), label=f'{v} HV30') for v in (400, 500, 600)]
    ax[0].legend(handles=h, title='Initial hardness', title_fontsize=6.5, frameon=False, loc='upper left')
    for c, r in d2.groupby('case'):
        ax[1].plot(r.time, r.VB, '-o', ms=1.8, lw=0.7, color='#8c510a' if r.material.iloc[0] == 1 else '#01665e')
    ax[1].axhline(0.3, ls='--', lw=0.6, color='0.3'); ax[1].text(60, 0.20, 'VB = 0.3 mm', fontsize=6.5)
    ax[1].set_xlabel('Cutting time (min)'); ax[1].set_ylabel('Flank wear VB (mm)'); ax[1].set_title('D2: 16 tool-life cases')
    ax[1].legend(handles=[Line2D([], [], color='#8c510a', label='cast iron'), Line2D([], [], color='#01665e', label='steel J45')], frameon=False)
    feat = 'X1_OutputPower'
    g = d3.groupby('experiment').agg(m=(feat, 'mean'), s=(feat, 'std'), worn=('worn', 'first'), n=('worn', 'size')).reset_index()
    meta = pd.read_csv('processed/D3_experiments.csv').set_index('No')
    g['feed'] = g.experiment.map(meta.feedrate)
    for _, r in g.iterrows():
        ax[2].errorbar(r.feed + (0.35 if r.worn else -0.35), r.m * 1e3, yerr=r.s * 1e3, fmt='o', ms=3, lw=0.6, capsize=1.5,
                       color='#b2182b' if r.worn else '#2166ac')
    ax[2].set_xlabel('Feed rate (mm/s)'); ax[2].set_ylabel('X-axis output power (W)'); ax[2].set_title('D3: 18 experiments')
    ax[2].legend(handles=[Line2D([], [], marker='o', ms=3, ls='', color='#2166ac', label='unworn tool'), Line2D([], [], marker='o', ms=3, ls='', color='#b2182b', label='worn tool')], frameon=False, loc='upper left')
    for a, s in zip(ax, 'abc'): tag(a, f'({s})')
    fig.tight_layout(w_pad=1.2); fig.savefig('figures/Figure1.png'); plt.close(fig)

def summary():
    d = pd.read_csv('results/cv_runs.csv'); out = []
    for (t, m), g in d.groupby(['task', 'model'], sort=False):
        col = 'bacc' if t.startswith('D3') else 'nrmse'
        r = g[g.protocol == 'row'].set_index('rep')[col]; gg = g[g.protocol == 'grouped'].set_index('rep')[col]
        u = (gg - r) / gg * 100 if col == 'nrmse' else (r - gg)
        out.append(dict(task=t, model=m, row=r.mean(), row_sd=r.std(ddof=1), grouped=gg.mean(), grouped_sd=gg.std(ddof=1),
                        logo=g[g.protocol == 'logo'][col].iloc[0], U=u.mean(), U_sd=u.std(ddof=1), U_min=u.min(), U_max=u.max(),
                        mcc_row=g[g.protocol == 'row'].mcc.mean() if col == 'bacc' else np.nan,
                        mcc_grouped=g[g.protocol == 'grouped'].mcc.mean() if col == 'bacc' else np.nan,
                        mcc_logo=g[g.protocol == 'logo'].mcc.iloc[0] if col == 'bacc' else np.nan))
    s = pd.DataFrame(out); s.to_csv('results/cv_summary.csv', index=False); return s

def fig3(s):
    icc = pd.read_csv('results/icc.csv')
    fig, ax = plt.subplots(1, 2, figsize=(W, 2.5), gridspec_kw=dict(width_ratios=[1, 1.6]))
    tasks = ['D1, Ra', 'D1, HV30', 'D2, VB']; x = np.arange(3)
    for j, (lab, c) in enumerate((('Unadjusted', '0.65'), ('Conditional', '#1f5fa8'))):
        v = [icc[(icc.task == t) & (icc.model == lab)].ICC.iloc[0] for t in tasks]
        b = ax[0].bar(x + (j - 0.5) * 0.36, v, 0.34, color=c, label=lab.lower() + ' ICC')
        ax[0].bar_label(b, fmt='%.2f', fontsize=6.5, padding=1)
    ax[0].set_xticks(x, ['D1 $R_a$', 'D1 HV30', 'D2 VB']); ax[0].set_ylim(0, 1.32); ax[0].set_ylabel('ICC'); ax[0].legend(frameon=False, loc='upper right', ncol=2, fontsize=6.5)
    mk = dict(zip(MODELS['reg'], 'osD^v'))
    for i, t in enumerate(tasks):
        for k, m in enumerate(MODELS['reg']):
            r = s[(s.task == t) & (s.model == m)].iloc[0]
            ax[1].errorbar(i + (k - 2) * 0.14, r.U, yerr=r.U_sd, fmt=mk[m], ms=4, lw=0.7, capsize=1.5, color=plt.cm.tab10(k), label=m if i == 0 else None)
    ax[1].set_xticks(x, ['D1 $R_a$', 'D1 HV30', 'D2 VB']); ax[1].set_ylabel('Underestimation of NRMSE by\nrow-wise CV, $U$ (%)'); ax[1].axhline(0, lw=0.6, color='0.3')
    ax[1].legend(frameon=False, ncol=5, loc='upper center', bbox_to_anchor=(0.5, 1.16))
    tag(ax[0], '(a)'); tag(ax[1], '(b)'); fig.tight_layout(); fig.savefig('figures/Figure3.png'); plt.close(fig)

def fig4():
    d = pd.read_csv('results/cv_runs.csv')
    fig, ax = plt.subplots(1, 4, figsize=(W, 2.6))
    for a, t, lab in zip(ax, ['D1, Ra', 'D1, HV30', 'D2, VB', 'D3, wear'], 'abcd'):
        cls = t.startswith('D3'); col = 'bacc' if cls else 'nrmse'; ms = MODELS['cls' if cls else 'reg']
        for k, m in enumerate(ms):
            g = d[(d.task == t) & (d.model == m)]
            for off, p, c in ((-0.17, 'row', C_ROW), (0.17, 'grouped', C_GRP)):
                v = g[g.protocol == p][col].values
                a.scatter(np.full(len(v), k + off) + np.random.default_rng(k).uniform(-0.05, 0.05, len(v)), v, s=4, color=c, alpha=0.5, lw=0)
                a.plot([k + off - 0.12, k + off + 0.12], [v.mean()] * 2, color=c, lw=1.4)
            a.plot([k - 0.3, k + 0.3], [g[g.protocol == 'logo'][col].iloc[0]] * 2, color=C_LOGO, lw=0.8, ls=':')
        a.set_xticks(range(5), ms, rotation=45); a.set_title(t.replace('Ra', '$R_a$'))
        a.set_ylabel('Balanced accuracy' if cls else 'NRMSE')
        if cls: a.axhline(0.5, ls='--', lw=0.6, color='0.4'); a.set_ylim(0.15, 0.85)
        tag(a, f'({lab})')
    h = [Line2D([], [], color=C_ROW, lw=1.4, label='row-wise CV (mean; dots = repetitions)'), Line2D([], [], color=C_GRP, lw=1.4, label='grouped CV'),
         Line2D([], [], color=C_LOGO, ls=':', label='leave-one-group-out'), Line2D([], [], color='0.4', ls='--', label='chance (D3)')]
    fig.legend(handles=h, ncol=4, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig('figures/Figure4.png'); plt.close(fig)

if __name__ == '__main__':
    import os, sys; os.makedirs('figures', exist_ok=True)
    s = summary(); fig1(); fig3(s); fig4()
    if 'all' in sys.argv:
        import figs_late; figs_late.run()
