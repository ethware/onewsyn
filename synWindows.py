# -*- coding:utf-8  -*-

import os, sys, time, subprocess, shutil
import settings as stts

static = [0,0,0] 

def onewsyn(path_src, path_dst='HELLO_BACKUP', samba=''):
    global static

    for i in range(0,len(static)):
        static[i] = 0
        
    print()

    print('********', 'Synchronizing', path_src, 'to', path_dst, '********')
    forward_update(path_src, path_dst) 
    backward_clean(path_src, path_dst)

    print("    ~~~Synchronizing timestamp", end='')
    timesyn_overall(path_src, path_dst)
    print(".  Operation Complete!")

    print('^_^ *** Operation Complete! Add %d files, Updated %d files, and Removed %d entries. *** ^_^' %(static[0], static[1], static[2]))
    print()

    return 0

def forward_update(path_src, path_dst):
    #备份文件夹的名字与源文件夹的名字可能不同
    #global tempDir
    #global synmode

    if not os.path.exists(path_src):
        print('Invalid Source Path!')
        return 0
    if not os.path.exists(path_dst):
        os.makedirs(path_dst)
    
    dirs_src = os.listdir(path_src)
    dirs_dst = os.listdir(path_dst)

    for item_src in dirs_src:
        abs_itm_src = os.path.join(path_src, item_src)
        abs_itm_dst = os.path.join(path_dst, item_src)
        
        if abs_itm_src in stts.ruleout:
            #不知道continue在这里为什么不起作用
            #print(abs_itm_src)
            #continue 
            print('    !! Ruling out', abs_itm_src)

        else:
            if item_src not in dirs_dst:
                add_orgy(abs_itm_src, abs_itm_dst)

            elif not os.path.isdir(abs_itm_src):
                
                update_file(abs_itm_src, abs_itm_dst)

            elif os.path.isdir(abs_itm_src) and (not os.path.islink(abs_itm_src)):
                forward_update(abs_itm_src, abs_itm_dst)

            elif os.path.islink(abs_itm_src):
                add_orgy(abs_itm_src, abs_itm_dst)

    return 0
    
def backward_clean(path_src, path_dst):

    #global synmode

    dirs_src = os.listdir(path_src)
    dirs_dst = os.listdir(path_dst)

    for item_dst in dirs_dst:

        abs_itm_src = os.path.join(path_src, item_dst)
        abs_itm_dst = os.path.join(path_dst, item_dst)

        if abs_itm_src in stts.ruleout:
            remove_orgy(abs_itm_dst)

        else:

            if item_dst not in dirs_src:
                remove_orgy(abs_itm_dst)

            elif os.path.isdir(abs_itm_dst) and (not os.path.islink(abs_itm_dst)):
                backward_clean(abs_itm_src, abs_itm_dst)

            elif os.path.islink(abs_itm_dst):
                pass
                #remove_orgy(os.path.join(path_dst, item_dst))
    return 0    


def timesyn_overall(path_src, path_dst):
    if not os.path.exists(path_dst):
        return 0
    dirs_src = os.listdir(path_src)
    dirs_dst = os.listdir(path_dst)
    
    for item_src in dirs_src:
        abs_itm_src = os.path.join(path_src, item_src)
        abs_itm_dst = os.path.join(path_dst, item_src)

        if not os.path.isdir(abs_itm_src):
            timesyn_solo(abs_itm_src, abs_itm_dst)
            
        elif os.path.isdir(abs_itm_src) and (not os.path.islink(abs_itm_src)):
            timesyn_overall(abs_itm_src, abs_itm_dst)

        elif os.path.islink(abs_itm_src):
            timesyn_solo(abs_itm_src, abs_itm_dst)

    timesyn_solo(path_src, path_dst)


def timesyn_solo(path_src, path_dst):

    state_src = os.stat(path_src, follow_symlinks=False)
    state_dst = os.stat(path_dst, follow_symlinks=False)

    if abs(state_dst.st_mtime - state_src.st_mtime) > 1:
        #print('Setting time of', path_dst)
        state = state_src
        os.utime(path_dst, (state.st_atime, state.st_mtime)) 

    return 0 


def update_file(file_path_src, file_path_dst):
    
    global static
    #global synmode

    state_src = os.stat(file_path_src, follow_symlinks=False)
    state_dst = os.stat(file_path_dst, follow_symlinks=False)

    if state_src.st_mtime - state_dst.st_mtime > 1:
        print('Updating item: ' + os.path.basename(file_path_src) + ' in ' + os.path.dirname(file_path_src), end='')
        #print(state_src.st_mtime, state_dst.st_mtime)
        '''
        p_copy = subprocess.Popen(['cp', '-a', file_path_src, file_path_dst])
        p_copy.wait()
        '''
        shutil.copy2(file_path_src, file_path_dst, follow_symlinks=False)

        print('.  Operation Complete!')
        static[1] = static[1] + 1

    return 0

def add_orgy(path_src, path_dst):

    global static
    #global synmode

    if not os.path.isdir(path_src):
        print('Adding item: ' + os.path.basename(path_src) + ' to ' + os.path.dirname(path_dst), end='')
        '''
        p_copy = subprocess.Popen(['cp', '-a', path_src, path_dst])
        p_copy.wait()
        '''
        shutil.copy2(path_src, path_dst, follow_symlinks=False)

        print('.  Operation Complete!')
        static[0] = static[0] + 1
    
    elif os.path.isdir(path_src) and (not os.path.islink(path_src)):
        if not os.path.exists(path_dst):
            os.makedirs(path_dst)
        
        dirs_src = os.listdir(path_src)
        for item_src in dirs_src:
            add_orgy(os.path.join(path_src, item_src), os.path.join(path_dst, item_src))
        
    elif os.path.islink(path_src):
        print('Adding item: ' + os.path.basename(path_src) + ' to ' + os.path.dirname(path_dst), end='')
        
        '''
        p_copy = subprocess.Popen(['cp', '-a', path_src, path_dst])
        p_copy.wait()
        '''
        shutil.copy2(path_src, path_dst, follow_symlinks=False)

        print('.  Operation Complete!')
        static[0] = static[0] + 1

    return 0


def remove_orgy(path):
    global static

    print('Removing item: ' + os.path.basename(path) + ' from ' + os.path.dirname(path), end='')
    
    '''
    p_remove = subprocess.Popen(['rm', '-rf', path])
    p_remove.wait()
    '''
    if not os.path.isdir(path):
        os.remove(path)
    elif os.path.isdir(path) and (not os.path.islink(path)):
        shutil.rmtree(path, ignore_errors=False)
    elif os.path.islink(path):
        os.remove(path)

    print('.  Operation Complete!')
    static[2] = static[2] +1

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

    
