# Token-Sale-Plutus-Contract

A repository of publicly verifiable token sale contracts. This will be the storage solution since it is easily attainable and usable.

The repo will work in a very similar fashion to the Cardano Foundation's token registry.

Please fork the repo then add in the contract addition, public verification key, and compiled plutus script into the contracts folder following the directions below. Use a pull request to add in your contribution into the smart contract repo when finished.


The folder containing the contract to be compiled will be placed in the contracts folder. The name of the folder will be the pubkeyhash, allowing a quick search method for a single seller, followed by an under score then the price of the shop in lovelace. Please see the example_contract_addition folder for an example addition.


# Usage
After forking the repo, clone the repo onto your system. Make a copy of the default folder into the contracts folder. Change the name of the copy folder into the pubKeyHash of the wallet that will be receiving payments for tokens sold followed by the price of tokens inside this contract. Edit the token-sale/src/TokenSale.hs file.The haskell code requires only two changes. The user will need to update the pubkeyhash and the price of the tokens. After the changes are made the user will need to compile the haskell into plutus such that other users can verify the correct output as well as have the correct plutus script file for usage.

## Finding the public key hash

```bash
cardano-cli address key-hash --payment-verification-key-file FILE # Filepath of the payment verification key.
# or use this command depending on the use case
cardano-cli address key-hash --payment-verification-key STRING    # Payment verification key (Bech32-encoded)
# For additional help please check out: cardano-cli address key-hash --help
```

## The Haskell to change
Look for this section of code inside the token-sale/src/TokenSale.hs file. 

```hs
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "PUB_KEY_HASH_HERE" -- Put in the seller's pubkeyhash here
                               , tsCost           = INTEGER_PRICE_HERE                    -- Price for the token in lovelace
                               }
```                               

## Compiling the plutus script

Inside the folder will be the cabal.project file and the token-sale directory. Change the directory into token-sale and run the commands below.

```bash
cabal clean
cabal build -w ghc-8.10.4
cabal run token-sale
```

The folder should be named correctly and contain haskell code that when compiled following the instructions above will result in the correct plutus script.

To get the smart contract address use the cardano-cli command below.

```bash
cardano-cli address build --mainnet --payment-script-file FILE # Filepath of the plutus script.
```