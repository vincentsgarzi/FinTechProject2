{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "4acef32a-93d8-474e-a1ac-9bb69d07da35",
   "metadata": {},
   "outputs": [],
   "source": [
    "def targetdf(inputdata):\n",
    "    return inputdata['Signal']\n",
    "\n",
    "def featuresdf(inputdata):\n",
    "    return inputdata[['symbol','close','actual_returns','ssma','ema','dema','tema','trima','sma_slow','sma_fast']].shift().dropna()\n",
    "\n",
    "def train_test(featuredf,targetdf):\n",
    "    # Select the start of the training period\n",
    "    training_begin = featuredf.index.min()\n",
    "    # Display the training begin date\n",
    "    # print(f'Training begins with 2 years of historical data. Starting point is: {training_begin}')\n",
    "    # Select the ending period for the training data with an offset of 6 months\n",
    "    training_end = featuredf.index.min() + DateOffset(months=6)\n",
    "    # Display the training end date\n",
    "    # print(f'Training ends with 6 months data from the start date. Training end point is: {training_end}')\n",
    "    \n",
    "    # Generate the X_train and y_train DataFrames\n",
    "    X_train=featuredf.loc[training_begin:training_end]\n",
    "    y_train=targetdf.loc[training_begin:training_end]\n",
    "    # print(f'Testing starts a day after the training ends. Testing start point is:{training_end+DateOffset(days=1)}')\n",
    "\n",
    "    X_test=featuredf.loc[training_end+DateOffset(days=1):]\n",
    "    y_test=targetdf.loc[training_end+DateOffset(days=1):]\n",
    "    # print(f'Testing ends one day before yesterday. Testing start point is:{X_test.index.max}')\n",
    "    return X_train, y_train, X_test, y_test\n",
    "\n",
    "def scaling(feature_train, feature_test, forecast_df):\n",
    "    # Create a StandardScaler instance\n",
    "    scaler = StandardScaler()\n",
    "    # Apply the scaler model to fit the X-train data\n",
    "    X_scaler = scaler.fit(feature_train)\n",
    "    # Transform the X_train and X_test DataFrames using the X_scaler\n",
    "    X_train_scaled = X_scaler.transform(feature_train)\n",
    "    X_test_scaled = X_scaler.transform(feature_test)\n",
    "    X_frcst_scaled = X_scaler.transform(forecast_df)\n",
    "    return X_train_scaled, X_test_scaled, X_frcst_scaled"
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
