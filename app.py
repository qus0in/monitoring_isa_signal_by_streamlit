import requests
import pandas as pd
from ast import literal_eval
import streamlit as st

st.set_page_config(page_title='Strategy Monitoring (ISA)', page_icon='📈')

def get_etfs():
    URL = 'https://finance.naver.com/api/sise/etfItemList.nhn'
    params = {'etfType': 0}
    res = requests.get(URL, params)
    res.raise_for_status()
    data = res.json().get('result').get('etfItemList')
    return pd.DataFrame(data)

@st.cache_data(ttl='1m')
def get_prices(symbol):
    URL = 'https://api.finance.naver.com/siseJson.naver'
    params = {
        'symbol': symbol,
        'timeframe': 'day',
        'requestType': 0,
        'count': 200
    }
    res = requests.get(URL, params)
    res.raise_for_status()
    data = literal_eval(res.text.replace('\n', ''))
    return pd.DataFrame(data[1:], columns=data[0])

def get_score(prices):
    periods = [3, 5, 8, 13, 21, 34, 55]
    # periods = [5, 10, 20, 60, 120]

    handler = lambda x: x.iloc[-1] / x.iloc[0] - 1
    scores = [handler(prices.종가.tail(p)) for p in periods]
    return sum(scores) / len(periods) * 252

symbols = ['360750', '133690', '381180', '114800',
           '251340', '132030', '261240', '400570']
df = get_etfs().set_index('itemcode').loc[symbols, ['itemname']]
df['score'] = [get_score(get_prices(idx)) for idx in df.index]
df.sort_values(by='score', ascending=False, inplace=True)
top3 = df.iloc[2]['score']
handler = lambda x: '🤗' if x >= top3 else '🫠' if x < 0 else '🫥'
df['signal'] = df['score'].apply(handler)

st.title('Strategy Monitoring (ISA)')
st.dataframe(df)