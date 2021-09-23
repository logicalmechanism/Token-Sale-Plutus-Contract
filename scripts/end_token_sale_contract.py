import transaction as trx
from sys import exit
from os.path import isdir, isfile


def end(tmp, wallet_skey_path, wallet_addr, script_addr, cost, datum_hash, plutus_script, seller_addr, policy_id, token_name, collateral):
    """
    Retrieves a token from a smart contract.
    """

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
        # print(script_currencies)
        contract_utxo_in = utxo_in
        for key in data_list:
            # A single UTXO with a single datum can be spent
            if data_list[key] == datum_hash:
                contract_utxo_in += ['--tx-in', key]
                break
        # print(contract_utxo_in)
        _, final_tip, block = trx.tip(tmp)
        print('\nThe current block:', block)
        utxo_out = trx.asset_change(tmp, script_currencies, wallet_addr) # This needs to create the output for the NFT being bought, with this it will give the change to the buyer, testing a seller change output logic
        utxo_out += trx.asset_change(tmp, currencies, wallet_addr) # Accounts for token change
        utxo_out += ['--tx-out', seller_addr+'+'+str(cost)]
        print('\nUTxO: ', utxo_out)
        additional_data = [
            '--tx-out-datum-hash', datum_hash,
            '--tx-in-datum-value', '"{}"'.format(trx.get_token_identifier(policy_id, token_name)),
            '--tx-in-redeemer-value', '""',
            '--tx-in-script-file', plutus_script
        ]
        print('\nCheck DATUM: ', additional_data)
        trx.build(tmp, wallet_addr, final_tip, contract_utxo_in, utxo_col, utxo_out, additional_data)

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
    # Buyer info

    # with open("/path/to/wallet/payment.addr", "r") as read_content: BUYER_ADDR = read_content.read().splitlines()[0]
    BUYER_ADDR      = "BUYER_ADDRESS_HERE"
    BUYER_SKEY_PATH = "/path/to/wallet/payment.skey"
    
    # Seller info

    # SELLER_ADDR = trx.get_address_from_vkey("/path/to/seller/payment.vkey")
    SELLER_ADDR = "SELLER_ADDRESS_HERE"
    
    # Script info
    PLUTUS_SCRIPT_PATH = "/path/to/compiled/contract/plutus.script"
    # SCRIPT_ADDR   = trx.get_script_address(PLUTUS_SCRIPT_PATH)
    SCRIPT_ADDR   = "SCRIPT_ADDRESS_HERE"

    # tmp folder for transactions
    TMP = "/path/to/tmp/folder/"

    # Token Name and Cost
    COST       = 25000000
    COLLATERAL = 17000000

    # Calculate the "fingerprint"
    POLICY_ID   = "POLICY_ID_HERE"
    TOKEN_NAME  = "TOKEN_NAME_HERE"
    
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    print('DATUM Hash: ', DATUM_HASH)
    
    end(TMP, BUYER_SKEY_PATH, BUYER_ADDR, SCRIPT_ADDR, COST, DATUM_HASH, PLUTUS_SCRIPT_PATH, SELLER_ADDR, POLICY_ID, TOKEN_NAME, COLLATERAL)
