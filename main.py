import glob
from utility.monster_features import MonsterFeatures
from utility.plot_learning_curve import plot_learning_curve
import matplotlib.pyplot as plt
from models.preprocessor import Preprocessor
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit

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

pipe = Pipeline([
    ("pre", Preprocessor()),
    ("clf", LogisticRegression(C=0.1,max_iter=1000))
])

#Generate Summary
cv = ShuffleSplit(n_splits=3, test_size=0.2, random_state=0)
title="Logisticregression Brute Force"
plot_learning_curve(pipe, title,features,target, axes=None, ylim=(0.0, 1.01),train_sizes=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8, 0.9, 1.],cv=cv,n_jobs=-1)
plt.show()
