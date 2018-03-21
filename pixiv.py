#-*- coding: utf-8
import requests
from bs4 import BeautifulSoup
import time

PIXIV = 'https://www.pixiv.net'
LOGIN_URL = 'https://accounts.pixiv.net/login'
LOGIN_POST_URL = 'https://accounts.pixiv.net/api/login?lang=zh_tw'

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
LOGIN_PARAM = { 'lang' : 'zh_tw',
				'source' : 'pc',
				'view_type' : 'page',
				'ref' : 'wwwtop_accounts_index',
				}

LOGIN_POST_DATA = {
	'pixiv_id' : '',
	'captcha' : '',
	'g_recaptcha_response' : '',
	'password' : '',
	'post_key' : '',
	'source' : 'pc',
	'ref' : 'wwwtop_accounts_index',
	'return_to' : 'https://www.pixiv.net/',
}

class PixivApi(object):
	'''
		set your pixiv_id and password, make you can fetch all image(over 18).
		pixiv = PixivApi(pixiv_id, password)
	'''
	def __init__(self, pixiv_id, password):	
		self.pixiv_id = pixiv_id
		self.password = password
		self.session = requests.Session()
		self.session.headers.update(headers)
		self.login()

	'''
		login your acount.
	'''
	def login(self):
		response = self.session.get(LOGIN_URL, params=LOGIN_PARAM)
		parser = BeautifulSoup(response.text, 'html.parser')
		post_key = parser.select('[name=post_key]')[0]['value']

		time.sleep(0.5)
		LOGIN_POST_DATA.update({'pixiv_id' : self.pixiv_id,
								'password' : self.password,
								'post_key' : post_key,})
		self.session.post(LOGIN_POST_URL, data=LOGIN_POST_DATA)

	'''
		Input:
			pages : how many pages that you want to fetch.
			start_page : start from which page(option, default=1)
		Output:
			list of image link.
	'''
	def get_follow(self, pages=1, start_page=1):
		assert pages>0, 'pages must > 0.'
		assert start_page>0, 'start_page must > 0'
		target_url = 'https://www.pixiv.net/bookmark_new_illust.php?p={}'
		imagePool = []
		for page_index in range(start_page, start_page+pages):
			response = self.session.get(target_url.format(page_index))
			parser = BeautifulSoup(response.text, 'html.parser')
			for block in parser.select('#js-mount-point-latest-following'):
				data = eval(block['data-items'].replace('null', 'None').replace('true', 'True').replace('false', 'False'))
				for image_item in data:
					imagePool.append(image_item['url'].replace('\\',''))
			time.sleep(0.5)
		return imagePool

	'''
		Input:
			images : numbers of image you want to crawl.
		Output:
			list content rank male image's link and author's link.
			[ {'img': image_link, 'author': author_link} ]
	'''
	def get_rank_male(self, images=10):
		assert images>=0, 'images must >= 0'
		target_url = 'https://www.pixiv.net/ranking.php?mode=male'
		response = self.session.get(target_url)
		parser = BeautifulSoup(response.text, 'html.parser')

		counter = 0
		imagePool = []
		for block in parser.select('.ranking-item'):
			if counter >= images:
				break
			image_block = block.find_all('div')[1]
			author_link = '{}{}'.format(PIXIV, image_block.a['href'])
			image_link = image_block.div.img['data-src']
			imagePool.append({'img' : image_link, 'author' : author_link})
			counter += 1

		return imagePool

	'''
		Input:
			images : numbers of image you want to crawl.
		Output:
			list content rank r18 image's link and author's link
			[ {'img': image_link, 'author': author_link} ]
	'''
	def get_r18_top(self, images=10):
		assert images>0, 'images must > 0.'
		target_url = 'https://www.pixiv.net/ranking.php?mode=daily_r18&content=illust'
		self.session.get(target_url)
		response = self.session.get(target_url)
		parser = BeautifulSoup(response.text, 'html.parser')

		counter = 0
		imagePool = []
		for block in parser.select('.ranking-item'):
			if counter >= images:
				break
			image_block = block.find_all('div')[1]
			author_link = '{}{}'.format(PIXIV, image_block.a['href'])
			image_link = image_block.div.img['data-src']
			imagePool.append({'img' : image_link, 'author' : author_link})
			counter += 1

		return imagePool

	def __del__(self):
		self.close()

	def close(self):
		self.session.close()