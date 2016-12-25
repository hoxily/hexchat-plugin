'''
hexchat python 插件参考文档 https://hexchat.readthedocs.io/en/latest/script_python.html
'''

__module_name__ = "KTV_BOT"
__module_version__ = "1.0"
__module_description__ = "IRC自动点歌插件，用于 hexchat。"

import hexchat
import re
import json

'''
接口文件。播放器会定时检测该文件内容，判断是否点播了新歌曲。
'''
notify_file = "C:\\Users\\hoxil\\Desktop\\ktv_bot\\newest.js"

'''
通知播放器，播放指定名字的歌曲
'''
def notify(name):
	global notify_file
	with open(notify_file, "wt", encoding="utf-8") as f:
		# 构造JSONP数据
		o = { "name": name }
		# 构造JSONP调用。此处写死了回调方法名字。
		t = "window.hox_jsonp(" + json.dumps(o) + ");"
		f.write(t)

'''
处理频道消息，提取出歌名。
'''
def process_message(msg):
	# 此处的正则需求：
	# 1.识别teleboto转发的消息；
	# 2.支持繁体命令；
	m1 = re.match("^\[[^\]]*\]\s?(点|點)歌 (.+)$", msg)
	if m1 != None:
		g = m1.groups()
		if len(g) == 2:
			name = g[1]
			return name
	# 非转发型的消息
	m2 = re.match("^(点|點)歌 (.+)$", msg)
	if m2 != None:
		g = m2.groups()
		if len(g) == 2:
			name = g[1]
			return name
	return None

'''
频道消息回调。
'''
def channel_message_callback(word, word_eol, userdata):
	# 如果对word里面有什么内容不清楚，可以把下方的注释去掉然后试运行一下。
	#for i in range(len(word)):
	#	print("prefix: " + word[i])
	msg = word[1]
	msg = hexchat.strip(msg) # 剔除掉颜色、格式
	name = process_message(msg)
	if name != None:
		channel = hexchat.get_info("channel")
		hexchat.command("MSG " + channel + " 收到点歌请求：" + name + "，请到 http://dwz.cn/4TsW0M 收听。")
		notify(name)
	return hexchat.EAT_NONE

# 注册 Channel Message 这种类型的消息事件
hexchat.hook_print("Channel Message", channel_message_callback)