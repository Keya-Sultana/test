# Part of Odoo. See LICENSE file for full copyright and licensing details.

# ISO 4217 codes of currencies supported by SSLCOMMERZ
SUPPORTED_CURRENCIES = (
    'AUD',
    'BRL',
    'CAD',
    'CNY',
    'CZK',
    'DKK',
    'EUR',
    'HKD',
    'HUF',
    'ILS',
    'JPY',
    'MYR',
    'MXN',
    'TWD',
    'NZD',
    'NOK',
    'PHP',
    'PLN',
    'GBP',
    'RUB',
    'SGD',
    'SEK',
    'CHF',
    'THB',
    'USD',
)

# Mapping of transaction states to SSLCOMMERZ payment statuses
# See https://developer.paypal.com/docs/api-basics/notifications/ipn/IPNandPDTVariables/
PAYMENT_STATUS_MAPPING = {
    'pending': ('Pending',),
    'done': ('Processed', 'Completed'),
    'cancel': ('Voided', 'Expired'),
}
