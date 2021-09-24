# Cardano Simple Token Sale Smart Contract

Forked from https://github.com/logicalmechanism/Token-Sale-Plutus-Contract, this project is simplified down and has been modified to just a Cardano Plutus smart contract for a token sale, based on the original code from upstream, and a simplified and modified pair of Python scripts for the seller and buyer.

# Usage

The smart contract itself needs to be compiled with the appropriate seller's address key-hash and the price for the token to be sold, in lovelace. Once compiled to a .plutus script, the seller (and later the buyer) use the provided Python script to perform a transaction (sell or buy). The Python scripts request input, so they are pretty self-explanatory. 

## Finding the public key hash

The user will be required to get the pubKeyHash using the cardano-cli. This will be used to name the folder inside the contracts folder.

```bash
cardano-cli address key-hash --payment-verification-key-file FILE # Filepath of the payment verification key.
# or use this command depending on the use case
cardano-cli address key-hash --payment-verification-key STRING    # Payment verification key (Bech32-encoded)
# For additional help please check out: cardano-cli address key-hash --help
```

# How the contract works

The contract is very simple. To spend the UTxo of the token inside the smart contract. The buyer will attach the correct Datum and will create two UTxOs. One UTxo will go directly to the seller with the predefined lovelace amount and the other UTxo will be the token being sent to the buyer's address. The datum value is known before hand because it follows the standard of hashing the hash of the concatentation of the policy id and token name. Please refer to scripts/transaction.py file, 

```python
FINGERPRINT = get_token_identifier(policy_id, token_name)
DATUM_HASH  = get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
```

NOTE: Tokens inside these smart contracts can only be removed with a succesful validation i.e. the token must be purchased. If a seller wants to remove their token from a smart contract then they must purchase the token from themselves.
