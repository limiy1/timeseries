#!/usr/bin/env python
import datasample


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

def test():
   testData = datasample.DataSample()
   testData.readFromFile('testcase.csv')
   listRatio = [0.05, 0.10, 0.15, 0.20]
   simu = Simulator(listRatio)
   simu.simulate(testData)
   print simu.resultMap

