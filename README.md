# Silent Payments light client workshop

This workshop is meant to introduce the silent payments scheme and prototype a light client using BIP 158 block filters.

You can read the draft BIP (and leave comments/feedback!) here: https://hackmd.io/@silent-payments/SJN8ewJk3

## Setup

You will need to compile `bitcoind` from the [Silent Payments DRAFT PR](https://github.com/bitcoin/bitcoin/pull/24897). Instructions for compiling Bitcoin from the source can be found [here](https://github.com/bitcoin/bitcoin/tree/master/doc#building).

Once you've successfully compiled the PR branch, you'll need to start a regtest node. For convenience, there is a `node-regtest/` folder included which has some helpful scripts and uses `direnv` to avoid conflicting with your local Bitcoin node/development environment. To use, simply copy your compiled `bitcoind` and `bitcoin-cli` binaries to the folder like so:

```bash
cp <path/to/bitcoin/repo>/src/bitcoind ~/silent-payments-workshop/node-regtest/bin
cp <path/to/bitcoin/repo>/src/bitcoin-cli ~/silent-payments-workshope/node-regtest/bin
```

Instructions for installing `direnv` can be found [here](https://direnv.net/docs/installation.html).

## Setting up your Bitcoin Core node

Use the following config options in your `bitcoin.conf` file:

```
regtest=1
fallbackfee=0.0001
txindex=1
daemon=1
blockfilterindex=1
peerblockfilters=1
rpcuser=silent
rpcpassword=payments
```

Next, create a `silent_payment` enabled wallet:

```
bitcoin-cli -named createwallet wallet_name=sender silent_payment=true
```

Mine some blocks and verify that your wallet has a spendable balance:

```
bitcoin-cli -generate 101
bitcoin-cli getwalletinfo
```

## Setting up your python venv

Create a python virtual environment:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

You should now be able to open the workshop notebook with:

```
jupyter notebook silent-payments-workshop.ipynb
```
