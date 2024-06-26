import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')

fw, fh = plt.rcParams["figure.figsize"]

def plot_repr(X, y, title=""):
    d = X.shape[1]
    fig_kw = {"nrows": 1,
              "figsize": (2 * fw, 2 * fh)}
    subplot_kw = {}
    if d >= 3:
        subplot_kw = {"projection": "3d"}
    fig, ax = plt.subplots(**fig_kw, subplot_kw=subplot_kw)
    for i, yi in enumerate(set(y)):
        coords = []
        for j in range(min((d, 3))):
            coords.append(X[yi == y, j])
        scatter_kw = {"c": plt.cm.tab20(i),
                      "label": str(yi),
                      "marker": "o",
                      "edgecolors": "k",
                      "linewidths": 0.2}
        ax.scatter(*coords, **scatter_kw)
    ax.set_xlabel("$C_1$")
    ax.set_ylabel("$C_2$")
    if d >= 3:
        ax.set_zlabel("$C_3$")
    ax.set_title(title)
    #ax.legend()
    return fig, ax