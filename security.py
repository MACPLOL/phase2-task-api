from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    #Receive the raw password from the user
    #use the password_hash variable to create
    #a secure hash
    hashed_password = password_hash.hash(password)

    #return the hash
    return hashed_password

def verify_password(password: str, hashed_password: str) -> bool:
    #Receive the password
    #Receive the hashed_password
    #Ask password_hash using tool to compare
    #password to its hashed version
    result = password_hash.verify(password, hashed_password)
    if result is True:
        return True
    return False
        #Return true or false depending on comparison