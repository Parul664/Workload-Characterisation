from datetime import time
import os
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

BTP_HOME = "/home/poarul/BTP"
AVERAGE_FILE = "average.txt"
PERF_RESULTS = os.path.join(BTP_HOME, "perfResults")
DRAWPLOT_RESULTS = os.path.join(BTP_HOME, "plots")

def temp(savPlot, specific = None):
    benchmarksPresent = os.listdir(path = PERF_RESULTS)
    
    for benchmark in benchmarksPresent:
        
        if specific is not None and specific != benchmark:
            continue

        benchmarkPath = os.path.join(PERF_RESULTS, benchmark)
        # -----
        drawplotPath = os.path.join(DRAWPLOT_RESULTS, benchmark)
        # -----
        testCasesPath = os.listdir(path = benchmarkPath)
        print("\nBENCHMARK :  ", benchmark, "\n")

        testCasesDir = [t for t in testCasesPath if os.path.isdir(os.path.join(benchmarkPath,t))]

        for test in testCasesDir:
            testCasePath = os.path.join(benchmarkPath, test)
            # ---
            testCaseDrawPath = os.path.join(drawplotPath, test)
            # ---

            if os.path.exists(os.path.join(testCasePath, AVERAGE_FILE)):
                print("     Deleting the pre-existing ", AVERAGE_FILE)
                os.remove(os.path.join(testCasePath, AVERAGE_FILE))

            testRunFiles = os.listdir(path = testCasePath)
            os.chdir(testCasePath)

            averageAndPlot(savPlot, testRunFiles, testCaseDrawPath)
        
        if len(testCasesDir) == 0:

            if os.path.exists(os.path.join(benchmarkPath, AVERAGE_FILE)):
                print("     Deleting the pre-existing ", AVERAGE_FILE)
                os.remove(os.path.join(benchmarkPath, AVERAGE_FILE))
            
            os.chdir(benchmarkPath)
            testRunFiles = os.listdir(path = benchmarkPath)
            averageAndPlot(savPlot, testRunFiles, drawplotPath)

            

            

def averageAndPlot(savPlot, testRunFiles, testCaseDrawPath):
    avgTimeStamp, avgValue = np.array([]), np.array([])
    flag = 0

    for testRun in testRunFiles:
        print("     Going through ", testRun)                
        timestamps, values = getDataFromFile(testRun)

        if not flag:
            avgTimeStamp = timestamps
            avgValue = values
            flag = 1
            continue

        a, b = len(avgTimeStamp), len(timestamps)
        if a > b:
            # avgTimeStamp = a
            values = np.pad(values, (0,a-b), mode = 'constant')
        elif a < b:
            avgTimeStamp = timestamps
            avgValue = np.pad(avgValue, (0,b-a), mode="constant")

        # avgTimeStamp = (avgTimeStamp + timestamps)/2
        avgValue = (avgValue + values)/2

    combinedData = np.vstack((avgTimeStamp, avgValue)).T
    np.savetxt(AVERAGE_FILE, combinedData, delimiter=',')
    # print("Path to save for testCase ",test, " is :", testCaseDrawPath)
    if(savPlot):
        print(testCaseDrawPath)
        if not os.path.exists(testCaseDrawPath):
            os.makedirs(testCaseDrawPath)
        final_plot_save_path = os.path.join(testCaseDrawPath,"averagePlot.jpg")
        plotLineGraph(avgTimeStamp, avgValue, final_plot_save_path)



def plotLineGraph(cordX, cordY, storePath, yLabel="Observed Value", xLabel="time"):
    timeStampsLen = cordX.shape[0]
    observedValuesLen = cordY.shape[0]
    assert(timeStampsLen == observedValuesLen)
    
    lowX, highX = np.min(cordX),np.max(cordX)
    lowY, highY = np.min(cordY), np.max(cordY)
    plt.plot(cordX, cordY, label = yLabel)
    plt.title("IPC v/s time")
    plt.xlim(lowX, highX, 1)
    plt.ylim(lowY, highY, 1)
    plt.legend()
    plt.xlabel(xLabel)
    plt.ylabel("IPC")
    print("------------------------\n"+storePath)
    plt.savefig(storePath)
    plt.clf()
                
# specific for IPC
def getDataFromFile(fileName):
    col_names = ['timestamp', 'value', 'unit', 'event', 'UNK1', 'UNK2', 'div_value', 'div']
    data = pd.read_csv(fileName, na_values=['none', '<not counted>'], skiprows=1, header=None, names=col_names)
    
    # taking average of only IPC
    # can be changed later if we want to consider other parameters
    df = data[data['div']=='insn per cycle']
    df = df[df['div_value'].notna()]

    timestamps = df['timestamp'].values
    values = df['div_value']
    # plt.plot(timestamps, values)
    # plt.show()

    return timestamps, values

drawPlot = sys.argv[1]
if len(sys.argv) > 2:
    temp(drawPlot, sys.argv[2])
else:
    temp(drawPlot)