from hashlib import sha256

h = sha256()
password = "Gaurav@41"
h.update(password.encode())
hash = h.hexdigest()
print(hash)

