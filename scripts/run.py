#!/usr/bin/python3

"""
python3 run.py -n $NUM_ITER -d $DATASET
"""

import glob
import json
import os
import sys
import argparse
import subprocess
import json
import glob
import re

if __name__ == "__main__":
    # TODO: check current path $PROJECT_PATH/target/benchbase-2021-SNAPSHOT
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, required=True, help='# of iteration')
    parser.add_argument('--d', type=str, required=True, help='specific dataset: tpcc / ycsb / all')
    args = parser.parse_args()

    result_path = os.path.join(os.getcwd(), "result")
    dataset = 'tpcc' if args.d == "tpcc" else 'ycsb'
    config = 'config/mysql/sample_tpcc_config.xml' if args.d == "tpcc" else "config/mysql/sample_ycsb_config.xml"
    
    print("result path: " + result_path)

    output = []

    summary_files = []
    summary_latency = []

    for i in range(args.n):
        print(dataset)
        proc = subprocess.check_output(['java', '-jar', 'benchbase.jar', '-b', dataset, '-c', config, '--create=true', '--load=true', '--execute=true'])
        out = proc.decode('utf-8').split('\n')
        print('*********************************************************************')
        for o in out:
            if "Rate limited reqs/s:" in o:
                res = re.split(": | = |, ", o.split(" - ")[1])
                throughput, goodput = "", ""
                for r in res:
                    if "throughput" in r:
                        print(r)
                    elif "goodput" in r:
                        print(r)
            if "Output summary data" in o:
                summary_file = os.path.join(result_path, o.split()[-1].strip())
                print(summary_file)
                summary_files.append(summary_file)
        if args.d == "all":
            proc = subprocess.check_output(['java', '-jar', 'benchbase.jar', '-b', 'tpcc', '-c', 'config/mysql/sample_tpcc_config.xml', '--create=true', '--load=true', '--execute=true'])
            out = proc.decode('utf-8').split('\n')
            print('*********************************************************************')
            for o in out:
                if "Rate limited reqs/s:" in o:
                    res = re.split(": | = |, ", o.split(" - ")[1])
                    throughput, goodput = "", ""
                    for r in res:
                        if "throughput" in r:
                            print(r)
                        elif "goodput" in r:
                            print(r)
                if "Output summary data" in o:
                    summary_file = os.path.join(result_path, o.split()[-1].strip())
                    print(summary_file)
                    summary_files.append(summary_file)

    
    for summary_json_file in sorted(glob.glob("./results/*.summary.json")):
        with open(summary_json_file) as summary_json:
            data = json.load(summary_json)
            dbms_type = str(data['DBMS Type']).strip()
            dbms_version = str(data['DBMS Version']).strip()
            benchmark = str(data['Benchmark Type']).strip()
            goodput = str(data['Goodput (requests/second)']).strip()
            throughput = str(data['Throughput (requests/second)']).strip()
            latency = data['Latency Distribution']
            latency_data = latency
            max_latency = str(latency_data['Maximum Latency (microseconds)']).strip()
            median_latency = str(latency_data['Median Latency (microseconds)']).strip()
            min_latency = str(latency_data['Minimum Latency (microseconds)']).strip()
            latency_25 = str(latency_data['25th Percentile Latency (microseconds)']).strip()
            latency_90 = str(latency_data['90th Percentile Latency (microseconds)']).strip()
            latency_95 = str(latency_data['95th Percentile Latency (microseconds)']).strip()
            latency_99 = str(latency_data['99th Percentile Latency (microseconds)']).strip()
            latency_75 = str(latency_data['75th Percentile Latency (microseconds)']).strip()
            avg_latency = str(latency_data['Average Latency (microseconds)']).strip()
            output.append((benchmark, throughput, goodput))
            summary_latency.append((max_latency, median_latency, min_latency, avg_latency, latency_25, latency_75, latency_90, latency_95, latency_99))
    
    for benchmark, throughput, goodput in output:
        print(benchmark + ', throughput: ' + throughput + ", goodput: " + goodput, end='\n')

    for max_latency, median_latency, min_latency, avg_latency, latency_25, latency_75, latency_90, latency_95, latency_99 in summary_latency:
        print(max_latency + ", " + median_latency + ", " + min_latency + ", " + avg_latency + ", " \
        + latency_25 + ", " + latency_75 + ", " + latency_90 + ", " + latency_95 + ", " + latency_99)

