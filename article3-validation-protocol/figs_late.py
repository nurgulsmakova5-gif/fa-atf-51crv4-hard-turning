import numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from figs import W, tag, C_ROW, C_GRP

def fig5():
    c = pd.read_csv('results/conformal.csv'); det = pd.read_csv('results/conformal_detail.csv')
    tasks = ['D1, Ra', 'D1, HV30', 'D2, VB']; V = ['row', 'grouped_row', 'grouped_cluster']
    lab = {'row': 'row-wise', 'grouped_row': 'grouped, row-level', 'grouped_cluster': 'grouped, cluster-level'}
    col = {'row': C_ROW, 'grouped_row': '#7fa7d9', 'grouped_cluster': C_GRP}
    fig, ax = plt.subplots(1, 3, figsize=(W, 2.6)); x = np.arange(3)
    for j, v in enumerate(V):
        r = c[c.variant == v].set_index('task').loc[tasks]
        ax[0].bar(x + (j - 1) * 0.27, r.marginal, 0.25, color=col[v], label=lab[v])
        ax[0].scatter(x + (j - 1) * 0.27, r.simultaneous, marker='_', s=60, color='k', zorder=3)
        ax[1].bar(x + (j - 1) * 0.27, r.width_sd, 0.25, color=col[v])
    ax[0].axhline(0.9, ls='--', lw=0.7, color='0.2'); ax[0].set_ylim(0.3, 1.05)
    ax[0].set_ylabel('Coverage'); ax[0].set_title('Coverage (bars: marginal;\n black marks: group-simultaneous)', fontsize=7)
    ax[1].set_ylabel('Interval width / SD of target'); ax[1].set_title('Mean interval width', fontsize=7)
    for a in ax[:2]: a.set_xticks(x, ['D1 $R_a$', 'D1 HV30', 'D2 VB'])
    for k, v in enumerate(V):
        dd = det[(det.task == 'D2, VB') & (det.variant == v)]
        ax[2].scatter(np.full(len(dd), k) + np.random.default_rng(k).uniform(-0.12, 0.12, len(dd)), dd.coverage, s=9, color=col[v], lw=0)
    ax[2].set_xticks(range(3), ['row-wise', 'grouped\nrow-level', 'grouped\ncluster-level']); ax[2].set_ylim(-0.05, 1.05)
    ax[2].set_ylabel('Coverage within tool life'); ax[2].set_title('D2: one point per held-out tool', fontsize=7)
    ax[2].axhline(0.9, ls='--', lw=0.7, color='0.2')
    fig.legend(handles=[Patch(color=col[v], label=lab[v]) for v in V], ncol=3, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.02))
    for a, s in zip(ax, 'abc'): tag(a, f'({s})')
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig('figures/Figure6.png'); plt.close(fig)

def fig6():
    pe = pd.read_csv('results/d3_per_experiment.csv'); meta = pd.read_csv('processed/D3_experiments.csv').set_index('No')
    fig, ax = plt.subplots(1, 2, figsize=(W, 2.6), sharey=True)
    for a, m, s in zip(ax, ['RF', 'GBM'], 'ab'):
        d = pe[pe.model == m].copy(); d['feed'] = d.experiment.map(meta.feedrate)
        d = d.sort_values(['worn', 'feed', 'experiment']); xs = np.arange(len(d))
        a.bar(xs - 0.2, d.frac_pred_worn_row, 0.38, color=C_ROW, label='row-wise CV')
        a.bar(xs + 0.2, d.frac_pred_worn_logo, 0.38, color=C_GRP, label='leave-one-experiment-out')
        a.axhline(0.5, ls='--', lw=0.6, color='0.3'); a.axvline(7.5, lw=0.8, color='0.2')
        a.set_xticks(xs, [f'{e}\n{f:g}' for e, f in zip(d.experiment, d.feed)], fontsize=6)
        a.text(3.5, 1.04, 'unworn tool', ha='center', fontsize=7); a.text(12.5, 1.04, 'worn tool', ha='center', fontsize=7)
        a.set_ylim(0, 1.12); a.set_xlabel('Experiment (top) and feed rate in mm/s (bottom)'); a.set_title(m, pad=14)
        tag(a, f'({s})')
    ax[0].set_ylabel('Fraction predicted "worn"')
    fig.legend(handles=[Patch(color=C_ROW, label='row-wise CV'), Patch(color=C_GRP, label='leave-one-experiment-out')], ncol=2, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig('figures/Figure5.png'); plt.close(fig)

def run(): fig5(); fig6()
if __name__ == '__main__': run()
