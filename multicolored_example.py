from ipdb import set_trace as db
import svgpathtools

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np


# convert -delay 5 frames/*.png -loop 0 epicycles.gif

N = 128
t = np.linspace(0, 2*np.pi, N+1)

PLOT = True
PNG = False


# style information copied from svg stylesheet
# TODO try https://pypi.org/project/svgelements/
# which supports both paths and styles
styles = {
    'cls-1': '#004379',
    'cls-2': '#c3d3dc',
    'cls-3': '#48b5cd',
}

cmap = ['#00000000', styles['cls-1'], styles['cls-2'], styles['cls-3']]


ds = 0.5  # delta-arclength; svg paths are interpolated with a step-size approximately matching this


def main():
    paths, colors = load_molecula_bug_paths(ds=0.5)
    path, color = combine_paths(paths, colors, ds=0.5)

    path = path.conj()
    path -= np.mean(path)
    animate_epicycles_linecollection(path, color, cmap, end_frames=50)


def load_molecula_bug_paths(ds=0.5):
    file = 'molecula-logo-bug.svg'

    paths = []
    colors = []
    svgpaths, attributes = svgpathtools.svg2paths(file)
    for n, (attrs, svgpath) in enumerate(zip(attributes, svgpaths)):

        cls = attrs['class']
        hexcolor = styles[cls]
        colors.append(hexcolor)
        print('path %d, class=%s, %d segments' % (n, cls, len(svgpath)))

        path = []
        for segment in svgpath:
            num_steps = int(segment.length()/ds)
            tt = np.linspace(0, 1, num_steps)
            xy = np.array([segment.point(t) for t in tt])
            if path and xy[0] == path[-1]:
                xy = xy[1:]
            path.extend(xy)
        paths.append(np.array(path))

    return paths, colors


def combine_paths(paths, colors, ds):
    # collapse list of paths into a single path,
    # connected by "blank" segments of similar step size.
    # also return a corresponding list of colormap indexes,
    # with color 0 = transparent for the blanks

    d1 = np.abs(paths[0][-1] - paths[1][0])
    blank1 = np.interp(np.linspace(0, 1, int(d1/ds)), [0, 1], [paths[0][-1], paths[1][0]])
    d2 = np.abs(paths[1][-1] - paths[2][0])
    blank2 = np.interp(np.linspace(0, 1, int(d2/ds)), [0, 1], [paths[1][-1], paths[2][0]])

    path = np.hstack((paths[0][:-1], blank1[:-1], paths[1][:-1], blank2[:-1], paths[2]))

    color = ([2] * (len(paths[0])-1) +
             [0] * (len(blank1)-1) +
             [3] * (len(paths[1])-1) +
             [0] * (len(blank2)-1) +
             [1] * len(paths[2]))
    return path, color


def animate_epicycles_linecollection(xy, colors, cmap, end_frames):
    # To use multiple colors, need to either
    # 1. use a different lineplot (expensive) for each colored segment, or
    # 2. use a different line element (cheap) for each step in the path.
    # option #2 seems simpler since the data is just the x, y, c arrays,
    # instead of a list of sets of those. but, that means using a LineCollection,
    # which is less familiar and has a clunkier interface.

    # compute DFT and sort by magnitude
    N = len(xy)
    t = np.linspace(0, 2*np.pi, N+1)
    Z = np.fft.fft(xy, N)/N
    k_sorted = np.argsort(-np.abs(Z))  # these indices can be thought of as the frequencies
    Z = Z[k_sorted]

    # set up plot stuff
    trace = []
    circle_plots = []
    for i in range(N):
        circle_plots.append(plt.plot([], [], 'gray', linewidth=0.5)[0])
    rad_plot = plt.plot([], [], 'k', linewidth=0.5)[0]

    cmap = ListedColormap(cmap)
    # TODO auto-size instead of hard-coded for 4 colors
    norm = BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], cmap.N)
    points = np.array([xy.real, xy.imag]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    trace_col = LineCollection(segments, array=colors, cmap=cmap, norm=norm,
                               zorder=10, linewidth=4, capstyle='round')
    plt.gca().add_collection(trace_col)

    plt.axis('equal')
    # TODO compute from paths
    plt.xlim([-30, 30])
    plt.ylim([-30, 30])
    plt.axis('off')
    plt.plot()

    # animate
    for n in range(len(Z)):
        # compute the IDFT sum, but with descending magnitudes
        centers = np.pad(np.cumsum(Z * np.exp(1j * k_sorted * t[n])), [1, 0])

        # update plot data
        rad_plot.set_data(centers.real, centers.imag)
        for i in range(20):
            circle_plots[i].set_data(np.abs(Z[i])*np.cos(t) + centers[i].real,
                                     np.abs(Z[i])*np.sin(t) + centers[i].imag)

        trace.append([centers[-1].real, centers[-1].imag])
        trace_col.set_array(np.pad(colors[:n], [0, len(colors)-n]))

        if PNG:
            print(n)
            plt.savefig('frames/%03d.png' % n)
        if PLOT:
            plt.draw()
            plt.pause(0.1)

    rad_plot.set_data([], [])
    for i in range(20):
        circle_plots[i].set_data([], [])

    for n in range(len(Z), len(Z)+end_frames):
        if PNG:
            print(n)
            plt.savefig('frames/%03d.png' % n)
        if PLOT:
            plt.draw()
            plt.pause(0.1)

    db()


main()
