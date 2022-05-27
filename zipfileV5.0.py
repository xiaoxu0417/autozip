# encoding = utf-8
import os
import sys
import time
from threading import Thread
import threading
from queue import Queue

isVIP = False
# 视频后缀list
video_suffix = ["mkv", "mp4", "m2ts", "rmvb", ".flv"]
zip_cmd_path = 'C:\\\"Program Files\"\\7-Zip\\7z.exe'
zip_cmd = ""
#zip_size_cmd = "-v4092m"
zip_size = 4092
big_zip_size = 8128
zip_size_cmd = "-v{}m".format(zip_size)
big_zip_size_cmd = "-v{}m".format(big_zip_size)

#命令行百度云盘指令
#xiaomi
#bypy_cmd_path = r"C:\Users\lxl\AppData\Local\Programs\Python\Python36-32\Scripts\bypy.exe"
bypy_cmd_path = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python38\Scripts\bypy.exe"


#注意：两个线程间通信使用,用来判断是否压缩完成、是否上传完成的文件名,均为视频文件,即:"MP4"等
def zipfile(file):

	ret_zip = []
	fullname = os.getcwd() + "\\" + file
	
	#小于20GB生成一个文件
	if (isVIP and os.path.getsize(fullname) / 1024 / 1024 /1024 < 4* 5) or os.path.getsize(fullname) / 1024 / 1024 < 1024 * 4:
		zip_cmd = "a {0} {1} {2}".format("\"" + fullname + ".7z" + "\"", "\"" + fullname + "\"", "-p4k0417")
		ret_zip.append(fullname + ".7z")
	elif isVIP and os.path.getsize(fullname)/1024/1024/1024 > 4*5:
		zip_cmd = "a {0} {1} {2} {3}".format("\"" + fullname + ".7z" + "\"", "\"" + fullname + "\"", big_zip_size_cmd,"-p4k0417")
		zipNum = int(os.path.getsize(fullname) / 1024 / 1024 / big_zip_size) + 1
		for i in range(1,zipNum+1):
			ret_zip.append(fullname + ".7z" + ".{:03d}".format(i))
	else:
		zip_cmd = "a {0} {1} {2} {3}".format("\"" + fullname + ".7z" + "\"", "\"" + fullname + "\"", zip_size_cmd,"-p4k0417")
		zipNum = int(os.path.getsize(fullname) / 1024 / 1024 / zip_size) + 1
		for i in range(1,zipNum+1):
			ret_zip.append(fullname + ".7z" + ".{:03d}".format(i))


	cmd = zip_cmd_path + " " + zip_cmd
	if os.system(cmd) == 0:
		print("zip ok")
	return ret_zip


def isVideo(file):
	for suf in video_suffix:
		if file.endswith(suf):
		#if file.endswith(".txt"):
			return True
	return False

class updateVideofiles(Thread):
	def __init__(self,update_queue):
		super().__init__()
		self.queue = update_queue
		#视频文件list
		self.org_file_list = []
		#查找时间间隔
		self.interval = 60 * 10
		self.last_update_time = 0
		self.times = 0
	def renamefile(file):
		#替换空格
		new = file.replace(" ","_")
		os.rename(file,new)
		return new

	def run(self):
		while True:
			#if time.time() - self.last_update_time > 6 *self.interval:
				#break
			self.times = self.times +1
			print("1开始第{0}次文件".format(self.times) + "at:" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
			files = os.listdir(os.getcwd())
			for file in files:
				if isVideo(file):
					if file in self.org_file_list:
						continue
					if file == "Breaking.Bad.S01E07.2160p.WEBRip.DTS-HD.MA5.1.x264-TrollUHD.mkv":
						continue
					#处理文件名中的空格并重命名
					print(file)
					#file = self.renamefile(file)
					self.org_file_list.append(file)
					self.queue.put(file)
					print("1找到文件个数:",len(self.org_file_list))
					self.last_update_time = time.time()

			#查找间隔十分钟
			time.sleep(self.interval)


class ziptask(Thread):
	def __init__(self,update_queue,upload_queue):
		super().__init__()
		self.update_queue = update_queue
		self.upload_queue = upload_queue
		self.zip_file = []
		self.searchtime = 0

	def run(self):
		while True:
			msg = self.update_queue.get()
			if msg not in self.zip_file:
				print("2开始压缩:"+msg)
				#time.sleep(10)
				zip_ret = zipfile(msg)
				print("2结束压缩:"+msg)
				self.zip_file.append(msg)
				#self.upload_queue.put(zip_ret)#压缩完的文件

			self.searchtime = self.searchtime + 1

class uploadtask(Thread):
	def __init__(self,upload_queue):
		super().__init__()
		self.upload_queue = upload_queue
		self.upload_file = []
	def run(self):
		while True:
			msg = self.upload_queue.get()
			for x in msg:
				if x not in self.upload_file:
					#上传文件不能有空格
					print("3开始上传:" + x)
					tack_name = " upload {0}".format(x)
					upload_cmd = bypy_cmd_path + tack_name
					print("3 upload:",os.system(upload_cmd))
					#os.remove(x)
					print("3上传结束:" + x)
					self.upload_file.append(x)

if __name__ == '__main__':
	updatequeue = Queue()
	upload_queue = Queue()

	update_Thread = updateVideofiles(updatequeue)
	zip_Thread = ziptask(updatequeue,upload_queue)
	upload_Thread = uploadtask(upload_queue)
	
	update_Thread.start()
	zip_Thread.start()
	upload_Thread.start()
