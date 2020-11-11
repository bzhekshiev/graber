# -*- coding: utf-8 -*-
from functools import lru_cache

import extruct
import requests
from bs4 import BeautifulSoup
from dateutil import parser


@lru_cache(maxsize=None)
def create_news_source_dict(filename):
    source = {}
    with open(filename, 'r') as f:
        for line in f.readlines():
            items = line.split('~')
            source[items[0].strip()] = items[1].strip().replace('\n', '')
    return source


SOURCES = create_news_source_dict('news_source.txt')


def news(source, limit=None):
    try:
        result = []
        rss = SOURCES[source]
        r = requests.get(rss)
        xml = BeautifulSoup(r.content, features='xml')
        items = xml.findAll('item')
        for item in items:
            title = item.find('title').text
            link = item.find('link').text
            description = item.find('description').text
            published = item.find('pubDate').text
            article = {
                'title': title,
                'link': link,
                'description': description.replace('\n', ''),
                'published': parser.parse(published).strftime('%d.%m.%Y %H:%M:%S')
            }
            result.append(article)
        return result[:limit]
    except Exception as ee:
        print(ee)


def get_html(url):
    req = requests.get(url)
    html = BeautifulSoup(req.content, 'html.parser')
    return str(html)


def parse_microdata(metadata):
    if metadata:
        try:
            properties = metadata[0].get('properties')
            title = properties.get('headline')
            content = properties.get('articleBody').split('\n\n')
            img = properties.get('image')
            if type(img) == str:
                image = img
            if type(img) == list and img[0].get('type'):
                image = properties.get('image')[0].get('properties').get('url')
            if type(img) == list and not img[0].get('type'):
                image = img[1]
            if type(img) == None:
                image = None
            article = {
                'title': title,
                'content': content,
                'image': image
            }
            return article
        except Exception as ee:
            print(ee)


def parse_json_ld(metadata):
    if metadata:
        try:
            title = metadata[0].get('headline')
            content = metadata[0].get('description')
            image = metadata[0].get('image')[0].get('url')
            article = {
                'title': title,
                'content': content,
                'image': image
            }
            return article
        except Exception as ee:
            print(ee)


def get_article_content(url):
    if extruct.extract(get_html(url)).get('microdata'):
        metadata = extruct.extract(get_html(url)).get('microdata')
        return parse_microdata(metadata)
    elif extruct.extract(get_html(url)).get('json-ld'):
        metadata = extruct.extract(get_html(url)).get('json-ld')
        return parse_json_ld(metadata)
