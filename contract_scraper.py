#!/usr/bin/env python3
import os
import sys
import csv
import time
import argparse
import data_sources.polygon as pg

from requests import Session
from web3 import exceptions


def parser_args():
    parser = argparse.ArgumentParser(description="Smart contract scraper")

    parser.add_argument("-k", "--key", dest="api_key", type=str, help="set API key")
    parser.add_argument(
        "-o",
        "--output",
        nargs=1,
        metavar="PATH",
        type=str,
        help="save output to a csv file",
    )
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
        print("finished retrieving verified contracts")

    if args.output:
        print(f"output will be written to {args.output[0]}")

        header = ["address", "name", "totalSupply", "maxSupply", "confidence (1-3)"]

        f = open(args.output[0], "w")
        writer = csv.writer(f)
        writer.writerow(header)

    api_session = Session()

    for c in contracts:
        print(f"getting info for {c}")
        confidence = 3
        try:
            address = c["address"]
            contract_name = c["contract_name"]
        except TypeError:
            address = c
            contract_name = "?"

        time.sleep(0.22)  # brief pause so we don't hit free tier rate limit (5/second)
        print(f"getting contract details for {address}")
        result = pg.get_contract_details(api_session, address, API_KEY)

        print("finished getting contract details")
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
            print("getting ABI")
            abi = result["ABI"]
            print("finished getting ABI")
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
            for wl in whitelist_terms:
                print(f"checking for '{wl}' in contract code")
                if wl in source.lower():
                    print(f"whitelist term found in ADDRESS {address}, skipping.")
                    break

            # check supply vars
            print(f"instantiating contract object for {address}")
            contract = pg.Contract(address, abi, NODE_ENDPOINT, NODE_API_KEY)
            print(f"finished instatiation")

            for s in supply_terms:
                try:
                    print(f"calling function {s}")
                    v = contract.call_func(s)

                    # if any of the supply values is >= than 1mil (arbitrary amount), it's probably a token, so we lower confidence
                    if v >= 1000000:
                        confidence += -1

                    supply.append(v)
                    print(f"{s}: {v}")
                except exceptions.ABIFunctionNotFound:
                    print(f"function {s} not present in contract")
                    pass
                except exceptions.NoABIFunctionsFound:
                    print("abi contains no function definitions, skipping")
                    break
                except:
                    print("couldn't invoke function, skipping")
                    break

            # try:
            if len(supply) < 1:
                print(f"no supply parameters found, skipping")
                continue
            elif len(supply) < 2:
                print(
                    f"contract {address} contains less than two of the defined 'supply' variables, can't determine if usable"
                )
                supply.append("N/A")
                confidence += -1
            elif supply[0] == supply[1]:
                print(
                    f"supply parameter values are the same, assuming no supply remaining."
                )
                print("max supply has been reached, skipping.")
                continue
            # except IndexError:
            #     print(
            #         f"MANUAL CHECK NEEDED: contract {address} contains less than two of the defined 'supply' variables, can't determine if usable"
            #     )
            #     supply.append("N/A")
            #     confidence += -1

            if args.output:
                print(f"writing {contract_name} to csv")
                data = [address, contract_name, supply[0], supply[1], confidence]
                writer.writerow(data)
                print("done writing")
            print(f"finished loop iteration through {contract_name}")

    if args.output:
        f.close()


if __name__ == "__main__":
    main()
