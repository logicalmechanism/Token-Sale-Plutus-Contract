# The Token Sale

This is a the guide to the token sale smart contract.

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
The example above forces the buyer to pay the 10 ADA to the sellers address in order for the buyer to spend the token utxo. The buyer tx occurs at once, paying the seller and retrieving the token.

## Compiling the plutus script

Inside the smartcontract folder will be the cabal.project file, from within this directory run the commands below. Be sure your ghc is at 8.10.4.

```bash
cabal clean
cabal build
cabal run token-sale
```
To make changes to the contract (such as creating a new one with a different seller address hash or price), make sure you've moved your previous .plutus script file (and saved a backup of your src/TokenSale.hs source file), then from the smartcontract directory issue:

```bash
cabal build
cabal run token-sale
```

The initial build may take a while depending on your Internet speed. 

After the `run` command, the smart contract script file will have been exported as tokensale.plutus

To get the smart contract address use the cardano-cli command below.

```bash
cardano-cli address build --mainnet --payment-script-file FILE # Filepath of the plutus script.
```

## Using The Token Sale Python Scripts

The token sale python scripts inside the pythonscripts folder of the repository are modified from the original to prompt the seller or buyer for input. Both scripts have a collateral set to 2 ADA. The seller or buyer should create a UTxO in their wallet containing this collateral before they run the script.

Each script will require user input. Instead of having the scripts auto complete it prompts the user to check the UTxO out, Datum hash, and the built transaction. If the information is correct the user can enter a confirmation to proceed with the transaction, submitting it to the blockchain.
