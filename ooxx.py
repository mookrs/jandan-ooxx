# -*- coding: utf-8 -*-
import os
import shutil
import socket
import time
from urllib.request import Request, urlopen, build_opener
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup


opener = build_opener()  # OpenerDirector
opener.addheaders = []
opener.addheaders.append(('User-agent', 'Mozilla/5.0'))
opener.addheaders.append(('Cookie', '458528247=db856X2bSPJdJD3mZ0qNgqHxstlcw%2BC4xtmr%2BPfjKA; jdna=596e6fb28c1bb47f949e65e1ae03f7f5#1466510995815'))

base_url = 'http://jandan.net/'
category = 'ooxx'


def is_img_type(response):
    mime = response.info()['Content-type']
    return mime.endswith(('jpeg', 'png', 'gif'))


def save_img(url, filename):
    try:
        img = opener.open(url, timeout=5)
        if is_img_type(img):
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img, f)
    except HTTPError as e:
        print('HTTPError at:', url)
        print('Error code:', e.code)
        return False
    except URLError as e:
        print('URLError at:', url)
        print('Reason:', e.reason)
        return False
    except socket.timeout as e:
        print('Failed to reach:', url)
        print('Socket timed out.')
        return False
    except:
        print('Except occured.')
        return False
    else:
        return True


def save_img2(url, filename):
    try:
        # http://stackoverflow.com/questions/2364593/urlretrieve-and-user-agent-python
        # can add headers for `urlretrieve`, but `FancyURLopener` has
        # deprecated since version 3.3.
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        img = urlopen(req, timeout=5)
        if is_img_type(img):
            with open(filename, 'wb') as f:
                f.write(img.read())
    except HTTPError as e:
        # See https://docs.python.org/3.5/howto/urllib2.html
        print('HTTPError at:', url)
        print('Error code:', e.code)
        return False
    except URLError as e:
        print('URLError at:', url)
        print('Reason:', e.reason)
        return False
    except socket.timeout as e:
        print('Failed to reach:', url)
        print('Socket timed out.')
        return False
    except:
        print('Except occured.')
        return False
    else:
        return True


def parse_page(page_num):
    print('--- Parsing page {} ---'.format(page_num))
    page_url = '{}{}/page-{}'.format(base_url, category, page_num)

    while True:
        try:
            html = opener.open(page_url)
            break
        except HTTPError as e:
            if e.code in [500, 501, 502, 503, 504, 505]:
                print('--- Meet 50x error. Sleep for some seconds... ---')
                time.sleep(30)
                continue
            else:
                raise

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', {'class': 'text'})
    for item in items:
        img_tags = item.find_all(
            'a', {'class': 'view_img_link'}) or item.find_all('img')
        if img_tags is None:
            continue

        # One item maybe has several `<a>` or `<img>` tags, e.g. page-2021
        for img_tag in img_tags:
            img_url = img_tag.get('href') or img_tag.get('src')
            img_extension = os.path.splitext(img_url)[1] or '.jpg'

            index = img_tags.index(img_tag)
            if index == 0:
                img_name = '{}{}'.format(item.span.a.get_text(), img_extension)
            else:
                img_name = '{}-{}{}'.format(item.span.a.get_text(),
                                            index + 1, img_extension)
            img_path = os.path.join(category, img_name)
            save_img(img_url, img_path)


def start_download(start_page, end_page):
    os.makedirs(category, exist_ok=True)
    for i in range(start_page, end_page + 1):
        parse_page(i)
        time.sleep(10)


if __name__ == '__main__':
    start_download(2000, 2010)
