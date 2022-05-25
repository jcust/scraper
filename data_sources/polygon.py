import re
import requests

from enum import Enum
from bs4 import BeautifulSoup


class IdxApi(Enum):
    SCAN = "https://api.polygonscan.com"
    VCON = "https://polygonscan.com/contractsVerified"

    def __str__(self):
        return str(self.value)


def get_verified_contracts(
    host: IdxApi = IdxApi.VCON, pages: int = 5, records: int = 100
) -> str:
    for page in range(1, pages + 1):
        response = requests.get(f"{host}/{page}?ps={records}").text
        soup = BeautifulSoup(response, "html.parser")
        rows = soup.select("tbody tr")
        for row in rows:
            contract = row.find_all("td")
            name = contract[1].text.strip()
            address = contract[0].text.strip()
            yield {"contract_name": name, "address": address}


def get_contract_details(address: str, api_key: str, host: IdxApi = IdxApi.SCAN):
    # print("querying url")
    response = requests.get(
        f"{host}/api?module=contract&action=getsourcecode&address={address}&apikey={api_key}"
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


# def get_all_filtered(filter_string: str, api_key: str) -> str:
#     filtered = []
#     for i in get_verified_contracts():
#         time.sleep(0.22)  # brief pause so we don't hit free tier rate limit (5/second)
#         source = get_source_code(i["address"], api_key)
#         if filter_source_code(source, filter_string):
#             print(f"{i['address']} contains {filter_string}")
#             filtered.append(i["address"])
#     return filtered
