## This script has functions related to all the modeling functions
## each modeling function returns the classification report, and a prediction for 'tomorrow'

# Import a new classifier from SKLearn
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
#imports for model performance metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

def supportvector(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):
    # Initiate the model instance
    svc_model=SVC()
    # Fit the model using the training data
    svc_model=svc_model.fit(X_train_scaled,y_train)
    # Use the testing dataset to generate the predictions for the new model
    svc_pred = svc_model.predict(X_test_scaled)
    svc_pred_tomorrow=svc_model.predict(X_frcst_scaled)
    method="SVC"
    return classification_report(y_test, svc_pred,output_dict=True), method, svc_pred_tomorrow
    
def logistic(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):
    # Initiate the model instance
    model_logistic=LogisticRegression()
    # Fit the model using the training data
    model_logistic = model_logistic.fit(X_train_scaled,y_train)
    # Use the testing dataset to generate the predictions for the new model
    logistic_pred = model_logistic.predict(X_test_scaled)
    logistic_pred_tomorrow=model_logistic.predict(X_frcst_scaled)
    method="Logit"
    return classification_report(y_test, logistic_pred,output_dict=True), method, logistic_pred_tomorrow

def tree(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):
    # Initiate the model instance
    model_dtree=DecisionTreeClassifier()
    # Fit the model using the training data
    model_dtree = model_dtree.fit(X_train_scaled,y_train)
    # Use the testing dataset to generate the predictions for the new model
    Dtree_predict = model_dtree.predict(X_test_scaled)
    DTree_pred_tomorrow=model_dtree.predict(X_frcst_scaled)    
    method="DecTree"
    return classification_report(y_test, Dtree_predict,output_dict=True), method, DTree_pred_tomorrow