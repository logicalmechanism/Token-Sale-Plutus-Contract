{-# LANGUAGE DataKinds             #-}
{-# LANGUAGE DeriveAnyClass        #-}
{-# LANGUAGE DeriveGeneric         #-}
{-# LANGUAGE DerivingStrategies    #-}
{-# LANGUAGE FlexibleContexts      #-}
{-# LANGUAGE NoImplicitPrelude     #-}
{-# LANGUAGE NamedFieldPuns        #-}
{-# LANGUAGE OverloadedStrings     #-}
{-# LANGUAGE ScopedTypeVariables   #-}
{-# LANGUAGE TemplateHaskell       #-}
{-# LANGUAGE TypeApplications      #-}
{-# LANGUAGE TypeFamilies          #-}
{-# LANGUAGE TypeOperators         #-}
{-# LANGUAGE MultiParamTypeClasses #-}

module TokenSaleWithRoyalty
  ( tokenSaleWithRoyaltyScript
  , tokenSaleWithRoyaltyScriptShortBs
  ) where

import           Codec.Serialise
import           Plutus.V1.Ledger.Contexts
import qualified PlutusTx
import           Cardano.Api.Shelley      (PlutusScript (..), PlutusScriptV1)
import           Prelude                  hiding (($))
import qualified Data.ByteString.Lazy     as LBS
import qualified Data.ByteString.Short    as SBS
import qualified Plutus.V1.Ledger.Scripts as Plutus
import qualified Ledger.Typed.Scripts     as Scripts
import           Ledger.Ada               as Ada
import           PlutusTx.Prelude         as P hiding (Semigroup (..), unless)
import           Ledger                   hiding (singleton)
{-
  A simple on-chain royalty contract. Using a seller address and royalty address.
  The seller vkey and royalty vkey must be public such that this script can be 
  compiled by any buyer to confirm authencity. The Cost is the total ADA payment
  such that the royalty will be included in the price.
  
  { tsSellerAddress  = pubKeyHashAddress "SELLERPUBKEYHERE"
  , tsRoyaltyAddress = pubKeyHashAddress "ARTISTPUBKEYHERE"
  , tsCost           = TOTALCOST
  , tsRoyalty        = ROYALTY -- royalty  = 1 / % of returns
  }
-}
data TokenSaleParams = TokenSaleParams
    { tsSellerAddress  :: !Address
    , tsRoyaltyAddress :: !Address
    , tsCost           :: !Integer
    , tsRoyalty        :: !Integer
    }
PlutusTx.makeLift ''TokenSaleParams


-- mkValidator :: Data -> () -> () -> Ctx -> Bool
{-# INLINABLE mkValidator #-}
mkValidator :: TokenSaleParams -> BuiltinData -> BuiltinData -> ScriptContext -> Bool
mkValidator ts _ _ context
    | (contextCostCheck currentTxOutputs) P.&& (contextRoyaltyCheck currentTxOutputs) = True  -- Buyer can remove trx from wallet
    | otherwise                                                                       = False -- Fail otherwise
    where

      info :: TxInfo
      info = scriptContextTxInfo context

      currentTxOutputs :: [TxOut]
      currentTxOutputs = txInfoOutputs info

      tokenCost :: Integer
      tokenCost = (tsCost ts)

      tokenRoyalty :: Integer
      tokenRoyalty = tsRoyalty ts
      
      royaltyPaymentCost :: Integer
      royaltyPaymentCost = P.quotient tokenCost tokenRoyalty

      sellerAddress :: Address
      sellerAddress = tsSellerAddress ts

      royaltyAddress :: Address
      royaltyAddress = tsRoyaltyAddress ts
      
      -------------------------------------------------------------------------------
      -- Functions for Checking the Token Cost
      ------------------------------------------------------------------------------
      
      -- This checks if an output transaction contains the correct seller payment in ADA.
      contextCostCheck :: [TxOut] -> Bool
      contextCostCheck [] = traceIfFalse "Incorrect Amount Of ADA Sent To Script Address" $ False
      contextCostCheck (x:xs)
        | ((txOutAddress x) P.== sellerAddress) P.&& ((txOutValue x) P.== (Ada.lovelaceValueOf tokenCost)) = True
        | otherwise = contextCostCheck xs
      
      ------------------------------------------------------------------------------
      -- Functions for Checking the Token Royalty
      ------------------------------------------------------------------------------   
      
      -- This checks if an output transaction contains the royalty payment in ADA.
      contextRoyaltyCheck :: [TxOut] -> Bool
      contextRoyaltyCheck [] = traceIfFalse "Incorrect Amount Of ADA Sent To Script Address" $ False
      contextRoyaltyCheck (x:xs)
        | ((txOutAddress x) P.== royaltyAddress) 
          P.&& 
          ((txOutValue x) P.== (Ada.lovelaceValueOf royaltyPaymentCost)) = True
        | otherwise = contextRoyaltyCheck xs


-- This determines the data type for Datum and Redeemer.
data Typed
instance Scripts.ValidatorTypes Typed where
    type instance DatumType    Typed = BuiltinData
    type instance RedeemerType Typed = BuiltinData


-- Now we need to compile the Typed Validator.
typedValidator :: TokenSaleParams -> Scripts.TypedValidator Typed
typedValidator ts = Scripts.mkTypedValidator @Typed
    ($$(PlutusTx.compile [|| mkValidator ||]) `PlutusTx.applyCode` PlutusTx.liftCode ts)
    $$(PlutusTx.compile  [|| wrap        ||]) -- Define wrap below
  where
    wrap = Scripts.wrapValidator @BuiltinData @BuiltinData -- @Datum @Redeemer

{-
  Given the vkey for the payment address this confirms the hash:

  cardano-cli address key-hash --payment-verification-key-file FILE
-}

-------------------------------------------------------------------------------
-- Define The Token Sale Parameters Here
-------------------------------------------------------------------------------
validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "d3fb616e18dcb9476f5167ab60b14a6954a14e0ad650cfa864d05d41" -- update to new seller
                               , tsRoyaltyAddress = pubKeyHashAddress "a26dbea4b3297aafb28c59772a4ef2964ebffb3375b5de313947e6c8" -- get original seller
                               , tsCost           = 35000000                                                                     -- Token Cost
                               , tsRoyalty        = 10                                                                           -- royalty  = 1 / % of returns
                               }


-------------------------------------------------------------------------------
-- The code below is required for the plutus script compile
-- DO NOT REMOVE
script :: Plutus.Script
script = Plutus.unValidatorScript validator

tokenSaleWithRoyaltyScriptShortBs :: SBS.ShortByteString
tokenSaleWithRoyaltyScriptShortBs = SBS.toShort . LBS.toStrict $ serialise script

tokenSaleWithRoyaltyScript :: PlutusScript PlutusScriptV1
tokenSaleWithRoyaltyScript = PlutusScriptSerialised tokenSaleWithRoyaltyScriptShortBs