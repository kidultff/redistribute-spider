#encoding:utf-8
from time import time, sleep
import sys
from config import *

try:
	import requests as r
	from bs4 import BeautifulSoup as bs
except:
	print("must install:\nrequests bs4\nuse pip install requests bs4")
	exit()

cache_file = sys.path[0] + cache_file

class xmcSpider:
	def __init__(self):
		self.__last = 0
		self.__saved_urls = self.__load_cache()
	
	def __load_cache(self):
		saved_urls = {}						#cache dict
		with open(cache_file, 'r') as f:	#read cache
			cache = f.readlines()
			for item in cache:
				if "#|#" not in item:
					continue
				_item = item.replace("\n", "").split("#|#")
				saved_urls[_item[0]] = _item[1]
		return saved_urls
	
	def GetHtmlObj(self, href, type = 0):	#0=>index, 1=>page
		if debug_info:
			print("[debug] Getting %s" % href)
		try:
			if type == 0:
				url = "http://muchong.com/f-430-%s-typeid-2304" % href
			else:
				url = "http://muchong.com/%s" % href
			while int(time()) - self.__last < interval:
				sleep(1)
			self.__last = int(time())
			html = r.get(url).text
			obj = bs(html, "html.parser")
			return obj
		except:
			if debug_info:
				print("[ERROR] GetHtmlObj(%s, %d)" % (href, type))
			return False
		
	def GetIndex(self, obj):
		try:
			index = obj.find_all('th', class_='thread-name')[1:]	#[1:] remove [竞价]
			urls = []
			for item in index:
				url = item.find_all('a', class_ = "a_subject")[0]['href']
				if "t-" in url:
					urls.append(url)
			return urls
		except:
			if debug_info:
				print("[ERROR] GetIndex()")
			return False
		
	def GetItem(self, url):
		try:
			save_urls_key = "http://muchong.com" + url
			if save_urls_key not in list(self.__saved_urls.keys()):	#if not in cache
				obj = self.GetHtmlObj(url, 1)
				inf = obj.find_all('table', class_='adjust_table')[0].text.replace(' ', '').replace('\n', '  ').replace('\r', '')
				detail = obj.find_all('div', class_="t_fsz")[0].td.text
				info = ("http://muchong.com"+url, inf)
				with open(cache_file, 'a') as f:#save to cache file
					if debug_info:
						print("[debug] Save to file: %s" % save_urls_key)
					f.write("%s#|#%s\n" % (info[0], info[1]))
			else:		#if hit cache
				if debug_info:
					print("[debug] hit cache: %s" % save_urls_key)
				return "http://muchong.com"+url, self.__saved_urls[save_urls_key]
		except:
			if debug_info:
				print("[ERROR] GetItem(%s)" % url)
			return False
		
	def fitter_word(self, _info):
		for word in exclude:			#for each exclude word
			if word in _info:
				return False
		for word in focus_include:
			if word not in _info:
				return False
		for word in include:			#for each include word
			if word in _info:
				return True
		return False

if __name__ == '__main__':
	spider = xmcSpider()
	for i in range(1, page_end+1):
		htmlobj = spider.GetHtmlObj(str(i))
		urls = spider.GetIndex(htmlobj)
		if not urls or not htmlobj:
			continue
		info = []
		for url in urls:						#foreach url
			info = spider.GetItem(url)
			if info and spider.fitter_word(info[0] + info[1]):
				print("链接：%s\n详情：%s\n" % (info[0], info[1]))