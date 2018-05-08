#!/usr/bin/env python
from sys import stdout
import time
import datasample
import numpy as np
import matplotlib.pyplot as plt

class Simulator:
   def __init__(self, lRatio):
      self.lRatioList = lRatio
      self.resultMap  = {}
      # Expected format of resultMap:
      # "date string": [-1, -1, 1, 0, 1, 1, ...]
      # ex: 20171212 021300:[-1, None, None, None, None, None]
      # +1/-1 mean upper/under bound will be reached in the future of "date string"

   def __eq__(self, other):
      return ((self.lRatioList == other.lRatioList) and (self.resultMap == other.resultMap))

   # @dataSample: all the data serie
   # @iActionPos: the pressumed action position
   def simulateOnce(self, dataSample, iActionPos):
      #print("Start simulation with action postion = " + repr(iActionPos))
      iSearchPos = iActionPos - 1
      for i in range(0, len(self.lRatioList)):
         resTmp = dataSample.searchBack(iActionPos, self.lRatioList[i], iSearchPos)
         if (resTmp != None):
            [idx, sKey, bRes] = resTmp
            iSearchPos = idx
            if (sKey not in self.resultMap):
               lRes = [None] * len(self.lRatioList)
               self.resultMap[sKey] = lRes
            j = i
            while (j>=0 and self.resultMap[sKey][j] == None):
               self.resultMap[sKey][j] = bRes
               j = j-1
         else:
            break

   def simulate(self, dataSample):
      tic = time.time()
      xPerSecond = 100
      lastPos = 0
      dataNum = dataSample.len()
      for iPos in range(1, dataNum):
         stdout.write("\r[%2.1f%%] Simulating with action postion %d/%d (%d/s, %1.1f min remained)" % (iPos/float(dataNum)*100, iPos, dataNum, xPerSecond, (dataNum-iPos)/60.0/xPerSecond) )
         stdout.flush()
         self.simulateOnce(dataSample, iPos)
         if (time.time() - tic > 1):
            xPerSecond = iPos - lastPos
            lastPos = iPos
            tic = time.time()
      stdout.write("\n")

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
      currentVal = sortedList[currentPos][1][ratioIdx]   # currentVal == +1 or -1

      # Under the same ratio, find the distance between the first -1 on the left and current position (+1)
      i = 1
      dist_left = 0
      while (currentPos - i >= 0):
         if ((sortedList[currentPos-i][1][ratioIdx] != None) and (sortedList[currentPos-i][1][ratioIdx] + currentVal == 0)):
            dist_left = datasample.getDiffInMinutes(sortedList[currentPos-i][0], currentTime)
         i = i + 1

      # Under the same ratio, find the distance between the first -1 on the left and current position (+1)
      j = 1
      dist_right = 0
      while (currentPos + j < maxnum):
         if ((sortedList[currentPos+j][1][ratioIdx] != None) and (sortedList[currentPos+j][1][ratioIdx] + currentVal == 0)):
            dist_right = datasample.getDiffInMinutes(currentTime, sortedList[currentPos+j][0])
         j = j + 1

      # If both are found, get the distance between the both -1 and mark both timestamps idx
      if ((dist_left != 0) and (dist_right != 0)):
         return ([24*60/(dist_left + dist_right), i, j])
      # Not found the frequency  
      else:
         return ([None, i, j])



   def plotPeriod(self):
      frequencies = [[] for i in range(len(self.lRatioList))]
      sortedList = sorted(self.resultMap.items())  # return a list of tuple (key, val), sorted by key (date)
      for pos in range(0, len(sortedList)):
         stdout.write("\rProcessing %d among %d" % (pos, len(sortedList)) )
         stdout.flush()
         for ratioIdx in range(0, len(self.lRatioList)):
            if (sortedList[pos][1][ratioIdx] != None):
               freq = self.getFrequencyFromNearestCounterPart(sortedList, pos, ratioIdx)
               if (freq != 0):
                  frequencies[ratioIdx].append(freq)
            else:
               break;

      stdout.write("\n")
      print(sortedList)
      print(frequencies)

   # Plot the statistic of resultMap per ratio:
   # - The number of +1
   # - The number of -1
   # - The ratio of (+1/-1)/(total reply)
   def plotStat(self):
      num = len(self.lRatioList)
      histoPos = np.zeros(num)
      histoNeg = np.zeros(num)
      histoDlm = np.zeros(num)
      for key, vList in self.resultMap.iteritems():
         for i in range(0, len(vList)):
            if (vList[i] != None):
               if (vList[i] > 0):
                  histoPos[i] += 1.0
               elif (vList[i] < 0):
                  histoNeg[i] += 1.0
               else:
                  histoDlm[i] += 1.0

      idx = np.arange(num)

      # Plot the (actionable ticks)/(all ticks)
      effectiveRatio = np.divide(histoPos + histoNeg, histoPos + histoNeg + histoDlm)*100

      # Set attributes
      fig = plt.figure()
      curveAx = fig.add_subplot(111)
      barAx = curveAx.twinx()

      curveAx.set_ylabel('Effec. Ratio (%)')
      barAx.set_ylabel('Occurence')

      # Plot
      curve, = curveAx.plot(idx, effectiveRatio, 'go-')
      positiveBar = barAx.bar(idx-0.15, histoPos, width = 0.3, color = 'b', align='center', alpha=0.5)
      negativeBar = barAx.bar(idx+0.15, histoNeg, width = 0.3, color = 'r', align='center', alpha=0.5)
      curveAx.legend([curve, positiveBar, negativeBar], ['Effec. Ratio', 'Positive', 'Negative'])

      curveAx.set_ylim([0, 102])

      # Set x-axis ticks
      objects = tuple(self.lRatioList)
      plt.xticks(idx, objects)

      plt.show()

def test():
   testData = datasample.DataSample()
   testData.readFromFile('testcase.csv')
   listRatio = [0.05, 0.10, 0.15, 0.20]
   simu = Simulator(listRatio)
   simu.simulate(testData)
   assert simu.resultMap['20180101 180900'] == [1, None, None, None]
   assert simu.resultMap['20180101 180700'] == [-1, -1, None, None]
   assert simu.resultMap['20180101 180300'] == [1, 1, None, None]
   assert simu.resultMap['20180101 180800'] == [-1, -1, None, None]
   assert simu.resultMap['20180101 180200'] == [1, 1, None, None]
   assert simu.resultMap['20180101 180100'] == [1, 1, 1, None]
   simu.saveToFile('resultmap.txt')
   simu2 = Simulator([])
   simu2.loadFromFile('resultmap.txt')
   assert simu == simu2
   simu.plotStat()
   print ('Simulator test ended.')

