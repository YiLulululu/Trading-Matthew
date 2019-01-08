#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 14:56:28 2019

@author: Du Chao and Lu Yi
"""
import numpy as np
import util

class PerfStruct:
    """
    struct for different indicators
    """
    def __init__(self, ROI, IRR, SR, MD, SUR):
        self.ROI = ROI
        self.IRR = IRR
        self.SR = SR
        self.MD = MD
        self.SUR = SUR
        
class Performance:
    """
    class for calculating performance indicators
    """
    def __init__(self, opt, holdings, stock_mat, available_dates, T_bill_rate, tar_grow):
        self.T_bill_rate = T_bill_rate
        self.tar_grow = tar_grow
        self.opt = opt
        self.holdings = holdings
        self.stock_mat = stock_mat
        self.available_dates = available_dates
        self.asset_values_SPY = []
        self.asset_values_div = []
        self.asset_values = []
        
        self.perf_self = None
        self.perf_SPY = None
        self.perf_div = None
        
    def get_record_SPY(self):
        """
        get the asset values record of investing SPY
        """
        self.asset_values_SPY = []
        
        # get SPY prices
        record_SPY = self.stock_mat.loc[self.available_dates[0]:self.available_dates[-1]].SPY
        
        # get holdings
        num_holdings = int(self.opt.initial_fund / (record_SPY[0]*(1+self.opt.trade_buffer)))
        
        self.asset_values_SPY = list(record_SPY * num_holdings)
        
    def get_record_div(self):
        """
        get the asset values record of investing diversily
        """        
        self.asset_values_div = []
        # get stock_mat within the time frame
        stock_mat = self.stock_mat.loc[self.available_dates[0]:self.available_dates[-1]]
        
        # get number of symbols
        num_symbols = len(stock_mat.columns)
        
        # get fund allocation for each stock
        fund_alloc = np.floor(self.opt.initial_fund / num_symbols)
        
        # get the initial price and holdings
        initial_price = stock_mat.iloc[0,:]
        holding_list = np.floor(fund_alloc / initial_price)
        
        remain_cash = self.opt.initial_fund - (stock_mat.iloc[0,:] * holding_list).sum()
        for i in range(len(stock_mat)):
            self.asset_values_div.append((stock_mat.iloc[i,:] * holding_list).sum() + remain_cash)        

    def get_record(self):
        """
        get the asset values record of our own trading strategy
        """
        self.asset_values = []
        cur = self.holdings.conn.cursor()
        cur.execute('select * from asset_values_record')
        temp_asset_values = cur.fetchall()
        for av in temp_asset_values:
            self.asset_values.append(av[1])
            
    def get_ROI(self, av_t1, av_t2):
        """ get ROI """
        return float(av_t2) / av_t1 - 1.0
    
    def get_IRR(self, av_t1, av_t2, t1, t2):
        """ get IRR """
        delta_days = (util.str_to_date(t2) - util.str_to_date(t1)).days
        return (av_t2 / av_t1) ** (1.0 / (delta_days / 365.0)) - 1.0
    
    def get_SR(self, av_list, IRR):
        """ get SR """
        temp_list = np.array(av_list)
        temp_list = np.log(temp_list[1:] / temp_list[:-1])
        if self.opt.is_daily:
            temp_list *= 365.0
        else:
            temp_list *= 52.0
            
        std = temp_list.std()
        return (IRR - self.T_bill_rate) / std 

    def get_SUR(self, av_list, IRR):
        """ get SUR """
        temp_sum = 0.0
        
        temp_list = np.array(av_list)
        temp_list = np.log(temp_list[1:] / temp_list[:-1])
        if self.opt.is_daily:
            temp_list *= 365.0
        else:
            temp_list *= 52.0
            
        for i in range(len(temp_list)):
            temp_sum += min(temp_list[i] - self.tar_grow, 0) ** 2
            
        std = (temp_sum / len(temp_list)) ** 0.5
        return (IRR - self.T_bill_rate) / std

    def get_single_perf(self, av_list):
        """
        get performance indicators for one asset value record
        """
        ROI = self.get_ROI(av_list[0], av_list[-1])
        IRR = self.get_IRR(av_list[0], av_list[-1], self.available_dates[0], self.available_dates[-1])
        SR = self.get_SR(av_list, IRR)
        MD = max(av_list) - min(av_list)
        SUR = self.get_SUR(av_list, IRR)
        
        print("ROI:", ROI)
        print("IRR", IRR)
        print("SR", SR)
        print("MD", MD)
        print("SUR", SUR)
        return PerfStruct(ROI, IRR, SR, MD, SUR)
        
    def get_performance(self):
        """
        get performance indicators for our strategy, SPY, and diversified investing
        """
        self.get_record_SPY()
        self.get_record_div()
        self.get_record()
        
        print("Our strategy:")
        self.perf_self = self.get_single_perf(self.asset_values)
        
        print("\nSPY:")
        self.perf_SPY = self.get_single_perf(self.asset_values_SPY)
        
        print("\nDiversified:")
        self.perf_div = self.get_single_perf(self.asset_values_div)
        
        