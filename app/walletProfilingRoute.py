from dotenv import load_dotenv
import os 
from  app.schemas.response_schemas import GetTransactionsResult,BalanceResult,AccountInfo,TokenAccountBalance, GetTokenAccountsResult,SignatureInfo,AccountInfo,TokenAccountBalance,Balance
import requests
from fastapi import APIRouter,HTTPException,status
import json 
load_dotenv()

try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/wallet",tags=["issues"])

@router.get("/{owner}/account-info")
def get_account_info(owner_address: str) -> AccountInfo:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": [owner_address, { "encoding": "base58" }]
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
    return AccountInfo(slot=slot,lamports=lamports,owner_address=owner_address,is_executable=executable,space=space)

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

#Only for Paid Plans
def get_transactions(wallet_address: str) -> GetTransactionsResult:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getTransactionsForAddress",
        "params": [
            wallet_address,
            {
                "transactionDetails": "signatures",
                "limit": 10
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(data)


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