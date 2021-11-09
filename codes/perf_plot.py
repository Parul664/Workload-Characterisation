import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

class Perf:
    def __init__(self, cmd, options):
        self.cmd = cmd
        self.options = options
    
    def __runCommand(self, cmd):
        try:
            os.system(cmd)
        except OSError as err:
            print("OS Exception occured: ", err)
        except: 
            print("Unknown Exception")
    
    def execute(self, processCommand):
        cmd = "sudo perf " + self.cmd
        for key, value in self.options.items():
            cmd += " -" + key + " " + value
        cmd += " " + processCommand
        print("The command to be executes is: ", cmd)
        self.__runCommand(cmd)
        if "o" in self.options.keys(): 
            return self.options["o"]

def plotLineGraph(cordX, cordY, yLabel="Observed Value", xLabel="time"):
    timeStampsLen = cordX.shape[0]
    observedValuesLen = cordY.shape[0]
    assert(timeStampsLen == observedValuesLen)
    
    lowX, highX = np.min(cordX),np.max(cordX)
    lowY, highY = np.min(cordY), np.max(cordY)
    plt.plot(cordX, cordY, label = yLabel)
    plt.title("Workload v/s time")
    plt.xlim(lowX, highX, 1)
    plt.ylim(lowY, highY, 1)
    plt.legend()
    plt.xlabel(xLabel)
    plt.ylabel("Count")

    
def __main__(command, fileName, onlyIPC):
    options = {"I": "100", "e": "\'{instructions, cycles}:S\'", "x": ",", "o": fileName}
    p = Perf("stat", options)
    outFileName = p.execute(command)

    col_names = ['timestamp', 'value', 'unit', 'event', 'UNK1', 'UNK2', 'div_value', 'div']
    data = pd.read_csv(outFileName, na_values=['none', '<not counted>'], skiprows=1, header=None, names=col_names)
    if not onlyIPC: 
        allEvents = data['event'].unique()
        for event in allEvents:
            df = data[data['event']==event]
            df = df[df['value'].notna()]
            plotLineGraph(df['timestamp'].values, df['value'].values, event)
    else:
        df = data[data['div']=='insn per cycle']
        df = df[df['div_value'].notna()]
        plotLineGraph(df['timestamp'].values, df['div_value'].values, 'insn per cycle')

    plt.show()
    return
# __main__("cheese", 'results.csv', 1)
# __main__("runspec --config=parul.cfg --size=ref --noreportable --tune=base --iterations=1 bzip2", "results.csv")
#__main__(" /home/poarul/BTP/cpu2006/benchspec/CPU2006/401.bzip2/run/run_base_ref_amd64-m64-gcc43-nn.0000/bzip2_base.amd64-m64-gcc43-nn input.source 280", "results.csv", 1)
__main__("./gcc_base.amd64-m64-gcc43-nn cccp.i","results.csv", 1)
