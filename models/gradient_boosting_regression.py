from models.logistic_regression import LogisticRegressionModel
import pandas as pd
from sklearn.pipeline import Pipeline
from models.preprocessor import Preprocessor
from sklearn.ensemble import GradientBoostingRegressor

from utility.monster_features import MonsterFeatures
from sklearn.model_selection import train_test_split

class GradientBoostingRegressionModel(LogisticRegressionModel):
    def __init__(self):
        self.X_train = pd.DataFrame()
        self.y_train = pd.DataFrame()
        self.X_test = pd.DataFrame()
        self.y_test = pd.DataFrame()

        self.original_features = pd.DataFrame()
        self.original_targets = pd.DataFrame()

        self.pipe = Pipeline([
            ("pre", Preprocessor()),
            ("clf", GradientBoostingRegressor(learning_rate=0.01, subsample=0.5, n_estimators=1000, verbose=1))
        ])


    def load_data(self, path):
        mf = MonsterFeatures()
        mf.load(path)
        self.original_features = mf.get_clean_features()
        self.original_targets = mf.get_target().apply(eval)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.original_features,
                                                                                self.original_targets,
                                                                                test_size=0.33)