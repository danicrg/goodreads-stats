import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime as dt
import config

KEY = config.KEY
SECRET =  config.SECRET

BOOKS_PER_PAGE = 200

s = requests.Session()

from collections import defaultdict

def xml2dict(xmlstring):
	tree = ET.fromstring(xmlstring)
	return etree_to_dict(tree)

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def get_books_on_page(user_id, page):

	url = "https://www.goodreads.com/review/list?v=2"
	params = {
		'v': 2,
		'id': user_id,
		'shelf': 'read',
		'sort': 'date_read',
		'page': page,
		'per_page': BOOKS_PER_PAGE,
		'key': KEY,
	}

	res = s.get(url, params=params)

	return xml2dict(res.text)

def get_books(user_id):
	page = 1
	res = get_books_on_page(user_id, page)['GoodreadsResponse']
	total_books = res['reviews']['@total']
	n_pages = -( - int(total_books) // BOOKS_PER_PAGE) # ROUNDUP

	books = res['reviews']['review']

	for page in range(2, n_pages+1):
		books.extend(get_books_on_page(user_id, page)['GoodreadsResponse']['reviews']['review'])

	return books

def get_books_df(user_id):
	books = get_books(user_id)

	for i, book in enumerate(books):
		books[i]['title'] = book['book']['title']
		books[i]['author'] = book['book']['authors']['author']['name']
		books[i]['image_url'] = book['book']['image_url']
		try:
			books[i]['num_pages'] = int(book['book']['num_pages'])
		except:
			books[i]['num_pages'] = None
		books[i]['published'] = book['book']['published'] if book['book']['published'] is not None else book['book']['publication_year']
		books[i]['average_rating'] = book['book']['average_rating']
		del books[i]['book']

		del books[i]['shelves']

	df = pd.DataFrame(books)

	df['started_at'] = pd.to_datetime(df['started_at'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce').apply(lambda dt: dt.replace(tzinfo=None))
	df['read_at'] = pd.to_datetime(df['read_at'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce').apply(lambda dt: dt.replace(tzinfo=None))
	df['date_added'] = pd.to_datetime(df['date_added'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce').apply(lambda dt: dt.replace(tzinfo=None))
	df['date_updated'] = pd.to_datetime(df['date_updated'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce').apply(lambda dt: dt.replace(tzinfo=None))

	df = df[~df['started_at'].isin([pd.NaT])]

	return df