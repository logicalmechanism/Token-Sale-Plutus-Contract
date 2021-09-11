from django.shortcuts import render, redirect
from django.http import Http404
import NFTs.scripts.update_db as db
import NFTs.scripts.helper    as help
from NFTs.scripts.end_token_sale_contract import buy_token
from NFTs.scripts.end_royalty_contract import buy_token_with_royalty
from NFTs.scripts.start_token_sale_contract import start_contract
from NFTs.scripts.start_royalty_contract import start_royalty
from NFTs.scripts.split_utxo import split_for_collateral
import NFTs.scripts.transaction as trx
import os
import copy
import json

###############################################################################
# Mainnet is True | testnet is False
MAINNET    = False
# 17 ADA collateral
COLLATERAL = 17000000
###############################################################################

def error_page(request):
    return render(request, 'error.html', {})


def get_wallet_currency():
    vkey_path = os.getcwd() + '/NFTs/wallet/payment.vkey'
    wallet_address = db.get_address_from_vkey(vkey_path, MAINNET)
    db.get_script_balance(wallet_address, MAINNET)
    currency = db.txin()
    # print(currency)
    return currency


def find_collateral():
    vkey_path = os.getcwd() + '/NFTs/wallet/payment.vkey'
    wallet_address = db.get_address_from_vkey(vkey_path, MAINNET)
    db.get_script_balance(wallet_address, MAINNET)
    file_name = os.getcwd() + '/tmp/utxo.json'
    try:
        with open(file_name, "r") as read_content:
            data = json.load(read_content)
    except FileNotFoundError:
        data = ''
    # print(data)
    collateral = {}
    for tx in data:
        for info in data[tx]:
            if info == 'value':
                if data[tx][info]['lovelace'] == COLLATERAL:
                    collateral[tx] = data[tx][info]
                    # print(tx, data[tx][info])
    return collateral

def processing_order(request):
    vkey_path = os.getcwd() + '/NFTs/wallet/payment.vkey'
    collateral = find_collateral()
    context = {
        'balance': get_wallet_currency(),
        'block'  : db.current_block(MAINNET),
        'data'   : collateral,
        'address' : db.get_address_from_vkey(vkey_path, MAINNET),
    }
    return render(request, 'order.html', context)


def create_collateral(request):
    vkey_path = os.getcwd() + '/NFTs/wallet/payment.vkey'
    skey_path = os.getcwd() + '/NFTs/wallet/payment.skey'
    wallet_address = db.get_address_from_vkey(vkey_path, MAINNET)
    split_for_collateral(os.getcwd() + '/tmp/', skey_path, wallet_address, COLLATERAL, MAINNET)
    context = {
        'balance': get_wallet_currency(),
        'block'  : db.current_block(MAINNET)
    }
    return redirect('order')


def starting_a_contract(request):
    contract         = request.POST.get('contract')
    (keyhash, price) = contract.split('_')
    price = int(price)
    # print('\nfolder', contract)
    # print('price', price)
    policy_id        = request.POST.get('policyID')
    token_name       = request.POST.get('tokenName')
    artist_address   = request.POST.get('artistAddress')
    tokenSale        = request.POST.get('tokenSale')
    royaltySale      = request.POST.get('royaltySale')
    tmp              = os.getcwd() + '/tmp/'
    vkey_path        = os.getcwd() + '/NFTs/wallet/payment.vkey'
    skey_path        = os.getcwd() + '/NFTs/wallet/payment.skey'
    wallet_addr      = db.get_address_from_vkey(vkey_path, MAINNET)
    datum_hash       = trx.get_datum_hash(policy_id, token_name)
    if tokenSale == 'True':
        if MAINNET:
            plutus_script = os.path.dirname(os.getcwd()) + '/token_sale_contracts/' + contract + '/token-sale/token_sale.plutus'
        else:
            plutus_script = os.path.dirname(os.getcwd()) + '/example_token_sale_addition/' + contract + '/token-sale/token_sale.plutus'
        script_addr = trx.get_script_address(plutus_script, MAINNET)
        # print('script_addr', script_addr)
        start_contract(tmp, skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, COLLATERAL, MAINNET)
    if royaltySale == 'True':
        if MAINNET:
            plutus_script = os.path.dirname(os.getcwd()) + '/royalty_sale_contracts/' + contract + '/token-sale-with-royalty/token_sale_with_royalty.plutus'
        else:
            plutus_script = os.path.dirname(os.getcwd()) + '/example_royalty_sale_addition/' + contract + '/token-sale-with-royalty/token_sale_with_royalty.plutus'
        script_addr = trx.get_script_address(plutus_script, MAINNET)
        # print('starting royal')
        start_royalty(tmp, skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, COLLATERAL, MAINNET)
    return redirect('order')


def sell_to_smart_contract(request):
    policy_id      = request.POST.get('policyID')
    token_name     = request.POST.get('tokenName')
    vkey_path      = os.getcwd() + '/NFTs/wallet/payment.vkey'
    wallet_hash    = db.get_key_hash(vkey_path).replace('\r', '').replace('\n', '')
    concat_pid_tkn = help.concat_pid_and_tkn(policy_id, token_name)
    metadata       = help.get_onchain_metadata(concat_pid_tkn)
    # print(metadata)

    # This metadata must contain artist pubkey hash
    try:
        artist_hash = metadata['artist-hash']
    except (KeyError, TypeError):
        artist_hash = None
        # REMOVE
        if not MAINNET:
            artist_hash = 'a26dbea4b3297aafb28c59772a4ef2964ebffb3375b5de313947e6c8'
    
    found = False
    token_sale_contracts   = []
    royalty_sale_contracts = []
    
    # Any token will work
    if MAINNET:
        token_sale_folders = os.listdir(os.path.dirname(os.getcwd()) + '/token_sale_contracts/')
    else:
        token_sale_folders = os.listdir(os.path.dirname(os.getcwd()) + '/example_token_sale_addition/')
    for folder in token_sale_folders:
        if wallet_hash in folder:
            found = True
            token_sale_contracts.append(folder)
    
    # Only tokens with pubkeys eqaul to artist.vkey will work.
    artist_address = ''
    if artist_hash is not None:
        if MAINNET:
            royalty_sale_path = os.path.dirname(os.getcwd()) + '/royalty_sale_contracts/'
        else:
            royalty_sale_path = os.path.dirname(os.getcwd()) + '/example_royalty_sale_addition/'
        royalty_sale_folders = os.listdir(royalty_sale_path)
        for folder in royalty_sale_folders:
            if wallet_hash in folder:
                # print(royalty_sale_path+folder)
                for files in os.listdir(royalty_sale_path+folder):
                    # print(files)
                    # This means the contract can be used.
                    if files == 'artist.vkey':
                        temp_artist_hash = db.get_key_hash(royalty_sale_path + folder + '/artist.vkey').replace('\r', '').replace('\n', '')
                        artist_address   = db.get_address_from_vkey(royalty_sale_path + folder + '/artist.vkey')
                        # print(temp_artist_hash)
                        if artist_hash == temp_artist_hash:
                            found = True
                            royalty_sale_contracts.append(folder)
    
    # nothing is found
    if found is False:
        return redirect('error')
    
    # Allow user to pick
    context = {
        'policy_id'   : policy_id,
        'token_name'  : token_name,
        'artist_addr' : artist_address,
        'tsContracts' : token_sale_contracts,
        'rsContracts' : royalty_sale_contracts,
    }
    return render(request, 'contracts.html', context)


def buy_from_smart_contract(request):
    script_addr    = request.POST.get('scriptAddress')
    seller_addr    = request.POST.get('sellerAddress')
    seller_hash    = request.POST.get('sellerHash').replace('\r', '').replace('\n','')
    artist_addr    = request.POST.get('artistAddress')
    policy_id      = request.POST.get('policyID')
    token_name     = request.POST.get('tokenName')
    price          = int(request.POST.get('price'))*1000000
    vkey_path      = os.getcwd() + '/NFTs/wallet/payment.vkey'
    skey_path      = os.getcwd() + '/NFTs/wallet/payment.skey'
    wallet_addr    = db.get_address_from_vkey(vkey_path, MAINNET)
    datum_hash     = trx.get_datum_hash(policy_id, token_name)
    fingerprint    = trx.get_token_identifier(policy_id, token_name)
    # Change to contract folder at live
    if artist_addr == '':
        if MAINNET:
            plutus_script  = os.path.dirname(os.getcwd()) + '/token_sale_contracts/{}_{}/token-sale/token_sale.plutus'.format(seller_hash, price)
        else:
            plutus_script  = os.path.dirname(os.getcwd()) + '/example_token_sale_addition/{}_{}/token-sale/token_sale.plutus'.format(seller_hash, price)
        # print('\nSale Contract.')
        buy_token(os.getcwd() + '/tmp/', skey_path, wallet_addr, script_addr, price, datum_hash, fingerprint, plutus_script, seller_addr, policy_id, token_name, COLLATERAL, MAINNET)
    else:
        if MAINNET:
            with open(os.path.dirname(os.getcwd()) + '/royalty_sale_contracts/{}_{}/royalty.amt'.format(seller_hash, price), "r") as read_content: royalty = read_content.read().splitlines()[0]
            plutus_script  = os.path.dirname(os.getcwd()) + '/royalty_sale_contracts/{}_{}/token-sale-with-royalty/token_sale_with_royalty.plutus'.format(seller_hash, price)
        else:
            with open(os.path.dirname(os.getcwd()) + '/example_royalty_sale_addition/{}_{}/royalty.amt'.format(seller_hash, price), "r") as read_content: royalty = read_content.read().splitlines()[0]
            plutus_script  = os.path.dirname(os.getcwd()) + '/example_royalty_sale_addition/{}_{}/token-sale-with-royalty/token_sale_with_royalty.plutus'.format(seller_hash, price)
        # print("\nRoyalty Contract.")
        buy_token_with_royalty(os.getcwd() + '/tmp/', skey_path, wallet_addr, script_addr, price, price // int(royalty), datum_hash, plutus_script, seller_addr, artist_addr, policy_id, token_name, COLLATERAL, MAINNET)
    return redirect('order')


def wallet(request):
    search_value = request.GET.get('search')
    # print(search_value)

    currency = get_wallet_currency()
    lovelace = currency['lovelace']
    del currency['lovelace']

    # tokens = currency.copy()
    tokens = copy.deepcopy(currency)
    # print(tokens)
    for pid in currency:
        for token in currency[pid]:
            if search_value is None:
                tokens[pid][token] = {
                    'amount': tokens[pid][token],
                    'image' : help.get_image(pid, token)
                }
            else:
                if search_value in pid or search_value in token:
                    tokens[pid][token] = {
                        'amount': tokens[pid][token],
                        'image' : help.get_image(pid, token)
                    }
                else:
                    del tokens[pid][token]
    context = {
        'lovelace': lovelace, 
        'tokens'  : tokens, 
        'address' : db.get_address_from_vkey(os.getcwd() + '/NFTs/wallet/payment.vkey', MAINNET),
        'collat'  : find_collateral()
    }
    return render(request, 'wallet.html', context)


def index(request):

    search_value = request.GET.get('search')
    # print(search_value)
    if MAINNET:
        path_to_ts_contracts = os.path.dirname(os.getcwd()) + "/token_sale_contracts/"
        db.update_database(path_to_ts_contracts, MAINNET)
        path_to_tswr_contracts = os.path.dirname(os.getcwd()) + "/royalty_sale_contracts/"
        db.search_all_contracts(path_to_tswr_contracts, MAINNET)
    else:
        path_to_ts_contracts = os.path.dirname(os.getcwd()) + "/example_token_sale_addition/"
        db.update_database(path_to_ts_contracts, MAINNET)
        path_to_tswr_contracts = os.path.dirname(os.getcwd()) + "/example_royalty_sale_addition/"
        db.search_all_contracts(path_to_tswr_contracts, MAINNET)
    #
    list_of_entries = []
    for token in db.get_all_entries():
        (scriptAddress, sellerAddress, sellerHash, artistAddress, price, policyID, tokenName) = token
        if search_value is None:
            entry = {
                'scriptAddress': scriptAddress,
                'sellerAddress': sellerAddress,
                'sellerHash'   : sellerHash,
                'artistAddress': artistAddress,
                'price'        : price,
                'policyID'     : policyID,
                'tokenName'    : tokenName,
                'image'        : help.get_image(policyID, tokenName),
            }
            list_of_entries.append(entry)
        else:
            if search_value in token:
            # if search_value in tokenName or search_value in policyID or search_value in scriptAddress or search_value in sellerAddress or search_value in price or search_value in artistAddress:
                entry = {
                    'scriptAddress': scriptAddress,
                    'sellerAddress': sellerAddress,
                    'sellerHash'   : sellerHash,
                    'artistAddress': artistAddress,
                    'price'        : price,
                    'policyID'     : policyID,
                    'tokenName'    : tokenName,
                    'image'        : help.get_image(policyID, tokenName),
                }
                list_of_entries.append(entry)
        # raise Http404("Question does not exist")
    currency = get_wallet_currency()
    lovelace = currency['lovelace']
    del currency['lovelace']
    context = {
        'lovelace': lovelace, 
        'entries' : list_of_entries,
        'address' : db.get_address_from_vkey(os.getcwd() + '/NFTs/wallet/payment.vkey', MAINNET),
        'collat'  : find_collateral()
    }
    return render(request, 'index.html', context)