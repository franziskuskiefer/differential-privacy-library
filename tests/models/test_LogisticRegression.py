import numpy as np
from unittest import TestCase

from diffprivlib.models.logistic_regression import LogisticRegression
from diffprivlib.utils import global_seed, PrivacyLeakWarning, DiffprivlibCompatibilityWarning


class TestLogisticRegression(TestCase):
    def setup_method(self, method):
        global_seed(3141592653)

    def test_not_none(self):
        self.assertIsNotNone(LogisticRegression)

    def test_no_params(self):
        clf = LogisticRegression()

        X = np.array(
            [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50, 4.00, 4.25, 4.50, 4.75,
             5.00, 5.50])
        y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])
        X = X[:, np.newaxis]

        with self.assertWarns(PrivacyLeakWarning):
            clf.fit(X, y)

    def test_large_norm(self):
        X = np.array(
            [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50, 4.00, 4.25, 4.50, 4.75,
             5.00, 5.50])
        y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])
        X = X[:, np.newaxis]

        clf = LogisticRegression(data_norm=1.0)

        with self.assertWarns(PrivacyLeakWarning):
            clf.fit(X, y)

    def test_trinomial(self):
        X = np.array(
            [0.50, 0.75, 1.00])
        y = np.array([0, 1, 2])
        X = X[:, np.newaxis]

        clf = LogisticRegression(data_norm=1.0)

        self.assertIsNotNone(clf.fit(X, y))

    def test_solver_warning(self):
        with self.assertWarns(DiffprivlibCompatibilityWarning):
            LogisticRegression(solver="newton-cg")

    def test_multi_class_warning(self):
        with self.assertWarns(DiffprivlibCompatibilityWarning):
            LogisticRegression(multi_class="multinomial")

    def test_different_results(self):
        from sklearn import datasets
        from sklearn import linear_model
        from sklearn.model_selection import train_test_split

        dataset = datasets.load_iris()
        X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.2)

        clf = LogisticRegression(data_norm=12)
        clf.fit(X_train, y_train)

        predict1 = clf.predict(X_test)

        clf = LogisticRegression(data_norm=12)
        clf.fit(X_train, y_train)

        predict2 = clf.predict(X_test)

        clf = linear_model.LogisticRegression(solver="lbfgs", multi_class="ovr")
        clf.fit(X_train, y_train)

        predict3 = clf.predict(X_test)

        self.assertFalse(np.all(predict1 == predict2))
        self.assertFalse(np.all(predict3 == predict1) and np.all(predict3 == predict2))

    def test_same_results(self):
        from sklearn import datasets
        from sklearn.model_selection import train_test_split
        from sklearn import linear_model

        dataset = datasets.load_iris()
        X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.2)

        clf = LogisticRegression(data_norm=12, epsilon=float("inf"))
        clf.fit(X_train, y_train)

        predict1 = clf.predict(X_test)

        clf = linear_model.LogisticRegression(solver="lbfgs", multi_class="ovr")
        clf.fit(X_train, y_train)

        predict2 = clf.predict(X_test)

        self.assertTrue(np.all(predict1 == predict2))

    def test_simple(self):
        X = np.array(
            [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25, 3.50, 4.00, 4.25, 4.50, 4.75,
             5.00, 5.50])
        y = np.array([0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1])
        X = X[:, np.newaxis]
        X -= 3.0
        X /= 2.5

        clf = LogisticRegression(epsilon=2, data_norm=1.0)
        clf.fit(X, y)

        # print(clf.predict(np.array([0.5, 2, 5.5])))

        self.assertIsNotNone(clf)
        self.assertFalse(clf.predict(np.array([(0.5 - 3) / 2.5]).reshape(-1, 1)))
        self.assertTrue(clf.predict(np.array([(5.5 - 3) / 2.5]).reshape(-1, 1)))
