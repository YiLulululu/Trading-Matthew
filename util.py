#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 23:04:32 2019

@author: Du Chao and Lu Yi
"""

import datetime

def days_ago(d, start_date=None):
    """
    get the date string for d days ago
    """
    #today is August 13, 10 days ago means August 3
    if start_date==None:
        date = datetime.datetime.today() - datetime.timedelta(days=d)
    else:
        date = str_to_date(start_date) - datetime.timedelta(days=d)
    return date.strftime("%Y-%m-%d")

def str_to_date(dt):
    """
    convert date string to datetime.date object
    """
    year, month, day = (int(x) for x in dt.split('-'))    
    return datetime.date(year, month, day)