# contract_scraper.py

python script for getting verified contracts from polygonscan.com and filtering for specific strings

## requirements
- python3 (tested on 3.8.10)
- polygonscan API key: https://polygonscan.com/apis
- access to a polygon node API and API key (tested with https://www.alchemy.com)

## setup
after cloning repo:

```
pip install -r requirements.txt
chmod +x contract_scraper.py (if needed)
export POLYGON_API_KEY=api_key_here
export NODE_API_KEY=node_api_key_here
export NODE_ENDPOINT=node_endpoint_here (default: https://polygon-mainnet.g.alchemy.com/v2/)
```

## usage
```
usage: contract_scraper.py [-h] [-k API_KEY]
                           [--contract [ADDRESS [ADDRESS ...]] | -q
                           STRING] [-s | -a | -d | -f]

Smart contract scraper

optional arguments:
  -h, --help            show this help message and exit
  -k API_KEY, --key API_KEY
                        set API key
  --contract [ADDRESS [ADDRESS ...]]
                        query one or more specific contracts. if used,
                        requires one of the arguments -s -a -d -f
  -q STRING, --query STRING
                        get verified contracts that contain the given
                        string
  -s, --source          get source code for one or more contract addresses
  -a, --abi             get ABI for one or more contract addresses
  -d, --description     get the description for one or more contract
                        addresses
  -f, --functions       get functions found in one or more contract's
                        source code
  -u, --usable          return only contracts that have remaining mintable
                        supply and aren't whitelist only
```

## examples

### list all verified contracts from polygonscan without filtering (note: they only show the 500 latest)
```
$ ./contract_scraper.py

no contract addresses specified, retrieving verified contracts

ADDRESS 0x827a109ce71097a25a1a0aee45e0f5ce4321d5f1 (NAME: TheSpaceRegistry)


ADDRESS 0x7067e461daf17c655815ef7e003d081cc7660645 (NAME: TheSpace)


ADDRESS 0x422F2d60d02A3cc435018Aaff4264c6de9Ef9d82 (NAME: Troll)


ADDRESS 0x8d2563f6c8943aea7c46f584e59ea71b03082282 (NAME: Treasury)


ADDRESS 0x8373b493d0a0807c5b82fccb9ff06259c8aa56dd (NAME: Boardroom)


ADDRESS 0x5703A306004C5b65AdE1836cD20d712B6Fec10B9 (NAME: MelalieStakingTokenUpgradableV2_3_2)
...
```

### list verified contracts from polygonscan and filter for a specific string
```
$ ./contract_scraper.py -q ERC1155

no contract addresses specified, retrieving verified contracts
FOUND: string 'ERC1155'

ADDRESS 0xBa7fa5D54B39cA4730CE809B074df6074867f927 (NAME: ontologyLand)

FOUND: string 'ERC1155'

ADDRESS 0x436364015f6d0e3d4909ba06f0395bebf659a62a (NAME: FDEXP1155)

FOUND: string 'ERC1155'

ADDRESS 0x5042e4DA0112d243cfC5b3fA7B0e4013EE897237 (NAME: ERC721Token)

FOUND: string 'ERC1155'
...
```

### get abi for verified contracts that contain string ERC721
```
$ ./contract_scraper.py -a -q ERC721

no contract addresses specified, retrieving verified contracts
FOUND: string 'ERC721'

ADDRESS 0x7067e461daf17c655815ef7e003d081cc7660645 (NAME: TheSpace)

[{"inputs":[{"internalType":"address","name":"currencyAddress_","type":"address"},{"internalType":"string","name":"tokenImageURI_","type":"string"},{"internalType":"address","name":"aclManager_","type":"address"},{"internalType":"address","name":"marketAdmin_","type":"address"},{"internalType":"address","name":"treasuryAdmin_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"Forbidden","type":"error"},{"inputs":[{"internalType":"uint256","name":"maxPrice","type":"uint256"}],"name":"PriceTooHigh","type":"error"},{"inputs":[],"name":"PriceTooLow","type":"error"},{"inputs":[{"internalType":"enum IACLManager.Role","name":"role","type":"uint8"}],"name":"RoleRequired","type":"error"},{"inputs":[],"name":"TokenNotExists","type":"error" ... <snip>

FOUND: string 'ERC721'

ADDRESS 0x422F2d60d02A3cc435018Aaff4264c6de9Ef9d82 (NAME: Troll)

[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event ... <snip>
```

### get description for a specific contract (this is spotty since not every contract has the description at the top)
```
$ ./contract_scraper.py -d --contract 0x7abf2442a50319958d2921d6885bb8b1e4efa205
args contain contracts, setting contract addresses

ADDRESS 0x7abf2442a50319958d2921d6885bb8b1e4efa205 (NAME: ?)

// SPDX-License-Identifier: MIT

//
/**
$$\      $$\ $$$$$$$$\ $$$$$$$$\ $$\   $$\ $$$$$$$\   $$$$$$\   $$$$$$\         $$$$$$\  $$\      $$\   $$\ $$$$$$$\
$$$\    $$$ |$$  _____|$$  _____|$$ | $$  |$$  __$$\ $$  __$$\ $$  __$$\       $$  __$$\ $$ |     $$ |  $$ |$$  __$$\
$$$$\  $$$$ |$$ |      $$ |      $$ |$$  / $$ |  $$ |$$ /  $$ |$$ /  \__|      $$ /  \__|$$ |     $$ |  $$ |$$ |  $$ |
$$\$$\$$ $$ |$$$$$\    $$$$$\    $$$$$  /  $$ |  $$ |$$ |  $$ |$$ |$$$$\       $$ |      $$ |     $$ |  $$ |$$$$$$$\ |
$$ \$$$  $$ |$$  __|   $$  __|   $$  $$<   $$ |  $$ |$$ |  $$ |$$ |\_$$ |      $$ |      $$ |     $$ |  $$ |$$  __$$\
$$ |\$  /$$ |$$ |      $$ |      $$ |\$$\  $$ |  $$ |$$ |  $$ |$$ |  $$ |      $$ |  $$\ $$ |     $$ |  $$ |$$ |  $$ |
$$ | \_/ $$ |$$$$$$$$\ $$$$$$$$\ $$ | \$$\ $$$$$$$  | $$$$$$  |\$$$$$$  |      \$$$$$$  |$$$$$$$$\\$$$$$$  |$$$$$$$  |
\__|     \__|\________|\________|\__|  \__|\_______/  \______/  \______/        \______/ \________|\______/ \_______/

 */

// File: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Context.sol


// OpenZeppelin Contracts v4.4.1 (utils/Context.sol)
```

### filter through usable verified contracts - usable meaning: no whitelist term found in contract, and supply isn't maxed (or needs to be manually verified)
```
$ ./contract_scraper.py -u
no contract addresses specified, retrieving verified contracts

ADDRESS 0x120495343e8d59Ff21c7f5aFcdAaabD3B061Ab6c (NAME: wtfmoon)

totalSupply: 0
function maxSupply not present in contract
function supply not present in contract
MANUAL CHECK NEEDED: contract 0x120495343e8d59Ff21c7f5aFcdAaabD3B061Ab6c contains less than two of the defined 'supply' variables, can't determine if usable

ADDRESS 0x2A7706Fc7cC560EaD651CD39713015491c3e941F (NAME: KtmFinance)

totalSupply: 10000000000000000000000000
function maxSupply not present in contract
function supply not present in contract
MANUAL CHECK NEEDED: contract 0x2A7706Fc7cC560EaD651CD39713015491c3e941F contains less than two of the defined 'supply' variables, can't determine if usable

ADDRESS 0x679e23631670f940462f78091680e3fbb6b53cac (NAME: Primates_wtf)

totalSupply: 71
maxSupply: 10000
function supply not present in contract
USABLE CONTRACT: ADDRESS 0x679e23631670f940462f78091680e3fbb6b53cac


ADDRESS 0xDC2F54190FC5f31Cb847CB535B3BAf57e5C32d8c (NAME: VeryLongTown)

function totalSupply not present in contract
function maxSupply not present in contract
function supply not present in contract
MANUAL CHECK NEEDED: contract 0xDC2F54190FC5f31Cb847CB535B3BAf57e5C32d8c contains less than two of the defined 'supply' variables, can't determine if usable

ADDRESS 0x3661B2A603162121E45fbCf82A6F016a78552BaF (NAME: OpenversePass)

function totalSupply not present in contract
function maxSupply not present in contract
function supply not present in contract
MANUAL CHECK NEEDED: contract 0x3661B2A603162121E45fbCf82A6F016a78552BaF contains less than two of the defined 'supply' variables, can't determine if usable

ADDRESS 0x31c614d73c5e828dddf7a1abd1a182da850917ab (NAME: PPR_Polygon)

totalSupply: 21
maxSupply: 5040
function supply not present in contract
USABLE CONTRACT: ADDRESS 0x31c614d73c5e828dddf7a1abd1a182da850917ab


ADDRESS 0xF7818DA260520dDb9719f9996A23aA3225F6298F (NAME: GeomePoly)

totalSupply: 1
maxSupply: 15625
function supply not present in contract
USABLE CONTRACT: ADDRESS 0xF7818DA260520dDb9719f9996A23aA3225F6298F
```