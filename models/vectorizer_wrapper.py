from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


class VectorizerWrapper:
    def __init__(self, *args, **kwargs):
        self.vectorizer = TfidfVectorizer(*args, **kwargs)
        self.vectorizer_dict = {}

    def fit(self, X, y=0):
        if "string" in X.columns:
            self.__fit_columns(X)
        else:
            print("Warning: No string columns found!")

    def __fit_columns(self, X):
        for c in X["string"].columns:
            X["string", c].fillna("", inplace=True)
            tmp = TfidfVectorizer()
            tmp.set_params(**self.vectorizer.get_params())
            self.vectorizer_dict[c] = tmp.fit(X["string", c])

    def transform(self, X, y=0):
        if "string" in X.columns:
            X = self.__transform_columns(X)
            return X.drop("string", axis=1, level=0)
        else:
            print("Warning: No string columns found!")

    def __transform_columns(self, X):
        for c in X["string"].columns:
            tmp_df = pd.DataFrame(self.vectorizer_dict[c].transform(X["string", c]).toarray(),
                                  columns=pd.MultiIndex.from_product([['vectorized_' + c],
                                                                      self.vectorizer_dict[c].get_feature_names()]),
                                  index=X.index)
            X = X.join(tmp_df)
        return X
