# Application Guide

This is the guide to using the GUI application to interact with the smart contracts.

## Requirements

- cardano-node
- cardano-cli
- python3
- django 3.2
- blockfrost api key

The app must have a synced cardano-node with the node.socket on path and cardano-cli on path. The application is designed for python3 and django 3.2. The required python modules are contained in the requirements.txt file. It is suggested to use a virtual environment to avoid version conflicts.

Inside the app folder there two folders that require additional files to be added. 

The folder app/NFTs/wallet/ will contain the vkey and skey for a CLI wallet. 
NOTE: This app is non custodial. At no point is there any way to upload the wallet files to any server. You are always in control of the wallet.

The file app/NFTs/blockfrost/api.key needs a mainnet api key. This will allow the app to query the metadata of tokens and display the images inside your wallet and in the marketplace.

When the cardano-node is running and fully synced run:

```bash
python manage.py runserver
# if python3 is required
python3 manage.py runserver
```

Open your browser go to http://127.0.0.1:8000/

If everything works, you will see all available tokens for sale inside the valid smart contracts.

### PLEASE USE AT YOUR OWN RISK!