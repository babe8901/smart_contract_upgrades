from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    network,
    config,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
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

    try:
        print(box.increment())
    except AttributeError as e:
        print(e)

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

    # initializer = box.store, 1
    box_encoded_initializer_function = encode_function_data()

    proxy = (
        TransparentUpgradeableProxy[-1]
        if len(TransparentUpgradeableProxy) != 0
        else TransparentUpgradeableProxy.deploy(
            box.address,
            proxy_admin.address,
            box_encoded_initializer_function,
            {"from": account, "gas_limit": 1000000},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")

    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account}).wait(1)
    print(proxy_box.retrieve())

    # proxy_box.increment({"from": account})

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
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)

    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account}).wait(1)
    print(proxy_box.retrieve())
