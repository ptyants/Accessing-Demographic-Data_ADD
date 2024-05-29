import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYW4iLCJleHAiOjE3MDY0MjExNDh9.i_vhRI8U1FBNcPJZCHjtQs4ErY8GGsKGqYQa_9YWnyk"  

try:
    payload = jwt.decode(token, "Key-chốnghacker-123.", algorithms=['HS256'])
    print(payload)
except jwt.ExpiredSignatureError:
    print("Token Expired Error: Signature has expired")
except jwt.InvalidTokenError as e:
    print("Token Decode Error:", e)