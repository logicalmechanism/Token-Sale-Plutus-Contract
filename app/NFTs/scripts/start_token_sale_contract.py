import NFTs.scripts.transaction as trx
from os.path import isdir, isfile

# May need to type this into terminal before starting
def start_contract(tmp, wallet_skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, collateral, flag=True):
    """
    This allows the seller to place a token to be sold into a smart contract.
    """
    print('\nSTART OF STARTING TOKEN SALE CONTRACT')
    print(policy_id)
    print(token_name)
    
    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exist.')
        return False
    
    # Delete contents from tmp; starts fresh
    trx.delete_contents(tmp)
    trx.protocol(tmp, flag)
    trx.utxo(wallet_addr, tmp, 'utxo.json', flag)
    
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exist.')
        return False
    utxo_in, utxo_col, currencies, collat_flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    # Check if collateral exists
    if collat_flag is True:
        _, final_tip, block = trx.tip(tmp, flag)
        # print('\nThe current block:', block)
        
        # Order matters
        utxo_out = trx.asset_change(tmp, currencies, wallet_addr, [policy_id, token_name]) # send anything but token_name to wallet
        utxo_out += trx.asset_change(tmp, currencies, script_addr, [policy_id, token_name], False) # Send just token_name to script
        # print('\nUTxO: ', utxo_out)
        additional_data = [
            '--tx-out-datum-hash', datum_hash # This has to be the hash of the fingerprint of the token
        ]
        # print('\nCheck Datum: ', additional_data)
        check_status = trx.build(tmp, wallet_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data, flag)
        if check_status != 0:
            print('The transaction build has failed.')
            return False
        
        # Ensure the tmp folder exists
        if isfile(wallet_skey_path) is False:
            print('The file:', wallet_skey_path, 'does not exist.')
            return False
        
        # This makes it live
        signers = [
            '--signing-key-file',
            wallet_skey_path
        ]
        trx.sign(tmp, signers, flag)
        trx.submit(tmp, flag)
        print('\nEND OF STARTING TOKEN SALE CONTRACT\n')
        return True

    else:
        print("The wallet did not account for collateral.")
        return False
