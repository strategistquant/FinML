''' Essential packages '''
import os
import pickle as pkl
from datetime import datetime
import numpy as np
import pandas as pd
import pandas_datareader as pdr


class StockMarket:
    def __init__(self, start_date=datetime(2010, 1, 1), end_date=datetime.now(), data_dir='data'):
        self.start_date = start_date
        self.end_date = end_date
        self.price_data = dict()

        self.data_dir = data_dir

    def get_stock_price(self, symbols, log_return=True):
        '''
        args:
            symbols: list of stock symbols, e.g. ['AAPL', 'AMZN', 'GOOGL']
            log_return: boolean. log return
        '''
        # File name starts with dates
        prefix = datetime.now().strftime('%Y%m%d')
        done_list = [file.split('.')[0] for file in os.listdir(self.data_dir)]
        
        # Load price data: if not exists, download with pdr.DataReader
        for symbol in symbols:
            if prefix+symbol in done_list:
                with open(os.path.join(self.data_dir, prefix+symbol+'.pkl'), 'rb') as f:
                    price_data = pkl.load(f)
            else:
                price_data = pdr.DataReader(symbol, 'yahoo', start=datetime(2000,1,1), end=self.end_date)
                with open(os.path.join(self.data_dir, prefix+symbol+'.pkl'), 'wb') as f:
                    pkl.dump(price_data, f)
            
            price_data = price_data[self.start_date <= price_data.index]
            price_data = price_data[price_data.index <= self.end_date]
            self.price_data[symbol] = price_data

        for symbol, df in self.price_data.items():
            df.sort_index(ascending=False, inplace=True)
            df['return'] =  np.log(df['Adj Close'].shift(1) / df['Adj Close']) if log_return else df['Adj Close'].shift(1) / df['Adj Close']-1
            self.price_data[symbol] = df.dropna() # remove rows with NaN

            
    def get_stock_statistics(self):
        '''
        return:
            df_return.columns: list of symbols
            mean_return: array of size [len(self.price_data), 1]
            covariance: array of size [len(self.price_data), len(self.price_data)]
        '''
        df_return = pd.DataFrame()

        for symbol, df in self.price_data.items():
            stock_return = df['return']
            stock_return.name = symbol
            df_return = pd.concat([df_return, stock_return], axis=1)

        mean_return = np.array(df_return.mean()).reshape(len(self.price_data), 1)
        covariance = np.array(df_return.cov())

        return mean_return, covariance, df_return.columns
