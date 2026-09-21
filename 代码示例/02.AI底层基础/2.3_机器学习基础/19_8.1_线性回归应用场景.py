from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

# 特征：面积(数值)、位置(类别)、房龄(数值)
preprocessor = ColumnTransformer([
    ('num', 'passthrough', ['area', 'age']),
    ('cat', OneHotEncoder(), ['location'])
])

# 管道化处理
from sklearn.pipeline import Pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

model.fit(X_train, y_train)
predictions = model.predict(X_test)
