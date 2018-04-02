# A script for calling KNN from cuda/script
#
# Note that the distance is calculated based on the maximum norm.
#
# Author: Peishi Jiang

import numpy as np
from sklearn.neighbors import KDTree, BallTree, DistanceMetric
import knn


def knn_scipy(querypts, refpts, k, approach='kdtree'):
    """KNN implementation based on scipy.

    Inputs:
    querypts -- the query points [numpy array with shape (qnpts, ndim)]
    refpts   -- the reference points [numpy array with shape (rnpts, ndim)]
    k        -- the number of nearest neighbor
    approach -- the approach for conducting KNN [string]

    Outputs:
    dist     -- the k nearest distances for querypts [numpy array with shape (qnpts, k)]
    ind      -- the indices of the k nearest neighbors for querypts [numpy array with shape (qpts, k)]
    """
    # The dimensions of querypts and refpts should be the same
    qnpts, qndim = querypts.shape
    rnpts, rndim = refpts.shape
    if qndim != rndim:
        raise Exception('The dimension of the query points %d is not the same as that of the reference points %d' % (qndim, rndim))
    else:
        ndim = qndim

    # k has to be smaller than or equal to rnpts
    if k > rnpts:
        raise Exception('k is larger than the number of reference points %d' % rnpts)

    # Define the maximum norm distance
    distmetric = DistanceMetric.get_metric('chebyshev')


    # Construct the KNN tree
    if approach is 'kdtree':
        tree = KDTree(refpts, metric=distmetric)
    elif approach is 'balltree':
        tree = BallTree(refpts, metric=distmetric)
    else:
        raise Exception('Unknown KNN search approach %s' % approach)

    # Conduct KNN
    dist, ind = tree.query(querypts, k=k)

    return dist, ind


def knn_cuda(querypts, refpts, k):
    """KNN implementation based on cuda.

    Inputs:
    querypts -- the query points [numpy array with shape (qnpts, ndim)]
    refpts   -- the reference points [numpy array with shape (rnpts, ndim)]
    k        -- the number of nearest neighbor

    Outputs:
    dist     -- the k nearest distances for querypts [numpy array with shape (qnpts, k)]
    ind      -- the indices of the k nearest neighbors for querypts [numpy array with shape (qpts, k)]
    """
    # Convert querypts and refpts to float32
    querypts = querypts.astype(np.float32)
    refpts   = refpts.astype(np.float32)

    # The dimensions of querypts and refpts should be the same
    qnpts, qndim = querypts.shape
    rnpts, rndim = refpts.shape
    if qndim != rndim:
        raise Exception('The dimension of the query points %d is not the same as that of the reference points %d' % (qndim, rndim))
    else:
        ndim = qndim

    # k has to be smaller than or equal to rnpts
    if k > rnpts:
        raise Exception('k is larger than the number of reference points %d' % rnpts)
    pass

    # Conduct KNN
    dist, ind = knn.knn(querypts.T, refpts.T, k)

    # Move the indices backward one step (Note that the returned ind starts from 1 instead of 0)
    ind -= 1

    # Transpose the matrices
    dist, ind = dist.T, ind.T

    return dist, ind


if __name__ == "__main__":
    # query = np.array([[1,2,3,4,5],
    #                   [1,3,5,7,9]], dtype='float32')
    # reference = query
    c = 128
    query = np.random.rand(1000,c).astype(np.float32)
    reference = np.random.rand(4000,c).astype(np.float32)

    k = 10

    # Scipy
    dist1, ind1 = knn_scipy(query, reference, k)

    # CUDA
    dist2, ind2 = knn_cuda(query, reference, k)

    print "Scipy result:"
    print dist1
    print ind1
    print ""
    print "CUDA result:"
    print dist2
    print ind2

    print np.sum(dist1 < 0.75*np.ones([1000,1]), axis=1)

    print np.sum(ind1-ind2)
