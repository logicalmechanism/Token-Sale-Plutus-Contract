# The Royalty Sale Guide

This is the guide to using the royalty smart contract.

Each smart contract addition must follow these folder layouts to be added into the smart contract folder.

```
pubKeyHash_lovelaceAmount/
    ->  dist-newstyle/
    ->  token-sale-with-royalty/
            ->  app/
                ->  token-sale-with-royalty.hs
            ->  src/
                ->  TokenSaleWithRoyalty.hs
            ->  token_sale_with_royalty.plutus
            ->  token-sale-with-royalty.cabal
    ->  .gitignore
    ->  cabal.project
    ->  royalty.amt
    ->  payment.vkey
    ->  artist.vkey
```
## The Haskell to change

Look for this section of code inside the token-sale-with-royalty/src/TokenSaleWithRoyalty.hs file, starts around line 134. The file to be edited should be inside the folder copied into the contracts folder. Please only change the values of the seller address and the cost.

The default file:

```hs
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "SELLER_PUB_KEY_HASH_HERE" -- update to new seller
                               , tsRoyaltyAddress = pubKeyHashAddress "ARTIST_PUB_KEY_HASH_HERE" -- get original artist
                               , tsCost           = TOTAL_LOVELACE_COST_HERE                     -- Token Cost
                               , tsRoyalty        = ROYALTY_AMOUNT_HERE                          -- royalty  = 1 / % of returns
                               }
```                               

An example of a properly filled out plutus script:

```hs
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "d3fb616e18dcb9476f5167ab60b14a6954a14e0ad650cfa864d05d41" -- update to new seller
                               , tsRoyaltyAddress = pubKeyHashAddress "a26dbea4b3297aafb28c59772a4ef2964ebffb3375b5de313947e6c8" -- get original artist
                               , tsCost           = 35000000                                                                     -- Token Cost
                               , tsRoyalty        = 10                                                                           -- royalty  = 1 / % of returns
                               }
```
The example above forces the buyer to pay the 35 ADA to the sellers address and 3.5 ADA to the original artist's address before the buyer can spend the token utxo. The total price is 35 ADA and the royalty is 10% of the total price.

## Compiling the plutus script

Inside the pubKeyHash_lovelaceAmount folder will be the cabal.project file and the token-sale-with-royalty directory. Change the directory into token-sale-with-royalty and run the commands below.

```bash
cabal clean
cabal build -w ghc-8.10.4
cabal run token-sale-with-royalty
```

This will produce a compiled plutus script.

The folder should be named correctly and contain haskell code that when compiled following the instructions above will result in the correct plutus script. A correctly named folder will have the format pubKeyHash_lovelaceAmount.

To get the smart contract address use the cardano-cli command below.

```bash
cardano-cli address build --mainnet --payment-script-file FILE # Filepath of the plutus script.
```

To get the wallet address from a verificaiton key use the cardano-cli command below.

```bash
cardano-cli address build --mainnet --payment-verification-key-file FILE # Filepath of the plutus script.
```

All additions that follow the format and can be compiled into the correct Plutus script will be added into the repository.

## Using The Royalty Sale Python Scripts

The royalty sale python scripts inside the scripts folder of the repository are designed to be either hardcoded with addresses and paths or copied into seperate folders so the cli wallets can be accessed with ease. The scripts require the user to find the policy id and the token name to be sold. 

Each script will require user input. Instead of having the scripts auto complete it prompts the user to check the UTxO out, Datum hash, and any other data associated with the transaction. If the information is correct the user can enter a confirmation to proceed with the transaction, submitting it to the blockchain.