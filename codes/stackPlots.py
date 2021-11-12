import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import cv2 

BTP_HOME = "/home/poarul/BTP"
AVERAGE_FILE = "average.txt"
PERF_RESULTS = os.path.join(BTP_HOME, "perfResults")
DRAWPLOT_RESULTS = os.path.join(BTP_HOME, "plots")

benchmarksPresent = os.listdir(path = DRAWPLOT_RESULTS)

m = 6
n = 8

fig, axs = plt.subplots(m, n)

i=0
j=0

for benchmark in benchmarksPresent:
    benchmarkPath = os.path.join(DRAWPLOT_RESULTS, benchmark)
    testCasesPath = os.listdir(path = benchmarkPath)
    
    testCasesDir = [t for t in testCasesPath if os.path.isdir(os.path.join(benchmarkPath,t))]    

    for test in testCasesDir:
        testCasePath = os.path.join(benchmarkPath, test)
        img = cv2.imread(os.path.join(testCasePath, 'averagePlot.jpg'))        
        axs[i, j].imshow(img)
        axs[i, j].title.set_text(benchmark)
        axs[i, j].set_xticks([])
        axs[i, j].set_yticks([])
        if j == n-1:
            j=-1
            i+=1
        j+=1

    if len(testCasesDir) == 0:
        img = cv2.imread(os.path.join(benchmarkPath, 'averagePlot.jpg'))        
        axs[i, j].imshow(img)
        axs[i, j].title.set_text(benchmark)
        axs[i, j].set_xticks([])
        axs[i, j].set_yticks([])
        if j == n-1:
            j=-1
            i+=1
        j+=1
plt.show()