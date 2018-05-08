#!/usr/bin/env python
import sys
import datasample
import simulator

inputFile = sys.argv[1]
print ('Read from file ' + inputFile + ':')
myData = datasample.DataSample()
myData.readFromFile(inputFile)
listRatio = [0.005, 0.010, 0.015, 0.020, 0.025, 0.030]
simu = simulator.Simulator(listRatio)
simu.simulate(myData)
simu.saveToFile(inputFile+'.res')
simu.plotStat()
