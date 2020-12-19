import pandas as pd
from utility.monster_features import MonsterFeatures
from sklearn.pipeline import Pipeline
from models.preprocessor import Preprocessor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from joblib import dump, load

class LogisticRegressionModel:
    def __init__(self):
        self.X_train = pd.DataFrame()
        self.y_train = pd.DataFrame()
        self.X_test = pd.DataFrame()
        self.y_test = pd.DataFrame()

        self.pipe = Pipeline([
            ("pre", Preprocessor()),
            ("clf", LogisticRegression(C=1.,max_iter=1000))
        ])

    def load_data(self, path):
        mf = MonsterFeatures()
        mf.load(path)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(mf.get_clean_features(),
                                                                                mf.get_target(),
                                                                                test_size=0.33)

    def train(self):
        self.pipe.fit(self.X_train, self.y_train)

    def save(self, path):
        dump(self, path+".joblib")

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