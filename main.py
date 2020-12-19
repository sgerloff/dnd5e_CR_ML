import glob
from utility.monster_features import MonsterFeatures
from models.logistic_regression import logistic_regression_model
import numpy as np
import pandas as pd

# Preprocessing of JSON Files
list_of_bestiaries = glob.glob("data/bestiary/*.json")
mf = MonsterFeatures()

# mf.read_json_files(list_of_bestiaries)
# mf.clean_data()
# print(mf.df.info())
# mf.save("data/monster_features")

mf.load("data/monster_features")

features = mf.get_clean_features()
target = mf.get_target()

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.33)


from models.preprocessor import Preprocessor
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ("pre", Preprocessor()),
    ("clf", LogisticRegression(max_iter=1000))
])
pipe.fit(X_train, y_train)
print(pipe.score(X_train, y_train))
print(pipe.score(X_test,y_test))


