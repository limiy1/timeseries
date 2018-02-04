#!/usr/bin/env python
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

   # @quotes: all the data serie
   # @start_pos: start position of the simulation
   def simulateOnce(self, dataSample, iActionPos):
      print("Start simulation with action postion = " + repr(iActionPos))
      for i in range(0, len(self.lRatioList)):
         [sKey, bRes] = dataSample.searchBack(iActionPos, self.lRatioList[i])
         if (sKey not in self.resultMap):
            lRes = [None] * len(self.lRatioList)
            self.resultMap[sKey] = lRes
         j = i
         while (j>=0 and self.resultMap[sKey][j] == None):
            self.resultMap[sKey][j] = bRes
            j = j-1

   def simulate(self, dataSample):
      for iPos in range(0, dataSample.len()):
         simulateOnce(dataSample, iPos)

