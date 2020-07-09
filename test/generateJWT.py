"""生成jwt"""
import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from sys import argv
filename=argv[1]
keyFile=open(filename, "r")
str=keyFile.read()
key=jwk.JWK.from_json(str)
sub=filename[filename.find("-")+1:filename.find(".")]
payload = {
  "sub": sub,
  "exp": 1574353114,
  "iat": 1574335114
}
token = jwt.generate_jwt(payload, key, 'RS512', datetime.timedelta(minutes=50))
header, claims = jwt.verify_jwt(token, key, ['RS512'])
# python generateJWT.py jwk-ingestUser.json
print(token)
