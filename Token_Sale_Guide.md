# The Token Sale

This is a the guide to the token sale smart contract.

Each smart contract addition must follow these folder layouts to be added into the smart contract folder.

```
pubKeyHash_lovelaceAmount/
    ->  dist-newstyle/
    ->  token-sale/
            ->  app/
                ->  token-sale.hs
            ->  src/
                ->  TokenSale.hs
            ->  token_sale.plutus
            ->  token-sale.cabal
    ->  .gitignore
    ->  cabal.project
    ->  payment.vkey
```

The dist-newstyle folder will be auto ignored when added to the repository. The payment.vkey is the verification key for the token seller. The hash of this vkey file must match the pubKeyHash inside the folder name.

## The Haskell to change

Look for this section of code inside the token-sale/src/TokenSale.hs file, starts around line 109. The file to be edited should be inside the folder copied into the contracts folder. Please only change the values of the seller address and the cost.

The default file:

```hs
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "PUB_KEY_HASH_HERE" -- Put in the seller's pubkeyhash here
                               , tsCost           = INTEGER_PRICE_HERE                    -- Price for the token in lovelace
                               }
```                               

An example of a properly filled out plutus script:

```hs
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "a26dbea4b3297aafb28c59772a4ef2964ebffb3375b5de313947e6c8" -- put in the seller address here
                               , tsCost           = 10000000                                                                     -- Price for the token in lovelace
                               }
```
The example above forces the buyer to pay the 10 ADA to the sellers address before the buyer can spend the token utxo.

## Compiling the plutus script

Inside the folder will be the cabal.project file and the token-sale directory. Change the directory into token-sale and run the commands below.

```bash
cabal clean
cabal build -w ghc-8.10.4
cabal run token-sale
```

Depending on your computer speed this may take a little while.

The folder should be named correctly and contain haskell code that when compiled following the instructions above will result in the correct plutus script. A correctly named folder will have the format pubKeyHash_lovelaceAmount.

To get the smart contract address use the cardano-cli command below.

```bash
cardano-cli address build --mainnet --payment-script-file FILE # Filepath of the plutus script.
```

All additions that follow the format and can be compiled into the correct Plutus script will be added into the repository.

## Using The Token Sale Python Scripts

The token sale python scripts inside the scripts folder of the repository are designed to be either hardcoded with addresses and paths or copied into seperate folders so the cli wallets can be accessed with ease. The scripts require the user to find the policy id and the token name to be sold. 

Each script will require user input. Instead of having the scripts auto complete it prompts the user to check the UTxO out, Datum hash, and any other data associated with the transaction. If the information is correct the user can enter a confirmation to proceed with the transaction, submitting it to the blockchain.