#-*- coding: utf-8 -*-
import json
from requests import Response

'''
	Datastructure for deal with response json data
'''

# Python object for json data
class JsonDict(dict):
	def __getattr__(self, key):
		try:
			return self[str(key)]
		except KeyError:
			return None

	def __setattr__(self, key, value):
		sefl[str(key)] = value

def convert_json(json_object: dict) -> JsonDict:
	o = JsonDict()
	for key, value in json_object.items():
		o[key] = value
	return o

def get_pretty_response(resp : Response) -> JsonDict:
	resp.encoding = 'utf-8'
	return json.loads(resp.text, object_hook=convert_json)