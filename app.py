from flask import Flask, request, jsonify
import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime
from GetWishListItems_pb2 import CSGetWishListItemsRes

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Use your working token here
BASE64_TOKEN = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjMiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxMjI2NDk5OTcyNSwibmlja25hbWUiOiLKmeG0j-G0m-G0gOG0heG0jcmqybQiLCJub3RpX3JlZ2lvbiI6IklORCIsImxvY2tfcmVnaW9uIjoiSU5EIiwiZXh0ZXJuYWxfaWQiOiI3ZjEwNjQ3MzBkMmVkYjc5N2Y3OGUwOGU3MTNiMTBjMCIsImV4dGVybmFsX3R5cGUiOjQsInBsYXRfaWQiOjAsImNsaWVudF92ZXJzaW9uIjoiIiwiZW11bGF0b3Jfc2NvcmUiOjEwMCwiaXNfZW11bGF0b3IiOnRydWUsImNvdW50cnlfY29kZSI6IlVTIiwiZXh0ZXJuYWxfdWlkIjozOTU5Nzg4NDI0LCJyZWdfYXZhdGFyIjoxMDIwMDAwMDcsInNvdXJjZSI6MCwibG9ja19yZWdpb25fdGltZSI6MTc0OTE5NDI1MywiY2xpZW50X3R5cGUiOjEsInNpZ25hdHVyZV9tZDUiOiIiLCJ1c2luZ192ZXJzaW9uIjowLCJyZWxlYXNlX2NoYW5uZWwiOiIiLCJyZWxlYXNlX3ZlcnNpb24iOiJPQjQ5IiwiZXhwIjoxNzQ5NTQyNzQwfQ.dWc6pxOY301Hyy0hdua2CTcVWWuggC-1E7_SihWmrYc"

# Encrypt UID function
def Encrypt_ID(uid):
    uid = int(uid)
    dec = [f"{i:02x}" for i in range(128, 256)]
    xxx = [f"{i:02x}" for i in range(1, 128)]
    x = uid / 128
    if x > 128:
        x /= 128
        if x > 128:
            x /= 128
            if x > 128:
                x /= 128
                m = int((((((x - int(x)) * 128) % 1) * 128) % 1) * 128)
                n = int(((((x - int(x)) * 128) % 1) * 128))
                z = int(((x - int(x)) * 128))
                y = int(x * 128 % 128)
                return dec[m] + dec[n] + dec[z] + dec[y] + xxx[int(x)]
            else:
                n = int(((((x - int(x)) * 128) % 1) * 128))
                z = int(((x - int(x)) * 128))
                y = int(x * 128 % 128)
                return dec[n] + dec[z] + dec[y] + xxx[int(x)]
    return None

# AES Encryption
def encrypt_api(plain_hex):
    plain_bytes = bytes.fromhex(plain_hex)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_bytes, AES.block_size))
    return cipher_text.hex()

# Timestamp formatting
def convert_timestamp(ts):
    try:
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %I:%M:%S %p')
    except Exception:
        return "Invalid Timestamp"

# New endpoint
@app.route('/wishlist-info', methods=['GET'])
def wishlist_info():
    uid = request.args.get("uid")
    region = request.args.get("region", "ind").lower()

    if not uid or not uid.isdigit():
        return jsonify({"error": "Invalid UID"}), 400

    encrypted_id = Encrypt_ID(int(uid))
    if not encrypted_id:
        return jsonify({"error": "UID encryption failed"}), 500

    encrypted_payload = encrypt_api(f"08{encrypted_id}1007")
    payload = bytes.fromhex(encrypted_payload)

    url = f"https://client.{region}.freefiremobile.com/GetWishListItems"
    headers = {
        "Authorization": f"Bearer {BASE64_TOKEN}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB49",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 10)",
        "Host": "clientbp.common.ggbluefox.com",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate, br",
    }

    try:
        res = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)
        decoded = CSGetWishListItemsRes()
        decoded.ParseFromString(res.content)

        wishlist = []
        for item in decoded.items:
            wishlist.append({
                "item_id": item.item_id,
                "uid": uid,
                "total_item": str(len(decoded.items)),
                "release_time": convert_timestamp(item.release_time)
            })

        return jsonify({
            "results": [
                {
                    "wishlist": wishlist
                }
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)