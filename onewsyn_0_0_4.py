# -*- coding:utf-8  -*-
import os, sys, time, subprocess
import settings as stts


#支持排除功能，跳过对所选路径的备份与同步；
#修复了一个链接判断使用短命称而没有使用绝对路径的bug；
#2021-05-21
 
#时间戳修改使用单独函数来完成；
#2021-05-18

#samba目录的文件时间戳修改
#[发现cp不能在samba目录保留时间戳！！！]
#区分‘local’模式和‘samba’模式，‘samba’模式下直接使用os.utime同步时间戳，而不进行事前判断。
#2021-05-12

#更好地使用操作系统提供的工具，如cp -a 才能更好的完成任务，避免与操作系统的从冲突.
#所以，作者要去学习shell了
#2021-05-06

#单向文件增量备份：
#   拷贝新建的目录与文件至备份处, 并同步备份处文件的时间戳;
#   拷贝并替换已经修改的源文件至备份处，并同步备份处文件的时间戳;
#   在备份处删除源目录已不存在的目录与文件.
#   支持本地与samba目录
#   参数1: 源路径；参数2: 目标路径[存在参数3时，为samba挂载下的子目录名]; 参数3: samba登陆挂载地址 "//userid:psswd@host/sharedfolder/"
#2021-04-29

synmode = 'local' # or 'samba'
tempDir = '/Users/Shared/tempforonewsyn'
static = [0,0,0] # Added files, Updated files and Removed entries

def onewsyn(path_src, path_dst='HELLO_BACKUP', samba=''):

    global static
    global tempDir
    global synmode

    #本地模式
    if samba == '':
        print('********', 'Synchronizing', path_src, 'to', path_dst, '********')
        synmode = 'local' 
        forward_update(path_src, path_dst) #增加和更新
        backward_clean(path_src, path_dst) #删除备份处多余的文件

    #samba模式
    else:
        print('********', 'Synchronizing', path_src, 'to', samba.split('@')[1] + path_dst, '********')
        tempdir_apear = 0
        synmode = 'samba'

        if not os.path.exists(tempDir):
            p_tempdir = subprocess.Popen(['mkdir', tempDir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = p_tempdir.stdout.read()
            err = p_tempdir.stderr.read()

            if out != b'':
                print(out)

            if err != b'':
                print(err)
                return 1
        else:
            tempdir_apear = 1
        
        p_msb = subprocess.Popen(['mount', '-t', 'smbfs', samba, tempDir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_msb.wait()
        out = p_msb.stdout.read()
        err = p_msb.stderr.read()

        if out != b'':
            print(out)

        if err != b'':
            print(err)
            print('Try Ejecting SMB Volume First!')
            return 1

        path_dst = tempDir + '/' + path_dst
        forward_update(path_src, path_dst) 
        backward_clean(path_src, path_dst)

        time.sleep(1)
        p_um = subprocess.Popen(['umount', tempDir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p_um.wait()
        out = p_um.stdout.read()
        err = p_um.stderr.read()

        if out != b'':
            print(out)

        if err != b'':
            print(err)
            return 1

        if tempdir_apear == 0:
            p_rm = subprocess.Popen(['rmdir', tempDir])
            p_rm.wait()

    #print('Operation Complete!')

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
        
        '''这里添加排除路径功能的代码'''
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
            
    
    timesyn(path_src, path_dst)

    return 0
    
def backward_clean(path_src, path_dst):

    #global synmode

    dirs_src = os.listdir(path_src)
    dirs_dst = os.listdir(path_dst)

    for item_dst in dirs_dst:

        abs_itm_src = os.path.join(path_src, item_dst)
        abs_itm_dst = os.path.join(path_dst, item_dst)

        if item_dst not in dirs_src:
            remove_orgy(abs_itm_dst)

        elif os.path.isdir(abs_itm_dst) and (not os.path.islink(abs_itm_dst)):
            backward_clean(abs_itm_src, abs_itm_dst)

        elif os.path.islink(abs_itm_dst):
            pass
            #remove_orgy(os.path.join(path_dst, item_dst))
    
    timesyn(path_src, path_dst)

    return 0    


def update_file(file_path_src, file_path_dst):
    
    global static
    #global synmode

    state_src = os.stat(file_path_src, follow_symlinks=False)
    state_dst = os.stat(file_path_dst, follow_symlinks=False)

    if state_src.st_mtime - state_dst.st_mtime > 1:
        print('Updating item: ' + os.path.basename(file_path_src) + ' in ' + os.path.dirname(file_path_src), end='')
        #print(state_src.st_mtime, state_dst.st_mtime)
        p_copy = subprocess.Popen(['cp', '-a', file_path_src, file_path_dst])
        p_copy.wait()

        timesyn(file_path_src, file_path_dst)

        print('.  Operation Complete!')
        static[1] = static[1] + 1

    return 0

def add_orgy(path_src, path_dst):

    global static
    #global synmode

    if not os.path.isdir(path_src):
        print('Adding item: ' + os.path.basename(path_src) + ' to ' + os.path.dirname(path_dst), end='')
        p_copy = subprocess.Popen(['cp', '-a', path_src, path_dst])
        p_copy.wait()

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
        p_copy = subprocess.Popen(['cp', '-a', path_src, path_dst])
        p_copy.wait()

        print('.  Operation Complete!')
        static[0] = static[0] + 1

    timesyn(path_src, path_dst)

    return 0


def remove_orgy(path):
    global static

    print('Removing item: ' + os.path.basename(path) + ' from ' + os.path.dirname(path), end='')
    p_remove = subprocess.Popen(['rm', '-rf', path])
    p_remove.wait()

    print('.  Operation Complete!')
    static[2] = static[2] +1

    return 0


def timesyn(path_src, path_dst):

    global synmode

    state_src = os.stat(path_src, follow_symlinks=False)
    state_dst = os.stat(path_dst, follow_symlinks=False)

    if synmode == 'local':
        if abs(state_dst.st_mtime - state_src.st_mtime) > 1:
            state = state_src
            os.utime(path_dst, (state.st_atime, state.st_mtime), follow_symlinks=False)
    elif synmode == 'samba':
        state = state_src
        os.utime(path_dst, (state.st_atime, state.st_mtime), follow_symlinks=False)
    else:
        if abs(state_dst.st_mtime - state_src.st_mtime) > 1:
            state = state_src
            os.utime(path_dst, (state.st_atime, state.st_mtime), follow_symlinks=False)        

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

    
