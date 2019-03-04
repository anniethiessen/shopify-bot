import time
import json
import random
import requests
import urllib3
from bs4 import BeautifulSoup
from django.db import models


class Address(models.Model):
    address_1 = models.CharField(max_length=100)
    address_2 = models.CharField(blank=True, max_length=100)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    region_code = models.CharField(max_length=10)

    @property
    def full_address(self):
        address = "{}, {}".format(
            self.address_1, self.address_2
        ) if self.address_2 else self.address_1
        return "{}, {}, {}, {}  {}".format(
            address, self.city, self.region, self.country, self.region_code)

    class Meta:
        verbose_name_plural = 'addresses'

    def __str__(self):
        return self.full_address


class Buyer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT)

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class CreditCard(models.Model):
    description = models.CharField(max_length=50)
    card_holder = models.CharField(max_length=60)
    card_number = models.CharField(max_length=16)
    cvv = models.CharField(max_length=5, verbose_name='CVV')
    expiry_month = models.CharField(max_length=2)
    expiry_year = models.CharField(max_length=4)
    billing_address = models.ForeignKey(Address, on_delete=models.PROTECT)

    @property
    def display(self):
        return "************{}".format(self.card_number[12:])

    def __str__(self):
        return "{} ({})".format(self.description, self.display)


class Product(models.Model):
    description = models.CharField(max_length=50)
    site_url = models.URLField()
    keywords = models.TextField(
        help_text="In-quotation and comma-separated list"
    )
    variant = models.CharField(
        blank=True,
        help_text="Specific colour, size, etc",
        max_length=30
    )
    random = models.BooleanField(help_text="Ignore variant if not found")

    def __str__(self):
        return self.description


class Bot(models.Model):
    description = models.CharField(max_length=50)
    buyer = models.ForeignKey(Buyer, on_delete=models.PROTECT)
    credit_card = models.ForeignKey(CreditCard, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    delay = models.PositiveIntegerField()

    def get_keyword_list(self):
        return list(self.product.keywords.split(', '))

    def get_products(self, session):
        link = self.product.site_url  # TO DO plus?
        request = session.get(link, verify=False)
        return json.loads(request.text)['products']

    def filter_products_by_keyword(self, products):
        for product in products:
            keys = 0
            for keyword in self.get_keyword_list():
                if keyword.upper() in product['title'].upper():
                    keys += 1
                if keys == len(self.get_keyword_list()):
                    return product

    def get_product_variant(self, product):
        if self.product.variant in product['title']:
            return str(product['id'])

        if self.product.random:
            variants = []

            for variant in product['variants']:
                variants.append(variant['id'])

            variant = str(random.choice(variants))
            return variant

    def get_product(self, session):
        return self.get_product_variant(
            self.filter_products_by_keyword(
                self.get_products(session)))

    def generate_cart_link(self, product):
        return self.product.site_url + "/cart/" + product + ":1"

    def get_payment_token(self):
        link = "https://elb.deposit.shopifycs.com/sessions"

        payload = {
            "credit_card": {
                "number": self.credit_card.card_number,
                "name": self.credit_card.card_holder,
                "month": self.credit_card.expiry_month,
                "year": self.credit_card.expiry_year,
                "verification_value": self.credit_card.cvv
            }
        }

        request = requests.post(link, json=payload, verify=False)
        return json.loads(request.text)['id']

    def get_shipping(self, session, cookie_jar):
        link = (
            self.product.site_url
            + "//cart/shipping_rates.json?shipping_address[zip]="
            + self.buyer.shipping_address.region_code
            + "&shipping_address[COUNTRY]="
            + self.buyer.shipping_address.country
            + "&shipping_address[PROVINCE]="
            + self.buyer.shipping_address.province
        )
        request = session.get(link, cookies=cookie_jar, verify=False)
        options = json.loads(request.text)
        option = options['shipping_rates'][0]['name'].replace(' ', '%20')
        price = options["shipping_rates"][0]["price"]
        return "shopify-" + option + "-" + price

    def add_to_cart(self, session, product):
        link = self.product.site_url + '/cart/add.js?quantity=1&id=' + product
        return session.get(link, verify=False)

    def submit_customer_info(self, session, cookie_jar):
        buyer = self.buyer
        address = self.buyer.shipping_address
        payload = {
            "utf8": u"\u2713",
            "_method": "patch",
            "authenticity_token": "",
            "previous_step": "contact_information",
            "step": "shipping_method",
            "checkout[EMAIL]": buyer.email,
            "checkout[buyer_accepts_marketing]": "0",
            "checkout[shipping_address][FIRST_NAME]": buyer.first_name,
            "checkout[shipping_address][LAST_NAME]": buyer.last_name,
            "checkout[shipping_address][company]": "",
            "checkout[shipping_address][ADDRESS_1]": address.address_1,
            "checkout[shipping_address][ADDRESS_2]": address.address_2,
            "checkout[shipping_address][CITY]": address.city,
            "checkout[shipping_address][COUNTRY]": address.country,
            "checkout[shipping_address][PROVINCE]": address.region,
            "checkout[shipping_address][zip]": address.region_code,
            "checkout[shipping_address][PHONE_NUMBER]": buyer.phone_number,
            "checkout[remember_me]": "0",
            "checkout[client_details][browser_width]": "1710",
            "checkout[client_details][browser_height]": "1289",
            "checkout[client_details][javascript_enabled]": "1",
            "button": ""
        }

        link = self.product.site_url + "//checkout.json"
        response = session.get(link, cookies=cookie_jar, verify=False)

        link = response.url
        checkout_link = link

        response = session.post(
            link, cookies=cookie_jar, data=payload, verify=False)

        return response, checkout_link

    def perform_task(self):
        session = requests.session()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        product = None

        while product is None:
            product = self.get_product(session)
            if product is None:
                time.sleep(self.delay)

        cart_link = self.generate_cart_link(product)
        request = self.add_to_cart(session, product)
        cookies = request.cookies
        payment_token = self.get_payment_token()
        request, checkout_link = self.submit_customer_info(session, cookies)
        ship = self.get_shipping(cookies)
        link = checkout_link + "?step=payment_method"
        request = session.get(link, cookies=cookies, verify=False)
        bs = BeautifulSoup(request.text, "html.parser")
        div = bs.find("div", {"class": "radio__input"})
        print(div)

        gateway = ""
        values = str(div.input).split('"')
        for value in values:
            if value.isnumeric():
                gateway = value
                break

        link = checkout_link
        buyer = self.buyer
        address = self.credit_card.billing_address
        payload = {
            "utf8": u"\u2713",
            "_method": "patch",
            "authenticity_token": "",
            "previous_step": "payment_method",
            "step": "",
            "s": payment_token,
            "checkout[payment_gateway]": gateway,
            "checkout[credit_card][vault]": "false",
            "checkout[different_billing_address]": "true",
            "checkout[billing_address][FIRST_NAME]": buyer.first_name,
            "checkout[billing_address][LAST_NAME]": buyer.last_name,
            "checkout[billing_address][ADDRESS_1]": address.address_1,
            "checkout[billing_address][ADDRESS_2]": address.address_2,
            "checkout[billing_address][CITY]": address.city,
            "checkout[billing_address][COUNTRY]": address.country,
            "checkout[billing_address][PROVINCE]": address.region,
            "checkout[billing_address][zip]": address.region_code,
            "checkout[billing_address][PHONE_NUMBER]": buyer.phone_number,
            "checkout[shipping_rate][id]": ship,
            "complete": "1",
            "checkout[client_details][browser_width]": str(
                random.randint(1000, 2000)),
            "checkout[client_details][browser_height]": str(
                random.randint(1000, 2000)),
            "checkout[client_details][javascript_enabled]": "1",
            "g-recaptcha-repsonse": "",
            "button": ""
        }

        session.post(link, cookies=cookies, data=payload, verify=False)

    def __str__(self):
        return self.description
