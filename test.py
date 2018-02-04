#!/usr/bin/env python
import csv
import time, datetime
import matplotlib.dates as dt

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

def getType(quotes, start_pos):
   print("Start simulation with start_pos = " + repr(start_pos))
   reference_p = quotes[start_pos-1][4]
   debugPrint("Reference price: " + repr(reference_p))
   result = STABLE
   test_pos = start_pos
   while test_pos < len(quotes):
      # find for 1st band
      if (result == STABLE):     
         if (quotes[test_pos][2] > reference_p*(1+low_alert_coef)):
            debugPrint("RISE_STALBE from " + repr(test_pos) + ":" + repr(quotes[test_pos][2]))
            result = RISE_STALBE
         if (quotes[test_pos][3] < reference_p*(1-low_alert_coef)):
            if (result == RISE_STALBE):
               debugPrint("1st band conlict encountered at " + repr(test_pos))
               return STABLE
            debugPrint("FALL_STABLE from " + repr(test_pos) + ":" + repr(quotes[test_pos][3]))
            result = FALL_STABLE

      # find for 2nd band
      if ((result == RISE_STALBE) or (result == FALL_STABLE)):     
         if (quotes[test_pos][2] > reference_p*(1+high_alert_coef)):
            debugPrint("XXXX_RISE from " + repr(test_pos) + ":" + repr(quotes[test_pos][2]))
            return result + 1        ## return RISE_RISE or FALL_RISE
         if (quotes[test_pos][3] < reference_p*(1-high_alert_coef)):
            if (result % 3 == 0):    ## if RISE_RISE or FALL_RISE
               debugPrint("2nd band conlict encountered at " + repr(test_pos))
               return result - 1     ## return RISE_STALBE or FALL_STABLE
            debugPrint("XXXX_FALL from " + repr(test_pos) + ":" + repr(quotes[test_pos][3]))
            return result - 1      ## return RISE_FALL or FALL_FALL
      test_pos = test_pos + 1
   debugPrint("STABLE since nothing found")
   return result

NORMALIZED_TICK_NUM = 120

def reduceTicks(quotes):
   result = []
   width = len(quotes)/NORMALIZED_TICK_NUM
   print("Reducing ticks : " + repr(width) + "ticks are merged together")
   counter = 0
   subcounter = width
   for tup in quotes:
      if (subcounter == width):   #first tick, intialization
         mergedTup = tup
         subcounter = 0

      if (tup[2] > mergedTup[2]):
         mergedTup[2] = tup[2]
      if (tup[3] < mergedTup[3]):
         mergedTup[3] = tup[3]
      
      if (subcounter + 1 == width):   #last tick, termination
         mergedTup[4] = tup[4]
         mergedTup[0] = counter
         result.append(mergedTup)
         counter = counter + 1

      subcounter = subcounter + 1

#def writeSample(quotes):
   


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

while test_start_pos < len(quotes):
   resulttype = getType(quotes, test_start_pos)
   samplequote = quotes[test_start_pos - data_sample_size:test_start_pos]
   print(resulttype)
   test_start_pos = test_start_pos + step_size
