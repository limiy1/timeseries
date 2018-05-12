#!/usr/bin/env python
from sys import stdout
import time
import datasample
import numpy as np
import matplotlib.pyplot as plt
from sets import Set

class Simulator:
   def __init__(self, lRatio):
      self.lRatioList = lRatio
      self.tmpMarkers = Set([])
      self.resultMap  = {}
      # Expected format of resultMap:
      # "date string": [-1, -1, 1, 0, 1, 1, ...]
      # ex: 20171212 021300:[-1, None, None, None, None, None]
      # +1/-1 mean upper/under bound will be reached in the future of "date string"

   def __eq__(self, other):
      return ((self.lRatioList == other.lRatioList) and (self.resultMap == other.resultMap))

   # @dataSample: all the data serie
   # @iActionPos: the pressumed action position
   def simulateOnceBackward(self, dataSample, iActionPos):
      datasample.debugPrint("Start simulation with action postion = " + repr(iActionPos))
      iSearchPos = iActionPos - 1

      for i in range(0, len(self.lRatioList)):
         resTmp = dataSample.searchBack(iActionPos, self.lRatioList[i], iSearchPos)
         if (resTmp != None):
            [idx, sKey, iRes] = resTmp
            self.tmpMarkers.add(idx)
            iSearchPos = idx
            if (sKey not in self.resultMap):
               lRes = [None] * len(self.lRatioList)
               self.resultMap[sKey] = lRes
            j = i
            while (j>=0 and self.resultMap[sKey][j] == None):
               self.resultMap[sKey][j] = iRes
               j = j-1
         else:
            break

   # @dataSample: all the data serie
   # @iActionPos: the pressumed action position
   def simulateOnceForward(self, dataSample, iActionPos):
      datasample.debugPrint("Start simulation with action postion = " + repr(iActionPos))
      iSearchPos = iActionPos + 1

      sKey = dataSample.data[iActionPos][0]
      lRes = self.resultMap[sKey]
      for i in range(0, len(self.lRatioList)):
         if (lRes[i] != None):
            resTmp = dataSample.searchForward(iActionPos, self.lRatioList[i], iSearchPos)
            if (resTmp != None):
               [idx, tmpkey, iRes] = resTmp
               lRes[i] = iRes
               iSearchPos = idx
            else:
               print('Error: forward and backward not compatible!')

   # @basetime: the base time in string format
   # @valList:  a list of integer representing minutes after basetime
   def checkDuplication(self, basetime, valList):
      keyForCheck = '';
      for i in range(0, len(valList)):
         if (valList[i] != None):
            keyForCheck += (',' + datasample.addMinutes(basetime, abs(valList[i])) )
         else:
            keyForCheck += ',None'
      if (keyForCheck in self.tmpMarkers):
         return True
      else:
         self.tmpMarkers.add(keyForCheck)
         return False

   def simulate(self, dataSample):
      tic = time.time()
      xPerSecond = 100
      lastPos = 0
      dataNum = dataSample.len()

      self.tmpMarkers.clear()
      # Backward to find key positions
      for iPos in range(0, dataNum):
         stdout.write("\r[%2.1f%%] Simulating with action postion %d/%d (%d/s, %1.1f min remained)" % (iPos/float(dataNum)*100, iPos, dataNum, xPerSecond, (dataNum-iPos)/60.0/xPerSecond) )
         stdout.flush()
         self.simulateOnceBackward(dataSample, iPos)
         if (time.time() - tic > 1):
            xPerSecond = iPos - lastPos
            lastPos = iPos
            tic = time.time()
      stdout.write("\n")

      # Forward check
      print('  Start forward check ...' )
      for iPos in self.tmpMarkers:
         self.simulateOnceForward(dataSample, iPos)
         if (time.time() - tic > 1):
            xPerSecond = iPos - lastPos
            lastPos = iPos
            tic = time.time()

      # Duplication check
      print('  Start duplication check ...' )
      self.tmpMarkers.clear()
      sortedList = sorted(self.resultMap.items())  # return a list of tuple (key, val), sorted by key (date)
      for pos in xrange(len(sortedList)-1, 0, -1):
         if (self.checkDuplication(sortedList[pos][0], sortedList[pos][1])):
            del self.resultMap[sortedList[pos][0]]


   # Save (sorted) result to file
   def saveToFile(self, filename):
      outFile = open(filename, 'w')
      outFile.write(str(self.lRatioList) + '\n')

      sortedList = sorted(self.resultMap.items())  # return a list of tuple (key, val), sorted by key (date)
      for pos in range(0, len(sortedList)):
         x = sortedList[pos][0]
         val = sortedList[pos][1]
         outFile.write( x + ':' +  str(val) + '\n')

   # Load result from file
   def loadFromFile(self, filename):
      inFile = open(filename, 'r')
      self.lRatioList = eval(inFile.readline())
      for line in inFile:
         [key, val] = line.split(':')
         self.resultMap[key] = eval(val)
  

   # Find the distance between two upper-touch or two bottom touch and return the frequency (in one day)
   def getFrequencyFromNearestCounterPart(self, sortedList, currentPos, ratioIdx):
      maxnum = len(sortedList)
      currentTime = sortedList[currentPos][0]
      currentVal = sortedList[currentPos][1][ratioIdx]   # currentVal can never be None or 0

      # Under the same ratio, find the distance between the first -1 on the left and current position (+1)
      i = 1
      dist_left = 0
      while (currentPos - i >= 0):
         if ((sortedList[currentPos-i][1][ratioIdx] != None) and (sortedList[currentPos-i][1][ratioIdx] * currentVal < 0) ):
            dist_left = datasample.getDiffInMinutes(sortedList[currentPos-i][0], currentTime)
            datasample.debugPrint('dist_left = ' + str(dist_left))
            break
         i = i + 1

      # Under the same ratio, find the distance between the first -1 on the left and current position (+1)
      j = 1
      dist_right = 0
      while (currentPos + j < maxnum):
         if ((sortedList[currentPos+j][1][ratioIdx] != None) and (sortedList[currentPos+j][1][ratioIdx] * currentVal < 0) ):
            dist_right = datasample.getDiffInMinutes(currentTime, sortedList[currentPos+j][0])
            datasample.debugPrint('dist_right = ' + str(dist_right))
            break
         j = j + 1

      # If both are found, get the distance between the both -1 and mark both timestamps idx
      if ((dist_left != 0) and (dist_right != 0)):
         return ([24*60.0/(dist_left + dist_right), currentPos - i, currentPos + j])
      # Not found the frequency  
      else:
         return ([None, currentPos - i, currentPos + j])

   # Plot how frequently the action window changes
   def plotPeriod(self, outputbase):
      frequencies = [[] for i in range(len(self.lRatioList))]
      sortedList = sorted(self.resultMap.items())  # return a list of tuple (key, val), sorted by key (date)

      for ratioIdx in range(0, len(self.lRatioList)):
         pos = 0
         while (pos < len(sortedList)):
            stdout.write("\rRatio %5.3f: Processing %d among %d" % (self.lRatioList[ratioIdx], pos, len(sortedList)) )
            stdout.flush()
            if (sortedList[pos][1][ratioIdx] != None):
               [freq, leftPos, rightPos] = self.getFrequencyFromNearestCounterPart(sortedList, pos, ratioIdx)
               if (freq != None):
                  frequencies[ratioIdx].append(freq)
               pos = rightPos
            else:
               pos = pos+1
         stdout.write("\n")
   
         if (frequencies[ratioIdx] != []):
            plt.hist(frequencies[ratioIdx], color='green', alpha=0.75, label=str(self.lRatioList[ratioIdx]))
            plt.legend(loc='upper right')
            plt.title( 'Window frequency (/day) (source:' + outputbase + ')' )
            plt.xlabel('Times/day')
            plt.ylabel('Occurences (Total=' + str(len(frequencies[ratioIdx])) + ')')
            #plt.show()
            plt.savefig(outputbase + '_freq_r' + str(self.lRatioList[ratioIdx]) + '.png')
            plt.close()
         else:
            break

      return frequencies

   # Plot the statistic of resultMap per ratio:
   # - The number of +1
   # - The number of -1
   # - The ratio of (+1/-1)/(total reply)
   def plotStat(self, outputbase):
      num = len(self.lRatioList)
      histoPos  = np.zeros(num)
      histoNeg  = np.zeros(num)
      histoDlm  = np.zeros(num)
      histoSumT = np.zeros(num)
      histoNumT = np.zeros(num)
      for key, vList in self.resultMap.iteritems():
         for i in range(0, len(vList)):
            if (vList[i] != None):
               histoNumT[i] += 1.0
               histoSumT[i] += abs(vList[i])
               if (vList[i] > 0):
                  histoPos[i] += 1.0
               elif (vList[i] < 0):
                  histoNeg[i] += 1.0
               else:
                  histoDlm[i] += 1.0

      idx = np.arange(num)

      # Plot the (actionable ticks)/(all ticks)
      effectiveRatio = np.divide(histoPos + histoNeg, histoPos + histoNeg + histoDlm)*100
      averageWaitTime = np.divide(histoSumT, histoNumT)

      # Set attributes
      fig = plt.figure()
      curveAx = fig.add_subplot(211)
      barAx = curveAx.twinx()

      curveAx.set_ylabel('Effec. Ratio (%)')
      barAx.set_ylabel('Occurence')

      # Plot
      curve, = curveAx.plot(idx, effectiveRatio, 'go-')
      positiveBar = barAx.bar(idx-0.15, histoPos, width = 0.3, color = 'b', align='center', alpha=0.5)
      negativeBar = barAx.bar(idx+0.15, histoNeg, width = 0.3, color = 'r', align='center', alpha=0.5)
      curveAx.legend([curve, positiveBar, negativeBar], ['Effec. Ratio', 'Positive', 'Negative'])

      curveAx.set_ylim([0, 102])
      objects = tuple(self.lRatioList)
      plt.xticks(idx, objects)

      # Add figure for wait time
      waitTimeAx = fig.add_subplot(212)
      waitTimeBar = waitTimeAx.bar(idx, averageWaitTime/60, width = 0.3, color = 'b', align='center', alpha=0.5)
      waitTimeAx.legend([waitTimeBar], ['Response Time (h)'], loc='upper left')
      waitTimeAx.set_xlabel('Ratio')


      # Set x-axis ticks
      plt.xticks(idx, objects)

      plt.title('Statistics (source:' + outputbase + ')' )
      plt.savefig(outputbase + '_stat.png')
      plt.close()
      #plt.show()

def test():
   testData = datasample.DataSample()
   testData.readFromFile('testcase.csv')
   listRatio = [0.05, 0.10, 0.15, 0.20]
   simu = Simulator(listRatio)
   simu.simulate(testData)
   assert simu.resultMap['20180101 180100'] == [2, 3, 3, None]
   assert simu.resultMap['20180101 180300'] == [1, 1, None, None]
   assert simu.resultMap['20180101 180700'] == [-2, -2, None, None]
   assert simu.resultMap['20180101 180800'] == [-1, -2, None, None]
   assert simu.resultMap['20180101 180900'] == [1, None, None, None]

   simu.saveToFile('resultmap.txt')
   simu2 = Simulator([])
   simu2.loadFromFile('resultmap.txt')
   assert simu == simu2
   simu.plotStat('test')

   freqs = simu.plotPeriod('test')
   assert freqs == [[240], [], [], []]
   print ('Simulator test ended.')

