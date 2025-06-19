import asyncio
import time
import httpx
import json
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from cachetools import TTLCache
from proto import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
from google.protobuf import json_format, message
from google.protobuf.message import Message
from Crypto.Cipher import AES
import base64

# === Settings ===
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
RELEASEVERSION = "OB49"
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
SUPPORTED_REGIONS = {
    "IND": {
        "uid": "3930873969",
        "password": "A7C2C6D4626074C70B978141C03D39350887BD4928D5E7CC9D86BE8B22269BC0"
    },
    "BR": {
        "uid": "3301387397",
        "password": "BAC03CCF677F8772473A09870B6228ADFBC1F503BF59C8D05746DE451AD67128"
    },
    "US": {
        "uid": "3919849222",
        "password": "05698DF41DD8418221FC677FB0D630AAD5B08E04C27F31FB9C49D3B02FCCDAEF"
    },
    "SAC": {
        "uid": "3301387397",
        "password": "BAC03CCF677F8772473A09870B6228ADFBC1F503BF59C8D05746DE451AD67128"
    },
    "NA": {
        "uid": "3919849222",
        "password": "05698DF41DD8418221FC677FB0D630AAD5B08E04C27F31FB9C49D3B02FCCDAEF"
    },
    "SG": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "RU": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "ID": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "PAK": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "TW": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "VN": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "TH": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "ME": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    },
    "CIS": {
        "uid": "3301239795",
        "password": "DD40EE772FCBD61409BB15033E3DE1B1C54EDA83B75DF0CDD24C34C7C8798475"
    },
    "BD": {
        "uid": "3801129444",
        "password": "D342D73097199DE590F228C53340B91376A1401E7EBD1602DB210DF12DAD9B9A"
    },
    "EU": {
        "uid": "3024328352",
        "password": "a0y6i2jpt7a5gk"
    }
}

# === Flask App Setup ===
app = Flask(__name__)
CORS(app)
cache = TTLCache(maxsize=100, ttl=300)
cached_tokens = defaultdict(dict)

# === Helper Functions ===
def pad(text: bytes) -> bytes:
    padding_length = AES.block_size - (len(text) % AES.block_size)
    return text + bytes([padding_length] * padding_length)

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    aes = AES.new(key, AES.MODE_CBC, iv)
    return aes.encrypt(pad(plaintext))

def decode_protobuf(encoded_data: bytes, message_type: message.Message) -> message.Message:
    instance = message_type()
    instance.ParseFromString(encoded_data)
    return instance

async def json_to_proto(json_data: str, proto_message: Message) -> bytes:
    json_format.ParseDict(json.loads(json_data), proto_message)
    return proto_message.SerializeToString()

def get_account_credentials(region: str) -> str:
    r = region.upper()
    if r in SUPPORTED_REGIONS:
        creds = SUPPORTED_REGIONS[r]
        return f"uid={creds['uid']}&password={creds['password']}"
    return "uid=3301239795&password=DD40EE772FCBD61409BB15033E3DE1B1C54EDA83B75DF0CDD24C34C7C8798475"

# === Token Generation ===
async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=payload, headers=headers)
        data = resp.json()
        return data.get("access_token", "0"), data.get("open_id", "0")

async def create_jwt(region: str):
    account = get_account_credentials(region)
    token_val, open_id = await get_access_token(account)
    body = json.dumps({
        "open_id": open_id,
        "open_id_type": "4",
        "login_token": token_val,
        "orign_platform_type": "4"
    })
    proto_bytes = await json_to_proto(body, FreeFire_pb2.LoginReq())
    payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        'User-Agent': USERAGENT,
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': RELEASEVERSION
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=payload, headers=headers)
        msg = json.loads(json_format.MessageToJson(decode_protobuf(resp.content, FreeFire_pb2.LoginRes)))
        cached_tokens[region] = {
            'token': f"Bearer {msg.get('token','0')}",
            'region': msg.get('lockRegion','0'),
            'server_url': msg.get('serverUrl','0'),
            'expires_at': time.time() + 25200
        }

async def initialize_tokens():
    tasks = [create_jwt(r) for r in SUPPORTED_REGIONS]
    await asyncio.gather(*tasks)

async def refresh_tokens_periodically():
    while True:
        await asyncio.sleep(25200)
        await initialize_tokens()

async def get_token_info(region: str) -> tuple:
    info = cached_tokens.get(region)
    if info and time.time() < info['expires_at']:
        return info['token'], info['region'], info['server_url']
    await create_jwt(region)
    info = cached_tokens[region]
    return info['token'], info['region'], info['server_url']

async def get_account_info(region: str, uid: str) -> dict:
    try:
        payload = await json_to_proto(json.dumps({'a': uid, 'b': "7"}), main_pb2.GetPlayerPersonalShow())
        data_enc = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, payload)
        token, _, server = await get_token_info(region)
        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'Authorization': token,
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': RELEASEVERSION
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(server + "/GetPlayerPersonalShow", data=data_enc, headers=headers)
            
            if resp.status_code == 200:
                decoded = decode_protobuf(resp.content, AccountPersonalShow_pb2.AccountPersonalShowInfo)
                return json.loads(json_format.MessageToJson(decoded))
            elif resp.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"UID {uid} not found in {region} server")
                
    except Exception as e:
        raise Exception(f"UID {uid} not found in {region} server") from e

# === Flask Route ===
@app.route('/player-info', methods=['GET'])
def player_info():
    region = request.args.get('region')
    uid = request.args.get('uid')
    
    if not region or not uid:
        return jsonify({"error": "Both region and uid parameters are required."}), 400
    
    region = region.upper()
    if region not in SUPPORTED_REGIONS:
        return jsonify({"error": f"Unsupported region. Supported regions: {', '.join(SUPPORTED_REGIONS.keys())}"}), 400
    
    try:
        data = asyncio.run(get_account_info(region, uid))
        return jsonify({"region": region, "data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404  # Changed to 404 for "not found" responses

@app.errorhandler(404)
def invalid_url(e):
    return jsonify({"error": "Invalid URL or Not Found."}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Invalid method. Only GET requests allowed on /player-info"}), 405

@app.route('/refresh', methods=['GET'])
def refresh_tokens_endpoint():
    try:
        asyncio.run(initialize_tokens())
        return jsonify({'message': 'Tokens refreshed for all regions.'}), 200
    except Exception as e:
        return jsonify({'error': f'Refresh failed: {e}'}), 500

# === Startup ===
async def startup():
    await initialize_tokens()
    asyncio.create_task(refresh_tokens_periodically())

if __name__ == '__main__':
    asyncio.run(startup())
    app.run(host='0.0.0.0', port=5000, debug=True)
