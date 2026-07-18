from pydantic import BaseModel


class RiskResponse(BaseModel):
    account_number: str
    score: float
    risk: str


class MoneyMule(BaseModel):
    account_number: str
    incoming_accounts: int


class FraudRing(BaseModel):
    accounts: list[str]
    risk: str