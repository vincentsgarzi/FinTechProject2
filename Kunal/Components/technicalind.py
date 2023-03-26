{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "bffac920-3455-414d-9bc2-d8dac77856f8",
   "metadata": {},
   "outputs": [],
   "source": [
    "def techinds(ticker,short_window,long_window):\n",
    "    today= pd.to_datetime(dt.date.today())\n",
    "    # today=pd.to_datetime('today').normalize().date\n",
    "    start= today - DateOffset(months=24)\n",
    "    training_start_date=start.date()\n",
    "    indicators_df=df_portfolio_year.loc[(df_portfolio_year.index>=training_start_date) & (df_portfolio_year['symbol']==ticker)].copy()\n",
    "    \n",
    "    # Create additional technical indicators\n",
    "    indicators_df[\"ssma\"] = TA.SSMA(indicators_df)\n",
    "    indicators_df[\"ema\"] = TA.EMA(indicators_df, 50)\n",
    "    indicators_df[\"dema\"] = TA.DEMA(indicators_df)\n",
    "    indicators_df[\"tema\"] = TA.TEMA(indicators_df)\n",
    "    indicators_df[\"trima\"] = TA.TRIMA(indicators_df)\n",
    "    indicators_df[\"trima\"] = TA.TRIMA(indicators_df)\n",
    "    indicators_df['sma_fast'] = TA.SMA(indicators_df, short_window)\n",
    "    indicators_df['sma_slow'] = TA.SMA(indicators_df, long_window)\n",
    "    # Create signals based on returns    \n",
    "    signals_df=indicators_df.loc[:,['symbol',\"close\",'ssma','ema','dema','tema','trima','sma_slow','sma_fast']]\n",
    "    signals_df['actual_returns']=signals_df['close'].pct_change()\n",
    "    signals_df=signals_df.dropna()\n",
    "    signals_df['Signal']=np.where(signals_df['actual_returns']>=0 ,1 ,-1)\n",
    "    return signals_df"
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
