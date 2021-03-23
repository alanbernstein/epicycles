import time

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

from ipdb import set_trace as db
from panda.debug import pm


@pm
def main():
    N = 100

    tvec = np.linspace(0, 2*np.pi, N)

    r = (((0.0*np.pi<=tvec) * (tvec<=0.5*np.pi)) * 1/np.cos(tvec-0.25*np.pi) +
         ((0.5*np.pi<tvec) * (tvec<=1.0*np.pi)) * 1/np.cos(tvec-0.75*np.pi) +
         ((1.0*np.pi<tvec) * (tvec<=1.5*np.pi)) * 1/np.cos(tvec-1.25*np.pi) +
         ((1.5*np.pi<tvec) * (tvec<=2.0*np.pi)) * 1/np.cos(tvec-1.75*np.pi)
         )
    x_orig, y_orig = np.cos(tvec) * r, np.sin(tvec) * r
    z = x_orig + 1j*y_orig

    Z = np.fft.fft(z, N)/N
    freqs, rads, phases = np.arange(N), np.abs(Z), np.angle(Z)
    idx = np.argsort(-rads)
    Z, freqs, rads, phases = Z[idx], freqs[idx], rads[idx], phases[idx]

    rad_min = 0.01

    wave = []
    t = 0
    dt = 2*np.pi/len(Z)
    cc = np.exp(1j*np.linspace(0, 2*np.pi, 64))

    plt.ion()
    orig_plot = plt.plot(x_orig, y_orig, 'gray', linewidth=1)[0]
    rad_plot = plt.plot([], [], 'k-')[0]
    wave_plot = plt.plot([], [], 'r-')[0]
    circle_plots = []
    for k in range(N):
        circle_plots.append(plt.plot([], [], 'g-', linewidth=1)[0])
    plt.axis('equal')

    for k in range(len(Z)):
        x, y = 0, 0
        centers, xs, ys = [], [], []
        for i in range(N):
            prevx, prevy = x, y
            x = x + rads[i] * np.cos(freqs[i] * t + phases[i])
            y = y + rads[i] * np.sin(freqs[i] * t + phases[i])
            xs.append(x)
            ys.append(y)
            centers.append([prevx, prevy])

        rad_plot.set_data(xs, ys)
        for i in range(N):
            xx = rads[i] * cc.real + centers[i][0]
            yy = rads[i] * cc.imag + centers[i][1]
            circle_plots[i].set_data(xx, yy)

        t += dt

        wave.append([x, y])

        wave_plot.set_data(*zip(*wave))
        plt.draw()
        plt.pause(0.1)


main()
