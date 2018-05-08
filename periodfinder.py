#!/usr/bin/env python
from sys import stdout
import simulator
import matplotlib.pyplot as plt

simu = simulator.Simulator([])
simu.loadFromFile('201801.csv.res')
simu.saveToFile('201801.csv.sorted')
simu.plotPeriod()
