import os

def getOutPutFileBase(inputFileName, outputfilePath='./result'):
   if not os.path.exists(outputfilePath):
      os.makedirs(outputfilePath)

   inp = inputFileName.rsplit('/', 1)[-1].split('.')[0]
   outp = outputfilePath + '/' + inp
   if not os.path.exists(outp):
      os.makedirs(outp)
   return (outp + '/' + inp)

