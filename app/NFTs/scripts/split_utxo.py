import NFTs.scripts.transaction as trx
from os.path import isdir, isfile


def split_for_collateral(tmp, wallet_skey_path, wallet_addr, minimum_ada, flag=True):
    """
    Splits the wallet for a primary and collateral utxo.
    """
    print('\nSTART OF SPLITTING UTXO FOR COLLATERAL\n')
    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exists')
        return False
    
    # clean up the contents
    trx.delete_contents(tmp)
    trx.protocol(tmp, flag)
    trx.utxo(wallet_addr, tmp, 'utxo.json', flag)
    
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exists')
        return False
    
    utxo_in, _, currencies, _, _ = trx.txin(tmp, 'utxo.json')
    _, final_tip, block = trx.tip(tmp, flag)
    
    # print('BLOCK:', block)
    utxo_out = ['--tx-out', wallet_addr+'+'+str(minimum_ada)]
    utxo_out += trx.asset_change(tmp, currencies, wallet_addr, [], False)
    # print('\n', utxo_out)
    
    # Build
    check_status = trx.build(tmp, wallet_addr, final_tip, utxo_in, [], utxo_out, [], flag)
    if check_status != 0:
        print('The transaction build has failed.')
        return False
    
    # Ensure the tmp folder exists
    if isfile(wallet_skey_path) is False:
        print('The file:', wallet_skey_path, 'does not exists')
        return False
    
    # This makes it live
    signers = [
        '--signing-key-file',
        wallet_skey_path
    ]
    trx.sign(tmp, signers, flag)
    trx.submit(tmp, flag)
    print('\nEND OF SPLITTING UTXO FOR COLLATERAL\n')
    return True

