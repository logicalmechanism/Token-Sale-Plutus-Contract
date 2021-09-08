import transaction as trx
from sys import exit
from os.path import isdir, isfile

# May need to type this into terminal before starting
def start(tmp, wallet_skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, collateral):
    """
    This allows the seller to place a token to be sold into a smart contract.
    """
    
    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exist.')
        exit(0)
    
    # Delete contents from tmp; starts fresh
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exist.')
        exit(0)
    utxo_in, utxo_col, currencies, flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    # Check if collateral exists
    if flag is True:
        _, final_tip, block = trx.tip(tmp)
        print('\nThe current block:', block)
        
        # Order matters
        utxo_out = trx.asset_change(tmp, currencies, wallet_addr, [policy_id, token_name]) # send anything but token_name to wallet
        utxo_out += trx.asset_change(tmp, currencies, script_addr, [policy_id, token_name], False) # Send just token_name to script
        print('\nUTxO: ', utxo_out)
        additional_data = [
            '--tx-out-datum-hash', datum_hash # This has to be the hash of the fingerprint of the token
        ]
        print('\nCheck Datum: ', additional_data)
        trx.build(tmp, wallet_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data)
        
        # Make User Confirm Data is Correct
        answer = -1
        while answer not in [0, 1]:
            try:
                answer = int(input("Proceed by entering 1 or exit by entering 0\n"))
            except ValueError:
                pass
        if answer == 0:
            print('The transaction information is incorrect.')
            exit(0)
        
        # Ensure the tmp folder exists
        if isfile(wallet_skey_path) is False:
            print('The file:', wallet_skey_path, 'does not exist.')
            exit(0)
        
        # This makes it live
        signers = [
            '--signing-key-file',
            wallet_skey_path
        ]
        trx.sign(tmp, signers)
        trx.submit(tmp)

    else:
        print("The wallet did not account for collateral.")
        exit(0)


if __name__ == "__main__":
    
    # seller info required to change send back
    # with open("/path/to/wallet/payment.addr", "r") as read_content: SELLER_ADDR = read_content.read().splitlines()[0]
    SELLER_ADDR      = "wallet_address_here"
    SELLER_SKEY_PATH = "/path/to/wallet/payment.skey"

    # SCRIPT_ADDR    = trx.get_script_address("/path/to/compiled/contract/plutus.script")
    SCRIPT_ADDR      = "smart_contract_address_here"
    
    # Tmp folder for transactions - This stores protocol params, etc
    TMP = "/path/to/tmp/folder/"
    
    # Policy ID and Token Name to be sold.
    POLICY_ID  = "policy_id_here"
    TOKEN_NAME = "token_name_here"
    
    # Calculate the "fingerprint"
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    print('Datum Hash: ', DATUM_HASH)
    
    COLLATERAL = 17000000 # This over accounts for the smart contract
    start(TMP, SELLER_SKEY_PATH, SELLER_ADDR, SCRIPT_ADDR, DATUM_HASH, POLICY_ID, TOKEN_NAME, COLLATERAL)