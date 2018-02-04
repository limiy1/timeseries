#!/usr/bin/env python
import csv
import time, datetime
import matplotlib.dates as dt
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc

low_alert_coef = 0.01
high_alert_coef = 0.02

debugMode = 0
def debugPrint(outputString):
   if (debugMode):
      print(outputString)

##################### Type matrix #######################
#
#   l\h   below_lower     nothing      above_higher
#
#   B_L    FALL_FALL    FALL_STABLE      FALL_RISE
#   N/A      XXXX         STABLE           XXXX
#   A_H    RISE_FALL    RISE_STALBE      RISE_RISE
#
#########################################################

STABLE      = 0
FALL_FALL   = 1
FALL_STABLE = 2
FALL_RISE   = 3
RISE_FALL   = 4
RISE_STALBE = 5
RISE_RISE   = 6
CONFLICT    = 7


def recordResult(result, startPos, actionPos, effectiveTicksDict):
  subdict = {} 
  if (actionPos not in effectiveTicksDict):
      subdict[result] = startPos
      effectiveTicksDict[actionPos] = subdict
  else:
      effectiveTicksDict[actionPos][result] = startPos
      

# @quotes: all the data serie
# @start_pos: start position of the simulation
def voteOnce(quotes, start_pos, effectiveTicksDict):
   print("Start simulation with start_pos = " + repr(start_pos))
   reference_p = quotes[start_pos-1][4]
   debugPrint("Reference price: " + repr(reference_p))
   result1 = STABLE
   result2 = STABLE
   tick1 = -1
   tick2 = -1
   test_pos = start_pos
   while test_pos < len(quotes):
      # find for 1st band
      if (result1 == STABLE):     
         if (quotes[test_pos][2] > reference_p*(1+low_alert_coef)):
            debugPrint("RISE_STALBE from " + repr(test_pos) + ":" + repr(quotes[test_pos][2]))
            result1 = RISE_STALBE 
            tick1 = test_pos
         if (quotes[test_pos][3] < reference_p*(1-low_alert_coef)):
            if (result1 == RISE_STALBE):
               debugPrint("1st band conlict encountered at " + repr(test_pos))   ## RISE_STABLE in conflict with FALL_STABLE
               result1 = CONFLICT
               tick1 = test_pos
               break
            debugPrint("FALL_STABLE from " + repr(test_pos) + ":" + repr(quotes[test_pos][3]))
            result1 = FALL_STABLE
            tick1 = test_pos

      # find for 2nd band
      if ((result1 == RISE_STALBE) or (result1 == FALL_STABLE)):     
         if (quotes[test_pos][2] > reference_p*(1+high_alert_coef)):
            debugPrint("XXXX_RISE from " + repr(test_pos) + ":" + repr(quotes[test_pos][2]))
            result2 = result1 + 1    ## return RISE_RISE or FALL_RISE
            tick2 = test_pos
            break
         if (quotes[test_pos][3] < reference_p*(1-high_alert_coef)):
            if (result % 3 == 0):    ## if RISE_RISE or FALL_RISE
               debugPrint("2nd band conlict encountered at " + repr(test_pos))    ## XXXX_RISE in conflict with XXXX_FALL
               result2 = CONFLICT    ## return RISE_STALBE or FALL_STABLE
               tick2 = test_pos
               break
            debugPrint("XXXX_FALL from " + repr(test_pos) + ":" + repr(quotes[test_pos][3]))
            result2 = result1 - 1        ## return RISE_FALL or FALL_FALL
            tick2 = test_pos
            break
      test_pos = test_pos + 1
   
   ## record result in dict ##
   if (result1 % 7 != 0):   # Not stable nor conflict
      recordResult(result1, start_pos, tick1, effectiveTicksDict)
   if (result2 % 7 != 0):   # Not stable nor conflict
      recordResult(result2, start_pos, tick2, effectiveTicksDict)
   return result2

NORMALIZED_TICK_NUM = 120

def reduceTicks(quotes, data_sample_size):
   result = []
   width = data_sample_size/NORMALIZED_TICK_NUM
   print("Reducing ticks : " + repr(width) + "ticks are merged together")
   counter = 0
   subcounter = width
   for tup in quotes:
      if (subcounter == width):   #first tick, intialization
         mergedList = list(tup)
         subcounter = 0

      if (tup[2] > mergedList[2]):
         mergedList[2] = tup[2]
      if (tup[3] < mergedList[3]):
         mergedList[3] = tup[3]
      
      if (subcounter + 1 == width):   #last tick, termination
         mergedList[4] = tup[4]
         mergedList[0] = counter
         result.append(tuple(mergedList))
         counter = counter + 1

      subcounter = subcounter + 1
   return result

#def writeSample(quotes):
   
def plotSample(quotes, endPos):
   plotquotes = []
   counter = 0
   for eachquote in quotes:
      plotquotes.append( (counter,) + eachquote[1:] )
      counter = counter + 1

   fig = plt.figure()
   ax1 = fig.add_subplot(111) # in this function, first number 1 represent the height,

   fig.subplots_adjust(bottom=0.2)
   barwidth = plotquotes[1][0] - plotquotes[0][0]     # Set the bar width

   candlestick_ohlc(ax1, plotquotes, width=barwidth)
   
   #ax1.xaxis_date()
   ax1.autoscale_view()
   #plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

   # second is for width and third is the plot number
   ylims = ax1.get_ylim();
   ax2 = fig.add_subplot(111) #  make sure both have same arguments for add_subplot function
   ax2.plot([endPos,endPos], ylims, color = 'b', linewidth=0.5, ls = ':')
   plt.show()

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

data_sample_size = 120*60
test_start_pos = data_sample_size
step_size = 60
effectiveTicksDict = {}

while test_start_pos < len(quotes):
   
   resulttype = voteOnce(quotes, test_start_pos, effectiveTicksDict)
   samplequote = quotes[test_start_pos - data_sample_size:test_start_pos]
   print(resulttype)
   test_start_pos = test_start_pos + step_size

for actionPos in effectiveTicksDict:
   print (actionPos)
   for result in effectiveTicksDict[actionPos]:
      start_pos = effectiveTicksDict[actionPos][result]
      samplequote = quotes[start_pos - data_sample_size:actionPos]
      plotSample(reduceTicks(samplequote, data_sample_size), NORMALIZED_TICK_NUM)
