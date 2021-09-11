"""
Running this file will update the local db with available tokens inside all 
the verified smart contracts. The database will be used to provide token
information to the frontend.
"""
import sqlite3
import os
import subprocess
import json

# Point to the socket
# CARDANO_NODE_SOCKET_PATH=/home/cardano/Documents/Work/testnet/cardano-node/result/testnet/state-node-testnet/node.socket
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


def current_block(flag=True):
    """
    Query the tip of the blockchain then save to a file.
    """
    func = [
        'cardano-cli',
        'query',
        'tip',
        '--out-file',
        'tmp/tip.json'
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()
    with open("tmp/tip.json", "r") as read_content:
        data = json.load(read_content)
    # print('\nblock', data)
    return int(data['block'])


def get_key_hash(vkey_path):
    func = [
        'cardano-cli', 
        'address', 
        'key-hash', 
        '--payment-verification-key-file', 
        vkey_path
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    # print('Hash: ', p)
    return p


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


def txin():
    """
    Construct the txin string, out going addresses list, token amount object,
    and the number of inputs inside the current wallet state.
    """
    amount = {}
    file_name = 'tmp/utxo.json'
    # open utxo json file
    try:
        with open(file_name, "r") as read_content:
            data = json.load(read_content)
    except FileNotFoundError:
        return {}
    # store all tokens from utxo
    for d in data:
        # print(data[d]['value'])
        # Get the currency
        for currency in data[d]['value']:
            # currency already in amount
            if currency in amount.keys():
                if currency == 'lovelace':
                    amount[currency] += data[d]['value'][currency]
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
                    amount[currency] = data[d]['value'][currency]
    return amount


def get_script_address(plutusScript, flag=True):
    """
    Get the script address from a plutus script file.
    """
    func = [
        'cardano-cli',
        'address',
        'build',
        '--payment-script-file',
        plutusScript
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def get_script_balance(scriptAddress, flag=True):
    func = [
        'cardano-cli',
        'query',
        'utxo',
        '--address',
        scriptAddress,
        '--out-file',
        'tmp/utxo.json'
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func)
    p.communicate()


def display_balance(scriptAddress, flag=True):
    func = [
        'cardano-cli',
        'query',
        'utxo',
        '--address',
        scriptAddress,
    ]
    func += whichnet(flag)
    p = subprocess.Popen(func, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
    return p


def con_obj():
    """
    Returns the connection object.
    """
    return sqlite3.connect(os.getcwd() + '/NFTs/db/token.db')


# This should not overwrite the db.
def create_table():
    """
    Creates the token table if it does not exists.
    """
    con = con_obj()
    cur = con.cursor()
    # Create table
    cur.execute("DROP TABLE IF EXISTS tokens;")
    con.commit()
    cur.execute("CREATE TABLE tokens (scriptAddress, sellerAddress, sellerHash, artistAddress, price, policyID, tokenName);")
    # Save (commit) the changes
    con.commit()
    # We can also close the connection if we are done with it.
    con.close()


def add_entry(entry):
    con = con_obj()
    cur = con.cursor()
    scriptAddress = entry['scriptAddress']
    sellerAddress = entry['sellerAddress']
    sellerHash    = entry['sellerHash']
    artistAddress = entry['artistAddress']
    price         = entry['price']
    policyID      = entry['policyID']
    tokenName     = entry['tokenName']
    cur.execute("INSERT OR IGNORE INTO tokens VALUES(?, ?, ?, ?, ?, ?, ?);", (scriptAddress, sellerAddress, sellerHash, artistAddress, price, policyID, tokenName))
    con.commit()
    con.close()


def search_all_contracts(path, flag=True):
    dir_list = [directory for directory in os.listdir(path) if os.path.isdir(path+directory)]
    for dir in dir_list:
        entry = {
            'scriptAddress': "",
            'sellerAddress': "",
            'sellerHash'   : "",
            'artistAddress': "",
            'price'        : 0 ,
            'policyID'     : "",
            'tokenName'    : ""
        }
        pubKeyHash, price = dir.split('_')
        entry['price'] = price
        for file in os.listdir(path+dir):
            if file == "payment.vkey":
                vkey_path = path+dir+"/"+file
                sellerAddress = get_address_from_vkey(vkey_path, flag)
                sellerHash = get_key_hash(vkey_path)
                entry['sellerAddress'] = sellerAddress
                entry['sellerHash'] = sellerHash
            if file == "artist.vkey":
                vkey_path = path+dir+"/"+file
                artistAddress = get_address_from_vkey(vkey_path, flag)
                entry['artistAddress'] = artistAddress
        #
        scriptFolder = path+dir+"/token-sale/"
        if os.path.isdir(path+dir+"/token-sale/") is False:
            scriptFolder = path+dir+"/token-sale-with-royalty/"
        for file in os.listdir(scriptFolder):
            if file.endswith(".plutus"):
                plutusScriptPath = scriptFolder+file
                scriptAddress = get_script_address(plutusScriptPath, flag)
                entry['scriptAddress'] = scriptAddress
                get_script_balance(scriptAddress, flag)
                currency = txin()
                # print('currency', currency)
                for policyID in currency.keys():
                    if policyID != 'lovelace':
                        for tokenName in currency[policyID]:
                            entry['policyID']  = policyID
                            entry['tokenName'] = tokenName
                            add_entry(entry)
                try:
                    os.remove('utxo.json')
                except FileNotFoundError:
                    pass


def update_database(path, flag=True):
    create_table()
    search_all_contracts(path, flag)


def find_specific_entry(pid, tkn):
    con = con_obj()
    cur = con.cursor()
    cur.execute("SELECT * FROM tokens WHERE policyID=? AND tokenName=?;", (pid, tkn))
    all_entries = cur.fetchall()
    con.close()
    return all_entries

def get_all_entries():
    con = con_obj()
    cur = con.cursor()
    cur.execute("SELECT * FROM tokens;")
    all_entries = cur.fetchall()
    con.close()
    return all_entries

    