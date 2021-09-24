import os
import transaction as trx
from sys import exit
from os.path import isdir, isfile

def buy(tmp, wallet_skey_path, wallet_addr, script_addr, cost, datum_hash, plutus_script, seller_addr, policy_id, token_name, collateral):

    # Ensure the tmp folder exists    
    if isdir(tmp) is False:
        print('The directory:', tmp, 'does not exists')
        exit(0)

    # Clean the folder
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    
    # Check if wallet address is correct
    if isfile(tmp+'utxo.json') is False:
        print('The file:', tmp+'utxo.json', 'does not exists')
        exit(0)
    utxo_in, utxo_col, currencies, flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    # Check for collateral
    if flag is True:
        trx.utxo(script_addr, tmp, 'utxo_script.json')
        if isfile(tmp+'utxo_script.json') is False:
            print('The file:', tmp+'utxo_script.json', 'does not exists')
            exit(0)
        _, _, script_currencies, _, data_list = trx.txin(tmp, 'utxo_script.json', collateral, True, datum_hash)
        contract_utxo_in = utxo_in
        for key in data_list:
            # A single UTXO with a single datum can be spent
            if data_list[key] == datum_hash:
                contract_utxo_in += ['--tx-in', key]
                break
        _, final_tip, block = trx.tip(tmp)
        print('\nThe current block:', block)
        utxo_out = trx.asset_change(tmp, script_currencies, wallet_addr) # UTxO to Send NFT to the Buyer
        utxo_out += trx.asset_change(tmp, currencies, wallet_addr) # Account for token change TODO: Double check fee calc error
        utxo_out += ['--tx-out', seller_addr+'+'+str(cost)] # UTxO to Send Payment to Seller
        print('\nUTxO: ', utxo_out)
        additional_data = [
            '--tx-out-datum-hash', datum_hash,
            '--tx-in-datum-value', '"{}"'.format(trx.get_token_identifier(policy_id, token_name)),
            '--tx-in-redeemer-value', '""',
            '--tx-in-script-file', plutus_script
        ]
        print('\nCheck DATUM: ', additional_data)
        trx.build(tmp, wallet_addr, final_tip, contract_utxo_in, utxo_col, utxo_out, additional_data)

        # User Confirms if Data is Correct
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
    
    # Get input from buyer
    BUYER_ADDR = input("\nYour Cardano ADA Buyer Address (eg addr1...) \n    Buyer Address:>")
    BUYER_SKEY_PATH = input("\nPath to Your Signing Key File (eg /home/user/node/wallet/buyer.skey) \n    Path to skey File:>")
    SELLER_ADDR = input("\nSeller's Cardano ADA Address (eg addr1...) \n    Seller Address:>")
    PLUTUS_SCRIPT_PATH = input("\nPath to Plutus SmartContract File (eg /home/user/node/wallet/scripts/token_sale_smartcontract.plutus) \n    Path to SmartContract File:>")
    SCRIPT_ADDR = input("\nSmartContract Cardano ADA Address (eg addr1...) \n    SmartContract Address:>")
    POLICY_ID = input("\nNFT Policy ID (eg 3cb979ba9d8d618acc88fb716e97782469f04727d5ba8b428a9a9258) \n    NFT Policy ID:>")
    TOKEN_NAME = input("\nNFT Name or Ticker (eg CypherMonkZero) \n    NFT Name:>")
    COST = input("\nPrice of the NFT represented in lovelace (eg for 10ADA, enter: 10000000) \n    Lovelace Price:>")
    
    print("\n-----------------------------\n| Please Verify Your Input! |\n-----------------------------\n")
    print("\nBuyer Address >> ",BUYER_ADDR)
    print("\nBuyer skey File Path >> ",BUYER_SKEY_PATH)
    print("\nSeller Address >> ",SELLER_ADDR)
    print("\nSmartContract File Path >> ",PLUTUS_SCRIPT_PATH)
    print("\nSmartContract Address >> ",SCRIPT_ADDR)
    print("\nTMP Folder Path >> ",TMP)
    print("\nNFT Policy ID >> ",POLICY_ID)
    print("\nNFT Name >> ",TOKEN_NAME)
    print("\nLovelace Price >> ",COST)
    
    VALUES_CORRECT = input("\n\nIs the information above correct? (yes or no): ")
    
    if VALUES_CORRECT == ("yes"):
        print("\n\nContinuing . . . \n")
    elif VALUES_CORRECT == ("no"):
        print("\n\nQuitting, please run again to try again!\n\n")
        exit(0)
    
    # Calculate the "fingerprint"
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    
    print('DATUM Hash: ', DATUM_HASH)
    
    buy(TMP, BUYER_SKEY_PATH, BUYER_ADDR, SCRIPT_ADDR, COST, DATUM_HASH, PLUTUS_SCRIPT_PATH, SELLER_ADDR, POLICY_ID, TOKEN_NAME, COLLATERAL)
