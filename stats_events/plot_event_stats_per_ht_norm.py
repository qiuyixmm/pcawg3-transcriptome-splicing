import sys
import os
import scipy as sp
import pickle
import h5py

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['lines.linewidth'] = 2
matplotlib.rcParams['axes.linewidth'] = 2
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

sys.path.append('/cluster/home/akahles/git/projects/2014/icgc/colors')
import ICGC_colors as ic

sys.path.append('/cluster/project/grlab/home/akahles/git/tools/python/viz/')
import axes as axs
sys.path.append('/cluster/home/akahles/git/software/spladder/python')

sys.path.append('..')
from paths import *

BASEDIR_GTEX = os.path.join(BASEDIR_AS, 'alternative_splicing_gtex')
BASEDIR_ICGC = os.path.join(BASEDIR_AS, 'alternative_splicing')
BASEDIR_ANNO = os.path.join(BASEDIR_AS, 'alternative_splicing_anno')
PLOTDIR      = os.path.join(BASEDIR_AS, 'alternative_splicing/plots/event_stats')
CONF = 2

event_types = ['exon_skip',
               'intron_retention',
               'alt_3prime',
               'alt_5prime',
               'mutex_exons',
               'mult_exon_skip']
#event_types = ['exon_skip']
if CONF == 3:
    event_types = event_types[:-1]
event_dict = {'exon_skip':'Exon Skip',
              'intron_retention':'Intron Retention',
              'alt_3prime':'Alternative 3\' Site',
              'alt_5prime':'Alternative 5\' Site',
              'mutex_exons':'Mutually Exclusive Exons',
              'mult_exon_skip':'Mult. Exon Skip'}


def main():
    figs = dict()
    figs['stats'] = plt.figure(figsize=(15, 8))
    figs['stats_log'] = plt.figure(figsize=(15, 8))
    gss = dict()
    gss['stats'] = gridspec.GridSpec(2, 3) #, wspace=0.0, hspace=0.0)
    gss['stats_log'] = gridspec.GridSpec(2, 3) #, wspace=0.0, hspace=0.0)

    for e, event_type in enumerate(event_types):

        print('Handling %s' % event_type, file=sys.stderr)
        
        ### load events detected in annotation only
        #anno = cPickle.load(open(os.path.join(BASEDIR_ANNO, 'merge_graphs_%s_C%i.pickle' % (event_type, CONF)), 'r'))
        #if isinstance(anno, tuple):
        #    anno = anno[0]

        ### load annotation index
        is_anno_gtex = pickle.load(open(os.path.join(BASEDIR_GTEX, 'merge_graphs_%s_C%i.anno_only.pickle' % (event_type, CONF)), 'r'))
        is_anno_icgc = pickle.load(open(os.path.join(BASEDIR_ICGC, 'merge_graphs_%s_C%i.anno_only.pickle' % (event_type, CONF)), 'r'))

        ### load confident events
        IN = h5py.File(os.path.join(BASEDIR_GTEX, 'merge_graphs_%s_C%i.counts.hdf5' % (event_type, CONF)), 'r')
        idx_conf_gtex = IN['conf_idx'][:]
        IN.close()
        IN = h5py.File(os.path.join(BASEDIR_ICGC, 'merge_graphs_%s_C%i.counts.hdf5' % (event_type, CONF)), 'r')
        idx_conf_icgc = IN['conf_idx'][:]
        IN.close()

        ### load psi filtered events
        #idx_psi_gtex = cPickle.load(open(os.path.join(BASEDIR_GTEX, 'merge_graphs_%s_C%i.counts.hdf5.psi_filt_per_ht.pickle' % (event_type, CONF)), 'r'))[1]
        idx_psi_icgc = pickle.load(open(os.path.join(BASEDIR_ICGC, 'merge_graphs_%s_C%i.counts.hdf5.psi_filt_per_ht_normalized.pickle' % (event_type, CONF)), 'r'))[1]

        ### get all histotypes
        htypes = sp.unique([x[0] for x in list(idx_psi_icgc.keys())])
        #colors = dict(zip(htypes, ic.get_color_scheme('tumor_subtype', labels=htypes)))
        colors = ic.get_color_scheme('tumor_subtype', labels=htypes)

        ### get counts
        counts = []
        dp = 0.3
        counts_anno = sp.array([sp.sum(is_anno_icgc[idx_psi_icgc[(ht, dp)]]) if (ht, dp) in idx_psi_icgc else 0 for ht in htypes])
        counts_new = sp.array([idx_psi_icgc[(ht, dp)].shape[0] - sp.sum(is_anno_icgc[idx_psi_icgc[(ht, dp)]]) if (ht, dp) in idx_psi_icgc else 0 for ht in htypes])

        ### plot stats for events by histotype
        ax = figs['stats'].add_subplot(gss['stats'][e / 3, e % 3])
        ax.bar(sp.arange(htypes.shape[0]) + 0.2, counts_anno, 0.6, color=colors, linewidth=0.5)
        ax.bar(sp.arange(htypes.shape[0]) + 0.2, counts_new, 0.6, bottom=counts_anno, color=colors, linewidth=0.5, alpha=0.5)
        #li, = ax.plot(sp.arange(data1_icgc.shape[0]), data1_icgc, '-r', label='ICGC')
        axs.set_ticks_outer(ax)
        axs.clean_axis(ax)
        #if e == len(event_types) - 1:
        #    ax.legend(handles=[lg, lga, li, lia], loc='upper right', frameon=False, fontsize=10)
        ax.set_xticks(sp.arange(htypes.shape[0]) + 0.5)
        ax.set_xlim([-0.2, htypes.shape[0]])
        if e < len(event_types) - 3:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(htypes, rotation=90, fontsize=10)
        ax.set_title(event_dict[event_type])
        ax.yaxis.grid(True)

        ### plot stats for events by histotype (log)
        ax = figs['stats_log'].add_subplot(gss['stats'][e / 3, e % 3])
        ax.bar(sp.arange(htypes.shape[0]) + 0.1, sp.log10(counts_anno + 1), 0.8, color=colors, linewidth=0.5)
        ax.bar(sp.arange(htypes.shape[0]) + 0.1, sp.log10(counts_new + 1), 0.8, bottom=sp.log10(counts_anno + 1), color=colors, linewidth=0.5, alpha=0.3)
        axs.set_ticks_outer(ax)
        axs.clean_axis(ax)
        ax.set_xticks(list(range(htypes.shape[0])))
        ax.set_xlim([-0.2, htypes.shape[0]])
        if e < len(event_types) - 3:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(htypes, rotation=90, fontsize=10)
        ax.set_title(event_dict[event_type])
        ax.yaxis.grid(True)


    for p in figs:
        figs[p].tight_layout()
        figs[p].savefig(os.path.join(PLOTDIR, 'event_overview_per_ht_norm_C%i_%s.pdf' % (CONF, p)), format='pdf', bbox_inches='tight')
        figs[p].savefig(os.path.join(PLOTDIR, 'event_overview_per_ht_norm_C%i_%s.png' % (CONF, p)), format='png', bbox_inches='tight')
        plt.close(figs[p])

if __name__ == "__main__":
    main()
