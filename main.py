from app.walletProfilingRoute import router as walletRouter
from app.transactionsRouter import router as transactionRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(walletRouter)
app.include_router(transactionRouter)