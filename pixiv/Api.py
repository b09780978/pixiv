#-*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import json
import os
from typing import Union
from requests import Session, Response, codes
from .utils import *
from .Exception import PixivApiException

def convert_bool(o):
	return 'true' if o else 'false'

PIXIV_APP_URL = 'https://app-api.pixiv.net'
PIXIV_OAUTH_URL = 'https://oauth.secure.pixiv.net'

DEFAULT_HEADERS = {
	'User-Agent' : 'PixivAndroidApp/5.0.64 (Android 6.0)',
	'Accept-Language' : 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
}

# restrict = [ public, private ]

class PixivApi(Session):
	client_id = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
	client_secret = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'
	hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'

	_access_token = None
	_refresh_token = None

	def __init__(self, username : str, password : str, access_token : str=None, refresh_token : str=None):
		super(PixivApi, self).__init__()
		self.headers.update(DEFAULT_HEADERS)
		self._username = username
		self._password = password
		self._auth = False
		self._auth = self.login()

	def login(self):
		current_time = datetime.now().isoformat()
		self.headers.update({
				'X-Client-Time' : current_time,
				'X-Client-Hash' : hashlib.md5((current_time + self.hash_secret).encode('utf-8')).hexdigest()
			})

		oauth_url = 'https://oauth.secure.pixiv.net/auth/token'

		oauth_post_data = {
			'get_secure_url' : 1,
			'client_id' : self.client_id,
			'client_secret' : self.client_secret,
		}

		'''
			Acording whether access_token and refresh_token exist to select oauth method
		'''
		if (self._access_token is not None) and (self._refresh_token is not None):
			oauth_post_data['grant_type'] = 'refresh_token'
			data['refresh_token'] = self._refresh_token

		elif (self._username is not None) and (self._password is not None):
			oauth_post_data['grant_type'] = 'password'
			oauth_post_data['username'] = self._username
			oauth_post_data['password'] = self._password

		else:
			self._auth = False
			raise PixivApiException('Unknow auth method')

		resp = self.post(oauth_url, data=oauth_post_data)

		if resp.status_code != codes.all_ok:
			raise PixivApiException('Pixiv Oauth fail\n{}: {}'.format(resp.status_code, resp.text))

		resp_json = get_pretty_response(resp)

		self._access_token = resp_json.response.access_token
		self._refresh_token = resp_json.response.refresh_token
		self._user_id = resp_json.response.user.id

		# Clean oauth request header and set Authorization to access_token
		self.headers.pop('X-Client-Time')
		self.headers.pop('X-Client-Hash')
		self.headers['Authorization'] = 'Bearer {}'.format(self._access_token)


	# get illust detail infomation
	def illust(self, illust_id : int) -> JsonDict:
		query_url = '{}/v1/illust/detail'.format(PIXIV_APP_URL)
		resp = self.get(query_url, params={	'illust_id' : illust_id, })
		return get_pretty_response(resp)

	def illust_related(self, illust_id : int, offset : int=0) -> JsonDict:
		query_url = '{}/v2/illust/related'.format(PIXIV_APP_URL)
		resp = self.get(query_url, params={'illust_id' : illust_id, 'filter' : 'for_ios', 'offset' : offset})
		return get_pretty_response(resp)

	def recommended(self, offset : int=None, ranking_label : bool=True, ranking_illust : bool=True, privacy : bool=True) -> JsonDict:
		recommand_url = '{}/v1/illust/recommended'.format(PIXIV_APP_URL)

		recommand_params = {
			'content_type' : 'illust',
			'filter' : 'for_ios',
			'include_ranking_label' : convert_bool(ranking_label),
			'include_ranking_illusts' : convert_bool(ranking_illust),
			'include_privacy_illusts' : convert_bool(privacy),
		}

		if offset is not None:
			recommand_params['offset'] = offset

		resp = self.get(recommand_url, params=recommand_params)
		return get_pretty_response(resp)

	# That's a bad idea. Only return JsonDict not check whether the illust is bookmarked
	def bookmark_info(self, illust_id : Union [ int, str ]) -> JsonDict:
		url = '{}/v2/illust/bookmark/detail'.format(PIXIV_APP_URL)
		resp = self.get(url, params={'illust_id' : illust_id })
		return get_pretty_response(resp)

	# It's works, but return empty dict back.
	def add_bookmark(self, illust_id : Union[ int, str ], restrict : str='public', tag : str=None) -> JsonDict:
		url = '{}/v2/illust/bookmark/add'.format(PIXIV_APP_URL)
		data = {
			'illust_id' : illust_id,
			'restrict' : restrict,
		}

		if tag is not None:
			data['tag'] = tag

		resp = self.post(url, data=data)
		return get_pretty_response(resp)

	def delete_bookmark(self, illust_id : Union[ int, str ]) -> JsonDict:
		url = '{}/v1/illust/bookmark/delete'.format(PIXIV_APP_URL)
		resp = self.post(url, data={'illust_id' : illust_id})
		return get_pretty_response(resp)

	def bookmark_tags(self, restrict : str='public', offset : int=None) -> JsonDict:
		url = '{}/v1/user/bookmark-tags/illust'.format(PIXIV_APP_URL)
		params = {
			'restrict' : restrict,
		}

		if offset is not None:
			params['offset'] = offset

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def hot_tags(self) -> JsonDict:
		url = '{}/v1/trending-tags/illust'.format(PIXIV_APP_URL)
		resp = self.get(url, params={'filter' : 'for_ios'})
		return get_pretty_response(resp)

	def user(self, user_id : Union[ int, str] ) -> JsonDict:
		user_url = '{}/v1/user/detail'.format(PIXIV_APP_URL)
		resp = self.get(user_url, params={'user_id' : user_id, 'filter' : 'for_ios'})
		return get_pretty_response(resp)

	def user_illusts(self, user_id : Union[ int, str ], offset : int=None) -> JsonDict:
		url = '{}/v1/user/illusts'.format(PIXIV_APP_URL)
		params = {
			'user_id' : user_id,
			'filter' : 'for_ios',
		}

		if offset is not None:
			params['offset'] = offset

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def user_bookmarks(self, user_id : Union[ int, str ], restrict : str='public', tag : str=None) -> JsonDict:
		url = '{}/v1/user/bookmarks/illust'.format(PIXIV_APP_URL)

		params = {
			'user_id' : user_id,
			'filter' : 'for_ios',
			'restrict' : restrict,
		}

		if tag is not None:
			params['tag'] = tag

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def new_follow_illusts(self, restrict : str='public', offset : int=None) -> JsonDict:
		url = '{}/v2/illust/follow'.format(PIXIV_APP_URL)
		params = {
			'restrict' : restrict,
		}

		if offset is not None:
			params['offset'] = offset

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def user_following(self, user_id : Union[ int, str ], restrict : str='public', offset : int=None) -> JsonDict:
		url = '{}/v1/user/following'.format(PIXIV_APP_URL)
		params = {
			'user_id' : user_id,
			'restrict' : restrict
		}

		if offset:
			params['offset'] = offset

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def user_follower(self, user_id : Union[ int, str ], offset : int=None) -> JsonDict:
		url = '{}/v1/user/follower'.format(PIXIV_APP_URL)
		params = {
			'user_id' : user_id,
			'filter' : 'for_ios',
		}

		if offset is not None:
			params['offset'] = offset

		resp = self.get(url, params=params)
		return get_pretty_response(resp)

	def _download(self, url: str, filename: str, path: str) -> bool:
		self.headers['Referer'] = 'https://app-api.pixiv.net/'
		success = True
		f = None

		try:
			f = open(filename, 'wb')
			resp = self.get(url, stream=True)

			for chunk in resp.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
		except Exception as e:
			success =  False
		finally:
			f.close()
			self.headers.pop('Referer')

		return True

	def download(self, illust_id: Union [ int, str ], filename: str=None, path : str=os.path.curdir) -> bool:
		illust = self.illust(illust_id)

		if illust.error is not None:
			return False

		if filename is None:
			filename = '{}_{}.jpg'.format(illust.illust.title, illust.illust.id)
			os.path.join(path, filename)

		image_url = illust.illust.image_urls.large
		
		success = self._download(image_url, filename, path)

		return success

	def download_all(self, illust_id: int, filename: str=None, path : str=os.path.curdir) -> bool:
		illust = self.illust(illust_id)

		if illust.error is not None:
			return False

		if filename is None:
			filename = '{}_{}'.format(illust.illust.title, illust.illust.id)
		else:
			filename = '{}_{}'.format(filename)
		filename += '_{}.jpg'
						
		illusts = illust.illust.meta_pages
		index = 0
		for item in illusts:
			self._download(item.image_urls.original, filename.format(index), path)
			index += 1

		return True

	'''
		keyword : string keyword
		desc_sort : True=> date_desc False=>date_asc
		search_title and strict: bool to choose ['exact_match_for_tags', 'partial_match_for_tags', 'title_and_caption']
	'''
	def search(self, keyword: str, desc_sort : bool=True, search_title : bool=True, strict : bool=False, duration : str='within_last_day', offset : int=0) -> JsonDict:
		query_url = '{}/v1/search/illust'.format(PIXIV_APP_URL)

		if desc_sort:
			sort = 'date_desc'
		else:
			sort = 'date_asc'

		if search_title and strict:
			search_policy = 'exact_match_for_tags'
		elif search_title and (not strict):
			search_policy = 'partial_match_for_tags'
		else:
			search_policy = 'title_and_caption'

		if duration not in ['within_last_day', 'within_last_week', 'within_last_month']:
			raise PixivApiException('duration must in if duration not in [ within_last_day, within_last_week, within_last_month ]')

		search_params = {
			'word' : keyword,
			'search_target' : search_policy,
			'sort' : sort,
			'filter' : 'for_ios',
			'duration' : duration,
			'offset' : offset,
		}

		resp = self.get(query_url, params=search_params)
		return get_pretty_response(resp)

	'''
		mode : [ 'day', 'week', 'month', 
		         'day_male', 'day_female', 'week_original',
		         'week_rookie', 'day_r18', 'day_male_r18',
		         'day_female_r18', 'week_r18', 'week_r18g'
		        ]
		 date format: YYYY-MM-DD
	'''
	def rank(self, day : str='day', male : str=None, r18 : bool=True, original : bool=False, rookie : bool=False, date : str=None, offset: int=None) -> JsonDict:
		if day not in ['day', 'week', 'month']:
			raise PixivApiException('day must in [ day, week, month] ')

		rank_url = '{}/v1/illust/ranking'.format(PIXIV_APP_URL)
		mode = day
		# ['day', 'day_r18', 'day_male', 'day_male_r18', 'day_female', 'day_female_r18']
		if day == 'day':
			if male is not None:
				mode += '_male' if male else '_female'
			if r18:
				mode += '_r18'
		# ignore original = True and rookie = True
		elif day == 'week':
			if original and (not rookie):
				mode += '_original'
			elif (not original) and rookie:
				mode += '_rookie'

		rank_params = {
			'mode' : mode,
			'filter' : 'for_ios',
		}

		if date is not None:
			rank_params['date'] = date
		if offset is not None:
			rank_params['offset'] = offset

		resp = self.get(rank_url, params=rank_params)
		return get_pretty_response(resp)

	def __del__(self):
		self.close() 