import transaction as trx

def end(tmp, wallet_name, wallet_addr, script_addr, cost, royalty, datum_hash, plutus_script,seller_addr,royalty_addr, token_name, collateral):
    trx.delete_contents(tmp)
    trx.protocol(tmp)
    trx.utxo(wallet_addr, tmp, 'utxo.json')
    utxo_in, utxo_col, currencies, flag, _ = trx.txin(tmp, 'utxo.json', collateral)
    if flag is True:
        trx.utxo(script_addr, tmp, 'utxo_script.json')
        _, _, script_currencies, _, data_list = trx.txin(tmp, 'utxo_script.json')
        contract_utxo_in = utxo_in
        for key in data_list:
            if data_list[key] == datum_hash:
                contract_utxo_in += ['--tx-in', key]
        _, final_tip, block = trx.tip(tmp)
        utxo_out = trx.asset_change(tmp, script_currencies, wallet_addr)
        utxo_out += trx.asset_change(tmp, currencies, wallet_addr) # Accounts for token change
        utxo_out += ['--tx-out', seller_addr+'+'+str(cost)]
        utxo_out += ['--tx-out', royalty_addr+'+'+str(royalty)]
        additional_data = [
            '--tx-out-datum-hash', datum_hash,
            '--tx-in-datum-value', '"{}"'.format(TOKEN_NAME),
            '--tx-in-redeemer-value', '""',
            '--tx-in-script-file', 'compiled-plutus-code/'+plutus_script
        ]
        print('BLOCK:', block)
        print(utxo_out)
        trx.build(tmp, wallet_addr, final_tip, contract_utxo_in, utxo_col, utxo_out, additional_data)
        signers = [
            '--signing-key-file',
            wallet_name + '/payment.skey',
        ]
        trx.sign(tmp, signers)
        trx.submit(tmp)
    else:
        print("SPLIT UP UTXO")

if __name__ == "__main__":
    BUYER_NAME = 'wallet-a'
    with open(BUYER_NAME + "/payment.addr", "r") as read_content: BUYER_ADDR = read_content.read().splitlines()[0]
    with open("wallet-c/payment.addr", "r") as read_content: SELLER_ADDR = read_content.read().splitlines()[0]
    with open("wallet-b/payment.addr", "r") as read_content: ROYALTY_ADDR = read_content.read().splitlines()[0]
    with open("contracts/royalty_sale.addr", "r") as read_content: SCRIPT_ADDR = read_content.read().splitlines()[0]
    #
    TMP = "tmp/"
    PLUTUS_SCRIPT = "token_sale_with_royalty.plutus"
    COLLATERAL = 17000000
    #
    COST = 35000000
    ROYALTY_RATIO = 10
    ROYALTY_COST = COST // ROYALTY_RATIO
    #
    TOKEN_NAME = "tokenC"
    DATUM_HASH = trx.get_hash_value('"{}"'.format(TOKEN_NAME)).replace('\n', '')
    end(TMP, BUYER_NAME, BUYER_ADDR, SCRIPT_ADDR, COST, ROYALTY_COST, DATUM_HASH, PLUTUS_SCRIPT, SELLER_ADDR, ROYALTY_ADDR, TOKEN_NAME, COLLATERAL)