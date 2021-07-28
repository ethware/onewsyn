# -*- coding:utf-8  -*-

import os, sys, time, subprocess
import settings as stts

def onewsyn(path_src, path_dst='HELLO_BACKUP', samba=''):

    return 0


if __name__ == '__main__':
    args = sys.argv

    if len(args) == 3:
        onewsyn(args[1], args[2])

    elif len(args) == 4:
        onewsyn(args[1], args[2], samba=args[3])

    else:
        for wkload in stts.workloads:
            nargs = len(wkload)

            if nargs == 2:
                onewsyn(wkload[0], wkload[1])

            elif nargs == 3:
                onewsyn(wkload[0], wkload[1], wkload[2])
                
            else:
                print('Bad arguments!')

    
