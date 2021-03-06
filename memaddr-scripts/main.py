#################################################################
##   This script is used to obtain the 'percentage of memory   ##
##   address instructions' of a series of programs at both     ##
##   the IR and assembly level.                                ##
#################################################################

#################################################################
# To invoke, run main.py in its root folder using python3. Each 
# program you wish to measure should be in its own subfolder 
# within the ./benchmarks folder, containing the following:
# 
#  - a text file with any command line input (filename: input.txt)
#  - any other input files required for that program
#  - the x86 executable (filename: x86) 
#  - the LLFI-indexed LLVM IR (filename: ir.ll)
#        -this should be the .ll file generated by LLFI during 
#         the profiling pass, found in the llfi experiment 
#         directory under "llfi/filename-llfi_index.ll"
#  - the fault injection logs as generated by LLFI 
#    (filename: llfi.stat.fi.injectedfaults.txt)
#        -if this file was not generated by LLFI, place the 
#         llfi_stat_output folder in this directory instead 
#         (this script will use these logs instead of the 
#         llfi.stat.fi.injectedfaults.txt file but it is slightly 
#         more time-consuming)
#
# You are also required to have a specifc PIN tool installed, 
# see README.md for more information.
# 
# NOTE: make sure the hardcoded filepaths for PIN are correct to 
#       your setup! see globals.py file
#################################################################

import os
import subprocess
import csv

from globals import *
from x86_analysis import *
from ir_analysis import *

def main():

    # array to hold results
    # format: (benchmark name, x86 memory address %, IR memory address %)
    results = []
    results.append(["Benchmark", "x86 dyn percent", "x86 static percent", "IR dyn percent", "IR static percent"])
    
    # loop through benchmark directories
    for folder in os.listdir(BENCHMARKS_DIR):
        if os.path.isdir(os.path.join(BENCHMARKS_DIR, folder)):
            # the code in this block is executed for each benchmark folder
            print("\nExecuting analysis for folder: ./benchmarks/" + folder + "\n")
            
            # set path variables
            benchmark_dir = os.path.join(BENCHMARKS_DIR, folder)
            ir_file       = os.path.join(benchmark_dir, "ir.ll")

            # get command line program inputs from input.txt
            input_file    = os.path.join(benchmark_dir, "input.txt")
            program_inputs = []
            try:
                with open(input_file, "r") as f:
                    # read contents of input file and save as a list of arguments
                    f_contents = f.read().split() 
                    program_inputs.extend(f_contents)
            except:
                print ("\tError reading input.txt, include the file even if it is empty (i.e., no input arguments)")
                continue # move onto next benchmark if exception is thrown

            # run analysis for x86 file
            try:
                x86_result, x86_static = x86_analysis(program_inputs, benchmark_dir)
                if x86_result < 0:
                    # unsuccessful analysis (return value negative), skip to next benchmark
                    print ("Unsuccessful analysis: x86_result = " + str(x86_result))
                    ir_result  = -1
                    ir_static  = -1
                    results.append([folder, x86_result, x86_static, ir_result, ir_static])
                    continue
                else:
                    # successful analysis, continue for this benchmark
                    print ("\tDone analysis for x86 executable\n")
                    pass
            except:
                # unsuccessful analysis (exception thrown), skip to next benchmark
                x86_result = -1
                x86_static = -1
                ir_result  = -1
                ir_static  = -1
                results.append([folder, x86_result, x86_static, ir_result, ir_static])
                continue
            
            # run analysis for IR file
            try:
                ir_result, ir_static = ir_analysis(benchmark_dir)
                if ir_result < 0:
                    # unsuccessful analysis (return value negative), skip to next benchmark
                    print ("Unsuccessful analysis: ir_result = " + str(ir_result))
                    results.append([folder, x86_result, x86_static, ir_result, ir_static])
                    continue
                else:
                    # successful analysis, continue for this benchmark
                    print ("\tDone analysis for LLVM IR code\n")
                    pass
            except:
                # unsuccessful analysis (exception thrown), skip to next benchmark
                ir_result  = -1
                ir_static  = -1
                results.append([folder, x86_result, x86_static, ir_result, ir_static])
                continue

            # save results for this benchmark
            results.append([folder, x86_result, x86_static, ir_result, ir_static])

    # save results to csv file
    results_file = os.path.join(ROOT_DIR, "results.csv")
    with open(results_file, "w") as f:
        writer = csv.writer(f)
        writer.writerows(results)


if __name__ == "__main__":
    main()
