from app.schemas.response_schemas import PrioritizationFee,GetSignatureResult,Signature, GetTransactionResult,Transaction_Two,TransactionMessage
from dotenv import load_dotenv
import os 
import requests
from fastapi import APIRouter,HTTPException,status
load_dotenv()
from app.schemas.response_schemas import GetTokenSupplyResult,GetTokenLargestAccountsResult,TokenSupplyValue,LargestAccount


try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/tokenIntelligence",tags=["transactions"])


url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
headers = {"Content-Type": "application/json"}

@router.get("/token-supply/{mint_address}")
def get_token_supply(mint_address: str) -> GetTokenSupplyResult:
    payload = {
        "jsonrpc": "2.0", "id": "1",
        "method": "getTokenSupply",
        "params": [mint_address]
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return GetTokenSupplyResult(
        slot=data["result"]["context"]["slot"],
        value=TokenSupplyValue(**data["result"]["value"])
    )


@router.get("/token-largest-accounts/{mint_address}")
def get_token_largest_accounts(mint_address: str) -> GetTokenLargestAccountsResult:
    payload = {
        "jsonrpc": "2.0", "id": "1",
        "method": "getTokenLargestAccounts",
        "params": [mint_address]
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    return GetTokenLargestAccountsResult(
        slot=data["result"]["context"]["slot"],
        value=[LargestAccount(**a) for a in data["result"]["value"]]
    )