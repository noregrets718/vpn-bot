from pydantic import BaseModel


class SUser(BaseModel):
    id: int
    username: str | None
    first_name: str | None
    last_name: str | None


class SUserFilter(BaseModel):
    id: int


class SUserUpdateSubscription(BaseModel):
    subscription_url: str | None
