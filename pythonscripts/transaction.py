#!/usr/bin/python
import subprocess
import json
import hashlib
import base64

# Cardano CLI global - Change according to your environment, eg "cardano-cli" if you have it in path
# IMPORTANT:
# If you are using mainnet, do a find/replace for all: '--testnet-magic', '1097911063'   and change to simply: '--mainnet'
# Script Assumes CARDANO_NODE_SOCKET_PATH=/path/to/wherever/is/the/node.socket is set in your system path, if not do so before running

cardano_cli = "/home/ulla/node/result/alonzo-purple/cardano-cli/bin/cardano-cli"

def get_address_from_vkey(vkey_path):
    func = [
        cardano_cli,
        'address',
        'build',
        '--testnet-magic', '1097911063',
        '--payment-verification-key-file',
        vkey_path
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print('Address: ', p)
    return p

def get_token_identifier(policy_id, token_name):
    """
    Takes the blake2b hash of the concat of the policy ID and token name.
    """
    hex_name = base64.b16encode(bytes(str(token_name).encode('utf-8'))).lower()
    b_policy_id = bytes(str(policy_id).encode('utf-8'))
    concat = b_policy_id+hex_name
    print('Hex Name: ', hex_name)
    print('Policy ID: ', b_policy_id)
    h = hashlib.blake2b(digest_size=20)
    h.update(concat)
    return h.hexdigest()

def estimate_trx_fee(tmp):
    func = [
        cardano_cli,
        'transaction',
        'calculate-min-fee',
        '--tx-body-file',
        tmp+'tx.draft',
        '--testnet-magic', '1097911063',
        '--protocol-params-file',
        tmp+ 'protocol.json',
        '--tx-in-count', '5',
        '--tx-out-count', '5',
        '--witness-count', '2'
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print('Hash: ', p)


def get_policy_id(file):
    func = [
        cardano_cli,
        'transaction',
        'policyid',
        '--script-file',
        file
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print('Value:', file)
    print('Hash: ', p)
    return p


def get_hash_value(value):
    func = [
        cardano_cli,
        'transaction',
        'hash-script-data',
        '--script-data-value',
        value
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print('Value:', value)
    print('Hash: ', p)
    return p


def get_script_address(script):
    func = [
        cardano_cli,
        'address',
        'build',
        '--payment-script-file',
        script,
        '--testnet-magic', '1097911063',
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print('ADDRESS: ', p)
    func = [
        cardano_cli,
        'query',
        'utxo',
        '--address',
        p,
        '--testnet-magic', '1097911063',
    ]
    a = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    print(a)
    return p



def asset_change(tmp, currencies, wallet_addr, exclude="", flag=True):
    if len(currencies) > 1:
        token_string = asset_utxo_string(currencies, exclude, flag)
        if len(token_string) != 0:
            minimum_cost = calculate_min_value(tmp, token_string)
            return ['--tx-out', wallet_addr+"+"+str(minimum_cost)+"+"+token_string]
        else:
            return []
    else:
        return []

def calculate_min_value(tmp, token_string):
    func = [
        cardano_cli,
        'transaction',
        'calculate-min-value',
        '--protocol-params-file',
        tmp + 'protocol.json',
        '--multi-asset',
        token_string
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    # Over assume minimum cost to send assets if protocol can not calculate required ada.
    try:
        p.split(' ')[1].replace('\n', '')
    except IndexError:
        p = 2000000
    return p

def asset_utxo_string(wallet_currency, exclude=[], flag=True):
    token_string = ''
    for token in wallet_currency:
        # lovelace will be auto accounted for using --change-address
        if token == 'lovelace':
            continue
        for asset in wallet_currency[token]:
            print(token, asset)
            if len(exclude) != 0:
                if flag is True:
                    if asset not in exclude and token not in exclude:
                        token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
                else:
                    if asset in exclude and token in exclude:
                        token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
            else:
                token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
    return token_string[:-1]

def balance(wallet_addr):
    """
    Prints the current wallet address balance to the terminal.
    """
    func = [
        cardano_cli,
        'query',
        'utxo',
        '--cardano-mode',
        '--testnet-magic', '1097911063',
        '--address',
        wallet_addr
    ]
    p = subprocess.Popen(func)
    p.communicate()


def version():
    """
    Current Cardano CLI Version
    """
    func = [
        cardano_cli,
        '--version'
    ]
    p = subprocess.Popen(func)
    p.communicate()


def delete_contents(tmp):
    from os import remove
    from glob import glob
    files = glob(tmp+'*')
    for f in files:
        remove(f)

def protocol(tmp):
    """
    Query the protocol parameters and save to the tmp folder.
    """
    func = [
        cardano_cli,
        'query',
        'protocol-parameters',
        '--testnet-magic', '1097911063',
        '--out-file',
        tmp+'protocol.json'
    ]
    p = subprocess.Popen(func)
    p.communicate()


def utxo(token_wallet, tmp, file_name):
    """
    Query the utxo from the wallet address and save to the tmp folder.
    """
    func = [
        cardano_cli,
        'query',
        'utxo',
        '--testnet-magic', '1097911063',
        '--address',
        token_wallet,
        '--out-file',
        tmp+file_name
    ]
    p = subprocess.Popen(func)
    p.communicate()


def txin(tmp, file_name, collateral=2000000, spendable=False, allowed_datum=''):
    """
    Construct the txin string, out going addresses list, token amount object,
    and the number of inputs inside the current wallet state.
    """
    txin_list = []
    data_list = {}
    txincollat_list = []
    amount = {}
    counter = 0
    with open(tmp+file_name, "r") as read_content:
        data = json.load(read_content)
    # store all tokens from utxo
    for d in data:
        # Store all the data
        try:
            data_list[d] = data[d]['data']
        except KeyError:
            pass
        # Get the currency
        for currency in data[d]['value']:
            # Check for the ADA collateral
            if currency == 'lovelace':
                if data[d]['value'][currency] == collateral:
                    txincollat_list.append('--tx-in-collateral')
                    txincollat_list.append(d)
            # Get all the currencies
            if currency in amount.keys():
                if currency == 'lovelace':
                    amount[currency] += data[d]['value'][currency]
                else:
                    if spendable is True:
                        pass
                    else:
                        for asset in data[d]['value'][currency]:
                            try:
                                amount[currency][asset] += data[d]['value'][currency][asset]
                            except KeyError:
                                amount[currency][asset] = data[d]['value'][currency][asset]
            else:
                if currency == 'lovelace':
                    amount[currency] = data[d]['value'][currency]
                else:
                    if spendable is True:
                        try:
                            if data[d]['data'] == allowed_datum:
                                amount[currency] = data[d]['value'][currency]
                        except KeyError:
                            pass
                    else:
                        amount[currency] = data[d]['value'][currency]
               
        # Build txin string
        txin_list.append('--tx-in')
        txin_list.append(d)
        # Increment the counter
        counter += 1
    if counter == 1:
        return txin_list, txincollat_list, amount, False, data_list
    return txin_list, txincollat_list, amount, True, data_list


def tip(tmp):
    """
    Query the tip of the blockchain then save to a file.
    """
    delta = 2000 # This is probably good
    func = [
        cardano_cli,
        'query',
        'tip',
        '--testnet-magic', '1097911063',
        '--out-file',
        tmp+'tip.json'
    ]
    p = subprocess.Popen(func)
    p.communicate()
    with open(tmp+"tip.json", "r") as read_content:
        data = json.load(read_content)
    print(data)
    return int(data['slot']), int(data['slot']) + delta, int(data['block'])


def build(tmp, change_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data):
    """
    Build a transaction and save the fileName into the tmp folder.
    """
    func = [
        cardano_cli,
        'transaction',
        'build',
        '--alonzo-era',
        '--cardano-mode',
        '--testnet-magic', '1097911063',
        '--protocol-params-file',
        tmp+'protocol.json',
        '--change-address',
        change_addr,
        '--invalid-hereafter',
        str(final_tip),
        '--out-file',
        tmp+'tx.draft'
    ]
    func += utxo_in
    func += utxo_col
    func += utxo_out
    func += additional_data
    print("\nCheck Transaction Details Before Proceeding!")
    print("\n-----------------TX Built--------------------\n")
    print(func)
    print("\n-------------------End------------------\n")
    p = subprocess.Popen(func)
    p.communicate()


def sign(tmp, signers):
    """
    Sign a transaction with the payment keys.
    """
    func = [
        cardano_cli,
        'transaction',
        'sign',
        '--tx-body-file',
        tmp+'tx.draft',
        '--testnet-magic', '1097911063',
        '--tx-file',
        tmp+'tx.signed'
    ]
    func += signers
    p = subprocess.Popen(func)
    p.communicate()


def submit(tmp):
    """
    Submit the transaction to the blockchain.
    """
    func = [
        cardano_cli,
        'transaction',
        'submit',
        '--cardano-mode',
        '--testnet-magic', '1097911063',
        '--tx-file',
        tmp+'tx.signed',
    ]
    p = subprocess.Popen(func)
    p.communicate()
