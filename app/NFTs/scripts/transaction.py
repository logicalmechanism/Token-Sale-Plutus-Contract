#!/usr/bin/python
"""
Assumes the socket is on path.

If socket not on path then directly point towards with

CARDANO_NODE_SOCKET_PATH=/path/to/the/node.socket 

before using the python scripts.

"""
import subprocess
import json
import hashlib
import base64
import os

def get_key_hash(vkey_path):
    func = [
        'cardano-cli', 
        'address', 
        'key-hash', 
        '--payment-verification-key-file', 
        vkey_path
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def get_datum_hash(policy_id, token_name):
    fingerprint = get_token_identifier(policy_id, token_name) # Not real fingerprint but works
    datum_hash  = get_hash_value('"{}"'.format(fingerprint)).replace('\n', '')
    return datum_hash


def whichnet(flag):
    """
    Check if the flag is bool then proceed to determine which net to use. If
    the flag is not a boolean then just return the mainnet.
    """
    if isinstance(flag, bool):
        if flag is True:
            return ['--mainnet']
        else:
            return ['--testnet-magic', '1097911063']
    else:
        return ['--mainnet']


def get_address_from_vkey(vkey_path, flag=True):
    func = [
        'cardano-cli',
        'address',
        'build',
        '--payment-verification-key-file',
        vkey_path
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def get_token_identifier(policy_id, token_name):
    """
    Takes the blake2b hash of the concat of the policy ID and token name.
    """
    hex_name = base64.b16encode(bytes(str(token_name).encode('utf-8'))).lower()
    b_policy_id = bytes(str(policy_id).encode('utf-8'))
    concat = b_policy_id+hex_name
    h = hashlib.blake2b(digest_size=20)
    h.update(concat)
    return h.hexdigest()


def estimate_trx_fee(tmp, flag=True):
    func = [
        'cardano-cli',
        'transaction',
        'calculate-min-fee',
        '--tx-body-file',
        tmp+'tx.draft',
        '--protocol-params-file',
        tmp+ 'protocol.json',
        '--tx-in-count', '5',
        '--tx-out-count', '5',
        '--witness-count', '2'
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')


def get_policy_id(file):
    func = [
        'cardano-cli',
        'transaction',
        'policyid',
        '--script-file',
        file
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def get_hash_value(value):
    func = [
        'cardano-cli',
        'transaction',
        'hash-script-data',
        '--script-data-value',
        value
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def get_script_address(script, flag=True):
    func = [
        'cardano-cli',
        'address',
        'build',
        '--payment-script-file',
        script,
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p



def asset_change(tmp, currencies, wallet_addr, exclude=[], ex_flag=True):
    if len(currencies) > 1:
        token_string = asset_utxo_string(currencies, exclude, ex_flag)
        if len(token_string) != 0:
            minimum_cost = calculate_min_value(tmp, token_string)
            return ['--tx-out', wallet_addr+"+"+str(minimum_cost)+"+"+token_string]
        else:
            return []
    else:
        return []


def calculate_min_value(tmp, token_string):
    func = [
        'cardano-cli',
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
        p = p.replace('\n','').split(' ')[1]
    except IndexError:
        p = 6000000
    return p


def asset_utxo_string(wallet_currency, exclude=[], ex_flag=True):
    token_string = ''
    for token in wallet_currency:
        # lovelace will be auto accounted for using --change-address
        if token == 'lovelace':
            continue
        for asset in wallet_currency[token]:
            # print(token, asset)
            if len(exclude) != 0:
                # Exclusion flag
                if ex_flag is True:
                    if asset not in exclude and token not in exclude:
                        token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
                    if asset not in exclude and token in exclude:
                        token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
                    # if asset not in exclude and token in exclude:
                    #     token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
                else:
                    if asset in exclude and token in exclude:
                        token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
            else:
                token_string += str(wallet_currency[token][asset]) + ' ' + token + '.' + asset + '+'
    return token_string[:-1]


def balance(wallet_addr, flag=True):
    """
    Prints the current wallet address balance to the terminal.
    """
    func = [
        'cardano-cli',
        'query',
        'utxo',
        '--cardano-mode',
        '--address',
        wallet_addr
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()


def version():
    """
    Current Cardano CLI Version
    """
    func = [
        'cardano-cli',
        '--version'
    ]
    p = subprocess.Popen(func)
    p.communicate()
    exit_code = p.wait()
    print(exit_code)


def delete_contents(tmp):
    from os import remove
    from glob import glob
    files = glob(tmp+'*')
    for f in files:
        remove(f)

def protocol(tmp, flag=True):
    """
    Query the protocol parameters and save to the tmp folder.
    """
    func = [
        'cardano-cli',
        'query',
        'protocol-parameters',
        '--out-file',
        tmp+'protocol.json'
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()
    p.wait()

    # force minUTxOValue to exist
    filename = tmp+'protocol.json'
    with open(filename, 'r') as f:
        data = json.load(f)
        data['minUTxOValue'] = 1200000 # <--- add `id` value.

    os.remove(filename)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def utxo(token_wallet, tmp, file_name, flag=True):
    """
    Query the utxo from the wallet address and save to the tmp folder.
    """
    func = [
        'cardano-cli',
        'query',
        'utxo',
        '--address',
        token_wallet,
        '--out-file',
        tmp+file_name
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()


def txin(tmp, file_name, collateral=1000000, spendable=False, allowed_datum=''):
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


def tip(tmp, flag=True):
    """
    Query the tip of the blockchain then save to a file.
    """
    delta = 20000 # This is probably good
    func = [
        'cardano-cli',
        'query',
        'tip',
        '--out-file',
        tmp+'tip.json'
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()
    try:
        with open(tmp+"tip.json", "r") as read_content:
            data = json.load(read_content)
    except FileNotFoundError:
        return 0, 0, 0
    return int(data['slot']), int(data['slot']) + delta, int(data['block'])


def build(tmp, change_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data, flag=True):
    """
    Build a transaction and save the fileName into the tmp folder.
    """
    func = [
        'cardano-cli',
        'transaction',
        'build',
        '--alonzo-era',
        '--cardano-mode',
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
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()
    exit_code = p.wait()
    return exit_code


def sign(tmp, signers, flag=True):
    """
    Sign a transaction with the payment keys.
    """
    func = [
        'cardano-cli',
        'transaction',
        'sign',
        '--tx-body-file',
        tmp+'tx.draft',
        '--tx-file',
        tmp+'tx.signed'
    ]
    func += signers
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()


def submit(tmp, flag=True):
    """
    Submit the transaction to the blockchain.
    """
    func = [
        'cardano-cli',
        'transaction',
        'submit',
        '--cardano-mode',
        '--tx-file',
        tmp+'tx.signed',
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()
