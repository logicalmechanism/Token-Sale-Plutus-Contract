import NFTs.scripts.transaction as trx

# May need to type this into terminal before starting
# CARDANO_NODE_SOCKET_PATH=./state-node-testnet/node.socket ./cardano-cli/bin/cardano-cli address key-hash --payment-verification-key-file FILE
# CARDANO_NODE_SOCKET_PATH=../state-node-alonzo-purple/node.socket


def start_royalty(tmp, wallet_skey_path, wallet_addr, script_addr, datum_hash, policy_id, token_name, collateral, flag):
    print('\nSTART OF STARTING ROYALTY SALE CONTRACT')
    print(policy_id)
    print(token_name)

    trx.delete_contents(tmp)
    trx.protocol(tmp, flag)
    trx.utxo(wallet_addr, tmp, 'utxo.json', flag)
    
    utxo_in, utxo_col, currencies, collat_flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    
    if collat_flag is True:
        _, final_tip, block = trx.tip(tmp, flag)
        
        # Order matters
        # print(currencies)
        utxo_out = trx.asset_change(tmp, currencies, wallet_addr, [policy_id, token_name])
        utxo_out += trx.asset_change(tmp, currencies, script_addr, [policy_id, token_name], False)
        additional_data = [
            '--tx-out-datum-hash', datum_hash
        ]
        
        # print('BLOCK:', block)
        # print(utxo_out)
        trx.build(tmp, wallet_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data, flag)
        
        signers = [
            '--signing-key-file',
            wallet_skey_path,
        ]
        trx.sign(tmp, signers, flag)
        trx.submit(tmp, flag)
        print('\nEND OF STARTING ROYALTY SALE CONTRACT\n')

    else:
        print("SPLIT UP UTXO")
