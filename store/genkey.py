from cryptography.fernet import Fernet

F_key = Fernet.generate_key()
print(F_key)
