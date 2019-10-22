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
	TestCase for PixivGuestApi Which you visit pixiv as a guest
'''
class PixivGuestApiTestCase(unittest.TestCase):

	def setUp(self):
		self.api = PixivApi(pixiv_id, password)

	def tearDown(self):
		self.api.close()

	def test_search(self):
		items = self.api.search('宝多六花')
		self.assertTrue(len(items)!=0)

	def test_illust(self):
		items = self.api.illust(71403018)
		self.assertTrue(items.error is None)

	def test_illust_related(self):
		items = self.api.illust_related(71403018)
		self.assertTrue(items.error is None)

	def test_rank_male(self):
		items = self.api.rank(male=True, r18=True)
		self.assertTrue(items.error is None)

	def test_rank_rookie(self):
		items = self.api.rank(day='week', rookie=True)
		self.assertTrue(items.error is None)

	def test_rank_original(self):
		items = self.api.rank(day='week', original=True)
		self.assertTrue(items.error is None)

	def test_rank_month(self):
		items = self.api.rank(day='month')
		self.assertTrue(items.error is None)

	def test_recommended(self):
		items = self.api.recommended()
		self.assertTrue(len(items)!=0)

	def test_hot_tags(self):
		items = self.api.hot_tags()
		self.assertTrue(len(items)!=0)

	def test_user(self):
		items = self.api.user(14095911)
		self.assertTrue(items.error is None)

	def test_user_illusts(self):
		items = self.api.user_illusts(14095911)
		self.assertTrue(items.error is None)

	def test_user_bookmarks(self):
		items = self.api.user_bookmarks(14095911)
		self.assertTrue(items.error is None)

	def test_new_follow_illusts(self):
		items = self.api.new_follow_illusts()
		self.assertTrue(items.error is None)

	def test_bookmark_info(self):
		items = self.api.bookmark_info(71403018)
		self.assertTrue(items.error is None)

	def test_bookmark_tags(self):
		items = self.api.bookmark_tags()
		self.assertTrue(items.error is None)

	def test_user_following(self):
		items = self.api.user_following(2864095)
		self.assertTrue(items.error is None)

	def test_user_follower(self):
		items = self.api.user_follower(2864095)
		self.assertTrue(items.error is None)


	def test_download(self):
		TEST_FILENAME = 'test.jpg'
		self.api.download(71403018, TEST_FILENAME)
		self.assertTrue(os.path.exists(TEST_FILENAME))
		os.remove(TEST_FILENAME)

		
		
if __name__ == '__main__':
	unittest.main()