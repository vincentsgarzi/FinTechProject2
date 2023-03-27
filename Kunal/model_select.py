## This script used the sorted performance summary dataframe and obtains the forecast of 
## the best performing model

def model_selection(forCompany,inputdata):
    forCompany_df=inputdata.loc[inputdata['Company']==forCompany].copy()
    # modelselect=forCompany_df.iloc[0]['ModelType']
    signalFrsct=forCompany_df.iloc[0]['Forecast']
    return signalFrsct