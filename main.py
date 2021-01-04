import glob
from utility.monster_features import MonsterFeatures

# Preprocessing of JSON Files
list_of_bestiaries = glob.glob("data/bestiary/*.json")
mf = MonsterFeatures()

# mf.read_json_files(list_of_bestiaries)
# mf.clean_data()
# # print(mf.df.info())
# mf.save("data/monster_features")

mf.load("data/monster_features")



#Generate Summary
# cv = ShuffleSplit(n_splits=3, test_size=0.2, random_state=0)
# title="Logisticregression Brute Force"
# plot_learning_curve(pipe, title,features,target, axes=None, ylim=(0.0, 1.01),train_sizes=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8, 0.9, 1.],cv=cv,n_jobs=-1)
# plt.show()

# from models.logistic_regression import LogisticRegressionModel
# lr = LogisticRegressionModel()
# lr.load_data("data/monster_features")
# lr.train()
# print(lr.pipe.score(lr.X_train, lr.y_train))
# print(lr.pipe.score(lr.X_test, lr.y_test))
# lr.save("data/lr_model")
# #
# lr.plot_learning_curve()
#
# from models.gradient_boosting import GradientBoostingModel
# gb = GradientBoostingModel()
# gb.load_data("data/monster_features")
# gb.train()
# print(gb.pipe.score(gb.X_train, gb.y_train))
# print(gb.pipe.score(gb.X_test, gb.y_test))
# gb.save("data/gb_model")
# #
# gb.plot_learning_curve()

from models.gradient_boosting_regression import GradientBoostingRegressionModel
gbr = GradientBoostingRegressionModel()
gbr.load_data("data/monster_features")
gbr.train()
print(gbr.pipe.score(gbr.X_train, gbr.y_train))
print(gbr.pipe.score(gbr.X_test, gbr.y_test))
gbr.save("data/gbr_model")