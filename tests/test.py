#-*- coding: utf-8 -*-
import os
import sys
import configparser
import unittest

'''
	Load pixiv package path
'''
try:
	CURRENT_DIR = os.getcwd()
	MODULE_PATH = '\\'.join(CURRENT_DIR.split('\\')[:-1])
	sys.path.append(MODULE_PATH)
	from pixiv import *
except (ImportError, ModuleNotFoundError):
	print('Import pixiv fail')
	sys.exit(1)

CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

pixiv_id = config['pixiv']['pixiv_id']
password = config['pixiv']['password']

'''
	TestCase for BasePixivApi
'''
class BaseApiTestCase(unittest.TestCase):

	def setUp(self):
		self.api = BaseGuestApi()

	def tearDown(self):
		self.api.close()

'''
	TestCase for PixivGuestApi Which you visit pixiv as a guest
'''
class PixivGuestApiTestCase(BaseApiTestCase):

	def setUp(self):
		self.api = PixivGuestApi()

	def test_search(self):
		items = self.api.search('宝多六花', 3)
		self.assertTrue(len(items)!=0)

	def test_get_get_author_images(self):
		items = self.api.get_author_images(72342)
		self.assertTrue(len(items)!=0)

	def test_get_rank_daily(self):
		items = self.api.get_rank(page=1, daily=True, r18=False)
		self.assertTrue(len(items)!=0)

	def test_get_rank_male(self):
		items = self.api.get_rank(page=1, male=True, r18=False)
		self.assertTrue(len(items)!=0)

	def test_get_rank_female(self):
		items = self.api.get_rank(page=1, male=False, r18=False)
		self.assertTrue(len(items)!=0)

'''
	TestCase for PixivApi Which you need to login your pixiv account
'''
class PixivApiTestCase(PixivGuestApiTestCase):

	def setUp(self):
		self.api = PixivApi(pixiv_id, password)

	def test_get_follow(self):
		items = self.api.get_follow(page=3)
		self.assertTrue(len(items)!=0)

	def test_get_favorite(self):
		items = self.api.get_favorite(page=1)
		self.assertTrue(len(items)!=0)

	def test_get_rank_daily_r18(self):
		items = self.api.get_rank(page=1, daily=True, r18=True)
		self.assertTrue(len(items)!=0)

	def test_get_rank_male_r18(self):
		items = self.api.get_rank(page=1, male=True, r18=True)
		self.assertTrue(len(items)!=0)

	def test_get_rank_female_r18(self):
		items = self.api.get_rank(page=1, male=False, r18=True)
		self.assertTrue(len(items)!=0)

	def test_download(self):
		TEST_FILENAME = '72727291_p0.jpg'
		self.api.download('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=72727291')
		self.assertTrue(os.path.exists(TEST_FILENAME))
		os.remove('72727291_p0.jpg')
		
if __name__ == '__main__':
	unittest.main()