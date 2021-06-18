import mne
from matplotlib import pyplot as plt
import numpy as np


# create new par with names of fr bands and change to f-strings
def plot_patterns(pl_type, ar, fr_bands, info):
    vmax = np.amax(ar)
    vmin = -vmax
    if pl_type not in ['topo', 'time_fr']:
        raise ValueError('pl_type should be topo or time_fr')
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(30, 20))
    for name, pos, plot_name, ind in zip(('patterns_', 'filters_'), (0.82, 0.5),
                                         ('Patterns', 'Filters'), (0, 1)):
        for i, key in enumerate(list(fr_bands.keys())):
            mne.viz.plot_topomap(ar[ind, i, :], info, vmin=vmin, vmax=vmax, axes=axes[ind, i],
                                 show=False)
            axes[ind, i].set_title(label='{}-{} Hz'.format(*fr_bands[key]),
                                   fontdict={'fontsize': 40, 'fontweight': 'semibold'})
            mne.viz.tight_layout()
        plt.figtext(0.5, pos, f'{plot_name}', va="center", ha="center", size=44, fontweight='semibold')
    m = plt.cm.ScalarMappable(cmap='RdBu_r')
    m.set_array([vmin, vmax])
    cax = fig.add_axes([1, 0.3, 0.03, 0.38])
    cb = fig.colorbar(m, cax)
    cb.ax.tick_params(labelsize=40)
    return fig
