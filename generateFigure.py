#!/usr/bin/env python
import sys
import simulator
import matplotlib.pyplot as plt
import pathenvironment

inputFile = sys.argv[1]
outputFile = pathenvironment.getOutPutFileBase(inputFile)
print ('Read from file ' + inputFile + ':')

simu = simulator.Simulator([])
simu.loadFromFile(inputFile)
simu.plotStat(outputFile)
simu.plotPeriod(outputFile)
