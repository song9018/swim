#!/usr/bin/env python
# coding=utf-8
import os, ctypes,struct
import glob


def judge(pathDir):
    file = open(pathDir, 'r')
    list = file.readlines()

    for i in range(len(list) - 1):

        if "1A9000" not in list[i]:
            time = int(list[i].split(":")[0], base=16)
            time1 = int(list[i + 1].split(":")[0], base=16)
            if time1 - time != 18:
                print("数据丢失：%s\n%s" % (time1, time))


def handle(pathDir, time):
    o_fd = open('%s_处理后数据xh3s.txt' % time, 'w', encoding="utf-8")
    o_fd.write('ax ay az gx gy gz mx my mz\n'.replace(' ', ' ' * 3))

    flash_addr = 0x1A9000
    for line in open(pathDir, 'r'):
        
        line = line.strip()
        if not len(line):
            continue

        sp = line.split(':')
        if len(sp) < 2:
            continue

        cur_addr = int(sp[0], base=16)
        if cur_addr != flash_addr:
            print ('数据有丢失', line, hex(cur_addr), hex(flash_addr))
        flash_addr = cur_addr + 18

        if sp[1] == 'f' * 36:
            continue

        u16s = [0] * 9
        for i in range(9):
            u16s[i] = int(sp[1][i * 4:i * 4 + 4], base=16)
        if 0xdcba == u16s[0] and (0x4321 == u16s[1] or u16s[1] > 0x9800):
            sec = (u16s[2] + (u16s[3] << 16)) % (24 * 60 * 60)
            minute = sec / 60
            hour = minute / 60


            if 0x4321 == u16s[1]:
                o_fd.write('time %d:%02d:%02d\t' % (hour, minute % 60, sec % 60))
                strokes = ctypes.c_short(u16s[4]).value
                laps = ctypes.c_short(u16s[6]).value
                style = ctypes.c_short(u16s[8]).value
                o_fd.write('strokes=%d\tlaps=%d\tstyle=%d\n' % (strokes, laps, style))
            elif 0x9876 == u16s[1]:
                # 开始游泳，记录地磁校准值
                o_fd.write('\ntime %d:%02d:%02d\t' % (hour, minute % 60, sec % 60))
                x = ctypes.c_short(u16s[4]).value
                y = ctypes.c_short(u16s[6]).value
                z = ctypes.c_short(u16s[8]).value
                o_fd.write('mag_center= %d %d %d\t\t' % (x, y, z))
            elif 0x9875 == u16s[1]:
                x = struct.unpack('f', struct.pack('I', u16s[2] + (u16s[3] << 16)))[0]
                y = struct.unpack('f', struct.pack('I', u16s[4] + (u16s[5] << 16)))[0]
                z = struct.unpack('f', struct.pack('I', u16s[6] + (u16s[7] << 16)))[0]
                o_fd.write('radii = %f %f %f\t\t' % (x, y, z))
            elif 0x9874 == u16s[1]:
                x = struct.unpack('f', struct.pack('I', u16s[2] + (u16s[3] << 16)))[0]
                y = struct.unpack('f', struct.pack('I', u16s[4] + (u16s[5] << 16)))[0]
                o_fd.write('fitacry = %f %f\n' % (x, y))
        else:
            for i in range(9):
                s = '%d ' % ctypes.c_short(u16s[i]).value
                o_fd.write(s)
            o_fd.write('\n')

    o_fd.close()



def get_data(time):
    file = open("%s_处理后数据xh3s.txt" % time, 'r', encoding="utf-8")
    k = 0
    list1 = []
    get_time = []
    time_list = 0
    list = file.readlines()
    for i in range(len(list)):
        if "time" in list[i] and "mag_center" in list[i]:
            qq = list[i].strip("\t\n").replace(":", "_")
            get_time.append(qq.split()[1])
            k += 1
            list1.append(i)
    list1.append(len(list) - 1)
    s = 0
    while k > time_list:

        o_fd = open('./拆分数据文件/九轴数据(时间)/xh3s_%s %s.txt' % (time, get_time[time_list]), 'w', encoding="utf-8")
        for i in range(len(list) - (list1[s]) - 1):
            o_fd.write(list[i + (list1[s])])
            if i + (list1[s]) + 1 == list1[s + 1]:
                break

        o_fd.close()
        s += 1
        time_list += 1


def get_time():
    file = glob.glob(".\\拆分数据文件\\九轴数据(时间)\\*.txt")
    for i in range(len(file)):
        file1 = open(file[i], 'r', encoding="utf-8")
        list = file1.readlines()
        list1 = []
        list2 = []
        list3=[]

        for k in range(len(list)):
            if "time" not in list[k]:
                list1.append(list[k])
            if "time" in list[k] and "mag_center" in list[k]:
                list3.append(list[k])
            if "time" in list[k] and "mag_center" not in list[k]:
                style = list[k].split()[4].split("=")[1]
                style1 = list[k].split()[4]

                if style == "1":
                    list2.append(list[k].replace(style1, "style=自由泳"))
                if style == "2":
                    list2.append(list[k].replace(style1, "style=蛙泳"))
                if style == "3":
                    list2.append(list[k].replace(style1, "style=仰泳"))
                if style == "4":
                    list2.append(list[k].replace(style1, "style=蝶泳"))

        path = file[i].split(".")[1].split("\\")[3]
        file2 = open(os.path.join(os.getcwd(), "拆分数据文件\九轴数据(无时间)\(纯数据)%s.txt" % path), 'w', encoding="utf-8")
        file2.writelines(list1)

        file3 = open(file[i], 'w', encoding="utf-8")
        file3.writelines(list3)
        file3.writelines(list1)
        file3.writelines(list2)
        file3.close()


def run():
    file = glob.glob("*.log")

    for i in range(len(file)):
        time = file[i].split("RTT_Terminal_")[1].split(".")[0]

        judge(file[i])
        handle(file[i], time)
        get_data(time)


def rm_file():
    for file in glob.glob(os.path.join(r'拆分数据文件\九轴数据(时间)', '*')):
        os.remove(file)
    for file in glob.glob(os.path.join(r'拆分数据文件\九轴数据(无时间)', '*')):
        os.remove(file)
    for file in glob.glob('*.txt'):
        os.remove(file)


if __name__ == '__main__':
    rm_file()
    run()
    get_time()
