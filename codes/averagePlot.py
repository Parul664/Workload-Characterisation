from datetime import time
import os
from pickle import dump
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

BTP_HOME = "/home/poarul/BTP"
AVERAGE_FILE = "average.csv"
MAIN_AVERAGE_DUMP_FOLDER = "/home/poarul/BTP/averageDump/"
PERF_RESULTS = os.path.join(BTP_HOME, "perfResults")
DRAWPLOT_RESULTS = os.path.join(BTP_HOME, "plots")

# Create a new dump folder for dumping all average files by hand
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

            # for dumping all files in a single folder
            dumpName = benchmark + "_" + test + ".csv"
            averageAndPlot(savPlot, testRunFiles, testCaseDrawPath, dumpName)
        
        if len(testCasesDir) == 0:

            if os.path.exists(os.path.join(benchmarkPath, AVERAGE_FILE)):
                print("     Deleting the pre-existing ", AVERAGE_FILE)
                os.remove(os.path.join(benchmarkPath, AVERAGE_FILE))
            
            os.chdir(benchmarkPath)
            testRunFiles = os.listdir(path = benchmarkPath)

            # for dumping all files in a single folder
            dumpName = benchmark + ".csv"
            averageAndPlot(savPlot, testRunFiles, drawplotPath, dumpName)

            

            

def averageAndPlot(savPlot, testRunFiles, testCaseDrawPath, fileNameForDump):
    avgTimeStamp, avgIpc, avgInstructions = np.array([]), np.array([]), np.array([])
    flag = 0

    for testRun in testRunFiles:
        print("     Going through ", testRun)                
        timestamps, ipcValues, instructionValues = getDataFromFile(testRun)

        if not flag:
            avgTimeStamp = timestamps
            avgIpc = ipcValues
            avgInstructions = instructionValues
            flag = 1
            continue

        a, b = len(avgTimeStamp), len(timestamps)
        if a > b:
            # avgTimeStamp = a
            ipcValues = np.pad(ipcValues, (0,a-b), mode = 'constant')
            instructionValues = np.pad(instructionValues, (0,a-b), mode = 'constant')
        elif a < b:
            avgTimeStamp = timestamps
            avgIpc = np.pad(avgIpc, (0,b-a), mode="constant")
            avgInstructions = np.pad(avgInstructions, (0,b-a), mode="constant")

        # avgTimeStamp = (avgTimeStamp + timestamps)/2
        avgIpc = (avgIpc + ipcValues)/2
        avgInstructions = (avgInstructions + instructionValues)/2

    combinedTimeIpc = np.vstack((avgTimeStamp, avgIpc))
    combinedTimeIpcInstructions = np.vstack((combinedTimeIpc, avgInstructions)).T
    np.savetxt(AVERAGE_FILE, combinedTimeIpcInstructions, delimiter=',')
    np.savetxt(os.path.join(MAIN_AVERAGE_DUMP_FOLDER,fileNameForDump), combinedTimeIpcInstructions, delimiter=',')

    # print("Path to save for testCase ",test, " is :", testCaseDrawPath)
    if(savPlot):
        print(testCaseDrawPath)
        if not os.path.exists(testCaseDrawPath):
            os.makedirs(testCaseDrawPath)
        final_plot_save_path = os.path.join(testCaseDrawPath,"averagePlot.jpg")
        plotLineGraph(avgTimeStamp, avgIpc, final_plot_save_path)



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
    ipc = df['div_value']
    instructions = df['value']
    # plt.plot(timestamps, values)
    # plt.show()

    return timestamps, ipc, instructions

# dumping average into a folder always enabled
drawPlot = sys.argv[1]
if len(sys.argv) > 2:
    temp(drawPlot, sys.argv[2])
else:
    temp(drawPlot)