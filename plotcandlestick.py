#!/usr/bin/env python
import csv
import time, datetime
import matplotlib.dates as dt
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc

###### Read the raw data ######
quotes = []

with open('test.csv', 'rb') as csvfile:
   spamreader = csv.reader(csvfile, delimiter=';')
   for row in spamreader:
      # Get the time in datatime format
      datetime_temp = datetime.datetime.strptime(row[0], "%Y%m%d %H%M%S")
      # tuple(date in float, open, high, low, close)
      quotes.append((dt.date2num(datetime_temp),
                          float(row[1]),
                          float(row[2]),
                          float(row[3]),
                          float(row[4])))

###### Start to plot #####
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

barwidth = quotes[1][0] - quotes[0][0]     # Set the bar width

candlestick_ohlc(ax, quotes, width=barwidth)

ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

plt.show()

