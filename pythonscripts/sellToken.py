import os
import transaction as trx
from sys import exit
from os.path import isdir, isfile

def sell(tmp, wallet_skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, collateral):

    # Ensure the tmp folder exists
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exist.')
        exit(0)
    
    # Clean the folder
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exist.')
        exit(0)
    utxo_in, utxo_col, currencies, flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    # Check for collateral
    if flag is True:
        _, final_tip, block = trx.tip(tmp)
        print('\nThe current block:', block)
        
        # Order matters
        utxo_out = trx.asset_change(tmp, currencies, wallet_addr, [policy_id, token_name]) # UTxO for all except token for sale
        utxo_out += trx.asset_change(tmp, currencies, script_addr, [policy_id, token_name], False) # Send just the token for sale to script
        print('\nUTxO: ', utxo_out)
        additional_data = [
            '--tx-out-datum-hash', datum_hash # This has to be the hash of the fingerprint of the token
        ]
        print('\nCheck Datum: ', additional_data)
        trx.build(tmp, wallet_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data)
        
        # User Confirms if Data is Correct
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
        
        # Sign and submit to the smartcontract script
        signers = [
            '--signing-key-file',
            wallet_skey_path
        ]
        trx.sign(tmp, signers)
        trx.submit(tmp)

    else:
        print("The wallet did not account for collateral. Please create a UTxO of 2 ADA (2000000 lovelace) before trying again.")
        exit(0)


if __name__ == "__main__":
    # Setup Temp Directory (try to)
    scptroot = os.path.realpath(os.path.dirname(__file__))
    tmpname = "tmp"
    tmppath = os.path.join(scptroot, tmpname)
    TMP = os.path.join(tmppath, '')
    try:
        os.mkdir(tmpname)
    except OSError:
        pass
    
    # Collateral for script transaction
    COLLATERAL = 2000000 # Should be min of 2000000 lovelace in a separate UTxO in buyer's wallet
    
    SELLER_ADDR = input("\nYour Cardano ADA Seller Address (eg addr1...) \n    Seller Address:>")
    SELLER_SKEY_PATH = input("Path to Your Signing Key File (eg /home/user/node/wallet/seller.skey) \n    Path to skey File:>")
    SCRIPT_ADDR = input("\nSmartContract Cardano ADA Address (eg addr1...) \n    SmartContract Address:>")
    POLICY_ID = input("\nNFT Policy ID (eg 3cb979ba9d8d618acc88fb716e97782469f04727d5ba8b428a9a9258) \n    NFT Policy ID:>")
    TOKEN_NAME = input("\nNFT Name or Ticker (eg CypherMonkZero) \n    NFT Name:>")
    
    # Calculate the "fingerprint"
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    print('Datum Hash: ', DATUM_HASH)
    
    sell(TMP, SELLER_SKEY_PATH, SELLER_ADDR, SCRIPT_ADDR, DATUM_HASH, POLICY_ID, TOKEN_NAME, COLLATERAL)
