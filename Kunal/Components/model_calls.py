{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7f36c6f4-3fb3-48b1-aa36-3d00f4ad4b05",
   "metadata": {},
   "outputs": [],
   "source": [
    "def supportvector(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):\n",
    "    # Initiate the model instance\n",
    "    svc_model=SVC()\n",
    "    # Fit the model using the training data\n",
    "    svc_model=svc_model.fit(X_train_scaled,y_train)\n",
    "    # Use the testing dataset to generate the predictions for the new model\n",
    "    svc_pred = svc_model.predict(X_test_scaled)\n",
    "    svc_pred_tomorrow=svc_model.predict(X_frcst_scaled)\n",
    "    method=\"SVC\"\n",
    "    return classification_report(y_test, svc_pred,output_dict=True), method, svc_pred_tomorrow\n",
    "    \n",
    "def logistic(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):\n",
    "    # Initiate the model instance\n",
    "    model_logistic=LogisticRegression()\n",
    "    # Fit the model using the training data\n",
    "    model_logistic = model_logistic.fit(X_train_scaled,y_train)\n",
    "    # Use the testing dataset to generate the predictions for the new model\n",
    "    logistic_pred = model_logistic.predict(X_test_scaled)\n",
    "    logistic_pred_tomorrow=model_logistic.predict(X_frcst_scaled)\n",
    "    method=\"Logit\"\n",
    "    return classification_report(y_test, logistic_pred,output_dict=True), method, logistic_pred_tomorrow\n",
    "\n",
    "def tree(X_train_scaled, X_test_scaled, X_frcst_scaled,y_train, y_test):\n",
    "    # Initiate the model instance\n",
    "    model_dtree=DecisionTreeClassifier()\n",
    "    # Fit the model using the training data\n",
    "    model_dtree = model_dtree.fit(X_train_scaled,y_train)\n",
    "    # Use the testing dataset to generate the predictions for the new model\n",
    "    Dtree_predict = model_dtree.predict(X_test_scaled)\n",
    "    DTree_pred_tomorrow=model_dtree.predict(X_frcst_scaled)    \n",
    "    method=\"DecTree\"\n",
    "    return classification_report(y_test, Dtree_predict,output_dict=True), method, DTree_pred_tomorrow"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.15"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
