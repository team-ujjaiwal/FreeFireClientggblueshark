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
BASE64_TOKEN = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxMjM3MjE1MjIzNiwibmlja25hbWUiOiJCb3RBZG1pblBLIiwibm90aV9yZWdpb24iOiJTRyIsImxvY2tfcmVnaW9uIjoiUEsiLCJleHRlcm5hbF9pZCI6IjhjOGE1ZmQ3OTVjMzVlMDBlNmNmYmJiNmI0ZWViOTIwIiwiZXh0ZXJuYWxfdHlwZSI6NCwicGxhdF9pZCI6MCwiY2xpZW50X3ZlcnNpb24iOiIiLCJlbXVsYXRvcl9zY29yZSI6MTAwLCJpc19lbXVsYXRvciI6dHJ1ZSwiY291bnRyeV9jb2RlIjoiVVMiLCJleHRlcm5hbF91aWQiOjM5Nzg2OTM2NDUsInJlZ19hdmF0YXIiOjEwMjAwMDAwNywic291cmNlIjowLCJsb2NrX3JlZ2lvbl90aW1lIjoxNzUwMDM1MTI1LCJjbGllbnRfdHlwZSI6MSwic2lnbmF0dXJlX21kNSI6IiIsInVzaW5nX3ZlcnNpb24iOjAsInJlbGVhc2VfY2hhbm5lbCI6IiIsInJlbGVhc2VfdmVyc2lvbiI6Ik9CNDkiLCJleHAiOjE3NTAxMDg4ODJ9.H34cvhTM2EBTvGroXtzE919ug9Naf2SDTokfW8Xwxh0"

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

    url = f"https://clientbp.ggblueshark.com/GetWishListItems"
    headers = {
            "Authorization": f"Bearer {BASE64_TOKEN}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB49",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-N975F Build/PI)",
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