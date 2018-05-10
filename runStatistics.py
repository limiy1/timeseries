#!/usr/bin/env python
import sys
import datasample
import simulator
import pathenvironment

inputFile = sys.argv[1]
outputFile = pathenvironment.getOutPutFileBase(inputFile)
print ('Read from file ' + inputFile + ':')
myData = datasample.DataSample()
myData.readFromFile(inputFile)
listRatio = [0.005, 0.010, 0.015, 0.020, 0.025, 0.030]
simu = simulator.Simulator(listRatio)
simu.simulate(myData)
simu.saveToFile(outputFile+'.res')
simu.plotStat(outputFile)
simu.plotPeriod(outputFile)
