from typing import List
import numpy as np
import sklearn
import sklearn.decomposition
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
import math
import scipy
from mne.decoding import LinearModel
from mne.decoding import get_coef


def n_cos(vect1, vect2):
    a = np.dot(vect1, vect2)
    b = math.sqrt(np.dot(vect1, vect1))
    c = math.sqrt(np.dot(vect2, vect2))
    d = a / (b * c)
    return d


def make_a(regres, x_train):
    a_list = []
    for i in range(np.shape(x_train)[0]):
        a = np.dot(regres, x_train[i, ...])
        a_list.append(a)
    return np.array(a_list)


# return None
# return regression object
# return simple regression object


def make_b(regres, x_train):
    b_list = []
    for i in range(x_train[0]):
        b = np.dot(x_train[i, ...], regres)
        b_list.append(b)
    return np.array(b_list)


# make with inheritance (use super_init_ method)

def simple_linear_regression(alphas, repr_train, repr_val, y_train, y_val, zone, normalize):
    scores_mse = []
    models_a1: List[Ridge] = []
    for index, alpha in enumerate(alphas):
        ridgereg_a = Ridge(alpha, normalize)
        ridgereg_a.fit(repr_train, y_train[:, zone])
        predicted_y_test_a = ridgereg_a.predict(repr_val)
        scores_mse.append(sklearn.metrics.mean_squared_error(y_val[:, zone], predicted_y_test_a))
        models_a1.append(ridgereg_a)
    ind = scores_mse.index(min(scores_mse))
    coefs = models_a1[ind].coef_
    model = models_a1[ind]
    return np.array(coefs), model


def patterns_evaluation(model):
    coef_list = []
    for name, i in zip(['patterns_', 'filters_'], [0, 1]):
        coef = get_coef(model, name, inverse_transform=True)
        coef_list.append(coef)
    return coef_list


# make noise with latent variables
# x_train dimensions N*FT
# optimize with results from ret
# make original  forecasting our signal
class linear_pattern_recognition:
    # class for finding patterns of ROI
    # add marks for anatomic T1
    # add splines to functions ft-fd

    def __init__(self, alphas=np.logspace(-3, 3, 7), normalize=False, epsilon=0.5):
        self.alphas = alphas
        self.normalize = normalize
        self.epsilon = epsilon
        self.topo_coefs_ = None
        self.spect_coefs_ = None
        self.model = None
        self.len_zones = None
        self.mse_scores = None
        self.pearson_scores = None
        self.r2_scores = None
        self.patterns_topo_ = None
        self.patterns_spect_ = None

    def fit(self, x_train, x_val, y_train, y_val):
        self.len_zones = np.shape(y_train)[1]
        len_chan = np.shape(x_train)[1]
        len_spect = np.shape(x_train)[2]
        models = []
        topo_coefs: List[None] = []
        spect_coefs: List[None] = []
        for zone in range(self.len_zones):
            topo_regr0 = np.random.rand(1, len_chan)
            spect_regr0 = np.random.rand(len_spect, 1)
            cos_regr1 = 1
            cos_regr2 = 1
            model = None
            topo_regr1 = None
            spect_regr1 = None

            while cos_regr1 > self.epsilon and cos_regr2 > self.epsilon:
                spect_repr_train = make_a(topo_regr0, x_train)
                spect_repr_val = make_a(topo_regr0, x_val)
                a_coefs, _ = simple_linear_regression(self.alphas, spect_repr_train, spect_repr_val, y_train, y_val,
                                                      zone,
                                                      self.normalize)
                spect_regr1 = a_coefs.reshape(len_spect, 1)
                cos_regr1 = n_cos(spect_regr0, spect_regr1)
                topo_repr_train = make_b(spect_regr1, x_train)
                topo_repr_val = make_b(spect_regr1, x_train)
                b_coefs, model = simple_linear_regression(self.alphas, topo_repr_train, topo_repr_val, y_train, y_val,
                                                          zone,
                                                          self.normalize)
                topo_regr1 = b_coefs.reshape(1, len_chan)
                cos_regr2 = n_cos(topo_regr0, topo_regr1)
                topo_regr0 = topo_regr1
                spect_regr0 = spect_regr1
            models.append(model)
            # check this statement
            topo_coefs.append(topo_regr1)
            spect_coefs.append(spect_regr1)
        self.topo_coefs_ = topo_coefs
        self.spect_coefs_ = spect_coefs
        self.model = models
        self.patterns_spect_ = patterns_evaluation(topo_coefs)
        self.patterns_topo_ = patterns_evaluation(spect_coefs)
        return self

    def test(self, x_test, y_test):
        """

        :rtype: object
        """ 

        predicted_values = []
        scores_mse = []
        scores_r2 = []
        scores_pearson = []
        for zone in range(self.len_zones):
            predicted_y_test = self.model.predict(x_test)
            predicted_values.append(predicted_y_test)
            scores_mse.append(sklearn.metrics.mean_squared_error(y_test[:, zone], predicted_y_test))
            scores_r2.append(sklearn.metrics.r2_score(y_test[:, zone], predicted_y_test))
            scores_pearson.append(scipy.stats.pearsonr(y_test[:, zone], predicted_y_test)[0])
        self.mse_scores = scores_mse
        self.r2_scores = scores_r2
        self.pearson_scores = scores_pearson
        return predicted_values
