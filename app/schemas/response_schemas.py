from pydantic import BaseModel 
from typing import Optional

#getAccountInfoResponse
class AccountInfo(BaseModel):
    slot: int 
    lamports: int 
    owner_address: str 
    is_executable: bool 
    space: int 


#get Balance response
class Balance(BaseModel):
    balance: int 


#getSignaturesforAddress response time
class SignatureInfo(BaseModel):
    signatures: list[str] 
    err: Optional[dict] = None 
    memo: Optional[int] = None 
    blockTime: Optional[int] = None 
    confirmationStatus: Optional[str] = None


#getTx for addr 
class TransactionMessage(BaseModel):
    accountKeys: list[str]
    instructions: list[dict]


class Transaction(BaseModel):
    signatures: list[str]
    message: TransactionMessage


class TransactionMeta(BaseModel):
    fee: int 
    preBalance: list[int]
    postBalances: list[int]


class TransactionData(BaseModel):
    slot: int 
    transactionIndex: int
    transaction: Transaction 
    meta: TransactionMeta 
    blockTime: Optional[int] = None 


class GetTransactionsResult(BaseModel):
    data: list[TransactionData]
    paginationToken: Optional[str] = None


class BalanceResult(BaseModel):
    amount: str 
    decimals: int
    uiAmount: float
    uiAmountString: Optional[str]


class TokenAccountBalance(BaseModel):
      slot: int 
      balance: BalanceResult


#getTokenAccountByOwner
class TokenAmount(BaseModel):
    amount: str
    decimals: int
    uiAmount: float
    uiAmountString: str

class TokenInfo(BaseModel):
    isNative: bool
    mint: str
    owner: str
    state: str
    tokenAmount: TokenAmount

class ParsedData(BaseModel):
    program: str
    parsed: dict
    space: int

class TokenAccount(BaseModel):
    lamports: int
    owner: str
    data: ParsedData
    executable: bool
    rentEpoch: float  
    space: int

class TokenAccountEntry(BaseModel):
    pubkey: str
    account: TokenAccount

class GetTokenAccountsResult(BaseModel):
   accounts: list[TokenAccountEntry]
   paginationKey: Optional[str] = None
   count: int