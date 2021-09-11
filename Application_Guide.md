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

## Things I Have Noticed

Each image is loaded with IPFS. Sometimes it can take a while to query every metadata image and then load it. Please be wait for images to load. It may be better to load the CLI wallet with only the tokens that will be sold that way it will reduce the load time for each image. In the future this will have to be accounted for when there are many smart contracts in use inside the marketplace.

This is an alpha test so please be kind. Smart contracts are very new and Plutus development is a challenge. 

### PLEASE USE AT YOUR OWN RISK!