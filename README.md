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

	# get 5 image from rank male.
	pool = pixivapi.get_rank_male(5)
	for item in pool:
		print('image link: {}'.format(item['img']))
		print('author link: {}'.format(item['author']))
	print()
	
	# get 2 image from rank r18.
	pool = pixivapi.get_r18_top(2)
	for item in pool:
		print('image link: {}'.format(item['img']))
		print('author link: {}'.format(item['author']))
	print()
	
	# get new image link from you follow author(page 3).
	pool = pixivapi.get_follow(3)
	for link in pool:
		print(link)
	print()

	# get author's image at page 1(pixiv_id, page)
	pool = pixivapi.get_author_images(2973809, 1)
	for link in pool:
		print(link)
```
