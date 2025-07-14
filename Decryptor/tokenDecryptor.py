import base64
import json
import msgpack
from cryptography.fernet import Fernet
import uuid
from datetime import datetime, timezone

def decode_uuid(bin_value):
    return str(uuid.UUID(bytes=bin_value))

def fix_padding(token):
    return token + '=' * (-len(token) % 4)

def decrypt_and_unpack_token(token, key_base64):
    fernet = Fernet(key_base64.encode())
    token = fix_padding(token)
    decrypted = fernet.decrypt(token.encode())
    unpacked = msgpack.unpackb(decrypted, raw=False)
    return unpacked

def decode_jwt(token):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    header_b64, payload_b64, signature_b64 = parts
    header_json = base64.urlsafe_b64decode(fix_padding(header_b64)).decode()
    payload_json = base64.urlsafe_b64decode(fix_padding(payload_b64)).decode()

    header = json.loads(header_json)
    payload = json.loads(payload_json)

    return header, payload

if __name__ == "__main__":
    method = input("Enter method to use (fer/jwt): ").strip().lower()

    if method == "fer":
        token = input("Enter Fernet token to decrypt: ").strip()
        #ENter your Fernet key here!
        key_base64 = "YOUR_FERNET_KEY_BASE64"
        data = decrypt_and_unpack_token(token, key_base64)

        user_id_bytes = data[1][1]
        project_id_bytes = data[3][1]
        expires_at = datetime.fromtimestamp(data[4], tz=timezone.utc)
        audit_ids = data[5]

        print("\nDecrypted Fernet token data:")
        print("  User ID:     ", decode_uuid(user_id_bytes))
        print("  Project ID:  ", decode_uuid(project_id_bytes))
        print("  Expires at:  ", expires_at)
        print("  Audit IDs:   ", [id.hex() for id in audit_ids])

    elif method == "jwt":
        token = input("Enter JWT token to decode: ").strip()
        header, payload = decode_jwt(token)

        print("\nDecoded JWT token data:")
        print("Header:")
        print(json.dumps(header, indent=2))
        print("Payload:")
        print(json.dumps(payload, indent=2))

    else:
        print("Unknown method. Please enter 'fernet' or 'jwt'.")
