import requests
import binascii
import json
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from datetime import datetime
from protobuf_decoder.protobuf_decoder import Parser
from GetWishListItems_pb2 import CSGetWishListItemsRes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def Encrypt_ID(x):
    x = int(x)
    dec = [ '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx= [ '1','01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', 
    '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x= x/128 
    if x>128:
        x =x/128
        if x >128:
            x= x/128
            if x>128:
                x= x/128
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                m=(n-int(strn))*128
                return dec[int(m)]+dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
            else:
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                return dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
    return plain_text.hex()
def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
BASE64_TOKEN = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxMjM3MjE1MjIzNiwibmlja25hbWUiOiJCb3RBZG1pblBLIiwibm90aV9yZWdpb24iOiJTRyIsImxvY2tfcmVnaW9uIjoiUEsiLCJleHRlcm5hbF9pZCI6IjhjOGE1ZmQ3OTVjMzVlMDBlNmNmYmJiNmI0ZWViOTIwIiwiZXh0ZXJuYWxfdHlwZSI6NCwicGxhdF9pZCI6MCwiY2xpZW50X3ZlcnNpb24iOiIiLCJlbXVsYXRvcl9zY29yZSI6MTAwLCJpc19lbXVsYXRvciI6dHJ1ZSwiY291bnRyeV9jb2RlIjoiVVMiLCJleHRlcm5hbF91aWQiOjM5Nzg2OTM2NDUsInJlZ19hdmF0YXIiOjEwMjAwMDAwNywic291cmNlIjowLCJsb2NrX3JlZ2lvbl90aW1lIjoxNzUwMDM1MTI1LCJjbGllbnRfdHlwZSI6MSwic2lnbmF0dXJlX21kNSI6IiIsInVzaW5nX3ZlcnNpb24iOjAsInJlbGVhc2VfY2hhbm5lbCI6IiIsInJlbGVhc2VfdmVyc2lvbiI6Ik9CNDkiLCJleHAiOjE3NTAxMDg4ODJ9.H34cvhTM2EBTvGroXtzE919ug9Naf2SDTokfW8Xwxh0"
player_id = 6701687488
encrypted_id = Encrypt_ID(player_id)
encrypted_api = encrypt_api(f"08{encrypted_id}1007")
TARGET = bytes.fromhex(encrypted_api)
url = "https://clientbp.ggblueshark.com/GetWishListItems"
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
response = requests.post(url, headers=headers, data=TARGET, verify=False)
decoded_response = CSGetWishListItemsRes()
decoded_response.ParseFromString(response.content)
print(decoded_response)