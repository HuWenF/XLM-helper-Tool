#! /usr/bin/env python
#coding=utf-8

import http.client
import time
import winsound
import threading
import tkinter
from tkinter.constants import *
import webbrowser
import inspect
import ctypes
import os
import configparser
import queue
import datetime

from conf import OpretionWithSite

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE= -11
STD_ERROR_HANDLE = -12

FOREGROUND_BLACK = 0x0
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED = 0x04 # text color contains red.
FOREGROUND_INTENSITY = 0x08 # text color is intensified.

BACKGROUND_BLUE = 0x10 # background color contains blue.
BACKGROUND_GREEN= 0x20 # background color contains green.
BACKGROUND_RED = 0x40 # background color contains red.
BACKGROUND_INTENSITY = 0x80 # background color is intensified.

class Color:
    ''''' See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    for information on Windows APIs.'''
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_cmd_color(self, color, handle=std_out_handle):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return bool

    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

    def print_red_text(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print (print_text,end='  ',flush=True)
        self.reset_color()


    def print_green_text(self, print_text):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print (print_text,end='  ',flush=True)
        self.reset_color()

    def print_blue_text(self, print_text):
        self.set_cmd_color(FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        print (print_text,end='',flush=True)
        self.reset_color()

    def print_red_text_with_blue_bg(self, print_text):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY| BACKGROUND_BLUE | BACKGROUND_INTENSITY)
        print (print_text,end='',flush=True)
        self.reset_color()

    def print_red_text_rate(self, *args):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print (*args,end='  ',flush=True)
        self.reset_color()

    def print_green_text_rate(self, *args):
        self.set_cmd_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print (*args,end='  ',flush=True)
        self.reset_color()




'''
#被遗弃的方法，无法让窗口弹出
def Myshow():
    hwnd = win32gui.FindWindow(None,'C:\WINDOWS\py.exe')
    print(hwnd)
    time.sleep(5)
    #win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0,
    #                      win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE| win32con.SWP_NOOWNERZORDER|win32con.SWP_SHOWWINDOW)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0,
                          win32con.SWP_SHOWWINDOW)

    print("Im in Myshow()")
    time.sleep(5)

def Myhide():
    hwnd = win32gui.FindWindow(None,'C:\WINDOWS\py.exe')
    win32gui.SetWindowPos(hwnd, win32con.HWND_BOTTOM, 0,0,0,0,
                          win32con.SWP_NOMOVE|win32con.SWP_NOSIZE|win32con.SWP_NOACTIVATE|win32con.SWP_NOOWNERZORDER)
    print("Im in Myhide()")
'''


class WriteFile(object):

    def __init__(self,FileName):
        self.que = queue.Queue(maxsize=100)
        # for i in range(100):
        #     self.que.put(i)
        self.ComsumerThread = threading.Thread(target=self.ComsumterT,args=(self.que,FileName,))
        self.GloubleTime = 0

    def StartThread(self):
        self.ComsumerThread.start()


    def WriteToFile(self,string):

        self.que.put(string)
        #self.GloubleTime += 1

        # for i in range(a):
        #     print(self.que.get_nowait())
        #     self.que.task_done()
        # print(self.que.empty())
        #self.que.join()


        #if self.GloubleTime >= 5:
            #self.que.join()
         #   self.GloubleTime = 0


    def ComsumterT(self,queT,FileName):
        while 1:
            if queT.empty():
                time.sleep(5)
                continue
            size = int(queT._qsize())
            if os.path.exists(FileName):
                with open(FileName,"a") as f:
                    for i in range(size):

                        f.write(str(queT.get_nowait()) + "\n")
                        #queT.task_done()
            else:
                with open(FileName,"x") as f:
                    for i in range(size):
                        f.write(str(queT.get_nowait()) + "\n")
                        #queT.task_done()

            continue


class MyThread(threading.Thread):

    def Mystart(self,Title,Message):
        self.m_title = Title
        self.m_message = Message
        self.start()

    def run(self):
        #获取参数进行转换
        #while True:
        #    time.sleep(1)
        #    print("我还活着 我是线程")

        #win32api.MessageBox(0,Message.format(number=str(TotleNumber)),Title,
        #                       win32con.MB_OK|win32con.MB_SYSTEMMODAL|win32con.MB_ICONWARNING)
        MyMessageBox(self.m_title,self.m_message)



    def Stop_thread(self,Mytid,exctype):
        tid = ctypes.c_long(Mytid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


#打开URl
def OpenUrl():
    webbrowser.open(Url,new=2)



#定义弹出框
def MyMessageBox(Title,Message):


    tk = tkinter.Tk()
    tk.wm_attributes('-topmost',1)



    tk.title(Title)
    #居中窗口大小
    screen_width = tk.winfo_screenwidth()
    screen_height = tk.winfo_screenheight() - 100


    tk.geometry('%dx%d+%d+%d' % (tk.winfo_width() + 90,
                                   tk.winfo_height() + 90,
                                   (screen_width - tk.winfo_width())/2,
                                   (screen_height - tk.winfo_height())/2) )
    #tk.minsize(500,500)
    #time.sleep(15)
    curtime = time.strftime('[%H:%M:%S]',time.localtime())
    frame = tkinter.Frame(tk, relief=RIDGE)
    frame.pack(fill=BOTH,expand=1)
    label = tkinter.Label(frame, text=curtime + Message,bg='#EE82EE',font='6')
    label.pack(fill=X, expand=1)

    #设置按钮
    tkinter.Button(tk,text="退出",anchor='center',command=tk.destroy,background='#FF4500').pack(side=RIGHT)
    tkinter.Button(tk,text="打开网站",anchor='center',command=OpenUrl,background='#00FFFF').pack(side=LEFT)
    tk.minsize(300,200)
    tk.mainloop()



def ConnUrl(url):
    global connPath
    headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; '
                                'Intel Mac OS X 10_12_3) AppleWebKit/537.36 '
                                '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
               }
    while 1 :
        i = 10
        conn = http.client.HTTPSConnection(url,timeout=20)
        conn.connect()
        while 1:
             try:
                i -= 1
                conn.request("GET",connPath,headers=headers)

                #if conn.getresponse().status == 200:
                yield  conn.getresponse()
                if i <= 0:
                    conn.close()
                    break
                time.sleep(0.2)
             except Exception as a:
                    print("网络连接关闭错误[%s]" % a)
                    time.sleep(0.1)
                    break



def PrintLine(Time,Total,ConpareLast,ConpareStart,rate):
    Mytotal = str(Total).strip()
    MyConpareLast = str(ConpareLast).strip()
    MyConpareStart = str(ConpareStart).strip()

    PrintColor = Color()
    #输出时间
    #print(Logger.OKBLUE,Time,end=' ',flush=True)
    PrintColor.print_red_text_with_blue_bg(Time)
    if Mytotal.startswith('-'):
        PrintColor.print_red_text("当前价格:" + Mytotal)
    else:
        PrintColor.print_green_text("当前价格:" + Mytotal)

    if MyConpareLast.startswith('-'):
        PrintColor.print_red_text("波动价格:" + MyConpareLast)
    else:
        PrintColor.print_green_text("波动价格:" + MyConpareLast)

    if MyConpareStart.startswith('-'):
        PrintColor.print_red_text("初始波动价:" + MyConpareStart )
        PrintColor.print_red_text_rate("%.2f%%" % (rate*100) )
    else:
        PrintColor.print_green_text("初始波动价:" + MyConpareStart)
        PrintColor.print_green_text_rate("%.2f%%" %  (rate*100))
    print('\n')

def GetNumberForFile(FileName,flage):
    if os.path.isfile(FileName) == FALSE:
        with open(FileName,mode='x') as f:
            return 0
    else:
        with open(FileName,mode='r+') as f:
            config = configparser.ConfigParser()
            config.read(FileName)

            global PriceStart
            global WarningUpnumber
            global WarningLownumber
            global ChangeNumber
            global soonPriceNumber
            global WarningRate
            global ChangeRate
            global NumList

            global Username
            global Password
            global sessionJWT

            li = list()

            PriceStart = float(config.get("config","PriceStart"))
            MyWarningUpnumber = float(config.get("config","WarningUpnumber"))
            MyWarningLownumber = float(config.get("config","WarningLownumber"))
            ChangeNumber = float(config.get("config","ChangeNumber"))
            soonPriceNumber = float(config.get("config","soonPriceWarningNumber"))
            ChangeRate = float(config.get("config","ChangeRate(%)"))/100
            MyWarningRate = float(config.get("config","WarningRate(%)"))/100

            Username = str(config.get("UserInfo","Username")).strip()
            Password = str(config.get("UserInfo","Password")).strip()


            li = [PriceStart,MyWarningUpnumber,MyWarningLownumber,ChangeNumber,soonPriceNumber,ChangeRate,MyWarningRate]

            if flage == None:
                WarningRate = MyWarningRate
                WarningUpnumber = MyWarningUpnumber
                WarningLownumber = MyWarningLownumber

                NumList = li
            elif flage == "1":
                if NumList != li:
                    NumList = li
                    WarningRate = MyWarningRate
                    WarningUpnumber = MyWarningUpnumber
                    WarningLownumber = MyWarningLownumber

def PreWriteToFile(filename,CurPrice):
    getDate = time.strftime('%Y-%m-%d',time.localtime())
    getTime = time.strftime('%H:%M:%S',time.localtime())
    dic = dict(Date=getDate,Time=getTime,Price=CurPrice)
    with open(filename,mode='a') as f:
        res = '{Date}---{Time}---{Price}'.format(Date=dic.get('Date'),Time=dic.get('Time'),Price=dic.get('Price'))
        f.writelines(str(res)+'\n')

def FuncInit():
    global wf
    global OperWithSite
    Myprint = Color()

    #获取时间
    now = datetime.datetime.now()
    LogFileName = now.strftime('%Y-%m-%d') +"-" + "LogFile.log"
    #获取初始波动阈值以及波动参数
    while 1:
        try:
            GetNumberForFile(FileName,None)
            break
        except BaseException as e:
            print("配置文件读取错误：[%s]",e)
            time.sleep(1)

    #初始化生产者队列
    wf = WriteFile(LogFileName)
    wf.StartThread()
    while 1:

        #初始化网站交互
        OperWithSite = OpretionWithSite.OpwithSite()
        OperWithSite.MyInit('api.o2btc.com',FileName,Type)
        #开始登陆
        print("准备登陆远程网站!!!" + '\n')
        if OperWithSite.logFromConfigFile():
            Myprint.print_green_text("根据cookie登陆成功!!" + '\n')
            break
        elif OperWithSite.login(Username,Password):
            Myprint.print_green_text("登陆成功!!" + '\n')
            break
        else:
            Myprint.print_red_text("登陆失败!!" + '\n')
            time.sleep(1)
            continue
    #更新用户数据
    OperWithSite.UpdateUserInfo()





# def CalcPriceandNumber(flag):
#
#     a = OpretionWithSite.OpwithSite()
#     b = OpretionWithSite.caculateDeal()
#     CNY = a.GetavalableCNYwithSite()
#     Price = b.GetLastPrice()
#     limit = a.GetLimitePrice()
#     print(limit)
#     if flag == 1:#买入
#         Price = Price + Price*0.005
#         if Price > limit.get("limitUp"):
#             print("已经到达购买价格上线，购买失败!!!")
#             return None
#     elif flag == 2:  #卖出
#         Price = Price - Price*0.005
#         if Price < limit.get("limitDown"):
#             print("已经到达购买价格下线，购买失败!!!")
#             return None
#     Num = round(CNY/Price)
#     if Num > 3000:
#         Num = 3000
#     Num - 1
#     Numdic = {"Price":Price,"Number":Num}
#
#     return Numdic






TryNumber = 10
TryNum = TryNumber
PriceLast = 0.000000
TotleNumber = 0.000000


Type = "XLM"


Title = Type + '胡氏交易'
Message = '胡氏交易软件'

Title2 = Type + '金额波动告警!!!'
Message2 = '初始波动{number},比率{numberRate}%'


Title3 = Type + '智能买卖告警!!!'
Message3 = '推荐买进价格{Price}'




LogString = '当前时间:{Curtime} 当前价格:{curPrice} 波动价格:{ChangeNum} 初始波动:{Lastnumber},比率{numberTate}%'
ChangeMessage = "波动金额超过{number}元"
SourUrl = 'api.o2btc.com'
Url = 'new.o2btc.com/trades/'+ Type + '/cny'
connPath = '/v1/public/tradingForOne/'+ Type +'/cny'
CountNum = 50
Count = CountNum
FileName = Type + '.conf'
GetTimeLast = '00:00:00'

LogString = '当前时间:{Curtime} 当前价格:{curPrice} 波动价格:{ChangeNum} 初始波动:{Lastnumber},比率{numberTate}%'


PriceStart = 0
WarningUpnumber = 0
WarningLownumber = 0
ChangeNumber  = 0
WarningRate = 0
ChangeRate = 0


NumList = list()

soonPriceNumber = 0
#PreWriteToFile(FileName,50)
GloubleTime = 0
wf = ""
OperWithSite =""


Username = ""
Password = ""


if __name__ == "__main__":


    #进行一些列初始化
    FuncInit()

    #链接网站生产者
    cc = ConnUrl(SourUrl)

    #计算交易实例
    calc = OpretionWithSite.caculateDeal()
    #calc.Myinit()

    #创建一个新线程对象
    Window = OpretionWithSite.WindowThread()


    #标记
    i = 5
    while True:
        try:
            res = cc.__next__()
            i -= 1
            if i == 0:
                while 1:
                    try:
                        GetNumberForFile(FileName,"1")
                        i = 5
                        break
                    except BaseException as e:
                        print("配置文件读取错误：[%s]",e)
                        time.sleep(1)

            #进行第一轮剔除
            #print(res.status)
            mydic = eval(res.read())  #使用eval使字符串变成字典
            mylist = list(mydic.get('trades'))

            #print(mylist[0])
            #进行第二轮剔除
            mydic2 = mylist[0]
            GetTime = mydic2.get('showDate') + '   '
            GetPrice =  str(mydic2.get('price'))
            #如果时间和上次一样就跳从新循环拿数据
            if GetTimeLast == GetTime:
                continue
            else:
                GetTimeLast = GetTime

            #分析完成后开始买入卖出流程

            if Window.isAlive() == False:
                Window.Mystart(Title=Title,Message=Message,rate=0)

            #time.sleep(0.02)
            #测试数据
            # with open("test3.txt","r") as f:
            #     for i in range(4):
            #         mystr = f.readline()
            #         test = mystr.partition("-")
            #         calc.PutDealData(test[0],round(float(test[2]),6))

            #开始进行数据分析
            #print(GetTime,GetPrice)
            calc.PutDealData(GetTime,float(GetPrice))
            result = calc.analysisData()
            if result.get("Warning") == 1:
                winsound.PlaySound('alert', winsound.SND_ASYNC)
                WarnTip = OpretionWithSite.WindowThread()
                WarnTip.Mystart(Title3,Message3.format(Price=result.get("CurPrice")),result.get("rate"))


            GetPriceFlot = float(GetPrice)
            if PriceLast == float(0):
                PriceLast = GetPriceFlot
                number = 0.000000
            else:
                number = GetPriceFlot - PriceLast
                PriceLast = GetPriceFlot

            TotleNumber = round(GetPriceFlot - PriceStart,6)
            TotleNumberrate = round(abs(TotleNumber/PriceStart),4)

            #创建线程弹出窗口警告
            #t = threading.Thread(target=MyMessageBox,args=(Title,Message.format(number=TotleNumber),))

            if TotleNumber >= WarningUpnumber or TotleNumber <= WarningLownumber or TotleNumberrate > WarningRate:
                print('准备警告')
                #判断线程是否存活
                # if t.is_alive() == True:
                #     #t.Stop_thread(t.ident,SystemExit)
                #     t.join()
                # elif t.is_alive() == False:
                time.sleep(0.2)
                #创建一个新线程对象
                t = MyThread()
                #开新线程发出弹窗
                t.Mystart(Title=Title2,Message=Message2.format(number=TotleNumber,numberRate=TotleNumberrate*100))
                #报警提示音
                winsound.PlaySound('alert', winsound.SND_ASYNC)
                #time.sleep(3)

                #调整阈值
                WarningRate += ChangeRate
                if TotleNumber > 0.000000:
                    WarningUpnumber += ChangeNumber
                else:
                    WarningLownumber -= ChangeNumber


            if   number.__abs__() >= soonPriceNumber:
                # if f.is_alive() == True:
                #     f.join()
                # elif f.is_alive() == False:
                time.sleep(0.2)
                f = MyThread()
                f.Mystart(Title=Title,Message=ChangeMessage.format(number=number))
                #报警提示音
                winsound.PlaySound('alert', winsound.SND_ASYNC)

            PrintLine(GetTime,GetPrice,round(number,6),round(TotleNumber,6),TotleNumberrate)
            #写入到日志文件中去
            wf.WriteToFile(LogString.format(Curtime=GetTime,
                                            curPrice=GetPrice.strip(),
                                            ChangeNum=round(number,6),
                                            Lastnumber=round(TotleNumber,6),
                                            numberTate=TotleNumberrate))
        except Exception as e:
            with open("err.log",mode='a') as f:
                #f.writelines(e)
                print(e)
                time.sleep(2)

