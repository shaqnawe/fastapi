from passlib.context import CryptContext

# create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash and return password
def hash_password(password: str) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password


# Compare password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
