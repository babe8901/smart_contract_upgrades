from scripts.helpful_scripts import get_account, encode_function_data
from brownie import (
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    network,
    config,
)


def test_proxy_delegate_calls():
    account = get_account()
    box = (
        Box[-1]
        if len(Box) != 0
        else Box.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )
    proxy_admin = (
        ProxyAdmin[-1]
        if len(ProxyAdmin) != 0
        else ProxyAdmin.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )
    box_encoded_initializer_funtion = encode_function_data()
    proxy = (
        TransparentUpgradeableProxy[-1]
        if len(TransparentUpgradeableProxy) != 0
        else TransparentUpgradeableProxy.deploy(
            box.address,
            proxy_admin.address,
            box_encoded_initializer_funtion,
            {"from": account, "gas_limit": 1000000},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    assert proxy_box.retrieve() == 0
    proxy_box.store(1, {"from": account})
    assert proxy_box.retrieve() == 1
