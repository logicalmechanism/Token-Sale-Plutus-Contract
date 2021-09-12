import NFTs.scripts.transaction as trx
from os.path import isdir, isfile


def buy_token(tmp, wallet_skey_path, wallet_addr, script_addr, cost, datum_hash, fingerprint, plutus_script, seller_addr, policy_id, token_name, collateral, flag):
    """
    Retrieves a token from a smart contract.
    """
    print('\nSTART OF BUYING FROM CONTRACT')
    print(policy_id)
    print(token_name)

    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exists')
        return False

    # Clean the folder
    trx.delete_contents(tmp)
    trx.protocol(tmp, flag)
    trx.utxo(wallet_addr, tmp, 'utxo.json', flag)
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exists')
        return False
    utxo_in, utxo_col, currencies, collat_flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    # Check for collateral
    if collat_flag is True:
        trx.utxo(script_addr, tmp, 'utxo_script.json', flag)
        if isfile(tmp+'utxo_script.json') is False:
            print('The file:', tmp+'utxo_script.json', 'does not exists')
            return False
        _, _, script_currencies, _, data_list = trx.txin(tmp, 'utxo_script.json', collateral, True, datum_hash)
        
        # print(script_currencies)
        contract_utxo_in = utxo_in
        for key in data_list:
            # A single UTXO with a single datum can be spent
            if data_list[key] == datum_hash:
                contract_utxo_in += ['--tx-in', key]
                break
        # print(contract_utxo_in)
        _, final_tip, block = trx.tip(tmp, flag)
        # print('BLOCK:', block)
        # print(script_currencies)
        utxo_out = trx.asset_change(tmp, script_currencies, wallet_addr, [policy_id, token_name], False)
        utxo_out += trx.asset_change(tmp, currencies, wallet_addr) # Accounts for token change
        utxo_out += ['--tx-out', seller_addr+'+'+str(cost)]
        additional_data = [
            '--tx-out-datum-hash', datum_hash,
            '--tx-in-datum-value', '"{}"'.format(fingerprint),
            '--tx-in-redeemer-value', '""',
            '--tx-in-script-file', plutus_script
        ]
        # print('\nCheck DATUM: ', additional_data)
        # print('\n', utxo_out)
        check_status = trx.build(tmp, wallet_addr, final_tip, contract_utxo_in, utxo_col, utxo_out, additional_data, flag)
        if check_status != 0:
            print('The transaction build has failed.')
            return False
        
        # Ensure the tmp folder exists
        if isfile(wallet_skey_path) is False:
            print('The file:', wallet_skey_path, 'does not exists')
            return False
        
        signers = [
            '--signing-key-file',
            wallet_skey_path
        ]
        trx.sign(tmp, signers, flag)
        trx.submit(tmp, flag)
        print('\nEND OF BUYING FROM CONTRACT\n')
        return True
    else:
        print("The wallet did not account for collateral.")
        return False
