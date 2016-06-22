# -*- coding: utf-8 -*-
# Useful links:
# http://stackoverflow.com/questions/2364593/urlretrieve-and-user-agent-python
# https://docs.python.org/3.5/howto/urllib2.html
import argparse
import os
import shutil
import socket
import time
from urllib.request import Request, urlopen, build_opener
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup


opener = build_opener()
opener.addheaders = []
opener.addheaders.append(('User-agent', 'Mozilla/5.0'))
opener.addheaders.append(
    ('Cookie', '458528247=db856X2bSPJdJD3mZ0qNgqHxstlcw%2BC4xtmr%2BPfjKA; jdna=596e6fb28c1bb47f949e65e1ae03f7f5#1466510995815'))

base_url = 'http://jandan.net/'
timeout = 5

def is_img_type(response):
    mime = response.info()['Content-type']
    # Some images include Content-Type `image%2Fjpeg; charset=ISO-8859-1`,
    # thus we can't use `endswith()`.
    return any(img_type in mime for img_type in img_types)


def save_img(url, filename):
    try:
        # Another way:
        # req = Request(url)
        # req.add_header('User-agent', 'Mozilla/5.0')
        # img = urlopen(req, timeout=timeout)
        img = opener.open(url, timeout=timeout)
        if is_img_type(img):
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img, f)
            return True
    except HTTPError as e:
        print('HTTPError at:', url)
        print('Error code:', e.code)
    except URLError as e:
        print('URLError at:', url)
        print('Reason:', e.reason)
    except socket.timeout as e:
        print('Failed to reach:', url)
        print('Socket timed out.')
    except:
        print('Exception occured.')
    return False


def make_soup(url):
    while True:
        try:
            html = opener.open(url)
            break
        except HTTPError as e:
            if e.code in [500, 501, 502, 503, 504, 505]:
                print('--- Meet 50x error. Sleep for some seconds... ---')
                time.sleep(30)
                continue
            else:
                # TimeoutError HTTP Error 403
                raise
    return BeautifulSoup(html, 'html.parser')


def parse_page(page_num):
    print('--- Parsing page {} ---'.format(page_num))
    page_url = '{}{}/page-{}'.format(base_url, category, page_num)

    soup = make_soup(page_url)
    items = soup.find_all('div', {'class': 'text'})
    for item in items:
        img_tags = item.find_all(
            'a', {'class': 'view_img_link'}) or item.find_all('img')

        # `img_tags` could be `[]`.
        # An item maybe has several `<a>` or `<img>` tags, e.g. page-2021.
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


def get_start_and_end_page(start_page, end_page, last_page):
    if start_page is not None and end_page is not None:
        if start_page > end_page:
            parser.error('startpage shouldn\'t be bigger than endpage!')
        elif start_page <= 0 or start_page > last_page:
            parser.error('startpage out of range!')
        elif end_page <= 0 or end_page > last_page:
            parser.error('endpage out of range!')
    elif start_page is None and end_page is not None:
        if end_page <= 0 or end_page > last_page:
            parser.error('endpage out of range!')
        start_page = end_page - 5 if end_page > 5 else 1
    elif start_page is not None and end_page is None:
        if start_page <= 0 or start_page > last_page:
            parser.error('startpage out of range!')
        end_page = last_page
    else:
        end_page = last_page
        start_page = end_page - 5

    # Wuliao pics only can access after page 8000.
    if category == 'pic' and start_page < 8000:
        parser.error('startpage in wuliao pics should be bigger than 8000, because jandan has disabled the access of pages before 8000!')

    return start_page, end_page


def get_last_page():
    url = '{}{}'.format(base_url, category)
    soup = make_soup(url)
    span = soup.find('span', {'class': 'current-comment-page'})
    return int(span.get_text()[1:-1])


def main():
    parser = argparse.ArgumentParser(
        description='Download images from jandan.net.')
    parser.add_argument('-p', '--pic', dest='category', action='store_const',
                        const='pic', default='ooxx',
                        help='download wuliao pics (default: meizi pics)')
    parser.add_argument('-s', '--startpage', type=int,
                        help='set start page (default: 5 pages before end page)')
    parser.add_argument('-e', '--endpage', type=int,
                        help='set end page (default: the last page in the category)')
    parser.add_argument('-t', '--type', nargs='+',
                        choices=['jpeg', 'png', 'gif'],
                        default=['jpeg', 'png', 'gif'],
                        help='choose image types (default: jpeg, png and gif)')

    args = parser.parse_args()
    global category, img_types
    category = args.category
    img_types = args.type
    start_page = args.startpage
    end_page = args.endpage

    last_page = get_last_page()
    start_page, end_page = get_start_and_end_page(
        start_page, end_page, last_page)

    start_download(start_page, end_page)


if __name__ == '__main__':
    main()
