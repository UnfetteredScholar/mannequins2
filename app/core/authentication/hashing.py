from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_bcrypt(password: str) -> CryptContext:
    return pwd_cxt.hash(password)


def hash_verify(hashed_password: str, plain_password: str) -> CryptContext:
    return pwd_cxt.verify(plain_password, hashed_password)
