from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

import numpy as np

import matplotlib.pyplot as plt

class logistic_regression_model:
    X_train = np.array(1)
    X_test = np.array(1)
    y_train = list()
    y_test = list()

    number_of_samples = list()
    train_scores = list()
    test_scores = list()

    def __init__(self, X, y):
        #Rescale Features:
        scaler = preprocessing.StandardScaler().fit(X)
        X_scale = scaler.transform(X)
        #Split data set:
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_scale, y, test_size=0.33, random_state=0)

    def plot_learning_curve(self, output_str):
        self.train_learning_curve()
        plt.figure()
        plt.plot(self.number_of_samples, self.train_scores, label="Training")
        plt.plot(self.number_of_samples, self.test_scores, label="Testing")
        plt.xlim(0, 900)
        plt.ylim(0, 1)
        plt.xlabel("# of samples")
        plt.ylabel("Accuracy Score")
        plt.title("Learning Curve")
        plt.legend()
        plt.savefig(output_str)
        plt.show()

    def train_learning_curve(self):
        self.number_of_samples = list()
        self.train_scores = list()
        self.test_scores = list()
        for i in range(10, len(self.y_train)):
            index = i + 1
            if index % 10 == 0:
                X_tmp = self.X_train[:index]
                y_tmp = self.y_train[:index]
                clf = LogisticRegression(random_state=0, max_iter=1000).fit(X_tmp, y_tmp)
                self.number_of_samples.append(index)
                self.train_scores.append(clf.score(X_tmp, y_tmp))
                self.test_scores.append(clf.score(self.X_test, self.y_test))