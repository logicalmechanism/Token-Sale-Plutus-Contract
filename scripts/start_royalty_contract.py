import transaction as trx

# May need to type this into terminal before starting
# CARDANO_NODE_SOCKET_PATH=./state-node-testnet/node.socket ./cardano-cli/bin/cardano-cli address key-hash --payment-verification-key-file FILE
# CARDANO_NODE_SOCKET_PATH=../state-node-alonzo-purple/node.socket


def start_royalty(tmp, wallet_name, wallet_addr, script_addr, datum_hash):
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    utxo_in, utxo_col, currencies, flag, _ = trx.txin(tmp, 'utxo.json', 17000000)
    if flag is True:
        _, final_tip, block = trx.tip(tmp)
        # Order matters
        utxo_out = trx.asset_change(tmp, currencies, script_addr)
        additional_data = [
            '--tx-out-datum-hash', datum_hash
        ]
        print('BLOCK:', block)
        print(utxo_out)
        trx.build(tmp, wallet_addr, final_tip, utxo_in, utxo_col, utxo_out, additional_data)
        signers = [
            '--signing-key-file',
            wallet_name + '/payment.skey',
        ]
        trx.sign(tmp, signers)
        trx.submit(tmp)
    else:
        print("SPLIT UP UTXO")


# if __name__ == "__main__":
#     SELLER_NAME = 'wallet-c'
#     with open(SELLER_NAME + "/payment.addr", "r") as read_content: SELLER_ADDR = read_content.read().splitlines()[0]
#     # with open("contracts/royalty_sale.addr", "r") as read_content: SCRIPT_ADDR = read_content.read().splitlines()[0]
#     SCRIPT_ADDR = "addr_test1wqlkj8a4lge6df0scc57cg575nctkugucxyclfusgay5e2ge9zxzu"
#     TMP = "tmp/"
#     TOKEN_NAME = "tokenC"
#     DATUM_HASH = trx.get_hash_value('"{}"'.format(TOKEN_NAME)).replace('\n', '')
#     start(TMP, SELLER_NAME, SELLER_ADDR, SCRIPT_ADDR, DATUM_HASH)