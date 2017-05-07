#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json
from random import randint, shuffle
import os
import codecs
import re
from sopel.tools.calculation import eval_equation as eval2
import dicebot

class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = ""
        self.robot_switch = True
        self.trigger_list = ['.roll','.help','.r','.class','.8ball','.zhan','.fate', '.calc', '.choice','.tips']
        self.class_files = self.list_classfiles("class" )
        fate_file = codecs.open("fate.list", encoding='utf-8')
        self.fate_list = []
        for i in fate_file.readlines():
            self.fate_list.append(i)

        fate_file.close()
        fate_file = codecs.open("zhan.list", encoding='utf-8')
        self.zhan_list = []
        for i in fate_file.readlines():
            self.zhan_list.append(i)

        fate_file.close()

        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def list_classfiles(self,class_path="class"):
        filelist = []
        for (dirpath,dirnames,filenames) in os.walk(class_path):
            for files in filenames:
                #print files
                filelist.append(str(files).decode('utf-8'))
            break
        return filelist

    def tuling_auto_reply(self, uid, msg):
        # deal with messages from here...
        #return u"知道啦"
        empty_reply = [u'好吧…',u'已阅',u'噢',u'收到',u'喔',u'嗯',u'这样啊']
        shuffle(empty_reply)
        result = ''
        msg_lst = msg.split()
        msg_len = len(msg_lst) 

        if any(cmd in msg.lower() for cmd in ['.help',]) :
            result = u'我是果壳翻译班协助机器人，我的主人是欧剃' #，果壳ID/新浪微博 Oicebot 其实是我。'
            result += u'\n目前我响应这几个命令：' + ' / '.join(self.trigger_list)
            result += u'\n更多功能还在开发中，敬请关注！'

        elif '.8ball' in msg.lower():
            pos = 0
            pos = msg_lst.index('.8ball')
            try:
                reason = msg_lst[pos + 1]
            except:
                result = u'请在 .8ball 后面输入你想问的内容。'
            else:
                string_tok = u'是的.是.没错.对的.可能是.应该是的吧.啊？这不知道.这真不知道.你问我，我问谁呢.千真万确.不是.不是吧.不对.不可能.是的可能性很低.你问我？不告诉你.从目前来看觉得是啊.啥？没听清.根据以往经验判断，不是.根据以往经验判断，是的.看起来不太像.这个……你想清楚再问.当然是啊.怎么可能'
                result_tok = string_tok.split(".")
                result = result_tok[randint(0, len(result_tok) - 1)]

        elif '.tips' in msg.lower():
            pos = 0
            pos = msg_lst.index('.tips')
            tips = codecs.open("Advts.r",encoding='utf-8')
            resultlist = []
            tipsfile = tips.readlines()
            for i in tipsfile:
                resultlist.append(i)

            tips.close()

            try:
                reason = msg_lst[pos + 1]
            except:
                number = randint(0,len(resultlist)-1)
                result = u'tips %d : %s' % (number , resultlist[number] )
                #result = u'tips %d %s' % (number , ' '.join(resultlist[number].split(' ')[1:]) )
                #result = ' '.join(resultlist[randint(0,len(resultlist)-1)].split(' ')[1:])
            else:
                if reason == '0':
                    result = u"我目前含有 %d 条 tips 呢。" % len(resultlist)
                elif reason.isdigit():
                    result = resultlist[int(reason) -1 ]
                elif reason.lower() == 'new':
                    result = u'最新tips为：' + resultlist[ -1 ]
                else:
                    number = randint(0,len(resultlist)-1)
                    result = u'tips %d : %s' % (number , resultlist[number] )


        elif '.roll' in msg.lower() :
            pos = 0
            diceface = 20

            try:
                pos = msg_lst.index('.roll')
            except ValueError:
                pos = msg_lst.index('.r')

            try:
                diceface = msg_lst[pos + 1]
            except:
                result = u'你丢了一个D20，结果为：%d' % randint(1,20)
            else:
                if diceface.isdigit():
                    diceface = int(diceface)
                    if diceface <= 0:
                        result = u'你拿出一颗祖传的克莱因瓶骰子，结果它直接消失在了空气中。'
                    elif diceface == 1:
                        result = u'你发现自己正盯着一个写着阿拉伯数字 1 的莫比乌斯环发呆。'
                    elif diceface == 2:
                        diceresult = randint(0,1)
                        result = u'你向空中抛出一枚硬币，结果是：%s' % ( u'正面(1)' if diceresult else u'反面(2)' )

                    elif diceface <= 1024:
                        diceresult = randint(1, diceface)
                        result = u'你丢了一个%d面骰，结果为：%d' % (diceface, diceresult )
                        if diceresult <= diceface / 20 or diceresult == 1:
                            if randint(1,10) < 6:
                                result += u"  …看来您的人品需要充值了呢。"
                    else:
                        result = u'你丢出一个圆滚滚的%d面骰，等到天荒地老这货都没能停下来。' % diceface

                elif diceface.startswith('-') and diceface[1:].isdigit():
                    result = u'你尝试丢%d个面的骰子的行为被未来局时空管理处制止了。' % int(diceface)
                else:
                    result = u'你丢了一个D20，结果为：%d' % randint(1,20)

        elif '.r' in msg.lower():
            pos = 0
            pos = msg_lst.index('.r')
            try:
                expr = msg_lst[pos+1:]
            except:
                result = u'用法： .r xDy+N describe'
            else:
                return dicebot.roll(expr)

        elif '.fate' in msg.lower():
            pos = 0
            pos = msg_lst.index('.fate')
            try:
                reason = msg_lst[pos + 1]
            except:
                result = u'请在 .fate 后面输入你心中的疑虑…'
            else:
                result = u'为 %s 进行了一次占卜，结果为\n' % reason
                result += self.fate_list[randint(0,43)]

        elif '.zhan' in msg.lower():
            pos = 0
            pos = msg_lst.index('.zhan')
            try:
                reason = msg_lst[pos + 1]
            except:
                result = u'请在 .zhan 后面输入你想占卜的内容。'
            else:
                result = u'为 %s 求了一卦，卦曰：\n' % reason
                result += '\n'.join(self.zhan_list[randint(0,63)].split(r'\n'))

        elif '.calc' in msg.lower():
            pat = '^[\d\+\-\*\/\(\)E\.]+$'
            pos = 0
            pos = msg_lst.index('.calc')
            try:
                expr = msg_lst[pos + 1]
            except:
                result = u'用法：在 .calc 后面跟一个算术表达式。'
            else:
                expr = expr.replace('pi','3.14159265359')
                expr = expr.replace(u'π','3.14159265359')
                expr = expr.replace('e','2.71828182846')
                if not re.search(pat,expr):
                    result = u'请在 .calc 后面跟一个算术表达式。'
                else:
                    try:
                        out = eval2(expr)
                    except ZeroDivisionError:
                        result = u'你的行为已经引起了姜峯楠的注意，小心咯。'
                    except:
                        result = u'表达式似乎有误，您再看看？有疑问请联系欧剃。'
                    else:
                        result = expr + '=' + str(out)

        elif '.choice'in msg.lower():
            pos = 0
            pos = msg_lst.index('.choice')
            try:
                expr = msg_lst[pos+1:]
            except:
                result = u'请在 .choice 后面跟若干选项，用空格隔开，我会用我聪明的头脑帮你挑一个。'
            else:
                return dicebot.choose(expr)

        elif '.class' in msg.lower():
            pos = msg_lst.index('.class')
            self.class_files = self.list_classfiles("class")
            currentfilelist = list(self.class_files)
            try:
                fileID = msg_lst[pos + 1]
            except IndexError:
                result = u"目前课程文件包含：\n"
                for files in self.class_files:
                    result += u"%02d : %s \n" % (currentfilelist.index(files), files) 

            else:
                if fileID.isdigit():
                    if int(fileID) < len(currentfilelist):
                        print fileID , currentfilelist[int(fileID)] 
                        #result = u"发送文件 [" + currentfilelist[int(fileID)] + " ]..." #+ uid
                        result = ""
                        self.send_file_msg_by_uid("./class/" + currentfilelist[int(fileID)], uid)
                elif "list" in fileID.lower():
                    result = u"目前课程文件包含：\n"
                    for files in self.class_files:
                        result += u"%02d :" % currentfilelist.index(files)
                        result += str(files) + '\n'


        else:
            result = empty_reply[0]

        print '    ROBOT:', result
        return result


    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开']
        start_cmd = [u'出来', u'启动', u'工作']
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])

    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 5 and msg['content']['type'] == 0:  # text message from contact
            self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])
        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0:  # group text message
            if 'detail' in msg['content']:
                message_text = msg['content']['desc'] 
                src_name = msg['content']['user']['name']
                #print '>' +  message_text
                #print msg['content']['user']
                if any(trigger_item in message_text.lower() for trigger_item in self.trigger_list):
                    reply = ''
                    #print 'name: ' + src_name
                    if msg['content']['type'] == 0:  # text message
                        #reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                        reply += self.tuling_auto_reply(msg['user']['id'], msg['content']['desc'])
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"

                    if reply:
                        reply = 'to ' + src_name + ': ' + reply
                        self.send_msg_by_uid(reply, msg['user']['id'])


def main():
    bot = TulingWXBot()
    bot.DEBUG = False #True
    bot.conf['qr'] = 'tty'

    bot.run()


if __name__ == '__main__':
    main()

