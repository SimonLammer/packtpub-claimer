import requests, json, base64
from lxml import html

with open('config.json') as json_data:
	config = json.load(json_data)
url = 'https://www.packtpub.com'
s = requests.Session()
headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

def do_get(url_suffix = ""):
	global r
	global tree
	r = s.get(url + url_suffix, headers=headers)
	tree = html.fromstring(r.content)

def get_last_ebook_name():
	do_get('/account/my-ebooks')
	return tree.xpath('//div[@id = "product-account-list"]/div[1]//div[contains(@class, "title")]/text()')[0].strip()

do_get()
form_xpath = '//form[@id = "packt-user-login-form"]'
hidden_inputs = tree.xpath(form_xpath + '//input[@type = "hidden"]')
payload = {
	'email': config['mail'],
	'password': base64.b64decode(config['password']),
}
for hidden_input in hidden_inputs:
	payload[hidden_input.name] = hidden_input.value

r = s.post(url, data=payload, headers=headers)
if r.ok:
	print "Login as " + config['mail'] + " successful."

last_ebook_name = get_last_ebook_name()
do_get('/packt/offers/free-learning')
claim_href = tree.xpath('//div[@id = "deal-of-the-day"]//div[contains(@class, "dotd-main-book-summary")]//a/@href')[0]
do_get(claim_href)
new_last_ebook_name = get_last_ebook_name()
if last_ebook_name != new_last_ebook_name:
	print 'Claimed new ebook: ' + new_last_ebook_name
