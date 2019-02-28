#-*- coding: utf-8 -*-
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from .Exception import PixivApiException

# pixiv url and login url.
PIXIV = 'https://www.pixiv.net'
LOGIN_URL = 'https://accounts.pixiv.net/login'
LOGIN_POST_URL = 'https://accounts.pixiv.net/api/login?lang=zh_tw'

# user-agnet.
headers = {
	'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}

# login data.
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

class BasePixivApi(requests.Session):
	'''
		set your pixiv_id and password, make you can fetch all image(over 18).
		pixiv = PixivApi(pixiv_id, password)
	'''
	def __init__(self, parser='html.parser'):
		super(BasePixivApi, self).__init__()
		self.parser = parser
		self.headers.update(headers)

	'''
		Input:
			author_id : author's pixiv id.
			page : which page your want to fetch.
		Output:
			image link list {'url' : image_url, 'id' : image_id}.
	'''
	def get_author_images(self, author_id):
		target_url = 'https://www.pixiv.net/ajax/user/{}/profile/top'
		response = self.get(target_url.format(author_id))

		# check whether author exits.
		if response.status_code != 200:
			raise PixivApiException('Author id {} doesn\'t exist, {}.'.format(author_id, response.status_code))

		pixiv_json = response.json()

		if pixiv_json['error'] != False:
			raise PixivApiException('Author id {} doesn\'t exist.'.format(author_id))

		imagePool = [ item[1]['url'] for item in pixiv_json['body']['illusts'].items() ]
		return imagePool

	'''
		Input:
			images : numbers of image you want to crawl.
		Output:
			list content rank male image's link and author's link.
			[ {'url': image_link, 'author': author_link, 'id' : image_id} ]
	'''
	def get_rank(self, page=1, male=True, daily=False, r18=False):
		mode = None
		page = 1 if page<1 else page
		# decide whether use daily.
		if daily:
			mode = 'daily_r18' if r18 else 'daily'
		else:
			mode = 'male' if male else 'female'
			if r18:
				mode += '_r18'

		target_url = 'https://www.pixiv.net/ranking.php?mode={}&p={}&format=json'.format(mode, page)
		response = self.get(target_url)

		# check whether can get page.
		if response.status_code != 200:
			raise PixivApiException('Get rank {} fail, {}.'.format(target_url, response.status_code))

		imagePool = []
		pixiv_json = response.json()

		if pixiv_json.get('error', None) is None:
			for item in pixiv_json['contents']:
				imagePool.append({'url' : item['url'], 'author_id' : item['user_id'], 'id' : item['illust_id']})

		return imagePool

	'''
	Input:
		keyword : the keyword you want to search.
		page : which page that you want to fetch.
		Output:
			list of image link.
	'''
	def search(self, keyword, page=1):
		if len(keyword) == 0:
			raise PixivApiException('Search keyword can\t be empty.')
		page = 1 if page<1 else page
		SEARCH_URL = 'https://www.pixiv.net/search.php?s_mode=s_tag&word={}&order=date_d&p={}'
		response = self.get(SEARCH_URL.format(keyword, page))
		if response.status_code != 200:
			raise PixivApiException('search fail, {}'.format(response.status_code))

		response.encoding = 'utf-8'

		FORMAT_IMAGE = ';(https.{,30}?img-master.+?(jpg|png|mp4))&quot'
		imagePool = [ match[0].replace('\\', '') for match in re.findall(FORMAT_IMAGE, response.text) ]

		return imagePool

'''
	Pixiv Guest Api:
		Without login your account, but the image you can get is limited
'''
class PixivGuestApi(BasePixivApi):
	pass

'''
	Pixiv Api:
		Auto login your account for you get image resource
'''
class PixivApi(BasePixivApi):
	'''
		set your pixiv_id and password, make you can fetch all image(over 18).
		pixiv = PixivApi(pixiv_id, password)
	'''
	def __init__(self, pixiv_id, password, parser='html.parser'):
		super(PixivApi, self).__init__(parser)
		self.pixiv_id = pixiv_id
		self.password = password
		self.headers.update(headers)
		self.login()

	'''
		login your acount.
	'''
	def login(self):
		response = self.get(LOGIN_URL, params=LOGIN_PARAM)
		parser = BeautifulSoup(response.text, self.parser)
		post_key = parser.select('[name=post_key]')[0]['value']

		# prevent to fast.
		time.sleep(0.5)
		LOGIN_POST_DATA.update({'pixiv_id' : self.pixiv_id,
								'password' : self.password,
								'post_key' : post_key,})
		self.post(LOGIN_POST_URL, data=LOGIN_POST_DATA)

		# use r18 rank to check whether success login.
		check_login_url = 'https://www.pixiv.net/ranking.php?mode=daily_r18&content=illust'
		response = self.get(check_login_url)
		if response.status_code != 200:
			raise PixivApiException('Login fail, {}.'.format(response.status_code))

	'''
		Input:
			page : which page that you want to fetch.
		Output:
			list of image link {'url' : image_url, 'id' : image_id}.
	'''
	def get_follow(self, page=1):
		page = 1 if page<1 else page
		target_url = 'https://www.pixiv.net/bookmark_new_illust.php?p={}'
		imagePool = []

		response = self.get(target_url.format(page))
		parser = BeautifulSoup(response.text, self.parser)
		for block in parser.select('#js-mount-point-latest-following'):
			data = json.loads(block['data-items'])
			for image_item in data:
				imagePool.append( { 'url' : image_item['url'].replace('\\',''), 'id' : image_item['illustId'] })

		return imagePool

	'''
		Input:
			page : which page that you want to fetch.
		Output:
			list of image link.
	'''
	def get_favorite(self, page=1):
		page = 1 if page<1 else page
		FAVORITE_URL = 'https://www.pixiv.net/bookmark.php?rest=show&p={}&order=desc'
		response = self.get(FAVORITE_URL.format(page))
		if response.status_code != 200:
			raise PixivApiException('Get favorite fail, {}.'.format(response.status_code))

		response.encoding = 'utf-8'
		
		parser = BeautifulSoup(response.text, self.parser)
		imagePool = [ element['data-src'] for element in parser.select('[data-src]') if re.search('(jpg|png|mp4)', element['data-src']) is not None ]

		return imagePool

	'''
		Input:
			image_url : image's url.
			file_name : store file name.
		Output:
			None, download the image.
	'''
	def download(self, image_url, file_name=None):
		FORMAT_ID = '\d{5,}'
		FORMAT_IMAGE = '\"https.{,30}img-original.+?(jpg|png|mp4)\"'

		image_id = re.search(FORMAT_ID, image_url)
		if image_id is None:
			raise PixivApiException('Can\'t get image id')

		image_id = image_id.group()
		referer_image_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}'.format(image_id)

		response = self.get(referer_image_url)

		if response.status_code != 200:
			raise 'Download fail, {}'.format(response.status_code)

		response.encoding = 'utf-8'
		url = re.search(FORMAT_IMAGE, response.text)
		if url:
			url = url.group()
			download_url = 'https://' + url[11:-1].replace('\\', '')
		else:
			raise PixivApiException('Download fail, illust_id: {} not found'.format(image_id))		

		if file_name is None:
			file_name = download_url.split('/')[-1]
		else:
			file_type = download_url.split('.')[-1]
			file_name_name += '.' + file_type

		# Set Referer header to bypass 403 forbidden
		self.headers['Referer'] = referer_image_url
		response = self.get(download_url, stream=True)

		# check whether can download.
		if response.status_code != 200:
			self.headers.pop('Referer')
			raise PixivApiException('Download {} fail, {}.'.format(image_url, response.status_code))

		# Download file and store in current directory
		with open(file_name, 'wb') as f:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)

		# Clean Referer header
		self.headers.pop('Referer')