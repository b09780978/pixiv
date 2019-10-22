#-*- coding: utf-8 -*-
from pixiv import PixivApi

pixiv_id = 'YOUR_PIXIV_ID'
password = 'YOUR_PIXIV_PASSWORD'


if __name__ == '__main__':
	api = PixivApi(pixiv_id, password)
	
	# get illust information
	print(api.illust(71403018))

	# get relate illust
	print(api.illust_related(71403018))

	# search
	print(len(api.search('宝多六花')))

	# download illust first image
	api.download(71403018)

	# download all illust image
	api.download_all(77337480)

	# get rank day_male_r18
	print(api.rank(male=True))

	# get rank day
	print(api.rank(r18=False))

	# get rank week_rookie
	print(api.rank(day='week', rookie=True))
	
	# get recommend illust
	print(api.recommended())

	# get current hot tags
	print(api.hot_tags())

	# get user information
	print(api.user(14095911))

	# get all user illust
	print(api.user_illusts(14095911))

	# get user bookmark
	print(api.user_bookmarks(14095911))
	
	# get user follow illust
	print(api.new_follow_illusts())

	# get illust infomation about whether bookmark
	print(api.bookmark_info(71403018))

	# get user bookmark tags
	print(api.bookmark_tags())

	# get user follwing
	print(api.user_following(14095911))

	# get user follower
	print(api.user_follower(14095911))

	# add and remove bookmark
	#print(api.add_bookmark(76642253))
	#print(api.delete_bookmark(76642253))
	
	api.close()
