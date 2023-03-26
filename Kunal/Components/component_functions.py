def techinds(ticker,short_window,long_window):
    today= pd.to_datetime(dt.date.today())
    # today=pd.to_datetime('today').normalize().date
    start= today - DateOffset(months=24)
    training_start_date=start.date()
    indicators_df=df_portfolio_year.loc[(df_portfolio_year.index>=training_start_date) & (df_portfolio_year['symbol']==ticker)].copy()
    
    # Create additional technical indicators
    indicators_df["ssma"] = TA.SSMA(indicators_df)
    indicators_df["ema"] = TA.EMA(indicators_df, 50)
    indicators_df["dema"] = TA.DEMA(indicators_df)
    indicators_df["tema"] = TA.TEMA(indicators_df)
    indicators_df["trima"] = TA.TRIMA(indicators_df)
    indicators_df["trima"] = TA.TRIMA(indicators_df)
    indicators_df['sma_fast'] = TA.SMA(indicators_df, short_window)
    indicators_df['sma_slow'] = TA.SMA(indicators_df, long_window)
    # Create signals based on returns    
    signals_df=indicators_df.loc[:,['symbol',"close",'ssma','ema','dema','tema','trima','sma_slow','sma_fast']]
    signals_df['actual_returns']=signals_df['close'].pct_change()
    signals_df=signals_df.dropna()
    signals_df['Signal']=np.where(signals_df['actual_returns']>=0 ,1 ,-1)
    return signals_df

def targetdf(inputdata):
    return inputdata['Signal']

def featuresdf(inputdata):
    return inputdata[['symbol','close','actual_returns','ssma','ema','dema','tema','trima','sma_slow','sma_fast']].shift().dropna()

def train_test(featuredf,targetdf):
    # Select the start of the training period
    training_begin = featuredf.index.min()
    # Display the training begin date
    # print(f'Training begins with 2 years of historical data. Starting point is: {training_begin}')
    # Select the ending period for the training data with an offset of 6 months
    training_end = featuredf.index.min() + DateOffset(months=6)
    # Display the training end date
    # print(f'Training ends with 6 months data from the start date. Training end point is: {training_end}')
    
    # Generate the X_train and y_train DataFrames
    X_train=featuredf.loc[training_begin:training_end]
    y_train=targetdf.loc[training_begin:training_end]
    # print(f'Testing starts a day after the training ends. Testing start point is:{training_end+DateOffset(days=1)}')

    X_test=featuredf.loc[training_end+DateOffset(days=1):]
    y_test=targetdf.loc[training_end+DateOffset(days=1):]
    # print(f'Testing ends one day before yesterday. Testing start point is:{X_test.index.max}')
    return X_train, y_train, X_test, y_test
    
def scaling(feature_train, feature_test, forecast_df):
    # Create a StandardScaler instance
    scaler = StandardScaler()
    # Apply the scaler model to fit the X-train data
    X_scaler = scaler.fit(feature_train)
    # Transform the X_train and X_test DataFrames using the X_scaler
    X_train_scaled = X_scaler.transform(feature_train)
    X_test_scaled = X_scaler.transform(feature_test)
    X_frcst_scaled = X_scaler.transform(forecast_df)
    return X_train_scaled, X_test_scaled, X_frcst_scaled

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
