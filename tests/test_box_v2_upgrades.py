from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    ProxyAdmin,
    exceptions,
    TransparentUpgradeableProxy,
    BoxV2,
    Contract,
    network,
    config,
)
import pytest


def test_proxy_upgrades():
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
    box_encoded_initializer_function = encode_function_data()
    proxy = (
        TransparentUpgradeableProxy[-1]
        if len(TransparentUpgradeableProxy) != 0
        else TransparentUpgradeableProxy.deploy(
            box.address,
            proxy_admin,
            box_encoded_initializer_function,
            {"from": account, "gas_limit": 1000000},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )

    box_v2 = (
        BoxV2[-1]
        if len(BoxV2) != 0
        else BoxV2.deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})

    upgrade(account, proxy, box_v2, proxy_admin_contract=proxy_admin)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
