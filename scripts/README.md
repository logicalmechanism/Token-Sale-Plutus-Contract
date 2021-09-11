# Python Helper Scripts

This folder contains scripts to be used with the token sale smart contract.

These are basic templates for any user to easily interact with the token sale smart contracts. They are meant to be copied into a seperate folder where the cardano-cli is on path as it typically is when installed from source. The user will need to fill in the correct lines near the bottom of the files.

The suggested folder structure for interesting with a given smart contract is:

```
folder/
    -> tmp/
    -> wallet/
        wallet.addr
        wallet.skey
        wallet.vkey
    -> scripts/
        __init__.py
        start_token_sale_contract.py
        end_token_sale_contract.py
        split_utxo.py
        transaction.py
    payment.vkey
    script.plutus
```

This simple structure will allow a user to start or end any compiled Plutus script. Inside helper python file is a __name__ == "__main__" statement that contains a set of parameters that need to be filled out. The code is designed to exit if any of the information does not work.

Please note it is extremely important that any token inside a smart contract contains Datum. Any UTxOs without a Datum will remain stuck inside a smart contract forever.

# Splitting UTxO For Collateral

```py
    # The wallet address can be opened from file or hardcoded.

    # with open("/path/to/wallet/payment.addr", "r") as read_content: WALLET_ADDR = read_content.read().splitlines()[0]
    WALLET_ADDR      = "wallet_address_here"
    WALLET_SKEY_PATH = "/path/to/wallet/payment.skey"
    
    # Tmp folder for transactions - This stores protocol params, etc
    TMP = "/path/to/tmp/folder/"
    
    # The required collateral for the contract.
    COLLATERAL = 17000000
```

# Starting A token sale

```py
    # The seller address can be opened from a file or hardcoded.

    # with open("/path/to/wallet/payment.addr", "r") as read_content: SELLER_ADDR = read_content.read().splitlines()[0]
    SELLER_ADDR      = "wallet_address_here"
    SELLER_SKEY_PATH = "/path/to/wallet/payment.skey"

    # The script address can be computed from the compiled Plutus script or hardcoded.

    # SCRIPT_ADDR    = trx.get_script_address("/path/to/compiled/contract/plutus.script")
    SCRIPT_ADDR      = "smart_contract_address_here"
    
    # Tmp folder for transactions - This stores protocol params, etc
    TMP = "/path/to/tmp/folder/"
    
    # The policy id and token name of the token to be sold inside the contract.
    POLICY_ID  = "policy_id_here"
    TOKEN_NAME = "token_name_here"
    
    # Calculate the "fingerprint"
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    print('Datum Hash: ', DATUM_HASH)
```

# Ending A Token Sale

```py

    # The buyer information can be opened by file or hardcoded.

    # with open("/path/to/wallet/payment.addr", "r") as read_content: BUYER_ADDR = read_content.read().splitlines()[0]
    BUYER_ADDR      = "BUYER_ADDRESS_HERE"
    BUYER_SKEY_PATH = "/path/to/wallet/payment.skey"
    
    # The seller information can be calculated by the provided verification key or hardcoded.

    # SELLER_ADDR = trx.get_address_from_vkey("/path/to/seller/payment.vkey")
    SELLER_ADDR = "SELLER_ADDRESS_HERE"
    
    # The script address can be computed from the compiled Plutus script or hardcoded.
    PLUTUS_SCRIPT_PATH = "/path/to/compiled/contract/plutus.script"
    # SCRIPT_ADDR   = trx.get_script_address(PLUTUS_SCRIPT_PATH)
    SCRIPT_ADDR   = ""

    # Tmp folder for transactions - This stores protocol params, etc
    TMP = "/path/to/tmp/folder/"

    # Token Name and Cost
    COST       = 25000000
    COLLATERAL = 17000000

    # Calculate the "fingerprint"
    POLICY_ID  = "policy_id_here"
    TOKEN_NAME = "token_name_here"
    FINGERPRINT = trx.get_token_identifier(POLICY_ID, TOKEN_NAME) # Not real fingerprint but works
    DATUM_HASH  = trx.get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
    print('Datum Hash: ', DATUM_HASH)
```