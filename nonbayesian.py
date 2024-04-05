# -*- coding: utf-8 -*-
"""SVM(including RVM now).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iQRzrpw6pFbNZzYVL6A3CRrWfPERlAaB
"""

# Commented out IPython magic to ensure Python compatibility.
# Imported Libraries

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA, TruncatedSVD
import tensorflow as tf
import matplotlib.patches as mpatches
import time

# Classifier Libraries
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import collections

# Other Libraries
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from imblearn.pipeline import make_pipeline as imbalanced_make_pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import NearMiss
from imblearn.metrics import classification_report_imbalanced
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score, classification_report, mean_squared_error
from collections import Counter
from sklearn.model_selection import KFold, StratifiedKFold
import warnings
warnings.filterwarnings("ignore")

# %matplotlib inline

"""**Section 1** \\
**Data Pre-processing**
"""

from google.colab import drive
drive.mount('/content/drive')
file_path = '/content/drive/My Drive/MLB_Project/creditcard.csv'  #sometimes the path of file may change

data = pd.read_csv(file_path) # Reading the file .csv
df = pd.DataFrame(data) # Converting data to Panda DataFrame

df.shape
# df.head()

target = df['Class'].value_counts()
num_legit = target[0]
num_fraud = target[1]
print(num_legit)
print(num_fraud)

categories = ['legit', 'fraud']
quantities = [num_legit, num_fraud]

plt.bar(categories, quantities, color=['blue', 'red'])


plt.title('Legit vs Fraud Transactions')
plt.xlabel('Transaction Type')
plt.ylabel('Quantity')

plt.show()

"""From the Histogram above we can conclude that the data set is unbalanced thus we need to re-select the data for training so we need to create a **sub-sample** set. Besides, all of the data have been scaled except **Time** and **Amount**, we gonna scale them."""

from sklearn.preprocessing import StandardScaler, RobustScaler

# RobustScaler is less prone to outliers.

std_scaler = StandardScaler()
rob_scaler = RobustScaler()

df['scaled_amount'] = rob_scaler.fit_transform(df['Amount'].values.reshape(-1,1))
df['scaled_time'] = rob_scaler.fit_transform(df['Time'].values.reshape(-1,1))

df.drop(['Time','Amount'], axis=1, inplace=True)

# After that, we split the data, and then undersampling

from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit

print('No Frauds', round(df['Class'].value_counts()[0]/len(df) * 100,2), '% of the dataset')
print('Frauds', round(df['Class'].value_counts()[1]/len(df) * 100,2), '% of the dataset')

X = df.drop('Class', axis=1)
y = df['Class']

sss = StratifiedKFold(n_splits=5, random_state=None, shuffle=False)

for train_index, test_index in sss.split(X, y):
    print("Train:", train_index, "Test:", test_index)
    original_Xtrain, original_Xtest = X.iloc[train_index], X.iloc[test_index]
    original_ytrain, original_ytest = y.iloc[train_index], y.iloc[test_index]

# Turn into an array
original_Xtrain = original_Xtrain.values
original_Xtest = original_Xtest.values
original_ytrain = original_ytrain.values
original_ytest = original_ytest.values

# See if both the train and test label distribution are similarly distributed
train_unique_label, train_counts_label = np.unique(original_ytrain, return_counts=True)
test_unique_label, test_counts_label = np.unique(original_ytest, return_counts=True)
print('-' * 100)

print('Label Distributions: \n')
print(train_counts_label/ len(original_ytrain))
print(test_counts_label/ len(original_ytest))
original_ytest.shape

## Sub-sampling

df = df.sample(frac=1)

# amount of fraud classes 492 rows keep them consistent.
fraud_df = df.loc[df['Class'] == 1]
non_fraud_df = df.loc[df['Class'] == 0][:492]

normal_distributed_df = pd.concat([fraud_df, non_fraud_df])

# Shuffle dataframe rows
new_df = normal_distributed_df.sample(frac=1, random_state=42)

new_df.shape
print('Distribution of the Classes in the subsample dataset')
print(new_df['Class'].value_counts()/len(new_df))

"""**Section 2**

**Undersampling and model selection**
"""

## Split the balanced data into train and test
X = new_df.drop('Class', axis=1)
y = new_df['Class']

# NearMiss

from imblearn.under_sampling import NearMiss
from collections import Counter
from sklearn.neural_network import MLPClassifier

# from skrvm import RVR,RVC
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten
from sklearn.metrics import mean_squared_error, confusion_matrix
from keras.utils import to_categorical, plot_model
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import EarlyStopping

nm = NearMiss()

# Undersample the majority class
X_resampled, y_resampled = nm.fit_resample(X, y)

print("Class distribution after Near-Miss undersampling:", Counter(y_resampled))

# This is explicitly used for undersampling.
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Turn the values into an array for feeding the classification algorithms.
X_train = X_train.values
X_test = X_test.values
y_train = y_train.values
y_test = y_test.values


classifiers = {
    "LogisticRegression": LogisticRegression(),
    "KNearest": KNeighborsClassifier(),
    "Support Vector Classifier": SVC(),
    "DecisionTreeClassifier": DecisionTreeClassifier(),
    "MLPClassifier": MLPClassifier(),
    # "CNN": cnn_model
    # "RVMClassifier": RVC()
}

"""*Training the dataset and envaluate each classifiers by accuracy and other scores etc.*"""

from sklearn.model_selection import cross_val_score


for key, classifier in classifiers.items():
    classifier.fit(X_train, y_train)
    training_score = cross_val_score(classifier, X_train, y_train, cv=5) #including cross-validation
    print("Classifiers: ", classifier.__class__.__name__, "Has a training score of", round(training_score.mean(), 2) * 100, "% accuracy score")

# Grid search part
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC, SVR, NuSVC, NuSVR
from sklearn.linear_model import BayesianRidge

# Logistic Regression
log_reg_params = {"penalty": ['l1', 'l2'], 'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}

grid_log_reg = GridSearchCV(LogisticRegression(), log_reg_params)
grid_log_reg.fit(X_train, y_train)
# We automatically get the logistic regression with the best parameters.
log_reg = grid_log_reg.best_estimator_
log_reg_best_params = grid_log_reg.best_params_

# KNN
knears_params = {"n_neighbors": list(range(2,5,1)), 'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']}

grid_knears = GridSearchCV(KNeighborsClassifier(), knears_params)
grid_knears.fit(X_train, y_train)
# KNears best estimator
knears_neighbors = grid_knears.best_estimator_
knears_best_params = grid_knears.best_params_

# SVC

svc_params = {'C': [0.5, 0.7, 0.9, 1], 'kernel': ['rbf', 'poly', 'sigmoid', 'linear'], 'gamma': ['scale', 'auto']}
grid_svc = GridSearchCV(SVC(), svc_params)
grid_svc.fit(X_train, y_train)
# SVC best estimator
svc = grid_svc.best_estimator_
svc_best_params = grid_svc.best_params_

# Decision Tree

tree_params = {"criterion": ["gini", "entropy"], "max_depth": list(range(2,4,1)),
              "min_samples_leaf": list(range(5,7,1))}
grid_tree = GridSearchCV(DecisionTreeClassifier(), tree_params)
grid_tree.fit(X_train, y_train)
# tree best estimator
tree_clf = grid_tree.best_estimator_
tree_best_params = grid_tree.best_params_


# MLP classifier

mlp_params = {
    'hidden_layer_sizes': [(50,50,50), (50,100,50), (100,)],
    'activation': ['relu', 'tanh', 'logistic'],
    'solver': ['sgd', 'adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant','adaptive'],
}

grid_mlp = GridSearchCV(MLPClassifier(), mlp_params)
grid_mlp.fit(X_train, y_train)
# MLP best estimator
mlp_clf = grid_mlp.best_estimator_
mlp_best_params = grid_mlp.best_params_

# Output best parameters for each model
best_params_dict = {
    "Logistic Regression": log_reg_best_params,
    "KNN": knears_best_params,
    "SVC": svc_best_params,
    "Decision Tree": tree_best_params,
    "MLP": mlp_best_params,
    # "RVM": rvc_best_params
}

print("Best parameters for each model:")
for model, params in best_params_dict.items():
    print(f"{model}: {params}")

# Overfitting Case

log_reg_score = cross_val_score(log_reg, X_train, y_train, cv=5)
print('Logistic Regression Cross Validation Score: ', round(log_reg_score.mean() * 100, 2).astype(str) + '%')


knears_score = cross_val_score(knears_neighbors, X_train, y_train, cv=5)
print('Knears Neighbors Cross Validation Score', round(knears_score.mean() * 100, 2).astype(str) + '%')

svc_score = cross_val_score(svc, X_train, y_train, cv=5)
print('Support Vector Classifier Cross Validation Score', round(svc_score.mean() * 100, 2).astype(str) + '%')

tree_score = cross_val_score(tree_clf, X_train, y_train, cv=5)
print('DecisionTree Classifier Cross Validation Score', round(tree_score.mean() * 100, 2).astype(str) + '%')

mlp_score = cross_val_score(mlp_clf, X_train, y_train, cv=5)
print('MLP Classifier Cross Validation Score', round(mlp_score.mean() * 100, 2).astype(str) + '%')

# rvc_score = cross_val_score(rvc_clf, X_train, y_train, cv=5)
# print('RVC Classifier Cross Validation Score', round(rvc_score.mean() * 100, 2).astype(str) + '%')

import itertools
from sklearn.metrics import confusion_matrix

# Create a confusion matrix
def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title, fontsize=14)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

undersample_predictions = tree_clf.predict(original_Xtest)
y_pred = tree_clf.predict(X_test)
# Accuracy
accuracy = accuracy_score(y_test, y_pred)

# Precision
precision = precision_score(y_test, y_pred)

# Recall
recall = recall_score(y_test, y_pred)

# F1-score
f1 = f1_score(y_test, y_pred)

# Mean Squared Error (for regression problems, not classification)
mse = mean_squared_error(y_test, y_pred)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1-score:", f1)
print("MSE:", mse)

undersample_cm = confusion_matrix(original_ytest, undersample_predictions)
actual_cm = confusion_matrix(original_ytest, original_ytest)
labels = ['No Fraud', 'Fraud']

fig = plt.figure(figsize=(16,8))

fig.add_subplot(221)
plot_confusion_matrix(undersample_cm, labels, title="Random Undersample \n Confusion Matrix", cmap=plt.cm.YlOrRd)

fig.add_subplot(222)
plot_confusion_matrix(actual_cm, labels, title="Confusion Matrix \n (with 100% accuracy)", cmap=plt.cm.Greens)

"""Therefore, after getting the best parameter of each model, accuracy improved."""

from sklearn.datasets import make_classification

def evaluate_model(model, X_train, X_test, y_train, y_test):
    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time

    start_time = time.time()
    y_pred = model.predict(X_test)
    predict_time = time.time() - start_time

    accuracy = round(accuracy_score(y_test, y_pred), 4)
    f1 = round(f1_score(y_test, y_pred), 4)
    recall = round(recall_score(y_test, y_pred), 4)
    precision = round(precision_score(y_test, y_pred), 4)
    mse = round(mean_squared_error(y_test, y_pred), 4)

    # Calculate computational complexity and memory requirements
    complexity = model.complexity if hasattr(model, 'complexity') else "Not available"
    memory_requirements = model.memory_requirements if hasattr(model, 'memory_requirements') else "Not available"

    return accuracy, f1, recall, precision, mse, train_time, predict_time, complexity, memory_requirements


# Evaluate models
models = {
    "SVC": svc,
    "k-NN": knears_neighbors,
    "Logistic Regression": log_reg,
    "Decision Tree": tree_clf,
    "MLP": mlp_clf,
    #"RVC": rvc_clf
    # "CNN": cnn_clf
}

results = {}
for name, model in models.items():
    print(f"Evaluating {name}...")
    results[name] = evaluate_model(model, X_train, X_test, y_train, y_test)
    accuracy, f1, recall, precision, mse, train_time, predict_time, complexity, memory_requirements = results[name]
    print(f"{name} - Accuracy: {accuracy}, F1: {f1}, Recall: {recall}, Precision: {precision}, MSE: {mse}")
    print(f"{name} - Training time: {train_time:.4f}, Prediction time: {predict_time:.4f}, Complexity: {complexity}, Memory requirements: {memory_requirements}")
    print()

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.model_selection import cross_val_predict


#For test data set
log_reg_pred = log_reg.predict(X_test)
knears_pred = knears_neighbors.predict(X_test)
svc_pred = svc.predict(X_test)
tree_pred = tree_clf.predict(X_test)
mlp_pred = mlp_clf.predict(X_test)
# cnn_pred = cnn_clf.predict(X_test)



log_fpr, log_tpr, log_thresold = roc_curve(y_test, log_reg_pred)
knear_fpr, knear_tpr, knear_threshold = roc_curve(y_test, knears_pred)
svc_fpr, svc_tpr, svc_threshold = roc_curve(y_test, svc_pred)
tree_fpr, tree_tpr, tree_threshold = roc_curve(y_test, tree_pred)
mlp_fpr, mlp_tpr, mlp_threshold = roc_curve(y_test, mlp_pred)
# cnn_fpr, cnn_tpr, cnn_threshold = roc_curve(y_test, cnn_pred)


def graph_roc_curve_multiple(log_fpr, log_tpr, knear_fpr, knear_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, mlp_fpr, mlp_tpr):
    plt.figure(figsize=(16,8))
    plt.title('ROC Curves', fontsize=18)
    plt.plot(log_fpr, log_tpr, label='Logistic Regression Classifier Score: {:.4f}'.format(roc_auc_score(y_test, log_reg_pred)))
    plt.plot(knear_fpr, knear_tpr, label='KNears Neighbors Classifier Score: {:.4f}'.format(roc_auc_score(y_test, knears_pred)))
    plt.plot(svc_fpr, svc_tpr, label='Support Vector Classifier Score: {:.4f}'.format(roc_auc_score(y_test, svc_pred)))
    plt.plot(tree_fpr, tree_tpr, label='Decision Tree Classifier Score: {:.4f}'.format(roc_auc_score(y_test, tree_pred)))
    plt.plot(mlp_fpr, mlp_tpr, label='Neural Network Classifier Score: {:.4f}'.format(roc_auc_score(y_test, mlp_pred)))
    # plt.plot(cnn_fpr, cnn_tpr, label='CNN Classifier Score: {:.4f}'.format(roc_auc_score(y_test, cnn_pred)))
    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([-0.01, 1, 0, 1])
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.annotate('Minimum ROC Score of 50% \n (This is the minimum score to get)', xy=(0.5, 0.5), xytext=(0.6, 0.3),
                arrowprops=dict(facecolor='#6E726D', shrink=0.05),
                )
    plt.legend()

graph_roc_curve_multiple(log_fpr, log_tpr, knear_fpr, knear_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr, mlp_fpr, mlp_tpr)
plt.show()


#For validation data
log_reg_pred = log_reg.predict(X_train)
knears_pred = knears_neighbors.predict(X_train)
svc_pred = svc.predict(X_train)
tree_pred = tree_clf.predict(X_train)
mlp_pred = mlp_clf.predict(X_train)
# cnn_pred = cnn_clf.predict(X_train)

log_fpr, log_tpr, log_thresold = roc_curve(y_train, log_reg_pred)
knear_fpr, knear_tpr, knear_threshold = roc_curve(y_train, knears_pred)
svc_fpr, svc_tpr, svc_threshold = roc_curve(y_train, svc_pred)
tree_fpr, tree_tpr, tree_threshold = roc_curve(y_train, tree_pred)
mlp_fpr, mlp_tpr, mlp_threshold = roc_curve(y_train, mlp_pred)
# cnn_fpr, cnn_tpr, cnn_threshold = roc_curve(y_train, cnn_pred)

def graph_roc_curve_multiple(log_fpr, log_tpr, knear_fpr, knear_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr):
    plt.figure(figsize=(16,8))
    plt.title('ROC Curves', fontsize=18)
    plt.plot(log_fpr, log_tpr, label='Logistic Regression Classifier Score: {:.4f}'.format(roc_auc_score(y_train, log_reg_pred)))
    plt.plot(knear_fpr, knear_tpr, label='KNears Neighbors Classifier Score: {:.4f}'.format(roc_auc_score(y_train, knears_pred)))
    plt.plot(svc_fpr, svc_tpr, label='Support Vector Classifier Score: {:.4f}'.format(roc_auc_score(y_train, svc_pred)))
    plt.plot(tree_fpr, tree_tpr, label='Decision Tree Classifier Score: {:.4f}'.format(roc_auc_score(y_train, tree_pred)))
    plt.plot(mlp_fpr, mlp_tpr, label='MLP Classifier Score: {:.4f}'.format(roc_auc_score(y_train, mlp_pred)))
    # plt.plot(cnn_fpr, cnn_tpr, label='CNN Classifier Score: {:.4f}'.format(roc_auc_score(y_train, cnn_pred)))

    plt.plot([0, 1], [0, 1], 'k--')
    plt.axis([-0.01, 1, 0, 1])
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.annotate('Minimum ROC Score of 50% \n (This is the minimum score to get)', xy=(0.5, 0.5), xytext=(0.6, 0.3),
                arrowprops=dict(facecolor='#6E726D', shrink=0.05),
                )
    plt.legend()

graph_roc_curve_multiple(log_fpr, log_tpr, knear_fpr, knear_tpr, svc_fpr, svc_tpr, tree_fpr, tree_tpr)
plt.show()

"""From roc curve and indicators above, we can conclude that MLP OR SVC with (...show parameter here...) is best among four approaches in non-bayesian approaches.

In the following section, we will envaluate the conditions of overesampling.
"""