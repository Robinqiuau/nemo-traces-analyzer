#!/usr/bin/env python

import sys, argparse

import logging
logging.basicConfig(level=logging.DEBUG)

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from drive_test_analysis import trace_loader as tl
from drive_test_analysis import nemo_trace_processor as ntp
from drive_test_analysis import data_plotter as dpl

def setup_args():
    parser = argparse.ArgumentParser(description='Plot drive test data.')
    parser.add_argument('-l','--list', action='store_true', help='List all data-set.')
    parser.add_argument('-s','--static', action='store_true', help='Keep samples with zero velocity.')
    parser.add_argument('-d','--select', type=int,
                        help='Select a particular data-set to display')
    parser.add_argument('library',type=str, nargs='+',
                        help='Select a particular library to pull data from')
    parser.add_argument('--print', type=str, help='Print figure to file.')  # nargs='+',
    parser.add_argument('--blind', action='store_true', help='Do not print some numerical data.')
    args   = parser.parse_args()
    return args


def main(args):
    data_file_list = tl.get_data_file_list(args.library)
    if args.list:
        tl.print_list(data_file_list)
        sys.exit(0)
    data = tl.load_data_file(data_file_list,args.select)

    if not args.static:
        logging.debug('Remove zero velocity samples')
        data = ntp.remove_non_positive_velocity_samples(data)

    # Get basic data
    ntp.process_data(data,ntp.process_lte_bw)
    # Now check for difference between 10 and 15 MHz
    ntp.process_data(data,ntp.process_lte_rsrp)
    ntp.process_data(data,ntp.process_lte_rsrp_bw)

    column_list = ['RSRP (serving)','RSRP (serving) 10','RSRP (serving) 15',
                   'RSRP/Antenna port - 1','RSRP/Antenna port - 1 10','RSRP/Antenna port - 1 15',
                   'RSRP/Antenna port - 2','RSRP/Antenna port - 2 10','RSRP/Antenna port - 2 15']
    if args.select is None:
        df = tl.concat_pandas_data([df[column_list] for df in data ])
    else:
        df = data


    plt.ion()
    plt.figure()
    plt.subplot2grid((2,1), (0,0))
    x = np.linspace(-140,-50,91)
    dpl.plot_ecdf_triplet(df['RSRP/Antenna port - 1 10'].dropna(),
                          df['RSRP/Antenna port - 1'].dropna(),
                          df['RSRP/Antenna port - 1 15'].dropna(),x,
                          'RSRP AP1 10 MHz','RSRP AP1','RSRP AP1 15 MHz','dB')
    if args.blind:
        plt.xticks([])
    plt.subplot2grid((2,1), (1,0))
    dpl.plot_ecdf_triplet(df['RSRP/Antenna port - 2 10'].dropna(),
                          df['RSRP/Antenna port - 2'].dropna(),
                          df['RSRP/Antenna port - 2 15'].dropna(),x,
                          'RSRP AP2 10 MHz','RSRP AP2','RSRP AP2 15 MHz','dB')
    if args.blind:
        plt.xticks([])
    if args.print:
        plt.savefig(args.print,dpi=300,bbox_inches='tight')

    input('Press any key')
    

if __name__ == "__main__":
    args = setup_args()
    main(args)
