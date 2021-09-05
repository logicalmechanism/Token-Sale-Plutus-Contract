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

module TokenSale
  ( tokenSaleScript
  , tokenSaleScriptShortBs
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
  Author: The Ancient Kraken
  
  A simple on-chain token sale contract. Using a seller address and a price.
  The seller vkey must be public such that this script can be 
  compiled by any buyer to confirm authencity.
  
  { tsSellerAddress  = pubKeyHashAddress "PUB_KEY_HASH_HERE"
  , tsCost           = INTEGER_PRICE_HERE
  }
-}
data TokenSaleParams = TokenSaleParams
    { tsSellerAddress  :: !Address
    , tsCost           :: !Integer
    }
PlutusTx.makeLift ''TokenSaleParams


-- mkValidator :: Data -> () -> () -> Ctx -> Bool
{-# INLINABLE mkValidator #-}
mkValidator :: TokenSaleParams -> BuiltinData -> BuiltinData -> ScriptContext -> Bool
mkValidator ts _ _ context
    | (contextCostCheck currentTxOutputs) = True                                                  -- Buyer can remove trx from wallet
    | otherwise                           = traceIfFalse "Incorrect Tx To Script Address" $ False -- Fail otherwise
    where

      info :: TxInfo
      info = scriptContextTxInfo context

      currentTxOutputs :: [TxOut]
      currentTxOutputs = txInfoOutputs info

      tokenCost :: Integer
      tokenCost = tsCost ts

      sellerAddress :: Address
      sellerAddress = tsSellerAddress ts

      -------------------------------------------------------------------------------
      -- Functions for Checking the Token Cost
      -------------------------------------------------------------------------------

      -- This checks if an output transaction contains the correct seller payment in ADA.
      contextCostCheck :: [TxOut] -> Bool
      contextCostCheck [] = traceIfFalse "Incorrect Amount Of ADA Sent To Script Address" $ False
      contextCostCheck (x:xs)
        | ((txOutAddress x) P.== sellerAddress) P.&& ((txOutValue x) P.== (Ada.lovelaceValueOf tokenCost)) = True
        | otherwise = contextCostCheck xs
      
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
--
-- This is the only code that can be change
-------------------------------------------------------------------------------

validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "PUBLIC_KEY_HASH_ADDRESS" -- put in the seller address here
                               , tsCost           = 1000000                               -- Price for the token in lovelace
                               }


-------------------------------------------------------------------------------
-- The code below is required for the plutus script compile
-- DO NOT REMOVE
script :: Plutus.Script
script = Plutus.unValidatorScript validator

tokenSaleScriptShortBs :: SBS.ShortByteString
tokenSaleScriptShortBs = SBS.toShort . LBS.toStrict $ serialise script

tokenSaleScript :: PlutusScript PlutusScriptV1
tokenSaleScript = PlutusScriptSerialised tokenSaleScriptShortBs