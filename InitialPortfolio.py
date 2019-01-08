#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 22:51:39 2019

@author: Du Chao and Lu Yi
"""

import pandas as pd
import datetime
import numpy as np

import util

class InitialPortfolio:
    def __init__(self, asset_value, stocks):
        self.asset_value = asset_value
        self.stocks = stocks
        self.stock_mat = self.stocks.stock_mat
        self.stocks_liq = None
        self.stocks_liq_mat = None
        self.top5 = None
        self.top5_price = None
        self.current_holding=[0,0,0,0,0]
        self.current_date = stocks.current_date #'2018-08-11'
        self.close_date = stocks.close_date #'2018-08-10'
        self.start_date = datetime.date(2017,9,18)
        self.current_port = None
        
#    def get_initial_portfolio(self):
#        # Select the Initial Portfolio Based on the growth rate of last month
#        temp = self.stocks.stock_list.groupby(u'Name').tail(21)       
#        temp = temp[(temp[u'Date'] > self.days_ago(35))]
#        start_val = temp.groupby(u'Name').nth(0)[u'Close']
#        end_val = temp.groupby(u'Name').nth(19)[u'Close']
#        inc_val = (end_val - start_val) / start_val 
#        inc_val = inc_val.sort_values(ascending=False)
#        self.top5 = inc_val.head(5)
#        
#        for i in range(5):
#            self.top5_price.append(end_val[self.top5.index.values[i]])
#            
#        for i in range(5):
#            self.current_holding[i] = self.asset_value/5/self.top5_price[i]
    def get_initial_portfolio(self):
        stock_sym = self.stock_mat.columns
        startdate = self.start_date.strftime("%Y-%m-%d")
        earlier_date = util.days_ago(28, self.start_date).strftime("%Y-%m-%d")
        sub_mat = self.stock_mat.loc[earlier_date:startdate].values
        mon_grow = (sub_mat[-1,:] - sub_mat[0,:]) / sub_mat[0,:]
        rank = np.argsort(-mon_grow)
        return_list = []
        for i in range(5):
            col = rank[i]
            price = sub_mat[-1,col]
            return_list.append([stock_sym[col], price, mon_grow[col], self.asset_value/5/price])
        self.current_port = return_list

        my_df = pd.DataFrame(return_list)
        my_df.to_csv('current_holding.csv', index=False, header=False)
            
#    def days_ago(self, d, startdate=None):
#        #today is August 13, 10 days ago means August 3
#        if startdate==None:
#            date = datetime.datetime.today() - datetime.timedelta(days=d)
#        else:
#            date = startdate - datetime.timedelta(days=d)
#        return date.strftime("%Y-%m-%d")
        
    def get_liquid(self):
        liquid_list = pd.read_csv('liquidtickers.csv').values.reshape([-1]).tolist()
        self.stocks_liq = self.stocks.stock_list.loc[self.stocks.stock_list['Name'].isin(liquid_list)]
        self.stocks_liq_mat = self.stocks_liq.pivot(index=u'Date',columns=u'Name',values=u'Close')

    def get_initial_liq_portfolio(self):
        stock_sym = self.stock_liq_mat.columns
        startdate = self.start_date.strftime("%Y-%m-%d")
        earlier_date = util.days_ago(28, self.start_date).strftime("%Y-%m-%d")
        sub_mat = self.stock_liq_mat.loc[earlier_date:startdate].values
        mon_grow = (sub_mat[-1,:] - sub_mat[0,:]) / sub_mat[0,:]
        rank = np.argsort(-mon_grow)
        return_list = []
        for i in range(5):
            col = rank[i]
            price = sub_mat[-1,col]
            return_list.append([stock_sym[col], price, mon_grow[col], self.asset_value/5/price])
        self.current_port = return_list

        my_df = pd.DataFrame(return_list)
        my_df.to_csv('current_holding.csv', index=False, header=False)