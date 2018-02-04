#!/usr/bin/env python
debugMode = 0

def debugPrint(outputString):
   if (debugMode):
      print(outputString)

def recordResult(result, startPos, actionPos, effectiveTicksDict):
  subdict = {} 
  if (actionPos not in effectiveTicksDict):
      subdict[result] = startPos
      effectiveTicksDict[actionPos] = subdict
  else:
      effectiveTicksDict[actionPos][result] = startPos

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

class Simulation:
   def __init__(self, lowcoef, highcoef):
      self.low_alert_coef = lowcoef
      self.high_alert_coef = highcoef

   # @quotes: all the data serie
   # @start_pos: start position of the simulation
   def simulateOnce(quotes, start_pos, effectiveTicksDict):
      print("Start simulation with start_pos = " + repr(start_pos))
      reference_p = quotes.data[start_pos-1][4]
      debugPrint("Reference price: " + repr(reference_p))
      result1 = STABLE
      result2 = STABLE
      tick1 = -1
      tick2 = -1
      test_pos = start_pos
      while test_pos < len(quotes.data):
         # find for 1st band
         if (result1 == STABLE):     
            if (quotes.data[test_pos][2] > reference_p*(1+self.low_alert_coef)):
               debugPrint("RISE_STALBE from " + repr(test_pos) + ":" + repr(quotes.data[test_pos][2]))
               result1 = RISE_STALBE 
               tick1 = test_pos
            if (quotes.data[test_pos][3] < reference_p*(1-self.low_alert_coef)):
               if (result1 == RISE_STALBE):
                  debugPrint("1st band conlict encountered at " + repr(test_pos))   ## RISE_STABLE in conflict with FALL_STABLE
                  result1 = CONFLICT
                  tick1 = test_pos
                  break
               debugPrint("FALL_STABLE from " + repr(test_pos) + ":" + repr(quotes.data[test_pos][3]))
               result1 = FALL_STABLE
               tick1 = test_pos

         # find for 2nd band
         if ((result1 == RISE_STALBE) or (result1 == FALL_STABLE)):     
            if (quotes.data[test_pos][2] > reference_p*(1+self.high_alert_coef)):
               debugPrint("XXXX_RISE from " + repr(test_pos) + ":" + repr(quotes.data[test_pos][2]))
               result2 = result1 + 1    ## return RISE_RISE or FALL_RISE
               tick2 = test_pos
               break
            if (quotes.data[test_pos][3] < reference_p*(1-self.high_alert_coef)):
               if (result % 3 == 0):    ## if RISE_RISE or FALL_RISE
                  debugPrint("2nd band conlict encountered at " + repr(test_pos))    ## XXXX_RISE in conflict with XXXX_FALL
                  result2 = CONFLICT    ## return RISE_STALBE or FALL_STABLE
                  tick2 = test_pos
                  break
               debugPrint("XXXX_FALL from " + repr(test_pos) + ":" + repr(quotes.data[test_pos][3]))
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
