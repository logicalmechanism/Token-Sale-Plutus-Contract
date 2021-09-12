import NFTs.scripts.transaction as trx
from os.path import isdir, isfile


def buy_token_with_royalty(tmp, wallet_skey_path, wallet_addr, script_addr, cost, royalty, datum_hash, plutus_script, seller_addr, royalty_addr, policy_id, token_name, collateral, flag):
    print('\nSTART OF BUYING ROYALTY SALE CONTRACT')
    print(policy_id)
    print(token_name)

    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exist.')
        return False
    
    # Clean start each time
    trx.delete_contents(tmp)
    trx.protocol(tmp, flag)
    
    trx.utxo(wallet_addr, tmp, 'utxo.json', flag)
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exist.')
        return False
    
    utxo_in, utxo_col, currencies, collat_flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    if collat_flag is True:
        #tmp
        trx.utxo(script_addr, tmp, 'utxo_script.json', flag)
        if isfile(tmp+'utxo_script.json') is False:
            print('The file:', tmp+'utxo_script.json', 'does not exists')
            return False
        
        _, _, script_currencies, _, data_list = trx.txin(tmp, 'utxo_script.json')
        contract_utxo_in = utxo_in
        for key in data_list:
            if data_list[key] == datum_hash:
                contract_utxo_in += ['--tx-in', key]
        
        _, final_tip, block = trx.tip(tmp, flag)
        
        utxo_out = trx.asset_change(tmp, script_currencies, wallet_addr, [policy_id, token_name], False)
        utxo_out += trx.asset_change(tmp, currencies, wallet_addr) # Accounts for token change
        utxo_out += ['--tx-out', seller_addr+'+'+str(cost)]
        utxo_out += ['--tx-out', royalty_addr+'+'+str(royalty)]
        additional_data = [
            '--tx-out-datum-hash', datum_hash,
            '--tx-in-datum-value', '"{}"'.format(trx.get_token_identifier(policy_id, token_name)),
            '--tx-in-redeemer-value', '""',
            '--tx-in-script-file', plutus_script
        ]
        # print('BLOCK:', block)
        # print(utxo_out)
        check_status = trx.build(tmp, wallet_addr, final_tip, contract_utxo_in, utxo_col, utxo_out, additional_data, flag)
        if check_status != 0:
            print('The transaction build has failed.')
            return False
        
        # Ensure the tmp folder exists
        if isfile(wallet_skey_path) is False:
            print('The file:', wallet_skey_path, 'does not exist.')
            return False
        
        signers = [
            '--signing-key-file',
            wallet_skey_path,
        ]
        trx.sign(tmp, signers, flag)
        trx.submit(tmp, flag)
        print('\nEND OF BUYING ROYALTY SALE CONTRACT\n')
        return True

    else:
        print("The wallet did not account for collateral.")
        return False
