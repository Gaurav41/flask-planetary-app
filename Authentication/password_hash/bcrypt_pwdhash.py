import bcrypt
import time

passwd = 'Gaurav@123'.encode()

salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(passwd, salt)

print(f"original password: {passwd}")
print(f"Salt: {salt}")
print(f"hashed_pass: {hashed}")

# check password
if bcrypt.checkpw(passwd, hashed):
    print("match")
else:
    print("does not match")


# Cost factore
start = time.time()
salt = bcrypt.gensalt(rounds=16)
hashed = bcrypt.hashpw(passwd, salt)
end = time.time()

print(end - start)

print(hashed)