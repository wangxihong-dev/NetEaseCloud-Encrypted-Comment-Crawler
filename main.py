#1.想办法得到网易没加密的原始参数
#2.想办法把参数进行加密（必须参考网易的逻辑），params  -->  encText,   encSeckey ---> encSeckey
#3.请求到网易，拿到评论信息
import requests
from Crypto.Cipher import AES   #导入的加密模块
from base64 import b64encode    #导入的编码模块
import json

#评论页URL
url='https://music.163.com/weapi/comment/resource/comments/get?csrf_token='

#通过断点和
data={
    'csrf_token':"",
    'cursor':"-1",
    'offset':"0",
    'orderType':"1",
    'pageNo':"1",
    'pageSize':"100",
    'rid':"R_SO_4_2082229673",
    'threadId':"R_SO_4_2082229673"
}

#服务于函数d的，是
e ='010001'
f='00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
g='0CoJUm6Qyw8W8jud'
i='ROGjNaU3ZXxQqKhV'    #手动固定的，--》人家函数的随机的

#转化成16的倍数，为下方的加密算法服务
def to_16(data):
    pad = 16 - len(data) % 16
    data += chr(pad) * pad
    return data
def get_encSeKey(): #因为i固定了所以得到固定的encSeKey，因为c（）函数没有变
    return '27256dfe37a32a42be039a12e35f39b8f698e807a54de7be67910e621ffb326fa90711315bcf836bf29356e251551c93c40dc504be3662fbcd02493c11f0d469b8bf0b9aae8f95f5b20f6cbf18e5fde692df68b2db2761e77c59e61065ef0c65de3de8a8a80f867503659e3a7bec733059e4a7f9d84df444bdac74dc7b7bc3f4'


#把参数进行加密
def get_params(data):       #这里默认data是字符串

    first=enc_params(data,g)
    second=enc_params(first,i)
    return second   #返回的是params


def enc_params(data,key):  #加密过程
    iv ='0102030405060708'
    data=to_16(data)
    aes = AES.new(key=key.encode('utf-8'),IV=iv.encode('utf-8'),mode=AES.MODE_CBC)  #创建加密器
    bs=aes.encrypt(data.encode('utf-8'))   #加密  加密的内容必须是16的倍数
    return str(b64encode(bs),'utf-8')   #转换成字符串返回

#页面源代码加密逻辑
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
        第一次：data + g ==> b=0ld_params, 第二次：b(old_params) + i ==> (new)params
"""

def main():
    print('开始爬取网易云音乐评论...')
    resp=requests.post(url,data={
        'params':get_params(json.dumps(data)),
        'encSecKey':get_encSeKey()
    })
    print(f'请求状态{resp.status_code}')
    pageSource=resp.json()
    comment_list=pageSource['data']['comments']

    with open('./output/歌曲_2082229673.txt','w',encoding='utf-8') as f:
        for index,comment in enumerate(comment_list,start=1):
            content=comment['content']
            name=comment['user']['nickname']
            f.write(f'[{index}]{name}:{content}\n')
        print('评论已保存至 output / 歌曲_2082229673_评论.txt')
        print(f'共爬取{len(comment_list)}条评论')
if __name__ == '__main__':
    main()


