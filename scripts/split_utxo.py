import transaction as trx
from sys import exit
from os.path import isdir, isfile


def split_for_collateral(tmp, wallet_skey_path, wallet_addr, minimum_ada):
    """
    Splits the wallet for a primary and collateral utxo.
    """
    
    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exists')
        exit(0)
    
    # clean up the contents
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exists')
        exit(0)
    
    utxo_in, _, currencies, _, _ = trx.txin(tmp, 'utxo.json')
    _, final_tip, block = trx.tip(tmp)
    
    print('BLOCK:', block)
    utxo_out = ['--tx-out', wallet_addr+'+'+str(minimum_ada)]
    utxo_out += trx.asset_change(tmp, currencies, wallet_addr)
    print('\n', utxo_out)
    
    trx.build(tmp, wallet_addr, final_tip, utxo_in, [], utxo_out, [])
    
    # Make User Confirm Data is Correct
    answer = -1
    while answer not in [0, 1]:
        try:
            answer = int(input("Proceed by entering 1 or exit with 0\n"))
        except ValueError:
            pass
    if answer == 0:
        print('The transaction information is incorrect.')
        exit(0)
    
    # Ensure the tmp folder exists
    if isfile(wallet_skey_path) is False:
        print('The file:', wallet_skey_path, 'does not exists')
        exit(0)
    
    # This makes it live
    signers = [
        '--signing-key-file',
        wallet_skey_path
    ]
    trx.sign(tmp, signers)
    trx.submit(tmp)

if __name__ == "__main__":
    
    # with open("/path/to/wallet/payment.addr", "r") as read_content: WALLET_ADDR = read_content.read().splitlines()[0]
    WALLET_ADDR      = "wallet_address_here"
    WALLET_SKEY_PATH = "/path/to/wallet/payment.skey"
    
    # tmp folder for trx files
    TMP = "/path/to/tmp/folder/"
    
    # Over account for collateral
    COLLATERAL = 17000000
    
    split_for_collateral(TMP, WALLET_SKEY_PATH, WALLET_ADDR, COLLATERAL)