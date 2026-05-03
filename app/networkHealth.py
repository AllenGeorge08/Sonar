from app.schemas.response_schemas import Slot,EpochInfo
from dotenv import load_dotenv
import os 
import requests
from fastapi import APIRouter,HTTPException,status
load_dotenv()


try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/tokenIntelligence",tags=["transactions"])


url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
headers = {"Content-Type": "application/json"}


def get_slot_at_commitment(commitment: str) -> Slot:
    if commitment not in { "confirmed" , "finalized" , "processed"}:
        raise ValueError("Invalid commitment type")

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getSlot",
        "params": [{ "commitment": "finalized" }]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print(f'The current slot with commitment level : {commitment} is : ', data["result"])
    slot_number = data["result"]
    print(slot_number)
    answer = Slot(slot_number=slot_number)
    return answer



def get_epoch_info(commitment: str, minContextSlot: int) -> EpochInfo:
    if commitment not in { "confirmed" , "finalized" , "processed"}:
        raise ValueError("Invalid commitment type")
    
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getEpochInfo",
        "params": [
            {
                "commitment": commitment,
                "minContextSlot": minContextSlot
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    absolute_value = data["result"]["absoluteSlot"]
    blockHeight = data["result"]["blockHeight"]
    epoch = data["result"]["epoch"]
    slotsInEpoch = data["result"]["slotsInEpoch"]   
    slotsIndex = data["result"]["slotIndex"]
    transactionCount = data["result"]["transactionCount"]
    return EpochInfo(absolute_slot=absolute_value,blockHeight=blockHeight,epoch=epoch,slotIndex=slotsIndex,slotsInEpoch=slotsInEpoch,transactionCount=transactionCount)
    

# 'slotIndex': 127644, 'slotsInEpoch': 432000, 'transactionCount': 18083310966},
    

      

if __name__ == "__main__":
    answer = get_slot_at_commitment("confirmed")
    print(answer)

    answer_2 = get_epoch_info("finalized",1000)
    print(answer_2)
