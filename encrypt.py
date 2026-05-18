# -------------------------- 网易云音乐加密核心模块 --------------------------
# 逆向来源：Chrome开发者工具断点调试 core.js 中的 d() 函数
# 加密逻辑：原始参数 → 第一次AES加密(g) → 第二次AES加密(i) → params
#          随机字符串i → RSA加密(e,f) → encSecKey
# 优化技巧：固定随机字符串i，绕过复杂的RSA加密实现

from Crypto.Cipher import AES
from base64 import b64encode
import json

# -------------------------- 网易云硬编码固定密钥 --------------------------
# 直接从JS中提取，服务于d
e ='010001'
f='00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
g='0CoJUm6Qyw8W8jud'

# 固定a函数生成的16位随机字符串
# 原理：RSA加密公钥固定，只要i不变，encSecKey就永远不变
# 好处：无需实现复杂的RSA加密，代码更简洁，运行更快
i='ROGjNaU3ZXxQqKhV'

# -------------------------- 加密工具函数 --------------------------
def to_16(data):
    """
    AES-CBC模式PKCS7填充
    要求明文长度必须是16的倍数，不足则填充对应长度的字节
    """
    pad = 16 - len(data) % 16
    data += chr(pad) * pad
    return data

def aes_params(data:str,key:str)->str:
    """
    单轮AES-CBC加密
    :param data: 待加密字符串
    :param key: AES密钥
    :return: base64编码后的加密结果
    """
    iv ='0102030405060708'
    data_16=to_16(data)
    aes = AES.new(key=key.encode('utf-8'),IV=iv.encode('utf-8'),mode=AES.MODE_CBC)  #创建加密器
    bs=aes.encrypt(data_16.encode('utf-8'))
    return str(b64encode(bs),'utf-8')

def get_params(raw_data):       #这里默认data是字符串
    """
    网易云双重AES加密入口函数
    :param raw_data: 原始未加密参数字典
    :return: (params, encSecKey) 加密后的参数对
    """
    # 第一步：将字典转成JSON字符串（加密输入必须是字符串）
    json_str = json.dumps(raw_data)

    # 第二步：第一次AES加密，用固定密钥g
    first=aes_params(json_str,g)

    # 第三步：第二次AES加密，用固定随机密钥i
    second=aes_params(first,i)

    # 返回加密后的参数params
    return second

def get_encSeKey():
    """固定encSecKey值，对应上面的i"""
    return '27256dfe37a32a42be039a12e35f39b8f698e807a54de7be67910e621ffb326fa90711315bcf836bf29356e251551c93c40dc504be3662fbcd02493c11f0d469b8bf0b9aae8f95f5b20f6cbf18e5fde692df68b2db2761e77c59e61065ef0c65de3de8a8a80f867503659e3a7bec733059e4a7f9d84df444bdac74dc7b7bc3f4'


# -------------------------- 页面源代码JS加密逻辑（保留作为原理说明） --------------------------
"""
function a(a) {     #返回一个随机的字符串
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)   #传入a=16  循环16次  
            e = Math.random() * b.length,   #生成一个随机数   如：2.345
            e = Math.floor(e),   #取整   如：2
            c += b.charAt(e);   #变成字符串   如：b[2]————》c  
        return c   
    }
    function b(a, b) {      #a是要加密的数据   b是密钥
        var c = CryptoJS.enc.Utf8.parse(b)  #第一次的b暂时不知道     从f可知c是加密的密钥 所以b是密钥
          , d = CryptoJS.enc.Utf8.parse("0102030405060708")
          , e = CryptoJS.enc.Utf8.parse(a)  #e等于数据
          , f = CryptoJS.AES.encrypt(e, c, {    #AES是加密算法   e是数据，说明c是加密的密钥
            iv: d,  #iv:偏移量
            mode: CryptoJS.mode.CBC #模式是cbc
        });
        return f.toString()     #f变成字符串返回
    }
    function c(a, b, c) {       #没有随机数，可以
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) {    d:data   e:010001  f:很长  g:0CoJUm6Qyw8W8jud
        var h = {}    #空对象
          , i = a(16);  #i得到一个16位的随机数
        h.encText = b(d, g),  #g是密钥
        h.encText = b(h.encText, i),    #返回的就是params  i是密钥
        h.encSecKey = c(i, e, f),       #返回的就是encSecKey   e,f都是定死的  如果将i定死就可以得到固定的值了
        return h
    }
    
    encText进行了两次加密：
        第一次：data + g ==> b=old_params, 第二次：b(old_params) + i ==> (new)params
"""