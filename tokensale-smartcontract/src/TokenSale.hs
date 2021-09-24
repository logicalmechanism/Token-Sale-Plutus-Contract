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

data TokenSaleParams = TokenSaleParams
    { tsSellerAddress  :: !Address
    , tsCost           :: !Integer
    }
PlutusTx.makeLift ''TokenSaleParams

{-# INLINABLE mkValidator #-}
mkValidator :: TokenSaleParams -> BuiltinData -> BuiltinData -> ScriptContext -> Bool
mkValidator ts _ _ context
    | (contextCostCheck currentTxOutputs) = True
    | otherwise                           = traceIfFalse "Incorrect Tx To Script Address" $ False
    where

      info :: TxInfo
      info = scriptContextTxInfo context

      currentTxOutputs :: [TxOut]
      currentTxOutputs = txInfoOutputs info

      tokenCost :: Integer
      tokenCost = tsCost ts

      sellerAddress :: Address
      sellerAddress = tsSellerAddress ts

      contextCostCheck :: [TxOut] -> Bool
      contextCostCheck [] = traceIfFalse "Incorrect Amount Of ADA Sent To Script Address" $ False
      contextCostCheck (x:xs)
        | ((txOutAddress x) P.== sellerAddress) P.&& ((txOutValue x) P.== (Ada.lovelaceValueOf tokenCost)) = True
        | otherwise = contextCostCheck xs

data Typed
instance Scripts.ValidatorTypes Typed where
    type instance DatumType    Typed = BuiltinData
    type instance RedeemerType Typed = BuiltinData

typedValidator :: TokenSaleParams -> Scripts.TypedValidator Typed
typedValidator ts = Scripts.mkTypedValidator @Typed
    ($$(PlutusTx.compile [|| mkValidator ||]) `PlutusTx.applyCode` PlutusTx.liftCode ts)
    $$(PlutusTx.compile  [|| wrap        ||])
  where
    wrap = Scripts.wrapValidator @BuiltinData @BuiltinData

validator :: Plutus.Validator
validator = Scripts.validatorScript (typedValidator ts)
    where ts = TokenSaleParams { tsSellerAddress  = pubKeyHashAddress "hash_of_seller_cardano_address" -- Change to key-hash of seller address
                               , tsCost           = 10000000 -- Change to price in lovelace
                               }

script :: Plutus.Script
script = Plutus.unValidatorScript validator

tokenSaleScriptShortBs :: SBS.ShortByteString
tokenSaleScriptShortBs = SBS.toShort . LBS.toStrict $ serialise script

tokenSaleScript :: PlutusScript PlutusScriptV1
tokenSaleScript = PlutusScriptSerialised tokenSaleScriptShortBs
