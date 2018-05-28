# pixiv
a python project to fetch pixiv.net's image.

# Usage
``` python
#-*- coding: utf-8 -*-
import pixiv

pixiv_id = YOUR_PIXIV_ACCOUNT
password = YOUR_PASSWORD

if __name__ == '__main__':
	pixivapi = pixiv.PixivApi(pixiv_id, password)

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

	# download pixiv image.
	pixivapi.download('https://i.pximg.net/c/240x240/img-master/img/2018/03/20/00/12/38/67820508_p0_master1200.jpg')

	# get user follow.
	pool = pixivapi.get_follow()
	for item in pool:
		print(item['id'], item['url'])
```
