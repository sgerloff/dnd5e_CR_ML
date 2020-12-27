import pandas as pd
from utility.monster_features import MonsterFeatures
from joblib import load

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

gb = load("data/gb_model.joblib")
predictions = gb.pipe.predict(gb.X_test)
wrong = gb.y_test != predictions

mf = MonsterFeatures()
mf.load("data/monster_features")
test_names = mf.df.loc[gb.X_test.index][["name"]]
test_names["predicted"] = predictions
test_names["true"] = gb.y_test

wrong_predictions = test_names[wrong]

for i in range(len(wrong_predictions)):
    name = wrong_predictions["name"].iloc[i]
    img = mpimg.imread('data/statblocks/' + name.replace('"','') + '.png')
    plt.imshow(img)
    plt.title("Predicted: {}; True: {}".format(wrong_predictions["predicted"].iloc[i], wrong_predictions["true"].iloc[i]))
    plt.show()