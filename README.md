![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)
![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)

# jandan-ooxx

又一个煎蛋妹子图爬虫。

jandan-ooxx is yet another Jandan "ooxx" pictrues crawler, also it can crawl "pic" column.

## Prerequisites

- [Python 3](https://www.python.org/downloads/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## Usage

```bash
$ python3 ooxx.py -h
usage: ooxx.py [-h] [-p] [-s STARTPAGE] [-e ENDPAGE]
               [-t {jpeg,png,gif} [{jpeg,png,gif} ...]] [--ox OX] [--oo OO]
               [--xx XX]

Download images from jandan.net.

optional arguments:
  -h, --help            show this help message and exit
  -p, --pic             download wuliao pics (default: meizi pics)
  -s STARTPAGE, --startpage STARTPAGE
                        set start page (default: 5 pages before end page)
  -e ENDPAGE, --endpage ENDPAGE
                        set end page (default: the last page in the category)
  -t {jpeg,png,gif} [{jpeg,png,gif} ...], --type {jpeg,png,gif} [{jpeg,png,gif} ...]
                        choose image types (default: jpeg, png and gif)
  --ox OX               set how many times oo is more than xx
  --oo OO               minimal oo number
  --xx XX               maximal xx number
```

## License

MIT