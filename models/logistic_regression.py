import pandas as pd
from utility.monster_features import MonsterFeatures
from sklearn.pipeline import Pipeline
from models.preprocessor import Preprocessor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from sklearn.model_selection import ShuffleSplit
from utility.plot_learning_curve import plot_learning_curve
import matplotlib.pyplot as plt


from joblib import dump, load

class LogisticRegressionModel:
    def __init__(self):
        self.X_train = pd.DataFrame()
        self.y_train = pd.DataFrame()
        self.X_test = pd.DataFrame()
        self.y_test = pd.DataFrame()

        self.original_features = pd.DataFrame()
        self.original_targets = pd.DataFrame()

        self.pipe = Pipeline([
            ("pre", Preprocessor()),
            ("clf", LogisticRegression(C=1.,max_iter=1000))
        ])

    def load_data(self, path):
        mf = MonsterFeatures()
        mf.load(path)
        self.original_features = mf.get_clean_features()
        self.original_targets = mf.get_target()
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.original_features,
                                                                                self.original_targets,
                                                                                test_size=0.33)

    def train(self):
        self.pipe.fit(self.X_train, self.y_train)

    def save(self, path):
        dump(self, path+".joblib")

    def plot_learning_curve(self):
        cv = ShuffleSplit(n_splits=3, test_size=0.2, random_state=0)
        title="Logisticregression Brute Force"
        plot_learning_curve(self.pipe, title,self.X_train,self.y_train, axes=None, ylim=(0.0, 1.01),train_sizes=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8, 0.9, 1.],cv=cv,n_jobs=-1)
        plt.show()

    # X_train = np.array(1)
    # X_test = np.array(1)
    # y_train = list()
    # y_test = list()
    #
    # number_of_samples = list()
    # train_scores = list()
    # test_scores = list()
    #
    # def __init__(self, X, y):
    #     #Rescale Features:
    #     scaler = preprocessing.StandardScaler().fit(X)
    #     X_scale = scaler.transform(X)
    #     #Split data set:
    #     self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X_scale, y, test_size=0.33)
    #
    # def plot_learning_curve(self, output_str):
    #     self.train_learning_curve()
    #     plt.figure()
    #     plt.plot(self.number_of_samples, self.train_scores, label="Training")
    #     plt.plot(self.number_of_samples, self.test_scores, label="Testing")
    #     plt.xlim(0, 900)
    #     plt.ylim(0, 1)
    #     plt.xlabel("# of samples")
    #     plt.ylabel("Accuracy Score")
    #     plt.title("Learning Curve")
    #     plt.legend()
    #     plt.savefig(output_str)
    #     plt.show()
    #
    # def train_learning_curve(self):
    #     self.number_of_samples = list()
    #     self.train_scores = list()
    #     self.test_scores = list()
    #     for i in range(10, len(self.y_train)):
    #         index = i + 1
    #         if index % 10 == 0:
    #             X_tmp = self.X_train[:index]
    #             y_tmp = self.y_train[:index]
    #             clf = LogisticRegression(max_iter=1000).fit(X_tmp, y_tmp)
    #             self.number_of_samples.append(index)
    #             self.train_scores.append(clf.score(X_tmp, y_tmp))
    #             self.test_scores.append(clf.score(self.X_test, self.y_test))