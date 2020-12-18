from sklearn import preprocessing


class StandardScalerWrapper:
    def __init__(self):
        self.standard_scaler = preprocessing.StandardScaler()

    def fit(self, X, y=0):
        if "numeric" in X.columns:
            return self.standard_scaler.fit(X["numeric"])
        else:
            print("Warning: No numeric data in df found!")

    def transform(self, X, y=0):
        if "numeric" in X.columns:
            X["numeric"] = self.standard_scaler.transform(X["numeric"])
            return X
        else:
            print("Warning: No numeric data in df found!")
