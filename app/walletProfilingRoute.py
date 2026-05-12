from dotenv import load_dotenv
import os 
from app.schemas.response_schemas import (
    GetTransactionsResult,
    BalanceResult,
    AccountInfo,
    TokenAccountBalance,
    GetTokenAccountsResult,
    SignatureInfo,
    Balance,
    TransactionData,
    Transaction,
    TransactionMessage,
    TransactionMeta,
)
import requests
from fastapi import APIRouter, HTTPException, Query, status
import json 
load_dotenv()

try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/wallet",tags=["issues"])

@router.get("/{owner}/account-info")
def get_account_info(owner: str) -> AccountInfo:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [owner, {"encoding": "base58"}]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(data.keys())
    print(data["result"])
    slot =  data["result"]["context"]['slot']
    executable = data["result"]['value']['executable']
    lamports = data["result"]['value']['lamports']
    space = data["result"]['value']['space']
    return AccountInfo(
        slot=slot,
        lamports=lamports,
        owner_address=owner,
        is_executable=executable,
        space=space,
    )

@router.get("/{owner}/token-accounts")
def get_token_accounts(owner: str) ->GetTokenAccountsResult:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
    payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "getTokenAccountsByOwnerV2",
    "params": [
        owner,
        { "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
        {
            "encoding": "jsonParsed",
            "limit": 100
        }
    ]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    return GetTokenAccountsResult(**data["result"]["value"])


@router.get("/get-token-account-balance")
def get_token_account_balance(token_account_addr: str) -> TokenAccountBalance:
   

    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getTokenAccountBalance",
        "params": [token_account_addr]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    slot = data["result"]["context"]['slot']
    amount = data["result"]["value"]["amount"]
    decimals = data["result"]["value"]["decimals"]
    uiAmount = data["result"]["value"]["uiAmount"]
    uiAmountString = data["result"]["value"]["uiAmountString"]
    balance = BalanceResult(
        amount=amount,
        decimals=decimals,
        uiAmount=uiAmount,
        uiAmountString=uiAmountString
    )
    return TokenAccountBalance(slot=slot, balance=balance)

@router.get("/get-account-balance")
def get_account_balance(owner_address: str) -> Balance:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
    payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "getBalance",
    "params": [owner_address]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    balance_retrieved = data["result"]["value"]
    return Balance(balance=balance_retrieved)

@router.get("/get-signatures")
def get_signaturesByAddress(owner_address: str) -> SignatureInfo:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
    payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "getSignaturesForAddress",
    "params": [
        owner_address,
        {
            "limit": 30
        }
        
        ]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    signatures = [item["signature"] for item in data["result"]]
    return SignatureInfo(signatures=signatures)

@router.get("/get-transactions-for-address")
def get_transactions_for_address(
    wallet_address: str,
    limit: int = Query(10, ge=1, le=100),
    pagination_token: str | None = Query(None),
) -> GetTransactionsResult:
    """Helius enhanced RPC; requires a plan that includes getTransactionsForAddress."""
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    options: dict = {
        "transactionDetails": "full",
        "limit": limit,
    }
    if pagination_token:
        options["paginationToken"] = pagination_token

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getTransactionsForAddress",
        "params": [wallet_address, options],
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    err = data.get("error")
    if err is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    result = data.get("result") or {}
    rows = result.get("data") or []
    pagination = result.get("paginationToken")

    parsed: list[TransactionData] = []
    for item in rows:
        tx = item.get("transaction") or {}
        msg = tx.get("message") or {}
        meta_raw = item.get("meta") or {}
        parsed.append(
            TransactionData(
                slot=item["slot"],
                transactionIndex=item["transactionIndex"],
                transaction=Transaction(
                    signatures=tx.get("signatures", []),
                    message=TransactionMessage(
                        accountKeys=msg.get("accountKeys", []),
                        instructions=msg.get("instructions", []),
                        header=msg.get("header"),
                    ),
                ),
                meta=TransactionMeta(
                    fee=meta_raw.get("fee", 0),
                    preBalances=meta_raw.get("preBalances", []),
                    postBalances=meta_raw.get("postBalances", []),
                ),
                blockTime=item.get("blockTime"),
            )
        )

    return GetTransactionsResult(data=parsed, paginationToken=pagination)


if __name__ == "__main__":
    result = get_token_accounts("A1TMhSGzQxMr1TboBKtgixKz1sS6REASMxPo1qsyTSJd")
    print(result)
    
    balance = get_account_balance("7ayANLfrWEzzUZyFFY9w7sHchPQUoge3kt7mi6LK5sw3")
    print(balance)

    signature = get_signaturesByAddress("7ayANLfrWEzzUZyFFY9w7sHchPQUoge3kt7mi6LK5sw3")
    print(signature)

    account_info = get_account_info("7ayANLfrWEzzUZyFFY9w7sHchPQUoge3kt7mi6LK5sw3")
    print(account_info)

    token_account_balance = get_token_account_balance("HBJYBAnMA94TdPWrhDLTcihR7Nkn42Kf6kEFTww6GRh")
    print(token_account_balance)

    # transactions = get_transactions("7ayANLfrWEzzUZyFFY9w7sHchPQUoge3kt7mi6LK5sw3")
    # print(transactions)