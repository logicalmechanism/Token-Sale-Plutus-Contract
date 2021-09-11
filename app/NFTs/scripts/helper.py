import os
import subprocess
import base64
import requests

def blockfrost_api_key():
    path = os.getcwd() + '/NFTs/blockfrost/api.key'
    # print(os.path.isfile(path))
    try:
        with open(path, "r") as read_content:
            api_key = read_content.read().splitlines()[0]
    except IndexError:
        api_key = ''
    # print('apikey', api_key)
    return api_key


def concat_pid_and_tkn(pid, tkn):
    return pid + token_name_to_hex_name(tkn)

def get_onchain_metadata(concat_of_policyID_and_tokenName):
    response = requests.get(
        'https://cardano-mainnet.blockfrost.io/api/v0/assets/{}'.format(concat_of_policyID_and_tokenName),
        headers={'project_id': blockfrost_api_key(),}
    )
    # print(response.json())
    try:
        metadata = response.json()['onchain_metadata']
    except KeyError:
        metadata = 'No Metadata'
    return metadata

def get_ipfs_image_from_metadata(concat_of_policyID_and_tokenName):
    # print(concat_of_policyID_and_tokenName)
    metadata = get_onchain_metadata(concat_of_policyID_and_tokenName)
    try:
        image = metadata['image']
        # print(image)
    except (KeyError, TypeError):
        # print('\nNo IPFS can be found.')
        image=''
    return image


def get_image(pid, token):
    # print(pid + token_name_to_hex_name(token))
    image = get_ipfs_image_from_metadata(pid+ token_name_to_hex_name(token))
    image = image.replace('ipfs://', 'https://ipfs.io/ipfs/')
    return image


def token_name_to_hex_name(token_name):
    hex_name = base64.b16encode(bytes(str(token_name).encode('utf-8'))).lower().decode('utf-8')
    # print(hex_name)
    return hex_name
