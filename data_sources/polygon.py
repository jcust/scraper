import re
import requests

from enum import Enum
from bs4 import BeautifulSoup

from web3 import Web3, HTTPProvider, exceptions
from web3.middleware import geth_poa_middleware


class IdxApi(Enum):
    SCAN = "https://api.polygonscan.com"
    VCON = "https://polygonscan.com/contractsVerified"

    def __str__(self):
        return str(self.value)


class Contract:
    def __init__(self, address, abi, node, api_key):

        web3 = Web3(HTTPProvider(node + api_key))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        try:
            self.contract = web3.eth.contract(address=address, abi=abi)
        except exceptions.InvalidAddress:
            # some of the contracts from the verified contracts page are
            # non-checksum addresses - not sure if best to skip over or convert
            checksum_address = Web3.toChecksumAddress(address)
            self.contract = web3.eth.contract(address=checksum_address, abi=abi)

        self._contract_funcs = self.contract.all_functions()

    # has to be exact match, was hoping this would any functions that match string
    def find_funcs_by_name(self, func):
        return self.contract.find_functions_by_name(func)

    def call_func(self, func: str):
        # f = getattr(self.contract.functions, func)
        f = self.contract.functions[func]
        return f().call()

    @property
    def funcs(self):
        return self._contract_funcs


def get_verified_contracts(
    host: IdxApi = IdxApi.VCON, pages: int = 10, records: int = 50
) -> str:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"
    }
    session = requests.Session()
    for page in range(1, pages + 1):
        # print(f"getting page {page} from verifiedcontracts page")
        response = session.get(
            f"{host}/{page}?ps={records}", timeout=15, headers=headers
        ).text
        # print(f"got page {page} from verifiedcontracts page")
        soup = BeautifulSoup(response, "html.parser")
        rows = soup.select("tbody tr")
        row_count = 0
        for row in rows:
            row_count += 1
            # print(f"parsing row {row_count}")
            contract = row.find_all("td")
            name = contract[1].text.strip()
            address = contract[0].text.strip()
            # print(f"finished parsing row {row_count}")
            yield {"contract_name": name, "address": address}


def get_contract_details(
    session: requests.Session, address: str, api_key: str, host: IdxApi = IdxApi.SCAN
):
    # print("querying url")
    session = session
    response = session.get(
        f"{host}/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}",
        timeout=15,
    ).json()
    if response["status"] == "1":
        # print("status is 1")
        result = response["result"][0]
        return result
    else:
        # print("status is not 1")
        raise Exception(response["result"])


def get_abi(address: str, api_key: str) -> str:
    return get_contract_details(address, api_key)["ABI"]


def get_source_code(address: str, api_key: str) -> str:
    return get_contract_details(address, api_key)["SourceCode"]


def filter_source_code(code: str, filter_string: str):
    if filter_string in code:
        return True


# def is_whitelist_only():
#     whitelist_terms = [
#         "onlywhitelist",
#         "onlywhitelisted",
#         "whitelistonly",
#         "whitelistedonly",
#         "onlyallowlist",
#         "onlyallowlisted",
#         "allowlistonly",
#         "allowlistedonly",
#     ]


# need to find a better way to do this since not all contracts have description at the top
def get_description(code: str) -> str:
    index = code.find("pragma solidity")
    return code[:index]


def get_contract_functions(code: str) -> str:
    functions = []
    for line in code.split("\n"):
        if re.search(r"^ {2,}function ", line):
            functions.append(line.strip(" ").split("(")[:1][0])
    return functions
