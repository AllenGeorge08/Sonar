from typing import Literal

from dotenv import load_dotenv
import os
import requests
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.response_schemas import Slot, EpochInfo

load_dotenv()

try:
    api_key = os.getenv("HELIUS_API_KEY")
    print("----API KEY LOADED----")
except Exception:
    raise EnvironmentError("Api Key Missing")

router = APIRouter(prefix="/api/v1/network", tags=["network"])

url = f"https://devnet.helius-rpc.com/?api-key={api_key}"
headers = {"Content-Type": "application/json"}

Commitment = Literal["processed", "confirmed", "finalized"]


class RpcJsonError(Exception):
    """JSON-RPC error object from the node (not an HTTP failure)."""

    def __init__(self, detail: object):
        self.detail = detail
        super().__init__(str(detail))


def _raise_if_rpc_error(data: dict) -> None:
    err = data.get("error")
    if err is not None:
        raise RpcJsonError(err)


def get_slot_at_commitment(commitment: str) -> Slot:
    if commitment not in {"confirmed", "finalized", "processed"}:
        raise ValueError("Invalid commitment type")

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getSlot",
        "params": [{"commitment": commitment}],
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    _raise_if_rpc_error(data)
    slot_number = data["result"]
    return Slot(slot_number=slot_number)


def get_epoch_info(commitment: str, min_context_slot: int) -> EpochInfo:
    if commitment not in {"confirmed", "finalized", "processed"}:
        raise ValueError("Invalid commitment type")

    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "getEpochInfo",
        "params": [
            {
                "commitment": commitment,
                "minContextSlot": min_context_slot,
            }
        ],
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    _raise_if_rpc_error(data)
    res = data["result"]
    return EpochInfo(
        absolute_slot=res["absoluteSlot"],
        blockHeight=res["blockHeight"],
        epoch=res["epoch"],
        slotIndex=res["slotIndex"],
        slotsInEpoch=res["slotsInEpoch"],
        transactionCount=res["transactionCount"],
    )


@router.get("/slot")
def read_slot(
    commitment: Commitment = Query("finalized"),
) -> Slot:
    try:
        return get_slot_at_commitment(commitment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RpcJsonError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail,
        ) from exc


@router.get("/epoch")
def read_epoch(
    commitment: Commitment = Query("finalized"),
    min_context_slot: int = Query(0, ge=0),
) -> EpochInfo:
    try:
        return get_epoch_info(commitment, min_context_slot)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RpcJsonError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail,
        ) from exc


if __name__ == "__main__":
    answer = get_slot_at_commitment("confirmed")
    print(answer)

    answer_2 = get_epoch_info("finalized", 1000)
    print(answer_2)
