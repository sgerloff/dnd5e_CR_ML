from models.logistic_regression import LogisticRegressionModel
import pandas as pd
from sklearn.pipeline import Pipeline
from models.preprocessor import Preprocessor
from sklearn.ensemble import GradientBoostingClassifier


class GradientBoostingModel(LogisticRegressionModel):
    def __init__(self):
        self.X_train = pd.DataFrame()
        self.y_train = pd.DataFrame()
        self.X_test = pd.DataFrame()
        self.y_test = pd.DataFrame()

        self.original_features = pd.DataFrame()
        self.original_targets = pd.DataFrame()

        self.pipe = Pipeline([
            ("pre", Preprocessor()),
            ("clf", GradientBoostingClassifier(learning_rate=0.01, subsample=0.5, n_estimators=1000, verbose=1))
        ])