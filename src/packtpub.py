import requests
from lxml import html

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

class PacktpubController(object):
	url = 'https://www.packtpub.com'

	def __init__(self):
		self.session = requests.Session()

	def __do_get(self, url_suffix = "", allow_redirects=True):
		global headers
		self.response = self.session.get(PacktpubController.url + url_suffix, headers=headers, allow_redirects=allow_redirects)
		if self.response.status_code == 200:
			self.tree = html.fromstring(self.response.content)
			return True
		else:
			return False

	def login(self, email, password):
		global headers
		if not self.__do_get():
			return False
		hidden_inputs = self.tree.xpath('//form[@id = "packt-user-login-form"]//input[@type = "hidden"]')
		payload = {
			'email': email,
			'password': password,
		}
		for hidden_input in hidden_inputs:
			payload[hidden_input.name] = hidden_input.value
		self.session.post(PacktpubController.url, data=payload, headers=headers)
		return self.__do_get('/account', False)

	def get_last_ebook_name(self):
		if self.__do_get('/account/my-ebooks'):
			books = self.tree.xpath('//div[@id = "product-account-list"]/div[1]//div[contains(@class, "title")]/text()')
			if len(books) == 0:
				return ""
			else:
				return books[0].strip()
		else:
			return False

	def claim_free_ebook(self):
		last_ebook_name = self.get_last_ebook_name()
		if not self.__do_get('/packt/offers/free-learning'):
			return False
		claim_href = self.tree.xpath('//div[@id = "deal-of-the-day"]//div[contains(@class, "dotd-main-book-summary")]//a/@href')[0]
		if not self.__do_get(claim_href):
			return False
		new_last_ebook_name = self.get_last_ebook_name()
		if not new_last_ebook_name:
			return False
		elif last_ebook_name == new_last_ebook_name:
			return True
		else:
			return new_last_ebook_name
