from brownie import Box, network, exceptions
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

# Verifying an already deployed contract
def verify_contract(_contract, _address):
    print(f"Verifying contract at address {_address} ...")
    account = get_account()
    contract = _contract.at(_address)
    try:
        _contract.publish_source(contract)
        print(f"Contract at address {_address} verified successfully.")
    except ValueError as e:
        print(e)


def main():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        verify_contract(Box, Box[-1].address)
