#!/usr/bin/env python3
import os
import sys
import time
import argparse
import data_sources.polygon as pg


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
    # TODO: save to file
    # parser.add_argument("-o", "--output", metavar="PATH", help="save output to a file")

    return parser.parse_args()


def main():
    args = parser_args()

    # set api key
    if args.api_key:
        API_KEY = args.api_key
    else:
        API_KEY = os.getenv("POLYGON_API_KEY")

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


if __name__ == "__main__":
    main()
