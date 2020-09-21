"""
Tests sklearn KNeighbor model (KNeighborsClassifier) converters.
"""
import unittest
import warnings

import numpy as np
import torch
from sklearn.neighbors import KNeighborsClassifier
from sklearn import datasets

import hummingbird.ml


class TestSklearnKNeighborsClassifiers(unittest.TestCase):
    def _test_kneighbors_classifier(
        self,
        n_neighbors=5,
        algorithm="brute",
        weights="uniform",
        metric="minkowski",
        metric_params={"p": 2},
        score_w_train_data=False,
    ):
        model = KNeighborsClassifier(
            n_neighbors=n_neighbors, algorithm=algorithm, weights=weights, metric=metric, metric_params=metric_params
        )

        for data in [datasets.load_breast_cancer(), datasets.load_iris()]:
            X, y = data.data, data.target
            X = X.astype(np.float32)

            n_train_rows = int(X.shape[0] * 0.6)
            model.fit(X[:n_train_rows, :], y[:n_train_rows])

            if not score_w_train_data:
                X = X[n_train_rows:, :]

            extra_config = {hummingbird.ml.operator_converters.constants.BATCH_SIZE: X.shape[0]}
            torch_model = hummingbird.ml.convert(model, "torch", extra_config=extra_config)
            self.assertTrue(torch_model is not None)
            np.testing.assert_allclose(model.predict_proba(X), torch_model.predict_proba(X), rtol=1e-6, atol=1e-5)

    # KNeighborsClassifier
    def test_kneighbors_classifer(self):
        self._test_kneighbors_classifier()

    # KNeighborsClassifier kdtree algorithm
    def test_kneighbors_classifer_kdtree(self):
        self._test_kneighbors_classifier(algorithm="kd_tree")

    # KNeighborsClassifier ball tree algorithm
    def test_kneighbors_classifer_balltree(self):
        self._test_kneighbors_classifier(algorithm="ball_tree")

    # KNeighborsClassifier auto algorithm
    def test_kneighbors_classifer_auto(self):
        self._test_kneighbors_classifier(algorithm="auto")

    # KNeighborsClassifier weights distance
    def test_kneighbors_classifer_distance_weight(self):
        self._test_kneighbors_classifier(3, weights="distance")

    # KNeighborsClassifier weights distance w train data
    def test_kneighbors_classifer_distance_weight_train_data(self):
        self._test_kneighbors_classifier(3, weights="distance", score_w_train_data=True)

    # KNeighborsClassifier euclidean metric type
    def test_kneighbors_classifer_euclidean(self):
        self._test_kneighbors_classifier(3, metric="euclidean")

    # KNeighborsClassifier minkowski metric p = 5
    def test_kneighbors_classifer_minkowski_p5(self):
        self._test_kneighbors_classifier(3, metric_params={"p": 5})


if __name__ == "__main__":
    unittest.main()
