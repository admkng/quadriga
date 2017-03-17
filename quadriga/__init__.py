from __future__ import absolute_import, unicode_literals

from quadriga.rest_client import RestClient
from quadriga.exceptions import *


class QuadrigaClient(object):
    """Python client for QuadrigaCX API v2.

    :param api_key: QuadrigaCX API key
    :type api_key: str | unicode
    :param api_secret: QuadrigaCX API secret
    :type api_secret: str | unicode
    :param client_id: QuadrigaCX client ID
    :type client_id: str | unicode
    :param default_book: the default order book
    :type default_book: str | unicode
    """

    # Order books in QuadrigaCX
    order_books = {
        'btc_cad',
        'btc_usd',
        'eth_cad',
        'eth_usd'
    }

    # Major currencies in QuadrigaCX
    currencies = {
        'bitcoin',
        'ether'
    }

    def __init__(self,
                 api_key,
                 api_secret,
                 client_id,
                 default_book='eth_cad'):
        """Initialize the client.

        :param api_key: QuadrigaCX API key
        :type api_key: str | unicode
        :param api_secret: QuadrigaCX API secret
        :type api_secret: str | unicode
        :param client_id: QuadrigaCX client ID
        :type client_id: str | unicode
        :param default_book: the default order book
        :type default_book: str | unicode
        """
        self._rest_client = RestClient(
            api_key=api_key,
            api_secret=api_secret,
            client_id=client_id
        )
        self._default_book = self._verify_book(default_book)

    def _verify_book(self, book):
        """Verify if the order book is valid and return it (or the default).
        
        :param book: the name of the order book
        :type book: str | unicode
        :returns: the name of the order book to use
        :rtype: str | unicode
        :raises InvalidOrderBookError: on invalid order book name
        """
        if book is None:
            return self._default_book
        if book not in self.order_books:
            raise InvalidOrderBookError(
                'Invalid order book "{}" (choose from {})'
                .format(book, list(self.order_books))
            )
        return book

    def _verify_currency(self, currency):
        """Verify if the currency is valid.
        
        :param currency: the major currency (``bitcoin`` or ``ether``)
        :type currency: str | unicode
        :raises InvalidCurrencyError: on invalid currency
        """
        if currency not in self.currencies:
            raise InvalidCurrencyError(
                'Invalid currency "{}" (choose from {})'
                .format(currency, list(self.currencies))
            )

    def get_summary(self, book=None):
        """Return the latest trading summary.

        :param book: the name of the order book
        :type book: str | unicode
        :returns: the trading summary
        :rtype: dict
        """
        self._verify_book(book)
        return self._rest_client.get(
            endpoint='/ticker',
            params={'book': self._verify_book(book)}
        )

    def get_public_orders(self, group=True, book=None):
        """Return all public open orders.

        :param group: group orders with the same price
        :type group: bool
        :param book: the name of the order book
        :type book: str | unicode
        :returns: all public open orders
        :rtype: dict
        """
        return self._rest_client.get(
            endpoint='/order_book',
            params={
                'book': self._verify_book(book),
                'group': 1 if group else 0
            }
        )

    def get_public_trades(self, time='hour', book=None):
        """Return recently completed public trades.

        :param time: the time frame (``minute`` or ``hour``)
        :type time: str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: a list of recent trades
        :rtype: [dict]
        """
        return self._rest_client.get(
            endpoint='/transactions',
            params={
                'book': self._verify_book(book),
                'time': time
            }
        )

    def get_orders(self, book=None):
        """Return a list of user's open orders.

        :param book: the name of the order book
        :type book: str | unicode
        :returns: a list of user's open orders
        :rtype: [dict]
        """
        return self._rest_client.post(
            endpoint='/open_orders',
            payload={'book': self._verify_book(book)}
        )

    def get_trades(self, limit=100, offset=0, sort='desc', book=None):
        """Return a list of user's completed trades.

        :param limit: the maximum number of trades to return (0 == all)
        :type limit: int
        :param offset: the number of trades to skip
        :type offset: int
        :param sort: sort by date and time (``desc`` or ``asc``)
        :type sort: str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: a list of user's completed trades
        :rtype: [dict]
        """
        return self._rest_client.post(
            endpoint='/user_transactions',
            payload={
                'book': self._verify_book(book),
                'limit': limit,
                'offset': offset,
                'sort': sort
            }
        )

    def get_balance(self):
        """Return the user's account balance.

        :returns: the user's account balance
        :rtype: dict
        """
        return self._rest_client.post(endpoint='/balance')

    def buy_market_order(self, amount, book=None):
        """Buy market order.

        :param amount: the amount of major currency to buy at market price
        :type amount: int | float | str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: the total amount of major currency purchased and a set of
            amount/price pairs, one for each order matched in the trade
        :rtype: dict
        """
        return self._rest_client.post(
            endpoint='/buy',
            payload={
                'book': self._verify_book(book),
                'amount': amount,
            }
        )

    def buy_limit_order(self, amount, price, book=None):
        """Buy limit order.

        :param amount: the amount of major currency to buy at limit price
        :type amount: int | float | str | unicode
        :param price: the limit price to buy at
        :type price: int | float | str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: the details of the order placed
        :rtype: dict
        """
        payload = {
            'book': self._verify_book(book),
            'amount': amount,
        }
        if price is not None:
            payload['price'] = price
        return self._rest_client.post(
            endpoint='/buy',
            payload=payload
        )

    def sell_market_order(self, amount, book=None):
        """Sell market order.
        
        :param amount: the amount of major currency to sell at market price
        :type amount: int | float | str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: te total amount of minor currency acquired in sale and a set
            of amount/price pairs, one for each matched in the trade
        :rtype: dict
        """
        return self._rest_client.post(
            endpoint='/sell',
            payload={
                'book': self._verify_book(book),
                'amount': amount
            }
        )

    def sell_limit_order(self, amount, price, book=None):
        """Sell a limit order.

        :param amount: the amount of the major currency to sell at limit price
        :type amount: int | float | str | unicode
        :param price: the limit price to sell at
        :type price: int | float | str | unicode
        :param book: the name of the order book
        :type book: str | unicode
        :returns: the details of the order placed
        :rtype: dict
        """
        payload = {
            'book': self._verify_book(book),
            'amount': amount
        }
        if price is not None:
            payload['price'] = price
        return self._rest_client.post(
            endpoint='/sell',
            payload=payload
        )

    def lookup_order(self, id):
        """Look up an order by its ID

        :param id: the ID of the order to cancel (64 hexadecmial characters)
        :type id: str | unicode
        :returns: ``True`` if order has been found and cancelled
        :rtype: bool
        """
        return self._rest_client.post(
            endpoint='/lookup_order',
            payload={'id': id}
        )

    def cancel_order(self, id):
        """Cancel an open order by its ID.

        :param id: the ID of the order to cancel (64 hexadecmial characters)
        :type id: str | unicode
        :returns: ``True`` if order has been found and cancelled
        :rtype: bool
        """
        return self._rest_client.post(
            endpoint='/cancel_order',
            payload={'id': id}
        )

    def get_deposit_address(self, currency):
        """Return the deposit address for funding on QuadrigaCX.

        :param currency: the major currency (``bitcoin`` or ``ether``)
        :type currency: str | unicode
        :returns: the user's deposit address on 
        :rtype: str | unicode
        :raises InvalidCurrencyError: on unknown currency
        """
        self._verify_currency(currency)

        if currency == 'bitcoin':
            return self._rest_client.post(
                endpoint='/bitcoin_deposit_address'
            )
        elif currency == 'ether':
            return self._rest_client.post(
                endpoint='/ether_deposit_address'
            )

    def withdraw(self, currency, amount, address):
        """Withdraw an amount of currency from QuadrigaCX to user's address.

        :param currency: the major currency (``bitcoin`` or ``ether``)
        :type currency: str | unicode
        :param amount: the amount to withdraw
        :type amount: int | float | str | unicode
        :param address: the address to send the amount to
        :type address: str | unicode
        :raises InvalidCurrencyError: on unknown currency
        """
        self._verify_currency(currency)

        payload = {'address': address, 'amount': amount}
        if currency == 'bitcoin':
            return self._rest_client.post(
                endpoint='/bitcoin_withdrawal',
                payload=payload
            )
        elif currency == 'ether':
            return self._rest_client.post(
                endpoint='/ether_withdrawal',
                payload=payload
            )