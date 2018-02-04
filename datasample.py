#!/usr/bin/env python
import csv
import time, datetime
import matplotlib.dates as dt
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc

#--------------- timeConverter ---------------
# @sTimeString: string containing a time to be converted to float
# @sFormat:     string represent the format
# @return:      a float represent the time
#---------------------------------------------
def timeConverter(sTimeString, sFormat):
   datetime_temp = datetime.datetime.strptime(sTimeString, sFormat)
   return dt.date2num(datetime_temp)

class DataSample:
   def __init__(self, other = None, iStartPos = 0, iEndPos = -1):
      # The format of a sample is:
      # date in float, open, high, low, close
      self.data = []   # Start with empty list
      if (other is not None):
         if (iEndPos == -1):
            iEndPos = other.len()
         self.readFromObject(other, iStartPos, iEndPos)

   def len(self):
      return len(self.data)

   #----------------------- readFromFile ------------------
   # @sourceFilename: the input of file
   # @length:         length of data to read, -1 means all
   # @return:         nothing
   #-------------------------------------------------------
   def readFromFile(self, sSourceFilename, iLength = 0):
      iCounter = 0
      with open(sSourceFilename, 'rb') as csvfile:
         csvreader = csv.reader(csvfile, delimiter=';')
         for row in csvreader:
            # tuple(date in float, open, high, low, close)
            self.data.append((timeConverter(row[0], "%Y%m%d %H%M%S"),
                                   float(row[1]),
                                   float(row[2]),
                                   float(row[3]),
                                   float(row[4])))
            iCounter = iCounter + 1
            if (iCounter == iLength): break

   #----------------------- readFromObject ----------------
   # @oSourceObj: the source object
   # @iStartPos:  start position
   # @iEndPos:    end position
   # @return:     nothing
   #-------------------------------------------------------
   def readFromObject(self, oSourceObj, iStartPos, iEndPos):
      self.data = oSourceObj.data[iStartPos:iEndPos]

#def writeSample(quotes):

   #------------------------- plot ---------------------------
   # @lDataSample:     the data sample to be plot
   # @iSeparatorPos:   the position of vertical line on x-axis 
   # @return:         a list of a tuple
   #-----------------------------------------------------------
   def plot(self, iSeparatorPos = 0):
      lPlotSample = []
      iCounter = 0
      for tup in self.data:
         lPlotSample.append( (iCounter,) + tup[1:] )
         iCounter = iCounter + 1

      fig = plt.figure()
      ax1 = fig.add_subplot(111) # in this function, first number 1 represent the height,

      fig.subplots_adjust(bottom=0.2)
      iBarwidth = lPlotSample[1][0] - lPlotSample[0][0]     # Set the bar width

      candlestick_ohlc(ax1, lPlotSample, width=iBarwidth)
      
      #ax1.xaxis_date()
      ax1.autoscale_view()
      #plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

      if (iSeparatorPos != 0):
         # second is for width and third is the plot number
         ylims = ax1.get_ylim();
         ax2 = fig.add_subplot(111) #  make sure both have same arguments for add_subplot function
         ax2.plot([iSeparatorPos,iSeparatorPos], ylims, color = 'b', linewidth=0.5, ls = ':')
      plt.show()

   #--------------- time2Index ---------------
   # @fRatio:      replace time field by index
   #----------------------------------------------
   def time2Index(self):
      for i in range(0, len(self.data)):
         self.data[i] = (i,) + self.data[i][1:]

   #--------------- reduceLength ---------------
   # @iTimes:    new length = old length/iTimes 
   # @return:    nothing
   #----------------------------------------------
   def reduceLength(self, iTimes):
      result = []
      #print("Reducing length : " + repr(iTimes) + " ticks are merged together")
      iCounter = 0
      iSubcounter = iTimes
      for tup in self.data:
         if (iSubcounter == iTimes):   #first tick, intialization
            mergedList = list(tup)
            iSubcounter = 0

         if (tup[2] > mergedList[2]):
            mergedList[2] = tup[2]
         if (tup[3] < mergedList[3]):
            mergedList[3] = tup[3]
         
         if (iSubcounter + 1 == iTimes):   #last tick, termination
            mergedList[4] = tup[4]
            mergedList[0] = iCounter
            result.append(tuple(mergedList))
            iCounter = iCounter + 1
         iSubcounter = iSubcounter + 1

      if (iSubcounter > 0):           #last data set, if not merged with iTimes data
         mergedList[4] = tup[4]
         mergedList[0] = iCounter
         result.append(tuple(mergedList))
         iCounter = iCounter + 1
      self.data = result

   #--------------- searchBack ---------------
   # @fRatio:      the threshold to search
   # @iStartPos:   start searching position (backward)
   # @return:      [position found, +/-1 indicating upper/bottom bound reached
   #----------------------------------------------
   def searchBack(self, iStartPos, fRatio):
      iPos = iStartPos - 1
      bTouchUpper  = None
      bTouchBottom = None
      while iPos >= 0:
         # iStartPos reach upper bound
         if (self.data[iStartPos][2] > self.data[iPos][2]*(1+fRatio)):
            bTouchUpper  = True
            #print ("upper bound reached at" + repr(iPos) )
         if (self.data[iStartPos][3] < self.data[iPos][3]*(1-fRatio)):
            bTouchBottom = True
            #print ("lower bound reached at" + repr(iPos) )
         if (bTouchUpper and bTouchBottom):
            return None
         elif (bTouchUpper):
            return [self.data[iPos][0], 1]
         elif (bTouchBottom):
            return [self.data[iPos][0], -1]
         iPos = iPos - 1
      return None


def test():
   testData = DataSample()
   testData.readFromFile('testcase.csv')
   assert testData.len() == 10
   #testData.plot()
   testData.time2Index()
   assert testData.searchBack(3, 0.05) == [2, 1]
   assert testData.searchBack(4, 0.05) == [2, 1]
   assert testData.searchBack(3, 0.05) == [2, 1]
   assert testData.searchBack(9, 0.04) == None
   assert testData.searchBack(8, 0.05) == [7, -1]
   assert testData.searchBack(7, 0.13) == None

   testData.reduceLength(2)
   assert testData.data[0][1:] == (1000, 1050, 1000, 1050)
   assert testData.data[1][1:] == (1050, 1200, 1020, 1100)
   assert testData.data[2][1:] == (1100, 1175, 1090, 1115)
   assert testData.data[3][1:] == (1115, 1125, 1065, 1065)
   assert testData.data[4][1:] == (1065, 1135, 935, 975)

   testData.reduceLength(2)
   assert testData.data[0][1:] == (1000, 1200, 1000, 1100)
   assert testData.data[1][1:] == (1100, 1175, 1065, 1065)
   assert testData.data[2][1:] == (1065, 1135, 935, 975)

   testData.reduceLength(2)
   assert testData.data[0][1:] == (1000, 1200, 1000, 1065)
   assert testData.data[1][1:] == (1065, 1135, 935, 975)

   testData.reduceLength(2)
   assert testData.data[0][1:] == (1000, 1200, 935, 975)
