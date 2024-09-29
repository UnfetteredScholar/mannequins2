from pydantic import BaseModel


class PasswordResetRequest(BaseModel):
    email: str
    token: str
    new_password: str


class ForgotPasswordOutput(BaseModel):
    message: str
    token_expire: str
    email: str
