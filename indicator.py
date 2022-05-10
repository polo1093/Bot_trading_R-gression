import pandas as pd
import ta




def SMAx(data, x=60 ,window_h=14, multi=1 ):
    """Exponential Moving Average"""
    if multi==1 :
        data[f'{x}_SMAx-x'] = ta.trend.sma_indicator(data['close'],
                                                     window_h*x)-ta.trend.sma_indicator(data['close'], window_h*x*3)
    else :
        data[f'{x}_SMAx-x*{multi}'] = ta.trend.sma_indicator(data['close'],
                                                     window_h*x*multi)-ta.trend.sma_indicator(data['close'], window_h*x*multi*3)
    return data

def get_chop(high, low, close, window):
    """ Choppiness index """
    tr1 = pd.DataFrame(high - low).rename(columns = {0:'tr1'})
    tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns = {0:'tr2'})
    tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns = {0:'tr3'})
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').dropna().max(axis = 1)
    atr = tr.rolling(1).mean()
    highh = high.rolling(window).max()
    lowl = low.rolling(window).min()
    ci = 100 * np.log10((atr.rolling(window).sum()) / (highh - lowl)) / np.log10(window)
    return ci

#indicateur
def indicator(data, x=60):

    window_h=14*x

#    data[f'{x}_RollingMax']    = data['close']-data['close'].shift(1).rolling(window=x).max()
#    data[f'{x}_RollingMin']    = data['close'].shift(1).rolling(window=x).min()-data['close']
#    data[f'{x}_SMA']=ta.trend.sma_indicator(data['close'], window=int(x))

    #Exponential Moving Average
    data=SMAx(data,x,window_h,1)
    data=SMAx(data,x,window_h,3)

    # #MACD
#    MACD = ta.trend.MACD(close=data['close'], window_fast=12, window_slow=26, window_sign=9)
#    data['MACD'] = MACD.macd()
#    data['MACD_SIGNAL'] = MACD.macd_signal()
#    data['MACD_DIFF'] = MACD.macd_diff() #Histogramme MACD
    
    # #Awesome Oscillator
    data[f'{x}_AWESOME_OSCILLATOR'] = ta.momentum.awesome_oscillator(high=data['high'], low=data['low'],
                                                                window1=int(window_h/7), window2=window_h)

    # # Kaufman’s Adaptive Moving Average (KAMA)
    #data['KAMA'] = ta.momentum.kama(close=data['close'], window=10, pow1=2, pow2=30)

    #Relative Strength Index (RSI)
    data[f'{x}_RSI'] =ta.momentum.rsi(close=data['close'], window=window_h)

    # #Stochastic RSI
    data[f'{x}_STOCH_RSI'] = ta.momentum.stochrsi(close=data['close'], window=window_h, smooth1=3, smooth2=3) #Non moyenné 
    #data['STOCH_RSI_D'] = ta.momentum.stochrsi_d(close=data['close'], window=window_h, smooth1=3, smooth2=3) #Orange TradingView
    #data['STOCH_RSI_K'] =ta.momentum.stochrsi_k(close=data['close'], window=window_h, smooth1=3, smooth2=3) #Bleu sur TradingView
   
    # -- Trix Indicator -- sell and buy
    trixLength = int(window_h*9/21)
    trixSignal = window_h
    data[f'{x}_TRIX_PCT'] = ta.trend.ema_indicator(ta.trend.ema_indicator(ta.trend.ema_indicator(close=data['close'],
                                            window=trixLength), window=trixLength), window=trixLength).pct_change()*100
    data[f'{x}_TRIX_HISTO'] = (data[f'{x}_TRIX_PCT'] - ta.trend.sma_indicator(data[f'{x}_TRIX_PCT'],trixSignal))*100
    #data.loc[:,'buy_TRIX+0_STOCH_RSI-0.8']=0
    #data.loc[(data['TRIX_HISTO']>0) & (data['STOCH_RSI']<0.8),'buy_TRIX+0_STOCH_RSI-0.8']=1
    data.loc[:,f'{x}_buy_TRIX+0_STOCH_RSI-0.7']=data[f'{x}_TRIX_HISTO']*(data[f'{x}_STOCH_RSI']-0.7)
    data.loc[:,f'{x}_buy_TRIX+0_STOCH_RSI-0.5']=data[f'{x}_TRIX_HISTO']*(data[f'{x}_STOCH_RSI']-0.5)
    #data.loc[:,'sell_TRIX-0_STOCH_RSI+0.2_0_1']=0
    #data.loc[(data['TRIX_HISTO']<0) & (data['STOCH_RSI']>0.2),'sell_TRIX-0_STOCH_RSI+0.2_0_1']=-data.loc[:,'buy_TRIX+0_STOCH_RSI-0.8']
    data.loc[:,f'{x}_sell_TRIX-0_STOCH_RSI+0.2']=-data[f'{x}_TRIX_HISTO']*(0.2-data[f'{x}_STOCH_RSI'])
    data.loc[:,f'{x}_buy_TRIX+0_STOCH_RSI']=data[f'{x}_TRIX_HISTO']+(data[f'{x}_STOCH_RSI'])
    data=data.drop(f'{x}_STOCH_RSI',axis=1)
    
    # #Average True Range (ATR) trop de NAN
    data[f'{x}_ATR'] = ta.volatility.average_true_range(high=data['high'], low=data['low'], close=data['close'], window=window_h)

    # #Choppiness index
    data[f'{x}_CHOP'] = get_chop(high=data['high'], low=data['low'], close=data['close'], window=window_h)  
    
        # #Super Trend
    #ST_length = 10
    #ST_multiplier = 3.0
    #superTrend = pda.supertrend(high=data['high'], low=data['low'], close=data['close'], length=ST_length,
    #                            multiplier=ST_multiplier)
    #data['SUPER_TREND'] = superTrend['SUPERT_'+str(ST_length)+"_"+str(ST_multiplier)] #Valeur de la super trend   
    return data