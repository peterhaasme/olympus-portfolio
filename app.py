# app.py
# enter wallet address into web app -> generate wonderland portfolio value

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from dotenv import load_dotenv
import json
import os
import requests
from token_info import tokens
from web3 import Web3

# INSTANCES ###

# Dash instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

# import nomics API key from .env
load_dotenv()
NOMICS_API_KEY = os.getenv('NOMICS_API_KEY')

# create Infura connection
INFURA_URL = os.getenv('INFURA_URL')
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# LAYOUT ###
# Layout components
wallet_input = [
    dbc.Label(
        children=html.H5('Enter Wallet Address'),
        html_for='wallet_input',
        width=3,
    ),
    dbc.Col(
        children=[
            dbc.Input(
                id='wallet_input',
                placeholder='Ex: 0x104d5ebb38af1ae5eb469b86922d1f10808eb35f',
                type='text',
                autofocus=True,
                class_name=''
            ),
            dbc.FormFeedback(
                children="Valid address",
                type="valid"
            ),
            dbc.FormFeedback(
                children="Invalid address",
                type="invalid",
            ),
        ],
        width=9
    )
]

ohm_balance = [
    dbc.Col(
        children='OHM balance',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='ohm_balance',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='OHM price',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='ohm_price',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='OHM value',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='ohm_value',
        children='',
        width=6,
        lg=2
    )
]

sohm_balance = [
    dbc.Col(
        children='sOHM balance',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='sohm_balance',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='sOHM price',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='sohm_price',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='sOHM value',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='sohm_value',
        children='',
        width=6,
        lg=2
    )
]

wsohm_balance = [
    dbc.Col(
        children='wsOHM balance',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='wsohm_balance',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='wsOHM price',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='wsohm_price',
        children='',
        width=6,
        lg=2
    ),
    dbc.Col(
        children='wsOHM value',
        width=6,
        lg=2
    ),
    dbc.Col(
        id='wsohm_value',
        children='',
        width=6,
        lg=2
    )
]

total_value = [
    dbc.Col(
        id='total_value',
        children=''
    )
]

interval = dcc.Interval(
            id='price_interval',
            interval=60000,  # 60000ms=1min
            n_intervals=0
        )

credits = dbc.Col(
    dcc.Markdown('''
        ##### Credits
        Price Data - [Nomics](https://p.nomics.com/cryptocurrency-bitcoin-api)
    ''')
)

notes = dbc.Col(
    dcc.Markdown('''
        ##### Notes
        - Test addresses:
            - OHM -> 0x12a8141ede9e39343e0aa2362762f6f53d10f292
            - sOHM V2 -> 0x71deff8dd6258fdade87db2c012d4a22bb0a527f
            - wsOHM (ETH Mainnet)-> 0x242489ccfe7d7081d4b2778931a6d6c0c1fb3806
            - gOHM (Ethereum)-> 0x5de56faec0190f6ff9fae65deb4dab4b1c5d1c73
        - Prices refresh every 60s
        - sOHM v2 balance only
        - [Github](https://github.com/peterhaasme/olympus-portfolio)
        - Coming soon: bonding rewards balance
    ''')
)

# Page Layout
app.layout = dbc.Container([
    dbc.Row(
        children=dbc.Col(html.H1('Olympus Portfolio Balance')),
        class_name='text-center mt-3'
    ),
    dbc.Row(
        children=wallet_input,
        class_name='my-4'
    ),
    dbc.Row(
        children=ohm_balance,
        class_name='text-center h5 my-3 p-3 bg-light rounded-3'
    ),
    dbc.Row(
        children=sohm_balance,
        class_name='text-center h5 my-3 p-3 bg-light rounded-3'
    ),
    dbc.Row(
        children=wsohm_balance,
        class_name='text-center h5 my-3 p-3 bg-light rounded-3'
    ),
    dbc.Row(
        children=total_value,
        class_name='text-center text-light h4 my-3 p-3 bg-info rounded-3'
    ),
    dbc.Row(
        children=credits,
        class_name=''
    ),
    dbc.Row(
        children=notes,
        class_name=''
    ),
    interval
])

# CALLBACKS ###


@app.callback(
    Output(
        component_id="wallet_input",
        component_property="valid"
    ),
    Output(
        component_id="wallet_input",
        component_property="invalid"
    ),
    Input(
        component_id="wallet_input",
        component_property="value"
    ),
)
def check_validity(value):
    ''' Validate wallet address
    '''
    if value:
        return Web3.isAddress(value), not Web3.isAddress(value)
    return False, False


def get_token_balance(token, wal_addr, currency):
    ''' Get token balance in a wallet address

    Keyword arguments:
    token - token symbol
    wal_addr - wallet address
    currency - denomination https://web3py.readthedocs.io/en/stable/examples.html?#converting-currency-denominations
    '''
    ctrct_addr = tokens[token]['address']
    checksum_address = web3.toChecksumAddress(ctrct_addr)
    wal_checksum = web3.toChecksumAddress(wal_addr)
    abi = tokens[token]['abi']
    abi = json.loads(abi)
    contract = web3.eth.contract(address=checksum_address, abi=abi)
    balance_gwei = contract.functions.balanceOf(wal_checksum).call()
    balance = web3.fromWei(balance_gwei, currency)
    return balance


@app.callback(
    Output(
        component_id='ohm_balance',
        component_property='children'
    ),
    Output(
        component_id='sohm_balance',
        component_property='children'
    ),
    Output(
        component_id='wsohm_balance',
        component_property='children'
    ),
    Output(
        component_id='ohm_price',
        component_property='children'
    ),
    Output(
        component_id='sohm_price',
        component_property='children'
    ),
    Output(
        component_id='wsohm_price',
        component_property='children'
    ),
    Output(
        component_id='ohm_value',
        component_property='children'
    ),
    Output(
        component_id='sohm_value',
        component_property='children'
    ),
    Output(
        component_id='wsohm_value',
        component_property='children'
    ),
    Output(
        component_id='total_value',
        component_property='children'
    ),
    Input(
        component_id='wallet_input',
        component_property='valid'
    ),
    Input(
        component_id='wallet_input',
        component_property='value'
    ),
    Input(
        component_id='price_interval',
        component_property='n_intervals'
    ),
)
def display_balances(valid, value, n):
    ''' Get token balances and prices. Compute indiv and total value.
    '''
    # If the wallet address is valid retrieve balances
    if valid:
        ohm_bal = get_token_balance(
            token='ohm',
            wal_addr=value,
            currency='gwei'
        )
        sohm_bal = get_token_balance(
            token='sohm',
            wal_addr=value,
            currency='gwei'
        )
        wsohm_bal = get_token_balance(
            token='wsohm',
            wal_addr=value,
            currency='ether'
        )
        ohm_bal_show = round(ohm_bal, 2)
        sohm_bal_show = round(sohm_bal, 2)
        wsohm_bal_show = round(wsohm_bal, 5)
    else:
        ohm_bal_show = '0'
        sohm_bal_show = '0'
        wsohm_bal_show = '0'

    # Get token prices. sOHM = OHM
    url = 'https://api.nomics.com/v1/currencies/ticker'
    payload = {
        'key': NOMICS_API_KEY,
        'ids': 'OHM,WSOHM'
    }
    response = requests.get(url, params=payload)
    ohm_price = response.json()[0]['price']
    ohm_price_show = f'${float(ohm_price):,.2f}'
    wsohm_price = response.json()[1]['price']
    wsohm_price_show = f'${float(wsohm_price):,.2f}'

    # If the wallet address is valid compute values
    if valid:
        ohm_value = float(ohm_bal) * float(ohm_price)
        ohm_value_show = f'${ohm_value:,.2f}'
        sohm_value = float(sohm_bal) * float(ohm_price)
        sohm_value_show = f'${sohm_value:,.2f}'
        wsohm_value = float(wsohm_bal) * float(wsohm_price)
        wsohm_value_show = f'${wsohm_value:,.2f}'
        total_value = ohm_value + sohm_value + wsohm_value
        total_value_show = f'Total Value = ${total_value:,.2f}'
    else:
        ohm_value_show = '$0'
        sohm_value_show = '$0'
        wsohm_value_show = '$0'
        total_value_show = 'Total Value = $0'

    # Return values
    return (ohm_bal_show, sohm_bal_show, wsohm_bal_show, ohm_price_show,
            ohm_price_show, wsohm_price_show, ohm_value_show, sohm_value_show,
            wsohm_value_show, total_value_show)
