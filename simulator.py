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
      # format expected of resultMap:
      # "data string": [-1, -1, 1, 0, 1, 1, ...]

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
   simu.plotStat()
   print ('Simulator test ended.')

