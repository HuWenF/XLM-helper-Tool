#! /usr/bin/env python

import http.client
import  json
import urllib.request
import time
import configparser
import  threading
import tkinter
from tkinter.constants import *



class OpwithSite(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls,*args,**kwargs)
        return cls._instance

    def MyInit(self,url,configFile,Type):
        self.url = url
        self.sessionJWT = ""
        self.config = configparser.ConfigParser()
        self.config.read(configFile)
        self.configFile = configFile
        self.CNY = 0
        self.LimitPrice = None
        self.coinNumber = None

        #买入卖出的URI
        self.exchangeOrder_buyURI = "/v1/exchangeOrder/buy/"+ Type +"/cny"
        self.exchangeOrder_sellURI = "/v1/exchangeOrder/sell/"+ Type +"/cny"
        #登陆的URI
        self.loginInURI = '/v1/public/login'
        #获取涨停跌停URI
        self.limitPriceURI = "/v1/exchangeOrder/tradingRule/" + Type +"/cny"

        self.avaliablePriceURI = "/v1/asset/availableNumber/cny"
        self.coinNumberURI = "/v1/asset/availableCoinNumber/"+Type

        self.CNYChange = 1
        self.CoinChange = 1
        self.LimitChange = 1
        self.UserStatus = 0

        self.Username=""
        self.Password=""


        self.default_sessionJWT = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJvMi10cmFkaW5nIiwiaWF0IjoxNTAyNDE2NDMzLCJzdWIiOiI4MDk1OTFBMjlGMUVCMUYxQUFCMTA3MDczMjZDRTI4MSIsImV4cCI6MTUwMjQ0NTIzMywiYXVkIjoiY2xpZW50In0.IHebj_dhf1tick5qVlmzgQFR0Onh46I4DVW19Ylk4gFvOBvZuBdbbaLC5JthdX-QAIKGAG0flKWxzs6lGMnIcA"
        self.default_header = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; '
                            'Intel Mac OS X 10_12_3) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           'Accept':'application/json, text/plain, */*',
           'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding':'gzip, deflate, br',
           'Referer':'https://new.o2btc.com/index',
           'Content-Type':'application/x-www-form-urlencoded;charset=utf-8',
           'Authorization':'cad38762-dfd8-4978-b037-60c49026a5d4_809591A29F1EB13511019223182335P01_6250239149327650816',
           'Content-Length':'55',
           'Origin':'https://new.o2btc.com',
           'Cookie':'',
           'sessionJWT':self.default_sessionJWT,
           'Connection':'close'
           }

        self.header = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; '
                            'Intel Mac OS X 10_12_3) AppleWebKit/537.36 '
                            '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           'Accept':'application/json, text/plain, */*',
           'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding':'gzip, deflate, br',
           #'Referer':'https://new.o2btc.com/trades/QUK/cny',
           'Content-Type':'application/x-www-form-urlencoded;charset=utf-8',
           'Authorization':'cad38762-dfd8-4978-b037-60c49026a5d4_809591A29F1EB13511019223182335P01_6250239149327650816',
           'Origin':'https://new.o2btc.com',
           #'Content-Length':'2',
           'Cookie':self.sessionJWT,
           'Connection':'close'
           }




    def UpdateUserInfo(self):
        #初始化获取用户数据
        self.CNYChange = 1
        self.CoinChange = 1
        self.LimitChange = 1
        self.GetavalableCNYwithSite()
        self.GetcoinNumber()
        self.GetLimitePrice()
        if self.UserStatus == 1:
            self.login(self.Username,self.Password)
            pass




    def InternelconnSite(self,urI,body,header,mothod):

        while 1:
            try:
                conn = http.client.HTTPSConnection(self.url,timeout=10)
                conn.connect()
                conn.request(mothod,urI,body,header)
                res = conn.getresponse()
                if res.status == 200:
                    return res
                else:
                    print("网页打开错误，错误代码[%d]",res.status)
                    print("准备重新获取")
            except Exception as a:
                print("异常网络连接错误[%s]" % a)
                conn.close()
                time.sleep(0.1)

    def logFromConfigFile(self):
        self.sessionJWT = str(self.config.get("cookie","sessionJWT")).strip()
        if self.sessionJWT.__len__() == 0:
            print("从文件中获取cookie失败,cookie长度为0")
            return False
        else:
            self.header.__setitem__("Cookie","sessionJWT=" + self.sessionJWT)
            if self.GetavalableCNYwithSite() == None:
                return False

            return True


    def login(self,username,password):
        #发送的数据
        sendUsr = urllib.request.quote(username)
        body = "account={account}&password={password}&code=q0w8".format(account=sendUsr,password=password)

        self.Username = username
        self.Password = password


        #logFromFile 先从文件中获取cookie

        res = self.InternelconnSite(self.loginInURI,body,self.default_header,"POST")
        Recdic = json.loads(str(res.read(),'utf8'))

        if self.ResultCode(Recdic):
            self.sessionJWT = Recdic.get("sessionJWT")
            self.header.__setitem__("Cookie","sessionJWT=" + self.sessionJWT)

            #写入到配置文件中去
            self.config.set("cookie","sessionJWT",self.sessionJWT)
            with open(self.configFile,"w+") as f:
                self.config.write(f)
            self.UserStatus = 0
            return  True
        else:
            return False

    def GetavalableCNYwithSite(self):
        if self.CNYChange == 1:
            res = self.InternelconnSite(self.avaliablePriceURI,"",self.header,"GET")
            Recdic = json.loads(str(res.read(),'utf8'))
            if self.ResultCode(Recdic):
                self.CNY = Recdic.get("availableNumber")
            else:
                self.UserStatus = 1
                self.CNY = None
            self.CNYChange = 0
        return  self.CNY

    def GetcoinNumber(self):
        if self.CoinChange == 1:
            res = self.InternelconnSite(self.coinNumberURI,"",self.header,"GET")
            Recdic = json.loads(str(res.read(),'utf8'))
            if self.ResultCode(Recdic):
                self.coinNumber = Recdic.get("availableNumber")
            self.CoinChange = 0
        return self.coinNumber


    def GetLimitePrice(self):
        if self.LimitChange == 1 :
            res = self.InternelconnSite(self.limitPriceURI,"",self.header,"GET")
            Recdic = json.loads(str(res.read(),'utf8'))
            if self.ResultCode(Recdic):
                dic = Recdic.get("data")
                self.LimitPrice = {"limitUp":dic.get("limitUp"),"limitDown":dic.get("limitDown")}
            self.LimitChange = 0
        return  self.LimitPrice


    def dealwithSite(self,Price,number,Order):
        #发送的数据
        urI = 0
        if Order == 1:
            #买进
            urI = self.exchangeOrder_buyURI
        elif Order == 2:
            #卖出
            urI = self.exchangeOrder_sellURI
        else:
            print("Order 命令出错[Order:%s]",Order)
            return
        body = "price={Pric}&number={Num}".format(Pric=round(Price,6),Num=number)
        print(body)

        res = self.InternelconnSite(urI,str(body),self.header,"POST")
        if res.status == 200:
            Recdic = json.loads(str(res.read(),'utf8'))
            print(Recdic)
            if self.ResultCode(Recdic):
                if Order == 1:
                    print("买入成功!!!单价[%s]-数量[%s]-总价:[%s]" % (Price,number,Price*number))
                elif Order == 2:
                    print("卖出成功!!!单价[%s]-数量[%s]-总价:[%s]" % (Price,number,Price*number))

                #开始更新余额，coin
                time.sleep(1)
                self.UpdateUserInfo()
                print("用户信息更新成功!!!--CNY:%s--coin:%s" %(self.CNY,self.coinNumber))

                self.CNY = self.CNY - Price*number
                return True
            else:
                print("买入失败!!")
                return False
        else:
            print("网络连接状态出错errorCode[%s]",res.status)
            return False



    def ResultCode(self,Recdic):
        if str(Recdic.get("errorCode")) == "0":
                return True
        elif str(Recdic.get("errorCode")) == "400":
            print("cookie错误")


            return False
        elif str(Recdic.get("errorCode")) == "408":

            print("密码错误")
            return False
        else:
            print("内部错误!!!")
            return False




class caculateDeal(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls,*args,**kwargs)
            cls.dealList = list()
            cls.dic = dict()
            cls.upflage = float(0)
            cls.lowflage = 0

            cls.baseUpPrice = 0
            cls.baseLowPrice = 0

            cls.BuyStatus = 0
            cls.UpPriceList = list()
            cls.flag = 0
        return cls._instance

    def PutDealData(self,Time,Price):
        self.dic.__setitem__("Time",Time)
        self.dic.__setitem__("Price",Price)
        self.dealList.append(self.dic.copy())
        #print(self.dealList.__len__())
        if self.dealList.__len__() > 100:
            for i in range(50):
                self.dealList.pop(i)

    def BuyInTime(self):
        self.BuyStatus = 1

    def GetLastPrice(self):
        return self.dealList[self.dealList.__len__() - 1].get("Price")


    def analysisData(self):
        result = {"Warning":0,
                  "CurTime":"",
                  "CurPrice":"",
                  }
        num = 6
        FlagNum = 10

        if self.dealList.__len__() < 3:
            return result
        else:

            Curdict = self.dealList[self.dealList.__len__() - 1]


            CurPrice = Curdict.get("Price")
            CurTime = Curdict.get("Time")


            sum = 0

            #获取最近10次数据来进行波动对比
            self.flag += 1
            if self.flag >= FlagNum:
                rateflag = 0
                dealSum = 0
                for i in range(FlagNum):
                    Price = self.dealList[self.dealList.__len__() - 1 - i].get("Price")
                    lastPrice = self.dealList[self.dealList.__len__() -2 - i].get("Price")
                    rate = abs(Price-lastPrice)/Price * 100
                    dealSum += Price
                    if rate < 0.3:
                        rateflag += 1
                    #print("rate:%f---i:%s---rateflag:%f" %(rate,i,rateflag))
                if rateflag >= FlagNum:
                    self.baseUpPrice = round(dealSum/FlagNum,6)
                    print("设置baseUpPrice为[%s]--Time:[%s]" % (self.baseUpPrice,self.dealList[self.dealList.__len__() - 1].get("Time")))
                    #重置flag
                    self.upflage = 0
                    self.UpPriceList.clear()
                    return result
                self.flag = 0

            #设置基础价格，用于对比
            if self.baseUpPrice == 0:
                for i in range(self.dealList.__len__()):
                    sum += self.dealList[i].get("Price")
                self.baseUpPrice = round(sum/self.dealList.__len__(),6)

            #当前价格如果大于基础价格，那么涨幅标记加一
            #print("CurPrice:%s,baseUpPrice:%s" %(CurPrice,self.baseUpPrice))
            if CurPrice > self.baseUpPrice:
                #print("当前输入test:",self.dealList[self.dealList.__len__() - 1])

                #计算权重
                takon = round((CurPrice-self.baseUpPrice)/self.baseUpPrice,6) * 100
                #print(takon)
                if takon >= 0.5:
                    self.upflage += 2
                    self.UpPriceList.append(Curdict)
                    self.baseUpPrice = CurPrice
                    print("takon+2-%s---%s" %(Curdict,takon))
                elif takon >= 0.1:
                    self.upflage += 1
                    self.UpPriceList.append(Curdict)
                    self.baseUpPrice = CurPrice
                    print("takon+1-%s---%s" %(Curdict,takon))
                # elif takon >= 0.1:
                #     self.upflage += 0.5
                #     self.UpPriceList.append(Curdict)
                #     self.baseUpPrice = CurPrice
                    #print("takon+0.5-%s---%s" %(Curdict,takon))
                #print(self.upflage)

                #如果涨幅标记大于5，那么报警
                #print(self.upflage)
                if self.upflage >= num :
                    print("历史记录为:")
                    self.UpPriceList.reverse()
                    LastNum = 0
                    rateSum = 0
                    for i in range(self.UpPriceList.__len__()):
                        tmp = self.UpPriceList.pop()
                        if LastNum == 0:
                            LastNum = tmp.get("Price")
                            print("Time:[%s]--Price[%f]" %(tmp.get("Time"),tmp.get("Price")))
                        else:

                            Uprate = round(float((tmp.get("Price") - LastNum)/LastNum),6) * 100
                            rateSum += Uprate
                            print("Time:[%s]--Price[%f]---涨幅比率:[%.2f%%]" %(tmp.get("Time"),tmp.get("Price"),Uprate))
                            LastNum = tmp.get("Price")
                    BuyPrice = CurPrice + ((rateSum/num)/100)*CurPrice


                    print("买入,当前价格为:[%s],当前时间为:[%s]" %(BuyPrice,CurTime))
                    result.__setitem__("Warning",1)
                    result.__setitem__("CurTime",CurTime)
                    result.__setitem__("CurPrice",BuyPrice)
                    result.__setitem__("rate",(rateSum/num)/100)
                    self.upflage = 0

        return result






            # elif CurPrice < self.baseLowPrice :
            #     self.lowflage += 1
            #     self.baseLowPrice = CurPrice
            #
            #
            #
            # elif self.lowflage >= 5 :
            #     print("卖出,当前价格为:[%s],当前时间为:[%s]" % (beforePrice,beforeTime))
            #     self.lowflage = 0



# a = caculateDeal()
#
#
#
# with open("test3.txt","r") as f:
#     for i in range(9999):
#         mystr = f.readline()
#         test = mystr.partition("-")
#
#         a.PutDealData(test[0],round(float(test[2]),6))
#         a.analysisData()
#
#         #time.sleep(0.02)

class WindowThread(threading.Thread):
    # _instance = None
    # def __new__(cls, *args, **kwargs):
    #     if  cls._instance is None:
    #         cls._instance = object.__new__(cls,*args,**kwargs)
    #     return cls._instance

    def Mystart(self,Title,Message,rate):
        self.m_title = Title
        self.m_message = Message
        self.rate = rate
        self.start()

    def run(self):
        #获取参数进行转换
        #while True:
        #    time.sleep(1)
        #    print("我还活着 我是线程")

        #win32api.MessageBox(0,Message.format(number=str(TotleNumber)),Title,
        #                       win32con.MB_OK|win32con.MB_SYSTEMMODAL|win32con.MB_ICONWARNING)
        MyMessageBox(self.m_title,self.m_message,self.rate)

def MyMessageBox(Title,Message,rate):

    tk = tkinter.Tk()
    tk.wm_attributes('-topmost',1)
    #获取与网站交互单实例
    tmp = OpwithSite()

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
    #b1 = tkinter.Button(tk,text="退出",anchor='center',command=tk.destroy,background='#FF4500').pack(side=RIGHT)
    #b2 = tkinter.Button(tk,text="打开网站",anchor='center',command=OpenUrl,background='#00FFFF').pack(side=LEFT)
    tkinter.Button(tk,text="买入",anchor='center',command=lambda : BuyOrSell(1,rate)  ,background='#7FFF00').pack(side=LEFT)
    tkinter.Button(tk,text="更新用户数据",anchor='center',command=UpdateUserInfo  ,background='#7FFFF0').pack(side=TOP)
    tkinter.Button(tk,text="卖出",anchor='center',command=lambda : BuyOrSell(2,rate),background='#FF0000').pack(side=RIGHT)
    tk.minsize(300,200)
    tk.mainloop()

def UpdateUserInfo():
    a = OpwithSite()
    a.UpdateUserInfo()
    coin = a.GetcoinNumber()
    CNY = a.GetavalableCNYwithSite()
    Limit = a.GetLimitePrice()
    print(Limit)
    print("用户信息更新成功!!!--CNY:%s--coin:%s" %(CNY,coin))
    pass




def BuyOrSell(Order,rate):
    #获取实例
    Deal = OpwithSite()

    #Order 1为买入,2为卖出
    #计算买入或者卖出的数量以及单价

    Num = CalcPriceandNumber(Order,rate)
    #Num = {"Price":1.5,"Number":100}
    if Num is None:
        return False
    #进行买入或者卖出操作
    Deal.dealwithSite(Num.get("Price"),Num.get("Number"),Order)


def CalcPriceandNumber(flag,rate):

    a = OpwithSite()
    b = caculateDeal()
    CNY = a.GetavalableCNYwithSite()
    Price = b.GetLastPrice()
    limit = a.GetLimitePrice()
    print(limit)

    if rate == 0:
        rate = 0.005

    if flag == 1:#买入
        #获取最新单价
        Price = Price + Price*rate
        if Price > limit.get("limitUp"):
            print("已经到达购买价格上线，购买失败!!!")
            return None
        Num = round(CNY/Price)

    elif flag == 2:  #卖出
        Price = Price - Price*rate
        if Price < limit.get("limitDown"):
            print("已经到达购买价格下线，购买失败!!!")
            return None
        #获取所拥有的积分
        Num = a.GetcoinNumber()

    if Num > 3000:
        Num = 3000
    Num - 1
    Numdic = {"Price":Price,"Number":Num}

    return Numdic



#定义弹出框






































