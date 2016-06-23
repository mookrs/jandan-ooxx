#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    ooxx
    ~~~~

    Yet another Jandan ooxx pictrues crawler.

    :copyright: (c) 2016 by mookrs.
    :license: MIT.
"""

import argparse
import os
import shutil
import sys
import time
from urllib.request import Request, urlopen, build_opener
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup


opener = build_opener()
opener.addheaders = []
opener.addheaders.append(('User-agent', 'Mozilla/5.0'))
opener.addheaders.append(
    ('Cookie', '458528247=db856X2bSPJdJD3mZ0qNgqHxstlcw%2BC4xtmr%2BPfjKA; jdna=596e6fb28c1bb47f949e65e1ae03f7f5#1466510995815'))

BASE_URL = 'http://jandan.net/'
TIMEOUT = 5
VISIT_INTERVAL = 10


def is_img_type(response):
    """Check if the response from server with image Content-Type header.

    Args:
        response: A http.client.HTTPResponse instance.

    Returns:
        The Boolean value of image Content-Type header checking.
    """
    mime = response.info()['Content-type']
    # Some images include Content-Type `image%2Fjpeg; charset=ISO-8859-1`,
    # thus we can't use `endswith()`.
    return any(img_type in mime for img_type in img_types)


def save_img(url, filename):
    """Download image from URL to disk.

    Args:
        url: An image URL.
        filename: A file name store on disk.

    Returns:
        The Boolean value of saving successfully.
    """
    try:
        # Another way:
        # req = Request(url)
        # req.add_header('User-agent', 'Mozilla/5.0')
        # img = urlopen(req, timeout=TIMEOUT)
        img = opener.open(url, timeout=TIMEOUT)
        if is_img_type(img):
            with open(filename, 'wb') as f:
                shutil.copyfileobj(img, f)
            return True
    except HTTPError as e:
        print('HTTPError at:', url)
        print('Error code:', e.code)
    except URLError as e:
        print('URLError at:', url)
        print('Error reason:', e.reason)
    except Exception as e:
        print('Exception at:', url)
        print('Error details:', e)
    return False


def make_soup(url):
    """Return BeautifulSoup instance base on url.

    Args:
        url: A URL.

    Returns:
        BeautifulSoup instance.
    """
    retry_times = 0
    while True:
        try:
            html = opener.open(url)
            break
        except HTTPError as e:
            if e.code in [500, 501, 502, 503, 504, 505]:
                print('50x error at:', url)
                retry_times += 1
                if retry_times > 5:
                    sys.exit('Exit because of already retrying 5 times.')
                print('Sleep for {} seconds...'.format(VISIT_INTERVAL))
                time.sleep(VISIT_INTERVAL)
                continue
            else:
                print('HTTPError at:', url)
                print('Error code:', e.code)
                sys.exit('Exit because of above error!')
        except Exception as e:
            print('Exception at:', url)
            print('Error details:', e)
            sys.exit('Exit because of above error!')
    return BeautifulSoup(html, 'html.parser')


def parse_page(page_num):
    """Parse page to find images url.

    Args:
        page_num: Page number.
    """
    print('--- Parsing page {} ---'.format(page_num))
    page_url = '{}{}/page-{}'.format(BASE_URL, category, page_num)

    soup = make_soup(page_url)
    items = soup.find_all('div', {'class': 'text'})
    for item in items:
        # `img_tags` could be `[]`.
        img_tags = item.find_all(
            'a', {'class': 'view_img_link'}) or item.find_all('img')

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
    """Download images from start page to end page.

    Args:
        start_page: Start page number.
        end_page: End page number.
    """
    os.makedirs(category, exist_ok=True)
    for i in range(start_page, end_page + 1):
        parse_page(i)
        time.sleep(VISIT_INTERVAL)


def get_start_and_end_page(start_page, end_page, last_page, parser):
    """Check if page numbers user typed in are legal, return start page
    number and end page number tuple.

    Args:
        start_page: Start page number user typed in or default.
        end_page: End page number user typed in or default.
        last_page: The last page number in special category.
        parser: An argparse.ArgumentParser instance.

    Returns:
        Final legal start page number and end page number tuple.
    """
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
        parser.error(
            'startpage in wuliao pics should be bigger than 8000, because Jandan has disabled the access before page-8000!')

    return start_page, end_page


def get_last_page():
    """Get the last page number in special category (ooxx or pic)."""
    url = '{}{}'.format(BASE_URL, category)
    soup = make_soup(url)
    span = soup.find('span', {'class': 'current-comment-page'})
    return int(span.get_text()[1:-1])


def main():
    """Program main function."""
    parser = argparse.ArgumentParser(
        description='Download images from jandan.net.')
    parser.add_argument('-p', '--pic', dest='category', action='store_const',
                        const='pic', default='ooxx',
                        help='download wuliao pics (default: meizi pics)')
    parser.add_argument('-s', '--startpage', type=int,
                        help='set start page (default: 5 pages before end page)')
    parser.add_argument('-e', '--endpage', type=int,
                        help='set end page (default: the last page in the category)')
    parser.add_argument('-o', '--ooxx', type=float,
                        help='set how many times oo is more than xx')
    parser.add_argument('-t', '--type', nargs='+',
                        choices=['jpeg', 'png', 'gif'],
                        default=['jpeg', 'png', 'gif'],
                        help='choose image types (default: jpeg, png and gif)')

    args = parser.parse_args()
    global category, img_types, ooxx
    category = args.category
    img_types = args.type
    ooxx = args.ooxx
    start_page = args.startpage
    end_page = args.endpage

    last_page = get_last_page()
    start_page, end_page = get_start_and_end_page(
        start_page, end_page, last_page, parser)

    start_download(start_page, end_page)


if __name__ == '__main__':
    main()
