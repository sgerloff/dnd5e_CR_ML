import glob
from utility.monster_features import MonsterFeatures

# Preprocessing of JSON Files
list_of_bestiaries = glob.glob("data/bestiary/*.json")
mf = MonsterFeatures()

# mf.read_json_files(list_of_bestiaries)
# mf.clean_data()
# print(mf.df.info())
# mf.save("data/monster_features")

mf.load("data/monster_features")

features = mf.get_features()
target = mf.get_target()

from models.logistic_regression import logistic_regression_model
model = logistic_regression_model(features,target)
model.plot_learning_curve( 'data/leaning_curve_logistic_regression_tag_features.png' )

