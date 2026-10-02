from pydantic import BaseModel, EmailStr


class AdminAllowlistCreate(BaseModel):
    email: EmailStr


class RequestAdminOtp(BaseModel):
    email: EmailStr


class VerifyAdminOtp(BaseModel):
    email: EmailStr
    otp: str
    name: str
    password: str