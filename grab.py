# -*- coding: utf-8 -*-
import extruct
import requests
from bs4 import BeautifulSoup

SOURCES = {
    'lenta': 'http://lenta.ru/rss',
    'interfax': 'http://www.interfax.ru/rss.asp',
    'kommersant': 'http://www.kommersant.ru/RSS/news.xml',
    'm24': 'http: // www.m24.ru/rss.xml'
}

# todo - дату отформатировать
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
                'published': published
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

#todo какая-то подстава с description
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


if __name__ == '__main__':
    # url = news('lenta', limit=3)[0]['link']
    # print(url)
    url = r'https://www.interfax.ru/world/736364'
    # url = r'https://lenta.ru/news/2020/11/10/backyard/'
    # url = r'https://www.m24.ru/news/obshchestvo/10112020/140776'
    # url = r'https://www.kommersant.ru/doc/4566162'

    if extruct.extract(get_html(url)).get('microdata'):
        metadata = extruct.extract(get_html(url)).get('microdata')
        print(parse_microdata(metadata))
    elif extruct.extract(get_html(url)).get('json-ld'):
        metadata = extruct.extract(get_html(url)).get('json-ld')
        print(parse_json_ld(metadata))
