# Token-Sale-Plutus-Contract

A repository of publicly verifiable token sale and royalty contracts. This will be the storage solution since it is easily attainable and usable. A more decentralized solution will come in the future but for now this will be the solution.

The repository will work in a very similar fashion to the Cardano Foundation's token registry. It will allow users to add their contribution to the repository so everyone can use a collection of trusted smart contracts. The goal is to create a micro-ecosystem of contracts that are simple enough to read and quick to compile.

To add a token sale contract to the repository: please fork the repo, add in the contract addition, public verification key, and compiled plutus script into the correct contracts folder following the directions below then use a pull request to add in your contribution into the smart contract repository when finished.

The folder containing the contract to be compiled will be placed in the correct contracts folder. The name of the folder will be the pubkeyhash, allowing a quick search method for a single seller, followed by an under score then the price of the shop in lovelace. Please see the example_token_sale_addition or example_royalty_sale_addition folders for an example additions.

# Usage

After forking the repo, clone the repo onto your system. Make a copy of the default folder into the correct contracts folder. Change the name of the copied folder into the pubKeyHash of the wallet that will be receiving payments for tokens sold followed by the price of tokens inside this contract. Additions will not be granted if the naming scheme is not followed. Place a copy of the wallets vkey, the public verification key, and any additional required information into the copied folder.

A user will only need to edit the token-sale/src/TokenSale.hs or token-sale-with-royalty/src/TokenSaleWithRoyalty.hs files. The haskell code requires only few changes, any other changes will result in a failed contract addition. The user will only need to update the pubkeyhash and the price of the tokens. After the changes are made to the TokenSale.hs or TokenSaleWithRoyalty.hs file, the user will need to compile the Haskell into Plutus such that other users can verify the correct output as well as have the correct plutus script file for usage.

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

```py
FINGERPRINT= get_token_identifier(policy_id, token_name)
DATUM_HASH = get_hash_value('"{}"'.format(FINGERPRINT)).replace('\n', '')
```

NOTE: Tokens inside these smart contracts can only be removed with a succesful validation i.e. the token must be purchased. If a seller wants to remove their token from a smart contract then they must purchase the token from themselves.

# Using the App

The app is designed to be the frontend for interacting with the collection of smart contracts. The user has the choice of working with contracts by hand or by using the app provided in the app folder. The app is based around running a local webserver and displaying the tokens for sale in a convenient way. Please refer to the Application_Guide.md for more information.