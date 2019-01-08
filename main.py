#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 15:43:11 2019

@author: Du Chao and Lu Yi
"""

import datetime
import Holdings
from StockPrice import StockPrice
import Strategies
import Performance

class Opt:
    def __init__(self, is_daily, is_liquid, initial_fund, diversity, allocation, trade_buffer, date=None):
        self.is_daily = is_daily
        self.is_liquid = is_liquid
        self.initial_fund = initial_fund
        self.max_holdings = int(float(initial_fund) / diversity)
        self.allocation = allocation
        self.trade_buffer = trade_buffer
        if date:
            self.date = date
        else:
            now = datetime.datetime.now()
            self.date = now.strftime("%Y-%m-%d") 
        
if __name__ == "__main__":
    # simulated start date
    start_date = '2018-01-01'
    test_days = 52
    opt = Opt(False, True, 25000.0, 1000, 'weighted_avg', 0.01, start_date)
 
    # get stock prices
    stock_price = StockPrice(opt)
    
    # get new stock prices, comment out the next line for testing
    #stock_price.update_data_csv()
    stock_price.get_stock_prices()
    available_dates = list(stock_price.stock_mat.loc[start_date:].index.values)

    # adjust start date
    opt.date = available_dates[0]
    
    # create test database
    holdings = Holdings.Holdings(opt, stock_price.stock_mat, 'test_db.db')
    holdings.create_tables()

    # clear tables for testing
    cur = holdings.conn.cursor()
    cur.execute('delete from holdings_record')
    cur.execute('delete from asset_values_record')
    cur.execute('delete from current_holdings')
    cur.execute('delete from orders_record')    
    
    # inject cash
    holdings.orders.append(Holdings.Order('cash', 1, opt.initial_fund, opt.date))
    holdings.update_holdings()
    
    for i in range(test_days):
        print("\n-----------Date:", opt.date, "-----------")
        # trade based on strategy S2
        holdings.orders = Strategies.S2(opt, holdings, stock_price.stock_mat, 4, 16)
        holdings.update_holdings()
        
        # trade based on strategy S1
        holdings.orders = Strategies.S1(opt, holdings, stock_price.stock_mat, 4, 16)
        holdings.update_holdings()
        
        # show current holdings and orders record
        print("\nCurrent Holdings:")
        #print("symbol \t\t num \t\t price \t\t avg_cost \t\t date")
        print("{:10}\t{:10}\t{:10}\t{:10}\t{:10}".format('symbol', 'num', 'price', 'avg_cost', 'date'))
        cur.execute('select * from current_holdings')
        temp_records = cur.fetchall()
        for stock in temp_records:
            #print(stock[0], '\t\t', stock[1], '\t\t', str.format('{0:.2f}', stock[2]), '\t\t', str.format('{0:.2f}', stock[3]), '\t\t', stock[4])
            print("{:10}\t{:10}\t{:10}\t{:10}\t{:10}".format(stock[0], stock[1], str.format('{0:.2f}', stock[2]), str.format('{0:.2f}', stock[3]), stock[4]))
        # update asset values and holdings record
        holdings.update_tables()
        
        # simulate another day
        opt.date = available_dates[1+i]

    cur.execute('select * from asset_values_record')
    print("\n-----------Asset Values Record-----------")
    #print("date \t\t asset_value \t orders \t\t diversity")
    print("{:10}\t{:10}\t\t{:10}\t{:10}".format('date', 'asset_value', 'orders', 'diversity'))
    temp_records = cur.fetchall()
    for av_record in temp_records:
        #print(av_record[0], '\t', str.format('{0:.2f}', av_record[1]), '\t', av_record[2], '\t\t', av_record[3])
        print("{:10}\t{:10}\t{:10}\t{:10}".format(av_record[0], str.format('{0:.2f}', av_record[1]), av_record[2], av_record[3]))
    
    # performance
    print("\n-----------Performance Indicators-----------")
    perf = Performance.Performance(opt, holdings, stock_price.stock_mat, available_dates[:test_days], 2.6, 0.05)
    perf.get_performance()
    
    # close database connection
    holdings.conn.close()