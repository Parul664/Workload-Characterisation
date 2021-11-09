import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def plotLineGraph(cordX, cordY, yLabel="Observed Value", xLabel="time"):
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
    plt.savefig("/home/poarul/BTP/perfResults/436.cactusADM/benchADM.par/results.jpg")

    
def __main__():
    outFileName = "/home/poarul/BTP/perfResults/436.cactusADM/benchADM.par/results.csv"

    col_names = ['timestamp', 'value', 'unit', 'event', 'UNK1', 'UNK2', 'div_value', 'div']
    data = pd.read_csv(outFileName, na_values=['none', '<not counted>'], skiprows=1, header=None, names=col_names)
    df = data[data['div']=='insn per cycle']
    df = df[df['div_value'].notna()]
    plotLineGraph(df['timestamp'].values, df['div_value'].values, 'insn per cycle')

    plt.show()
    return

__main__()