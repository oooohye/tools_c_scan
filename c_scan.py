# coding=utf-8
import sys

import requests
from queue import Queue
from config import *
from common import *
from IPy import IP
import threading
import os
import re


class C_scan(object):
    dict = None

    def __init__(self):
        self._ips = []
        self._c_ip = ""
        self._queue = Queue()
        self._thread_count = 0
        self._threads = []
        self.result = []

    def _init_queue(self, ips):
        self._ips = ips
        for i in self._ips:
            for port in ports:
                self._queue.put(f"http://{i}:{port}")
                self._queue.put(f"https://{i}:{port}")

    # 检测是否有相同数据结果文件，有则删除，保留最新结果
    def _init_file(self):
        mkdir(path)
        mkdir(nmap_path)
        if os.path.exists(self._path):
            os.remove(self._path)

    def _get_nmap_ips(self):
        if not os.path.exists(nmap_ips_path):
            print("nmap文件不存在！！")
            exit(-1)
        with open(nmap_ips_path, "r") as f:
            # 将数据全部读取出来
            ips_data = f.read()
            # 写正则
            pattern = r'<address addr="(.*?)" addrtype="ipv4"/>'
            ips = re.findall(pattern, ips_data)
        st = str(ips[0]).rsplit('.')
        st[-1] = "0"
        c_ip = ""
        for i in st:
            c_ip += i + "."
        c_ip = c_ip.rstrip('.') + "/24"
        self._c_ip = c_ip
        self._path = path + str(self._c_ip).replace('.', '_').replace('/', '_') + ".txt"
        return ips

    def start(self):
        print("是否启用nmap联合扫描 y/n：")
        res = sys.stdin.readline().strip()
        if res == 'y' or res == 'Y':
            ips = self._get_nmap_ips()
            self._init_queue(ips)
            print("请输入线程数量")
            self._thread_count = int(sys.stdin.readline().strip())
        elif res == 'n' or res == 'N':
            self._init_info()
            self._init_queue(IP(self._c_ip))
        else:
            print("输入错误!!!")
            exit(-1)
        self._init_file()
        print("开始扫描：")
        for i in range(self._thread_count):
            self._threads.append(self.Scan(self._queue, self._c_ip, self._path))
        for t in self._threads:
            t.start()
        for t in self._threads:
            t.join()
        print("\n扫描完成!!")
        with open(self._path, "r") as f:
            print(f.read())

    def _init_info(self):
        print("请输入你想查询的IP段")
        self._c_ip = sys.stdin.readline().strip()
        print("请输入线程数量")
        self._thread_count = int(sys.stdin.readline().strip())
        self._path = path + str(self._c_ip).replace('.', '_').replace('/', '_') + ".txt"

    class Scan(threading.Thread):
        def __init__(self, queue, ip, spath):
            super().__init__()
            self._queue = queue
            self._max = self._queue.qsize()
            self._ip = ip
            self._path = spath

        def run(self):
            while not self._queue.empty():
                scan_url = str(self._queue.get())
                progress(int(100 - self._queue.qsize() / self._max * 100))
                try:
                    response = requests.get(scan_url, timeout=1)
                    if response.status_code != 404:
                        with open(self._path, 'a+') as f:
                            f.write(scan_url + '\n')
                except Exception as e:
                    pass


if __name__ == "__main__":
    c = C_scan()
    sys.stdout.write("\r")
    c.start()
