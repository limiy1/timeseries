#!/usr/bin/env python
import datasample
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
      print("Start simulation with action postion = " + repr(iActionPos))
      for i in range(0, len(self.lRatioList)):
         resTmp = dataSample.searchBack(iActionPos, self.lRatioList[i])
         if (resTmp != None):
            [sKey, bRes] = resTmp
            if (sKey not in self.resultMap):
               lRes = [None] * len(self.lRatioList)
               self.resultMap[sKey] = lRes
            j = i
            while (j>=0 and self.resultMap[sKey][j] == None):
               self.resultMap[sKey][j] = bRes
               j = j-1

   def simulate(self, dataSample):
      for iPos in range(1, dataSample.len()):
         self.simulateOnce(dataSample, iPos)

   def plotStat(self):
      histo = [0] * len(self.lRatioList)
      for key, vList in self.resultMap.iteritems():
         for i in range(0, len(vList)):
            if (vList[i] != None):
               histo[i] += 1

      objects = tuple(self.lRatioList)
      x_pos = range(0, len(histo))
      plt.bar(x_pos, histo, align='center', alpha=0.5)
      plt.ylabel('Frequency')
      plt.xticks(x_pos, objects)
      plt.title('Statistics')
 
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

