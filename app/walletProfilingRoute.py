from dotenv import load_dotenv
import os 
from  schemas.response_schemas import  GetTokenAccountsResult,AccountInfo,TokenAccount,TokenAccountBalance,TokenAccountEntry,Balance
import requests
from fastapi import APIRouter,HTTPException,status
import json 

load_dotenv()

try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/wallet",tags=["issues"])

@router.get("/{owner}/{api_key}")
def get_token_accounts(owner: str,api_key: str) ->GetTokenAccountsResult:
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
    # print(json.dumps(data["result"],indent=2))
    # print(list(data["result"].keys()))
    # print(type(data["result"]["value"]))
    # print(list(data["result"]["value"].keys()))
    return GetTokenAccountsResult(**data["result"]["value"])

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
    print("Type of retrieved balance : ", type(balance), "Balance :  ",balance)
    return Balance(balance=balance_retrieved)


if __name__ == "__main__":
    # result = get_token_accounts("A1TMhSGzQxMr1TboBKtgixKz1sS6REASMxPo1qsyTSJd", api_key)
    # print(result)
    
    balance = get_account_balance("7ayANLfrWEzzUZyFFY9w7sHchPQUoge3kt7mi6LK5sw3")
    print(balance)