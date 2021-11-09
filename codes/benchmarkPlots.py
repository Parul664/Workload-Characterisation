import os
import numpy as np
from pathlib import Path
import sys

MAIN_FOLDER = "/home/poarul/BTP"
BENCHMARKS = os.path.join(MAIN_FOLDER, "cpu2006/benchspec/CPU2006")
CONFIGS = os.path.join(MAIN_FOLDER, "cpu2006/config")
HOME = os.path.join(MAIN_FOLDER, "cpu2006")
CONFIG = "parul.cfg"

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


benchmarkInputFiles = {}

benchmarkInputFiles["400.perlbench"]=["-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1","-I./lib diffmail.pl 4 800 10 17 19 300", "-I./lib splitmail.pl 1600 12 26 16 4500"] #confirmed
benchmarkInputFiles["401.bzip2"]=["input.source 280"]#,"chicken.jpg 30", "liberty.jpg 30", "input.program 280", "text.html 280", "input.combined 200"]  #confirmed
benchmarkInputFiles["403.gcc"]=["166.i","200.i", "cp-decl.i", "c-typeck.i", "expr2.i", "expr.i", "g23.i", "s04.i", "scilab.i"] #confirmed
benchmarkInputFiles["410.bwaves"]=[] #confirmed
#benchmarkInputFiles["416.gamess"]=[] #setup to check ***************************************************************************************************
benchmarkInputFiles["429.mcf"]=["inp.in"] #confirmed
#benchmarkInputFiles["433.milc"]=[] #asking 0 1 during runtime (what to do ?) --also not stopping when no prompts is given ****************************************
benchmarkInputFiles["434.zeusmp"]=[] #confirmed 
benchmarkInputFiles["435.gromacs"]=["-silent -deffnm gromacs -nice 0"] #confirmed
benchmarkInputFiles["436.cactusADM"]=["benchADM.par"] #confirmed
#benchmarkInputFiles["437.leslie3d"]=[] #not stopping (may be issue with input -i) ********************************************************************************
benchmarkInputFiles["444.namd"]=["--input namd.input --iterations 38"] #confirmed
benchmarkInputFiles["445.gobmk"]=["--gtp-input score2.tst --mode gtp", "--gtp-input 13x13.tst --mode gtp", "--gtp-input nngs.tst --mode gtp", "--gtp-input trevorc.tst --mode gtp", "--gtp-input trevord.tst --mode gtp"] #confirmed
#benchmarkInputFiles["447.dealII"]=[] #build-err ******************************************************************************************************************
#benchmarkInputFiles["450.soplex"]=[] #build-err - no input doubtful **********************************************************************************************
benchmarkInputFiles["453.povray"]=["SPEC-benchmark-ref.ini"] #confirmed
benchmarkInputFiles["454.calculix"]=["-i hyperviscoplastic"] #confirmed
benchmarkInputFiles["456.hmmer"]=["nph3.hmm swiss41","--fixed 0 --mean 500 --num 500000 --sd 350 --seed 0 retro.hmm"] #confirmed
benchmarkInputFiles["458.sjeng"]=["ref.txt"] #confirmed
benchmarkInputFiles["459.GemsFDTD"]=[] #confirmed
benchmarkInputFiles["462.libquantum"]=["1397 8"] #confirmed 
benchmarkInputFiles["464.h264ref"]=["-d foreman_ref_encoder_baseline.cfg","-d foreman_ref_encoder_main.cfg", "-d sss_encoder_main.cfg"] #confirmed
benchmarkInputFiles["465.tonto"]=[] #confirmed 
benchmarkInputFiles["470.lbm"]=["3000 reference.dat 0 0 100_100_130_ldc.of"] #confirmed
benchmarkInputFiles["471.omnetpp"]=["omnetpp.ini"] #confirmed 
benchmarkInputFiles["473.astar"]=["BigLakes2048.cfg", "rivers.cfg"] #confirmed 
benchmarkInputFiles["481.wrf"]=[] #confirmed -- can be a problem (commands file says so)
# command not present in "commands" file  
benchmarkInputFiles["482.sphinx3"]=["ctlfile . args.an4"] #confirmed # different name of executable
benchmarkInputFiles["483.xalancbmk"]=["-v t5.xml xalanc.xsl"] #confirmed
benchmarkInputFiles["998.specrand"]=["1255432124 234923"] #confirmed 
benchmarkInputFiles["999.specrand"]=["1255432124 234923"] #confirmed 

def getUniqueName(filepath):
    filename, extension = os.path.splitext(filepath)
    cnt = 1
    while os.path.exists(filepath):
        filepath = filename + str(cnt) + extension
        cnt += 1
    return filepath

def perfExecute(command, fileName, perfFilter="instructions,cycles"):
    options = {"I": "1000", "e": "\'{"+perfFilter+"}:S\'", "x": ",", "o": fileName}
    p = Perf("stat", options)
    outFileName = p.execute(command)
    print("Perf csv output saved in: ", outFileName)

def runCommands(benchmarkInputFiles, config, inpSize="ref", specific=None):
    RUN_DIR = "run/run_base_" + inpSize + "_amd64-m64-gcc43-nn.0000"
    EXEC_COMMON_NAME = "_base.amd64-m64-gcc43-nn"

    try:
        os.chdir(HOME)
        #os.system("source shrc")
    except:
        print("Please setup cpu2006 first.")
        return

    for benchspec in benchmarkInputFiles.keys():
        # skip build errors
        if benchspec == "447.dealII" or benchspec == "450.soplex":
            print("Skipping " + benchspec)
            continue
        
        # to run specific benchspec, give full name with number
        if specific is not None and specific != benchspec:
            continue

        EXEC_NAME = benchspec.split(".")[1] + EXEC_COMMON_NAME

        if (benchspec == "482.sphinx3"):
            EXEC_NAME = "sphinx_livepretend_base.amd64-m64-gcc43-nn"
        if (benchspec == "483.xalancbmk"):
            EXEC_NAME = "Xalan_base.amd64-m64-gcc43-nn"

        EXEC_DIR = os.path.join(BENCHMARKS, benchspec+"/"+RUN_DIR)
        EXEC_PATH = os.path.join(EXEC_DIR, EXEC_NAME)

        

        # if executable not found
        if not os.path.exists(EXEC_PATH):
            print(benchspec + " executable not found, setting up run directories")

            if benchspec == "400.perlbench": #require manual changes
                print("Please setup perlbench manually. Update makefile.")
                continue
            try:
                os.system("runspec --config=" + config + " --noreportable --tune=base --action=setup --iterations=1 " + benchspec)
            except OSError as err:
                print("Setting up run direcory - OS Exception occured: ", err)
                continue
            except:
                print("Setting up run direcory - Some error occured with setting up run directories for "+ benchspec + ". Please setup manually and rerun.")
                continue
        
        lst = benchmarkInputFiles[benchspec]
        RESULT_DIR = os.path.join(MAIN_FOLDER, "perfResults/"+benchspec)
        Path(RESULT_DIR).mkdir(parents=True, exist_ok=True)
        cmd = None
        os.chdir(EXEC_DIR)
        
        if len(lst) == 0:
            print("running benchmark: ", benchspec)
            cmd = EXEC_PATH
            resultFilePath = getUniqueName(os.path.join(RESULT_DIR, "results.csv"))
            perfExecute(cmd, resultFilePath)
            #os.system("python3 " + os.path.join(MAIN_FOLDER, "codes/runPerf.py " + cmd + " " + resultFilePath))

        else:
            for inp in lst:
                print("running benchmark: ", benchspec, " with input: ", inp)
                inp2 = inp.replace(" ", "_")
                RESULT2_DIR = os.path.join(RESULT_DIR, inp2.replace("/", "_"))
                Path(RESULT2_DIR).mkdir(parents=True, exist_ok=True)
                cmd = EXEC_PATH + " " + inp
                resultFilePath = getUniqueName(os.path.join(RESULT2_DIR, "results.csv"))
                print(os.getcwd())
                perfExecute(cmd, resultFilePath)
        
        os.chdir(HOME)
        print("******************************************************************************************************\n\n\n")


if len(sys.argv) > 1:
    specific = sys.argv[1]
    runCommands(benchmarkInputFiles, CONFIG, specific=specific)
else:
    runCommands(benchmarkInputFiles, CONFIG)


