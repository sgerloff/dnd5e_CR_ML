from sklearn import preprocessing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


class Preprocessor:
    def __init__(self):
        self.to_scale = ["hp.average", "str", "dex", "con", "int", "wis", "cha", "speed.walk", "speed.fly",
                         "speed.burrow", "speed.swim", "speed.climb"]
        self.to_binarize = ["size", "conditionImmune", "conditionInflictSpell", "spellcastingTags", "conditionInflict",
                            "miscTags", "damageTags", "actionTags", "senseTags", "traitTags", "senses", "vulnerable",
                            "immune", "resist", "spellcasting"]
        self.to_vectorize = ["action", "reaction", "trait"]

        self.scaler = preprocessing.StandardScaler()
        self.binarizers = {}
        self.vectorizers = {}


    def fit(self, X, y=0):
        self.scaler.fit(X[self.to_scale])
        #Build binarizer Database:
        self.binarizers = {}
        for key in self.to_binarize:
            self.binarizers[key] = CountVectorizer(analyzer=set).fit(X[key])
        #Build vectorizer Database:
        self.vectorizers = {}
        for key in self.to_vectorize:
            self.vectorizers[key] = TfidfVectorizer(stop_words="english").fit(X[key].fillna(""))

    def transform(self, X, y=0):
        features = X.copy()

        tmp = features[self.to_scale]
        tmp = self.scaler.transform(tmp.values)
        features[self.to_scale] = tmp

        for key in self.to_binarize:
            tmp = features[key]
            tmp = pd.DataFrame(self.binarizers[key].transform(tmp).toarray(),
                               columns=self.binarizers[key].get_feature_names(),
                               index=features.index).add_prefix(key+"_")
            features = features.join(tmp)
            features.drop(key, axis=1, inplace=True)

        for key in self.to_vectorize:
            tmp = features[key].fillna("")
            tmp = pd.DataFrame(self.vectorizers[key].transform(tmp).toarray(),
                               columns=self.vectorizers[key].get_feature_names(),
                               index=features.index).add_prefix(key+"_")
            features = features.join(tmp)
            features.drop(key, axis=1, inplace=True)

        return features

    def fit_transform(self,X,y=0):
        self.fit(X)
        return self.transform(X)