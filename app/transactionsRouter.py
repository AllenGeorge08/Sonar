from app.schemas.response_schemas import PrioritizationFee,GetSignatureResult,Signature, GetTransactionResult,Transaction_Two,TransactionMessage
from dotenv import load_dotenv
import os 
import requests
from fastapi import APIRouter, HTTPException, Query, status
load_dotenv()

try:
    api_key = os.getenv('HELIUS_API_KEY')
    print("----API KEY LOADED----")
except:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/transactions",tags=["transactions"])

@router.get("/get-transaction")
def get_transaction_details(transaction_signature: str) -> GetTransactionResult:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getTransaction",
        "params": [transaction_signature, { "commitment": "finalized" }]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    slot = data["result"]["slot"]
    accountKeys = data["result"]["transaction"]["message"]["accountKeys"]
    header = data["result"]["transaction"]["message"]["header"]
    instructions = data["result"]["transaction"]["message"]["instructions"]
    signatures = data["result"]["transaction"]["signatures"]


    tx_message = TransactionMessage(accountKeys=accountKeys,header=header,instructions=instructions)
    tx  = Transaction_Two(message=tx_message,signatures=signatures)
    return GetTransactionResult(slot=slot,transaction=tx)


@router.get("/get-signature-status")
def get_signature_status(signature: str) -> GetSignatureResult:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getSignatureStatuses",
        "params": [[signature], { "searchTransactionHistory": True }]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    current_slot = data["result"]["context"]["slot"]
    value = data["result"]["value"]
    tx = value[0]
    signature_slot = tx["slot"]
    confirmation_status = tx["status"]
    confirmations = tx["confirmations"]
    err = tx['err']
    signature = Signature(signature_slot=signature_slot,confirmations=confirmations,err=err,confirmation_status=confirmation_status)
    result = GetSignatureResult(current_slot=current_slot,signature=signature)
    return result


@router.get("/get-priorization-fee")
def prioritization_fee(
    account_addresses: list[str] = Query(default=[]),
) -> PrioritizationFee:
    url = f"https://devnet.helius-rpc.com/?api-key={api_key}"

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getRecentPrioritizationFees",
        "params": [account_addresses if account_addresses else []]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    err = data.get("error")
    if err is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    rows = data.get("result") or []
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Empty prioritization fee result from RPC",
        )
    slot = rows[0]["slot"]
    fee = rows[0]["prioritizationFee"]
    return PrioritizationFee(current_slot=slot, prioritization_fee=fee)



# if __name__ == "__main__":
#     # get_tx_details = get_transaction_details("HDHmXw75rJYzp8uqKt7yVNRkCTP3EAJqoMcuerbcmeRMKHPPUEt7c3HNeGf2MBpaYhZEJwLxMSiTHDgAkUzPFJH")
#     # print(get_tx_details)

#     # get_sig_status = get_signature_status("HDHmXw75rJYzp8uqKt7yVNRkCTP3EAJqoMcuerbcmeRMKHPPUEt7c3HNeGf2MBpaYhZEJwLxMSiTHDgAkUzPFJH")
#     # print("Signature details...")
#     # print("\n Current Slot : " , get_sig_status.current_slot)
#     # print("\n Signature  Slot : " , get_sig_status.signature.signature_slot)
#     # print("\n Confirmation Status: ",get_sig_status.signature.confirmation_status)
#     # print("\n Confirmations : ",get_sig_status.signature.confirmations)

#     prioritizationFee = prioritization_fee(["CxELquR1gPP8wHe33gZ4QxqGB3sZ9RSwsJ2KshVewkFY"])
#     print(prioritizationFee)



