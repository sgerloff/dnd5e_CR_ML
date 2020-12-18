import glob
from utility.monster_features import MonsterFeatures
from models.logistic_regression import logistic_regression_model
import numpy as np

# Preprocessing of JSON Files
list_of_bestiaries = glob.glob("data/bestiary/*.json")
mf = MonsterFeatures()

# mf.read_json_files(list_of_bestiaries)
# mf.clean_data()
# print(mf.df.info())
# mf.save("data/monster_features")

mf.load("data/monster_features")

# Simple Logistic Regression Learning Curve
# features = mf.get_clean_features()[["numeric", "one_hot"]]
# target = mf.get_target()
# model = logistic_regression_model(features, target)
# model.plot_learning_curve('data/leaning_curve_logistic_regression_tag_features.png')
#



from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(mf.get_clean_features(), mf.get_target(), test_size=0.33)

from models.standard_scaler_wrapper import StandardScalerWrapper

scaler = StandardScalerWrapper()
scaler.fit(X_train)
X_train = scaler.transform(X_train)

from models.vectorizer_wrapper import VectorizerWrapper

vectorizer = VectorizerWrapper(stop_words="english")
vectorizer.fit(X_train)
X_train = vectorizer.transform(X_train)


from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(max_iter=1000).fit(X_train, y_train)
print(clf.score(X_train, y_train))
X_test = scaler.transform(X_test)
X_test = vectorizer.transform(X_test)
print(clf.score(X_test, y_test))

from sklearn.pipeline import Pipeline

# pipe = Pipeline([("scaler", StandardScalerWrapper()),
#                  ("vectorizer", VectorizerWrapper(stop_words="english")),
#                  ("clf", LogisticRegression(max_iter=1000))])
#
# pipe.fit(X_train,y_train)
# print(pipe.score(X_test,y_test))

# TODO: trait, action, reaction, spellcasting
