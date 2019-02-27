#-*- coding: utf-8 -*-
from pixiv import PixivApi

pixiv_id = YOUR_PIXIV_ACCOUNT
password = YOUR_PASSWORD

if __name__ == '__main__':
	pixivapi = PixivApi(pixiv_id, password)

	'''
		Search by keyword.
	'''
	for item in pixivapi.search('宝多六花', 2):		
		print(item)

	'''
		Get rank page.
	'''
	# get daliy r18
	pool = pixivapi.get_rank(1, daily=True, r18=True)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get daliy
	pool = pixivapi.get_rank(1, daily=True)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get rank male
	pool = pixivapi.get_rank(1)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get rank female
	pool = pixivapi.get_rank(1, male=False)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get rank male r18
	pool = pixivapi.get_rank(1, r18=True)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get rank female r18
	pool = pixivapi.get_rank(1, male=False, r18=True)
	for item in pool:
		print(item['id'], item['author_id'], item['url'])

	# get author's image at page 1.
	pool = pixivapi.get_author_images(2973809, 1)
	for item in pool:
		print(item['id'], item['url'])

	# download pixiv image by url.
	pixivapi.download('https://i.pximg.net/c/240x240/img-master/img/2018/03/20/00/12/38/67820508_p0_master1200.jpg')
	# download pixiv image by illust_id
	pixivapi.download('73124903')

	# get user follow.
	pool = pixivapi.get_follow()
	for item in pool:
		print(item['id'], item['url'])

	# download favorite images.
	pool = pixivapi.get_favorite(3)
	for item in pool:
		pixivapi.download(item)

	# Note you need to close PixivApi session.
	pixivapi.close()
	print('Finish test')