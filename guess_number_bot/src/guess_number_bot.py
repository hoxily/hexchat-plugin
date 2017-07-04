'''
hexchat python 插件参考文档 https://hexchat.readthedocs.io/en/latest/script_python.html
'''

__module_name__ = "guess_number_bot"
__module_version__ = "1.0"
__module_description__ = "自动猜数字机器人，TideBot猜数字游戏爱好者！"

import hexchat
import re
import random

PREFERENCE_KEY_TOGGLE = 'guess_number_bot.toggle'
MAX = 10000
g_possibles = []
g_last_guess = 0

'''
判断一个4位数是否是一个从0~9这十个数字中选出4个数字的排列
'''
def is_permutation(num):
	if num >= MAX or num < 0:
		return False
	d = {}
	for i in range(0, 10):
		d[i] = 0
	for i in range(0, 4):
		d[num % 10] = d[num % 10] + 1
		num = num // 10
	for i in range(0, 10):
		if d[i] > 1:
			return False
	return True
	
'''
初始化可选答案列表
'''
def initialize_possibles():
	global g_possibles
	g_possibles.clear()
	for i in range(1000, MAX):
		if is_permutation(i):
			g_possibles.append(i)
	g_possibles.reverse()
'''
以target作为正确答案，计算猜测guess时应给出的A数量（即数字猜中，并且那个数字在正确的位置。这样的数字的个数。
'''
def how_many_a(target, guess):
	d1 = {}
	d2 = {}
	a = 0
	for i in range(0, 4):
		d1[i] = target % 10;
		d2[i] = guess % 10;
		target = target // 10
		guess = guess // 10
		if d1[i] == d2[i]:
			a = a + 1
	return a
'''
以target作为正确答案，计算猜测guess时应给出的B数量（即数字猜中，并且那个数字并不在正确的位置。这样的数字的个数。）
'''
def how_many_b(target, guess):
	a = how_many_a(target, guess);
	d1 = {}
	d2 = {}
	for i in range(0, 10):
		d1[i] = 0
		d2[i] = 0
	for i in range(0, 4):
		d1[target % 10] = d1[target % 10] + 1;
		d2[guess % 10] = d2[guess % 10] + 1;
		target = target // 10
		guess = guess // 10
	b = 0
	for i in range(0, 10):
		if (d1[i] == d2[i]) and (d1[i] == 1):
			b = b + 1
	return (b - a)
'''
以target作为正确答案，guess作为猜测的数，判断是否满足给定的A，B
'''
def is_possible(target, guess, a, b):
	a_ = how_many_a(target, guess)
	b_ = how_many_b(target, guess)
	return (a == a_) and (b == b_)
'''
根据反馈结果，筛选可选答案列表
'''
def filter_possibles(guess, a, b):
	global g_possibles
	filtered = []
	for num in g_possibles:
		if is_possible(num, guess, a, b):
			filtered.append(num)
	g_possibles = filtered
'''
处理频道消息。主要是三种消息：
1. 游戏开始；
2. 某次猜测结果；
3. 游戏结束；
'''
def process_message(channel, sender, msg):
	global g_possibles
	global g_last_guess
	# 识别TideBot的消息
	# 某次游戏开始
	m1 = re.match("^猜数字 游戏 #(\d+) 开始.+$", msg)
	if m1 != None:
		# 初始化
		initialize_possibles()
		if len(g_possibles) > 0:
			num = random.choice(g_possibles)
			print(sender + '\t' + msg)
			hexchat.command("MSG " + channel + " " + sender + ": " + str(num))
			g_last_guess = num
			return True
	# 某次游戏结束
	m2 = re.match("^猜数字 游戏 #(\d+) 结束.+$", msg)
	if m2 != None:
		# 清理工作
		g_last_guess = 0
		g_possibles.clear()
		print(sender + '\t' + msg)
		hexchat.command("MSG " + channel + " 猜数字") 
		return True
	# 某次猜测的结果
	my_nick = hexchat.get_info('nick')
	m3 = re.match("^" + my_nick + ": #\d+: (\d)A(\d)B.+$", msg)
	if m3 != None:
		# 处理本次筛选结果
		g = m3.groups();
		if len(g) == 2:
			a = int(g[0])
			b = int(g[1])
			filter_possibles(g_last_guess, a, b)
			if len(g_possibles) > 0:
				num = random.choice(g_possibles)
				print(sender + '\t' + msg)
				hexchat.command("MSG " + channel + " " + sender + ": " + str(num))
				g_last_guess = num
				return True
	return False

'''
频道消息回调。
'''
def channel_message_callback(word, word_eol, userdata):
	toggle = hexchat.get_pluginpref(PREFERENCE_KEY_TOGGLE)
	if toggle != 'on':
		return hexchat.EAT_NONE
	# 如果对word里面有什么内容不清楚，可以把下方的注释去掉然后试运行一下。
	#for i in range(len(word)):
	#	print("prefix: " + word[i])
	sender = hexchat.strip(word[0]) # 剔除掉颜色、格式
	msg = hexchat.strip(word[1]) 
	channel = hexchat.get_info('channel')
	has_reply = process_message(channel, sender, msg)
	if has_reply:
		return hexchat.EAT_HEXCHAT
	else:
		return hexchat.EAT_NONE
'''
guess_number_bot插件开关命令
'''
def guess_number_bot_callback(word, word_eol, userdata):
	toggle = hexchat.get_pluginpref(PREFERENCE_KEY_TOGGLE)
	if toggle == 'on':
		hexchat.set_pluginpref(PREFERENCE_KEY_TOGGLE, 'off')
		print('已关闭guess_number_bot插件功能。')
	else:
		hexchat.set_pluginpref(PREFERENCE_KEY_TOGGLE, 'on')
		print('已启用guess_number_bot插件功能。')
	# /guess_number_bot 命令只针对本插件有效
	return hexchat.EAT_ALL
# 注册 Channel Message 这种类型的消息事件
hexchat.hook_print("Channel Message", channel_message_callback)
# 注册 Channel Msg Hilight 这种类型的消息事件
hexchat.hook_print("Channel Msg Hilight", channel_message_callback)
# 注册 guess_number_bot 命令
hexchat.hook_command('guess_number_bot', guess_number_bot_callback, help='启用或者关闭guess_number_bot插件功能')
# 报告 guess_number_bot 插件的当前启用状态
toggle = hexchat.get_pluginpref(PREFERENCE_KEY_TOGGLE)
if toggle == 'on':
	print('guess_number_bot插件功能处于开启状态。你可以使用 /guess_number_bot 命令来关闭它。')
else:
	print('guess_number_bot插件功能处于关闭状态。你可以使用 /guess_number_bot 命令来打开它。')