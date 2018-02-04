#!/usr/bin/env python
import datasample
import simulation

###### Read the raw data ######
quotes = datasample.DataSample()
quotes.readFromFile('test.csv')

subsample_size = 120*60
test_start_pos = subsample_size
step_size = 60
effectiveTicksDict = {}

# First pass, record all action information in effectiveTicksDict
while test_start_pos < quotes.len():
   resulttype = simulation.simulateOnce(quotes, test_start_pos, effectiveTicksDict)
   print(resulttype)
   test_start_pos = test_start_pos + step_size

# Create subsamples with effectiveTicksDict
for actionPos in effectiveTicksDict:
   print (actionPos)
   for result in effectiveTicksDict[actionPos]:
      start_pos = effectiveTicksDict[actionPos][result]
      samplequote = datasample.DataSample(quotes, start_pos - subsample_size, actionPos)
      samplequote.reduceLength(60)
      samplequote.plot(120)
