#!/usr/bin/env python3
import os
import sys
import time
import argparse
import data_sources.polygon as pg

from web3.exceptions import ABIFunctionNotFound


def parser_args():
    parser = argparse.ArgumentParser(description="Smart contract scraper")

    parser.add_argument("-k", "--key", dest="api_key", type=str, help="set API key")
    contract_group = parser.add_mutually_exclusive_group()
    contract_group.add_argument(
        "--contract",
        nargs="*",
        metavar="ADDRESS",
        type=str,
        help="query one or more specific contracts. if used, requires one of the arguments -s -a -d -f",
    )
    contract_group.add_argument(
        "-q",
        "--query",
        nargs=1,
        metavar="STRING",
        type=str,
        help="get verified contracts that contain the given string",
    )

    group = parser.add_mutually_exclusive_group(required="--contract" in sys.argv)
    group.add_argument(
        "-s",
        "--source",
        action="store_const",
        dest="opts",
        const="s",
        help="get source code for one or more contract addresses",
    )
    group.add_argument(
        "-a",
        "--abi",
        action="store_const",
        dest="opts",
        const="a",
        help="get ABI for one or more contract addresses",
    )
    group.add_argument(
        "-d",
        "--description",
        action="store_const",
        dest="opts",
        const="d",
        help="get the description for one or more contract addresses",
    )
    group.add_argument(
        "-f",
        "--functions",
        action="store_const",
        dest="opts",
        const="f",
        help="get functions found in one or more contract's source code",
    )
    group.add_argument(
        "-u",
        "--usable",
        action="store_const",
        dest="opts",
        const="u",
        help="return only contracts that have remaining mintable supply and aren't whitelist only",
    )
    # TODO: save to file
    # parser.add_argument("-o", "--output", metavar="PATH", help="save output to a file")

    return parser.parse_args()


def main():
    args = parser_args()

    if os.getenv("NODE_API_KEY"):
        NODE_API_KEY = os.getenv("NODE_API_KEY")
    else:
        print(f"Missing node API key, recommend setting NODE_API_KEY env var.\n")
        NODE_API_KEY = input("Enter node API key:\n")

    if os.getenv("NODE_ENDPOINT"):
        NODE_ENDPOINT = os.getenv("NODE_ENDPOINT")
    else:
        NODE_ENDPOINT = "https://polygon-mainnet.g.alchemy.com/v2/"

    if args.api_key:
        API_KEY = args.api_key
    elif os.getenv("POLYGON_API_KEY"):
        API_KEY = os.getenv("POLYGON_API_KEY")
    else:
        print(
            f"Missing PolygonScan API key, recommend setting POLYGON_API_KEY env var.\n"
        )
        API_KEY = input("Enter PolygonScan API key:\n")

    # get list of contract addresses to query
    if args.contract:
        print("args contain contracts, setting contract addresses")
        contracts = args.contract
    else:
        # if --contracts arg is not passed, get verified contracts from polygonscan
        print("no contract addresses specified, retrieving verified contracts")
        contracts = [c for c in pg.get_verified_contracts()]

    for c in contracts:
        try:
            address = c["address"]
            contract_name = c["contract_name"]
        except TypeError:
            address = c
            contract_name = "?"

        time.sleep(0.22)  # brief pause so we don't hit free tier rate limit (5/second)
        result = pg.get_contract_details(address, API_KEY)
        source = result["SourceCode"]

        if args.query:
            if not pg.filter_source_code(source, args.query[0]):
                # print(f"NOT FOUND: string '{args.query[0]}'")
                continue
            else:
                print(f"FOUND: string '{args.query[0]}'")

        print(f"\nADDRESS {address} (NAME: {contract_name})\n")
        if args.opts == "a":
            abi = result["ABI"]
            print(f"{abi}\n")
        elif args.opts == "d":
            desc = pg.get_description(source)
            print(f"{desc}\n")
        elif args.opts == "f":
            funcs = pg.get_contract_functions(source)
            [print(func) for func in funcs]
            print("\n")
        elif args.opts == "s":
            print(f"{source}\n")
        elif args.opts == "u":
            abi = result["ABI"]
            whitelist_terms = [
                "onlywhitelist",
                "onlywhitelisted",
                "whitelistonly",
                "whitelistedonly",
                "onlyallowlist",
                "onlyallowlisted",
                "allowlistonly",
                "allowlistedonly",
            ]
            # supply = {"totalSupply": "", "maxSupply": "", "supply": ""}
            supply_terms = ["totalSupply", "maxSupply", "supply"]
            supply = []

            # check source code for strings in whitelist_terms
            if any(wl in whitelist_terms for wl in source):
                print(f"whitelist term found in ADDRESS {address}, skipping.")
                continue

            # check supply vars
            contract = pg.Contract(address, abi, NODE_ENDPOINT, NODE_API_KEY)
            # for k in supply:
            #     supply[k] = contract.call_func(k)
            #     print(f"{k}: {supply[k]}")

            for s in supply_terms:
                try:
                    v = contract.call_func(s)
                    supply.append(v)
                    print(f"{s}: {v}")
                except ABIFunctionNotFound:
                    print(f"function {s} not present in contract")
                    pass

            try:
                if supply[0] == supply[1]:
                    print(
                        f"supply parameter values are the same, assuming no supply remaining."
                    )
                    print("max supply has been reached, skipping.")
                    continue
            except IndexError:
                print(
                    f"MANUAL CHECK NEEDED: contract {address} contains less than two of the defined 'supply' variables, can't determine if usable"
                )
                continue

            print(f"USABLE CONTRACT: ADDRESS {address}\n")


if __name__ == "__main__":
    main()
