#!/usr/bin/env python
import csv
import time, datetime
import matplotlib.dates as dt
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc

debugMode = 0

TIME_FORMAT="%Y%m%d %H%M%S"

def debugPrint(outputString):
   if (debugMode):
      print(outputString)

#--------------- timeConverter ---------------
# @sTimeString: string containing a time to be converted to float
# @sFormat:     string represent the format
# @return:      a float represent the time
#---------------------------------------------
def timeConverter(sTimeString, sFormat = TIME_FORMAT):
   datetime_temp = datetime.datetime.strptime(sTimeString, sFormat)
   return dt.date2num(datetime_temp)

def getDiffInMinutes(timeString1, timeString2, sFormat = TIME_FORMAT):
   datetime1 = datetime.datetime.strptime(timeString1, sFormat)
   datetime2 = datetime.datetime.strptime(timeString2, sFormat)
   deltaTime = datetime2 - datetime1
   return int(deltaTime.total_seconds() / 60)

def addMinutes(timeString, minutes, sFormat = TIME_FORMAT):
   dt = datetime.datetime.strptime(timeString, sFormat)
   dt = dt + datetime.timedelta(seconds=minutes*60)
   return dt.strftime(sFormat)

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
            self.data.append(     (row[0],
                                   float(row[1]),
                                   float(row[2]),
                                   float(row[3]),
                                   float(row[4])) )
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
   # @return:          a list of a tuple
   #-----------------------------------------------------------
   def plot(self, iSeparatorPos = 0):
      self.time2Index()

      fig = plt.figure()
      ax1 = fig.add_subplot(111) # in this function, first number 1 represent the height,

      fig.subplots_adjust(bottom=0.2)
      iBarwidth = self.data[1][0] - self.data[0][0]     # Set the bar width

      candlestick_ohlc(ax1, self.data, width=iBarwidth)
      
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
   # description: replace time field by index
   #----------------------------------------------
   def time2Index(self):
      for i in range(0, len(self.data)):
         self.data[i] = (i,) + self.data[i][1:]

   #--------------- time2float ---------------
   # description: replace time field by float time
   #              (mainly for plot)
   #----------------------------------------------
   def time2float(self):
      for i in range(0, len(self.data)):
         tmp_floattime = timeConverter(self.data[i][0], TIME_FORMAT)
         self.data[i] = (tmp_floattime ,) + self.data[i][1:]


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
   # @iRefPos:     the position of reference (action) data
   # @iStartPos:   start searching position (backward)
   #                  NB: There is always (iStartPos < iRefPos), since iStartPos is only for acceleration purpose
   # @return:      [position found, date string of back search result, 
   #                a number indicating the distance between bound reached pos and reference pos
   #                >0: upper bound reached
   #                <0: lower bound reached
   #                =0: conflicts ]
   #----------------------------------------------
   def searchBack(self, iRefPos, fRatio, iStartPos = None):
      if (iStartPos is None):
         iStartPos = iRefPos - 1
      iPos = iStartPos
      bTouchUpper  = None
      bTouchBottom = None
      while iPos >= 0:
         # Positive benifit
         if (self.data[iRefPos][2] > self.data[iPos][2]*(1+fRatio)):
            bTouchUpper  = True
            debugPrint ("upper bound reached at " + repr(iPos) )
         # Negative benifits
         if (self.data[iRefPos][3] < self.data[iPos][3]*(1-fRatio)):
            bTouchBottom = True
            debugPrint ("lower bound reached at " + repr(iPos) )
         if (bTouchUpper or bTouchBottom):
            diffInMinutes = getDiffInMinutes(self.data[iPos][0],self.data[iRefPos][0])

         if (bTouchUpper and bTouchBottom):
            return [iPos, self.data[iPos][0], 0]   # 0 represents a conflict
         elif (bTouchUpper):
            return [iPos, self.data[iPos][0], diffInMinutes]
         elif (bTouchBottom):
            return [iPos, self.data[iPos][0], -diffInMinutes]
         iPos = iPos - 1
      return None   # None represents not found


   #--------------- searchForward ---------------
   # @fRatio:      the threshold to search
   # @iRefPos:     the position of reference (action) data
   # @iStartPos:   start searching position (forward)
   #                  NB: There is always (iRefPos < iStartPos), since iStartPos is only for acceleration purpose
   # @return:      [position found,
   #                a number indicating the distance between bound reached pos and reference pos]
   #                >0: upper bound reached
   #                <0: lower bound reached
   #                =0: conflicts ]
   #----------------------------------------------
   def searchForward(self, iRefPos, fRatio, iStartPos = None):
      if (iStartPos is None):
         iStartPos = iRefPos + 1
      iPos = iStartPos
      bTouchUpper  = None
      bTouchBottom = None
      maxnum = len(self.data)
      while iPos < maxnum:
         # Positive benifit
         if (self.data[iPos][2] > self.data[iRefPos][2]*(1+fRatio)):
            bTouchUpper  = True
            debugPrint ("upper bound reached at" + repr(iPos) )
         # Negative benifits
         if (self.data[iPos][3] < self.data[iRefPos][3]*(1-fRatio)):
            bTouchBottom = True
            debugPrint ("lower bound reached at" + repr(iPos) )
         if (bTouchUpper or bTouchBottom):
            diffInMinutes = getDiffInMinutes(self.data[iRefPos][0],self.data[iPos][0])

         if (bTouchUpper and bTouchBottom):
            return [iPos, self.data[iPos][0], 0]   # 0 represents a conflict
         elif (bTouchUpper):
            return [iPos, self.data[iPos][0], diffInMinutes]
         elif (bTouchBottom):
            return [iPos, self.data[iPos][0], -diffInMinutes]
         iPos = iPos + 1
      return None   # None represents not found

def test():

   assert getDiffInMinutes('20180101 180300', '20180101 190400') == 61
   print(addMinutes('20180101 180300', 195))
   assert addMinutes('20180101 180300', 195) == '20180101 211800'

   testData = DataSample()
   testData.readFromFile('testcase.csv')
   assert testData.len() == 10
   #testData.plot()
   assert testData.searchBack(3, 0.05) == [2, '20180101 180300', 1]
   assert testData.searchBack(4, 0.05) == [2, '20180101 180300', 2]
   assert testData.searchBack(3, 0.05) == [2, '20180101 180300', 1]
   assert testData.searchBack(9, 0.04) == [8, '20180101 180900', 0]
   assert testData.searchBack(8, 0.05) == [7, '20180101 180800', -1]
   assert testData.searchBack(7, 0.13) == None

   assert testData.searchForward(0, 0.05) == [2, '20180101 180300', 2]
   assert testData.searchForward(1, 0.05) == [3, '20180101 180400', 2]
   assert testData.searchForward(2, 0.05) == [3, '20180101 180400', 1]
   assert testData.searchForward(3, 0.05) == [8, '20180101 180900', -5]
   assert testData.searchForward(4, 0.05) == [8, '20180101 180900', -4]
   assert testData.searchForward(8, 0.04) == [9, '20180101 181000', 0]
   assert testData.searchForward(9, 0.05) == None

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

   print ('DataSample test ended.')
