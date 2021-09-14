import os
import subprocess
import base64
import requests


def blockfrost_api_key():
    """
    Retrieve the blockfrost API key from the api.key folder.
    Visit https://blockfrost.io/ to get an API key. They are free.
    """
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
    """
    Returns the concatentation of the policy id and the hex encoded token name.
    """
    return pid + token_name_to_hex_name(tkn)


def get_onchain_metadata(concat_of_policyID_and_tokenName):
    """
    Return the onchain metadata, the data used in the minting transaction, 
    using the blockfrost api. If the metadata can not be found then it will
    return a string that indicates there is no metadata available.
    """
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
    """
    Using the onchain metadata search for the token's image.
    """
    metadata = get_onchain_metadata(concat_of_policyID_and_tokenName)
    try:
        image = metadata['image']
    except (KeyError, TypeError):
        image=''
    return image


def get_image(pid, token):
    """
    Returns the IPFS url for the image inside a token's metadata.
    
    TODO: Download each image locally then serve them dynamically.
    The wait time for loading images is painful.
    """
    # print(pid + token_name_to_hex_name(token), token)
    image = get_ipfs_image_from_metadata(pid+ token_name_to_hex_name(token))
    image = image.replace('ipfs://', 'https://ipfs.io/ipfs/')
    # print(image)
    return image


def token_name_to_hex_name(token_name):
    """
    Returns the hex encoded, base 16, representation of the token name. This is
    used for the blockfrost api and token identification.
    """
    hex_name = base64.b16encode(bytes(str(token_name).encode('utf-8'))).lower().decode('utf-8')
    return hex_name
