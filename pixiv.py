#-*- coding: utf-8
import requests
from bs4 import BeautifulSoup
import time

# pixiv url and login url.
PIXIV = 'https://www.pixiv.net'
LOGIN_URL = 'https://accounts.pixiv.net/login'
LOGIN_POST_URL = 'https://accounts.pixiv.net/api/login?lang=zh_tw'

# user-agnet.
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

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

'''
	PixivApiException: deal with PixivApi Exception.
'''
class PixivApiException(Exception):

	def __init__(self, error_message):
		self.error_message = error_message

	def __str__(self):
		return self.error_message

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
		Input:
			image_url : image's url.
			file_name : store file name.
		Output:
			None, download the image.
	'''
	def download(self, image_url, file_name=None):
		if file_name is None:
			file_name = image_url.split('/')[-1]
		else:
			file_type = image_url.split('.')[-1]
			file_name_name += '.' + file_type

		response = self.session.get(image_url, stream=True)

		# check whether can download.
		if response.status_code != 200:
			raise PixivApiException('Download {} fail, {}.'.format(image_url, response.status_code))

		with open(file_name, 'wb') as f:
			for chunk in response.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)


	'''
		login your acount.
	'''
	def login(self):
		response = self.session.get(LOGIN_URL, params=LOGIN_PARAM)
		parser = BeautifulSoup(response.text, 'html.parser')
		post_key = parser.select('[name=post_key]')[0]['value']

		# prevent to fast.
		time.sleep(0.5)
		LOGIN_POST_DATA.update({'pixiv_id' : self.pixiv_id,
								'password' : self.password,
								'post_key' : post_key,})
		self.session.post(LOGIN_POST_URL, data=LOGIN_POST_DATA)

		# use r18 rank to check whether success login.
		check_login_url = 'https://www.pixiv.net/ranking.php?mode=daily_r18&content=illust'
		response = self.session.get(check_login_url)
		if response.status_code != 200:
			raise PixivApiException('Login fail, {}.'.format(response.status_code))

	'''
		Input:
			page : which page that you want to fetch.
		Output:
			list of image link {'url' : image_url, 'id' : image_id}.
	'''
	def get_follow(self, page=1):
		assert page>0, 'pages must > 0.'
		target_url = 'https://www.pixiv.net/bookmark_new_illust.php?p={}'
		imagePool = []

		response = self.session.get(target_url.format(page))
		parser = BeautifulSoup(response.text, 'html.parser')
		for block in parser.select('#js-mount-point-latest-following'):
			data = eval(block['data-items'].replace('null', 'None').replace('true', 'True').replace('false', 'False'))
			for image_item in data:
				imagePool.append( { 'url' : image_item['url'].replace('\\',''), 'id' : image_item['illustId'] })

		return imagePool

	'''
		Input:
			author_id : author's pixiv id.
			page : which page your want to fetch.
		Output:
			image link list {'url' : image_url, 'id' : image_id}.
	'''
	def get_author_images(self, author_id, page=1):
		assert page>0, 'page must > 0.'
		target_url = 'https://www.pixiv.net/member_illust.php?id={}&type=all&p={}'
		response = self.session.get(target_url.format(author_id, page))

		# check whether author exits.
		if response.status_code != 200:
			raise PixivApiException('Author id {} doesn\'t exist, {}.'.format(author_id, response.status_code))

		parser = BeautifulSoup(response.text, 'html.parser')

		imagePool = []
		for item in parser.select('._layout-thumbnail'):
			imagePool.append( { 'url' : item.img['data-src'], 'id' : item.img['data-id'] })

		return imagePool

	'''
		Input:
			images : numbers of image you want to crawl.
		Output:
			list content rank male image's link and author's link.
			[ {'url': image_link, 'author': author_link, 'id' : image_id} ]
	'''
	def get_rank(self, images=10, male=True, daily=False, r18=False):
		assert images>=0, 'images must >= 0'

		mode = None
		# decide whether use daily.
		if daily:
			mode = 'daily_r18' if r18 else 'daily'
		else:
			mode = 'male' if male else 'female'
			if r18:
				mode += '_r18'

		target_url = 'https://www.pixiv.net/ranking.php?mode={}'.format(mode)
		response = self.session.get(target_url)

		# check whether can get page.
		if response.status_code != 200:
			raise PixivApiException('Get rank {} fail, {}.'.format(target_url, response.status_code))

		parser = BeautifulSoup(response.text, 'html.parser')

		counter = 0
		imagePool = []
		for block in parser.select('.ranking-item'):
			if counter >= images:
				break
			image_block = block.find_all('div')[1]
			author_link = '{}{}'.format(PIXIV, image_block.a['href'])
			image_id = block['data-id']
			image_link = image_block.div.img['data-src']
			imagePool.append({'url' : image_link, 'author' : author_link, 'id' : image_id })
			counter += 1

		return imagePool

	def __del__(self):
		self.session.close()

	def close(self):
		self.session.close()
