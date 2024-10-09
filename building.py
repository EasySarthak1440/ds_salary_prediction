

import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import joblib  # Import joblib for saving and loading models
import warnings

df = pd.read_csv('eda_data.csv')

# choose relevant columns 
df.columns

df_model = df[['avg_salary','Rating','Size','Type of ownership','Industry','Sector','Revenue','hourly',
             'job_state','age','python_yn','spark','cloud','machine_learning','statistics','job_simp','seniority','desc_len']]

# get dummy data 
df_dum = pd.get_dummies(df_model)

# train test split 
from sklearn.model_selection import train_test_split

X = df_dum.drop('avg_salary', axis=1)
y = df_dum.avg_salary.values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# multiple linear regression 
import statsmodels.api as sm

# Ensure X and y are numpy arrays and have the correct dtype
X_np = np.asarray(X).astype(np.float64)
y_np = np.asarray(y).astype(np.float64)

X_sm = sm.add_constant(X_np)
model = sm.OLS(y_np, X_sm)
results = model.fit()
print(results.summary())

from sklearn.linear_model import LinearRegression, Lasso
from sklearn.model_selection import cross_val_score

lm = LinearRegression()
lm.fit(X_train, y_train)

np.mean(cross_val_score(lm, X_train, y_train, scoring='neg_mean_absolute_error', cv=3))

# lasso regression 
lm_l = Lasso(alpha=0.13, max_iter=100000, warm_start=True)  # Using warm_start=True
lm_l.fit(X_train, y_train)
np.mean(cross_val_score(lm_l, X_train, y_train, scoring='neg_mean_absolute_error', cv=3))

alpha = []
error = []

for i in range(1, 100):
    alpha_val = i / 100
    alpha.append(alpha_val)
    lml = Lasso(alpha=alpha_val, max_iter=100000, warm_start=True)  # Using warm_start=True
    error.append(np.mean(cross_val_score(lml, X_train, y_train, scoring='neg_mean_absolute_error', cv=3)))

plt.plot(alpha, error)

err = tuple(zip(alpha, error))
df_err = pd.DataFrame(err, columns=['alpha', 'error'])
best_alpha = df_err.loc[df_err['error'].idxmax()]['alpha']

print("Best alpha:", best_alpha)

# random forest 
from sklearn.ensemble import RandomForestRegressor
rf = RandomForestRegressor()

np.mean(cross_val_score(rf, X_train, y_train, scoring='neg_mean_absolute_error', cv=3))

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor()

parameters = {
    'n_estimators': range(50, 100, 150),
    'criterion': ('squared_error', 'absolute_error'),
    'max_features': ('sqrt', 'log2', None)  # Replace 'auto' with None
}

gs = GridSearchCV(rf, parameters, scoring='neg_mean_absolute_error', cv=3)
gs.fit(X_train, y_train)

best_score = gs.best_score_
best_estimator = gs.best_estimator_

print(f'Best Score: {best_score}')
print(f'Best Estimator: {best_estimator}')

# Test ensembles
tpred_lm = lm.predict(X_test)
tpred_lml = lm_l.predict(X_test)
tpred_rf = best_estimator.predict(X_test)

from sklearn.metrics import mean_absolute_error

mae_lm = mean_absolute_error(y_test, tpred_lm)
mae_lml = mean_absolute_error(y_test, tpred_lml)
mae_rf = mean_absolute_error(y_test, tpred_rf)
mae_ensemble = mean_absolute_error(y_test, (tpred_lm + tpred_rf) / 2)

print(f'MAE Linear Regression: {mae_lm}')
print(f'MAE Lasso Regression: {mae_lml}')
print(f'MAE Random Forest: {mae_rf}')
print(f'MAE Ensemble: {mae_ensemble}')


# Save the model using joblib

model_file = 'model_file.joblib'
joblib.dump(gs.best_estimator_, model_file)


# Load the model using joblib
model = joblib.load(model_file)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    
# Make a prediction using the correct DataFrame structure
prediction = model.predict(X_test.iloc[1, :].to_frame().T)

# Print the prediction and the feature values
print("Prediction:", prediction)
print("Feature values:", list(X_test.iloc[1, :]))
