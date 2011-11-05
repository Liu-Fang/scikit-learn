"""
============================================================
Empirical evaluation of the impact of k-means initialization
============================================================

Evaluate the ability of k-means initializations strategies to make
the algorithm convergence robust as measured by the relative standard
deviation of the inertia of the clustering (i.e. the sum of distances
to the nearest cluster center).

The dataset used for evaluation is a 2D grid of isotropic gaussian
clusters widely spaced.

"""
print __doc__

# Author: Olivier Grisel <olivier.grisel@ensta.org>
# License: Simplified BSD

import numpy as np
import pylab as pl
import matplotlib.cm as cm

from sklearn.utils import shuffle
from sklearn.utils import check_random_state
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import KMeans

random_state = np.random.RandomState(0)

# Number of run (with randomly generated dataset) for each strategy so as
# to be able to compute an estimate of the standard deviation
n_runs = 5

# k-means models can do several random inits so as to be able to trade
# CPU time for convergence robustness
n_init_range = np.array([1, 5, 10, 15])

# Datasets generation parameters
n_samples_per_center = 100
grid_size = 3
n_clusters = grid_size ** 2


def make_data(random_state, n_samples_per_center, grid_size):
    random_state = check_random_state(random_state)
    centers = np.array([[i, j]
                        for i in range(grid_size)
                        for j in range(grid_size)])
    n_clusters_true, n_featues = centers.shape
    n_samples_per_center = 100

    noise = random_state.normal(scale=0.1, size=(n_samples_per_center, 2))
    X = np.concatenate([c + noise for c in centers])
    y = np.concatenate([[i] * n_samples_per_center
                        for i in range(n_clusters_true)])
    return shuffle(X, y, random_state=random_state)


# Batch k-means with various init

experiments = []
for init in ['k-means++', 'random']:
    print "Evaluation of batch k-means with %s init" % init
    inertia = np.empty((len(n_init_range), n_runs))

    for run_id in range(n_runs):
        X, y = make_data(run_id, n_samples_per_center, grid_size)
        for i, n_init in enumerate(n_init_range):
            km = KMeans(k=n_clusters,
                        init=init,
                        random_state=run_id,
                        verbose=0,
                        n_init=n_init).fit(X)
            inertia[i, run_id] = km.inertia_
            print "Inertia for n_init=%02d, run_id=%d: %0.3f" % (
                n_init, run_id, km.inertia_)
    experiments.append((init, inertia))

fig = pl.figure()
plots = []
legends = []
for init, inertia in experiments:
    plots.append(
        pl.errorbar(n_init_range, inertia.mean(axis=1), inertia.std(axis=1)))
    legends.append("k-means with %s init" % init)

pl.xlabel('n_init')
pl.ylabel('inertia')
pl.legend(plots, legends)
pl.title("Mean and Std deviation inertia for various k-means init")

# Part 2: qualitative visual inspection of the convergence

#X, y = make_data(random_state, n_samples_per_center, grid_size)
#km = MiniBatchKMeans(k=n_clusters, random_state=0, verbose=1,
#                     max_iter=100).fit(X)
#
#fig = pl.figure()
#for k in range(n_clusters):
#    my_members = km.labels_ == k
#    color = cm.spectral(float(k) / n_clusters, 1)
#    pl.plot(X[my_members, 0], X[my_members, 1], 'o', marker='.', c=color)
#    cluster_center = km.cluster_centers_[k]
#    pl.plot(cluster_center[0], cluster_center[1], 'o',
#            markerfacecolor=color, markeredgecolor='k', markersize=6)
#    pl.title("Example cluser allocation with a single random init")

pl.show()