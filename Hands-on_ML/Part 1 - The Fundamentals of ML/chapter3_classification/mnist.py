#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn.datasets import fetch_mldata
mnist = fetch_mldata('MNIST original')
mnist


# In[2]:


x,y = mnist['data'], mnist['target']
x.shape


# In[3]:


y.shape


# In[4]:


#get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib
import matplotlib.pyplot as plt

some_digit = x[36000]
some_digit_image = some_digit.reshape(28,28)

plt.imshow(some_digit_image, cmap = matplotlib.cm.binary, interpolation='nearest')
plt.axis('off')
plt.show()


# In[5]:


y[36000]


# In[6]:


# Creating a test and training set

x_train, x_test, y_train, y_test = x[:60000], x[60000:], y[:60000], y[60000:]

# shuffling the training to set to ensure the cross validation folds will be similar.
import numpy as np
shuffle_index = np.random.permutation(60000)
x_train, y_train = x_train[shuffle_index], y_train[shuffle_index]


# In[7]:


# Identify binaries

y_train_5 = (y_train == 5) # True for all 5s, False for all other digits
y_test_5 = (y_test ==5)

from sklearn.linear_model import SGDClassifier

sgd_clf = SGDClassifier(random_state=42)
sgd_clf.fit(x_train, y_train_5)

sgd_clf.predict([some_digit])


# In[8]:


### Measuring Accuracy Using Cross-Validation ###

# Implementing Cross-Validation

# Code below does the same thing as sklearn cross_val_score

from sklearn.model_selection import StratifiedKFold
from sklearn.base import clone

# Stratified sampling. Folds that contain a representative ratio of each class. 
skfolds = StratifiedKFold(n_splits=3, random_state=42)

for train_index, test_index in skfolds.split(x_train, y_train_5):
    clone_clf = clone(sgd_clf)
    x_train_folds = x_train[train_index]
    y_train_folds = y_train_5[train_index]
    x_test_fold = x_train[test_index]
    y_test_fold = y_train_5[test_index]
    
    clone_clf.fit(x_train_folds, y_train_folds)
    y_pred = clone_clf.predict(x_test_fold)
    n_correct = sum(y_pred == y_test_fold)
    print(n_correct / len(y_pred)) # prints .94675, .9528, and .95165


# In[9]:


from sklearn.model_selection import cross_val_score
cross_val_score(sgd_clf, x_train, y_train_5, cv=3, scoring='accuracy')


# In[10]:


from sklearn.base import BaseEstimator

class Never5Classifier(BaseEstimator):
    def fit(self, x, y=None):
        pass
    def predict(self, x):
        return np.zeros((len(x), 1), dtype=bool)
    
never_5_clf = Never5Classifier()
cross_val_score(never_5_clf, x_train, y_train_5, cv=3, scoring='accuracy')


# In[11]:


# Confusion Matrix

from sklearn.model_selection import cross_val_predict

y_train_pred = cross_val_predict(sgd_clf, x_train, y_train_5, cv=3)

from sklearn.metrics import confusion_matrix
confusion_matrix(y_train_5, y_train_pred)


# In[12]:


# Sklearn classifier functions

# precision score = TP/FP+TP

# recall score = TP/FN+TP

from sklearn.metrics import precision_score, recall_score
precision_score(y_train_5, y_train_pred)


# In[13]:


recall_score(y_train_5, y_train_pred)


# In[14]:


# Calculate f1 score

# f1 score favores similar precision and recall
# f1 = 2/((1/precision)+(1/recall)) = 2*(precision*recall)/(precision+recall) = TP/(TP+(FN+FP/2))

from sklearn.metrics import f1_score
f1_score(y_train_5, y_train_pred)


# In[15]:


# Setting precision versus recall thresholds

y_scores = sgd_clf.decision_function([some_digit])
y_scores


# In[16]:


threshold = 0
y_some_digit_pred = (y_scores > threshold)
y_some_digit_pred


# In[17]:


# Raising the threshold decreases recall
threshold = 200000
y_some_digit_pred = (y_scores > threshold)
y_some_digit_pred


# In[18]:


# Compute precision and recall for all possible thresholds using the precision_recall_curve()

y_scores = cross_val_predict(sgd_clf, x_train, y_train_5, cv=3, method='decision_function')
from sklearn.metrics import precision_recall_curve

precisions, recalls, thresholds = precision_recall_curve(y_train_5, y_scores)

def plot_precision_recall_vs_threshold(precisions, recalls, thresholds):
    plt.figure(figsize=(15,6))
    plt.plot(thresholds, precisions[:-1], 'b--', label='Precision')
    plt.plot(thresholds, recalls[:-1], 'g-', label='Recall')
    plt.xlabel('Threshold')
    plt.legend(loc='center left')
    plt.ylim([0, 1])
    
plot_precision_recall_vs_threshold(precisions, recalls, thresholds)
plt.show()


# In[19]:


y_train_pred_90 = (y_scores > 70000)

precision_score(y_train_5, y_train_pred_90)


# In[20]:


recall_score(y_train_5, y_train_pred_90)


# In[21]:


# The ROC Curve

# plts the true positive rate (another name for recall) against the false positive rate.
# FPR: the ratio of negative instances that are incorrectly classified as positive. 

# Comput TPR and FPR for various trheshold values.
from sklearn.metrics import roc_curve

fpr, tpr, thresholds = roc_curve(y_train_5, y_scores)

def plot_roc_curve(fpr, tpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0,1],[0,1],'k--')
    plt.axis([0,1,0,1])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    
plot_roc_curve(fpr,tpr)
plt.show()


# In[22]:


# Further away the blue line is from the dotted line (ROC curve of a purely random classifier) the better.

# ROC AUC: area between the two ROC curves.

from sklearn.metrics import roc_auc_score
roc_auc_score(y_train_5, y_scores)


# In[23]:


from sklearn.ensemble import RandomForestClassifier

forest_clf = RandomForestClassifier(random_state=42)
y_probas_forest = cross_val_predict(forest_clf, x_train, y_train_5, cv=3, method='predict_proba')

# Need scores not propabilities. Use the postive slcass's probability as the score:

y_scores_forest = y_probas_forest[:, 1] # Score = proba of poisitive class
fpr_forest, tpr_forest, thresholds_forest = roc_curve(y_train_5,y_scores_forest)

plt.plot(fpr,tpr, 'b', label='SGD')
plot_roc_curve(fpr_forest, tpr_forest, 'random forest')
plt.legend(loc='lower right')
plt.show()


# In[24]:


# ROC AUC score of the random forest
roc_auc_score(y_train_5, y_scores_forest)

# print('Precision')
# precision_score(y_train_5, y_scores_forest)

# print('Recall')
# recall_score(y_train_5, y_scores_forest)


# In[25]:


# Multiclass Classification

# Identifying more than one class. 

sgd_clf.fit(x_train, y_train) 
sgd_clf.predict([some_digit])


# In[26]:


# The highest score is the one that coresponds to class 5
some_digit_scores = sgd_clf.decision_function([some_digit])
some_digit_scores


# In[27]:


np.argmax(some_digit_scores)


# In[28]:


sgd_clf.classes_


# In[29]:


sgd_clf.classes_[5]


# In[30]:


from sklearn.multiclass import OneVsOneClassifier
ovo_clf = OneVsOneClassifier(SGDClassifier(random_state=42))
ovo_clf.fit(x_train, y_train)
ovo_clf.predict([some_digit])


# In[31]:


len(ovo_clf.estimators_)


# In[32]:


forest_clf.fit(x_train, y_train)
forest_clf.predict([some_digit])


# In[33]:


forest_clf.predict_proba([some_digit])


# In[34]:


cross_val_score(sgd_clf, x_train, y_train, cv=3, scoring='accuracy')


# In[35]:


from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train.astype(np.float64))
cross_val_score(sgd_clf, x_train_scaled, y_train, cv=3, scoring="accuracy")


# In[ ]:


y_train_pred = cross_val_predict(sgd_clf, x_train_scaled, y_train, cv=3)
conf_mx = confusion_matrix(y_train, y_train_pred)
conf_mx

