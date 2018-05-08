#!/usr/bin/env python
from sys import stdout
import simulator
import matplotlib.pyplot as plt

simu = simulator.Simulator([])
simu.loadFromFile('resultmap.txt')
simu.plotPeriod()
