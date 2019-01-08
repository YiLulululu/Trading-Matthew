#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 00:11:42 2019

@author: Du Chao and Lu Yi
"""

#import numpy as np
#import pandas as pd
from Holdings import Order
import math

def S1(opt, holdings, stock_mat_ori, sma_days, lma_days):
    """
    buy stocks based on the ratio of short term and long term moving averages
    """
    # retrieve data up to the current date
    stock_mat = stock_mat_ori.loc[:opt.date]
    
    # get short term moving average, long term moving average, and the ratio for today and yesterday
    sma_today = stock_mat.iloc[-sma_days:,:].sum() / sma_days
    lma_today = stock_mat.iloc[-lma_days:,:].sum() / lma_days
    ratio_today = sma_today / lma_today   
    
    sma_yesterday = stock_mat.iloc[-sma_days-1:-1,:].sum() / sma_days
    lma_yesterday = stock_mat.iloc[-lma_days-1:-1,:].sum() / lma_days
    ratio_yesterday = sma_yesterday / lma_yesterday
    
    # pick those ratios which today > 1 and yesterday < 1
    pick_list = (ratio_today > 1) & (ratio_yesterday < 1)
    ratio_pick = ratio_today[pick_list]
    
    # sort ratios based on ratios today
    ratio_pick = ratio_pick.sort_values(ascending=False)

    # get current available cash
    holdings.get_current_holdings()
    available_cash = holdings.holdings['cash'].price
    
    # decided the number of kinds of stock
    current_diversity = len(holdings.holdings.keys()) - 1
    available_holdings = opt.max_holdings - current_diversity
    if available_holdings == 0:
        return []
    
    num_pick = len(ratio_pick)
    if num_pick > available_holdings:
        num_pick = available_holdings
        
    if num_pick == 0:
        return []
    
    # calculate the weights for each stock
    wgt_avg = []
    if opt.allocation == 'weighted_avg':    
        wgt_avg_sum = ratio_pick[:num_pick].sum()
        wgt_avg = [ratio_pick[i] / wgt_avg_sum for i in range(num_pick)]
    else:
        wgt_avg = [1.0 / num_pick for i in range(num_pick)]
    
    # calculate available funds and number of holdings for each stock
    fund_alloc = [available_cash * wgt_avg[i] for i in range(num_pick)]
    
    latest_price = stock_mat.iloc[-1,:]
    orders = []
    for i in range(num_pick):
        stock_name = ratio_pick[i:i+1].index[0]
        price = latest_price.loc[stock_name]
        if math.isnan(price) or price==0 or price==None:
            continue
        max_hold = int(fund_alloc[i] / (price*(1+opt.trade_buffer)))
        if max_hold > 0:
            orders.append(Order(stock_name, max_hold, price, opt.date))
        
    return orders


def S2(opt, holdings, stock_mat_ori, sma_days, lma_days):
    """
    sell stocks based on the ratio of short term and long term moving averages
    """
    # retrieve data up to the current date
    stock_mat = stock_mat_ori.loc[:opt.date]
    
    # get short term moving average, long term moving average, and the ratio for today and yesterday
    sma_today = stock_mat.iloc[-sma_days:,:].sum() / sma_days
    lma_today = stock_mat.iloc[-lma_days:,:].sum() / lma_days
    ratio_today = sma_today / lma_today   
    
    sma_yesterday = stock_mat.iloc[-sma_days-1:-1,:].sum() / sma_days
    lma_yesterday = stock_mat.iloc[-lma_days-1:-1,:].sum() / lma_days
    ratio_yesterday = sma_yesterday / lma_yesterday
    
    # pick those ratios which today < 1 and yesterday > 1
    pick_list = (ratio_today < 1) & (ratio_yesterday > 1)
    ratio_pick = ratio_today[pick_list]
    
    # sort ratios based on ratios today
    ratio_pick = ratio_pick.sort_values(ascending=False)

    # get current holdings
    holdings.get_current_holdings()
    latest_price = stock_mat.iloc[-1,:]
    
    # prepare orders
    orders = []
    for i in range(len(ratio_pick)):
        stock_name = ratio_pick[i:i+1].index[0]
        price = latest_price.loc[stock_name]
        
        if math.isnan(price) or price==0 or price==None:
            continue
        
        # check if the stock is in holdings
        if stock_name in holdings.holdings.keys():
            sell_num = holdings.holdings[stock_name].num_holdings
            orders.append(Order(stock_name, -sell_num, price, opt.date))
            
    return orders

