#1.想办法得到网易没加密的原始参数
#2.想办法把参数进行加密（必须参考网易的逻辑），params  -->  encText,   encSeckey ---> encSeckey
#3.请求到网易，拿到评论信息
import requests
from encrypt import get_params,get_encSeKey
from utils import save_comments,ensure_output_dir


# 网易云评论接口地址
url='https://music.163.com/weapi/comment/resource/comments/get?csrf_token='

#未加密前原始的请求参数，通过JS断点获得
data={
    'csrf_token':"",
    'cursor':"-1",
    'offset':"0",
    'orderType':"1",    # 1=热度排序，2=时间排序
    'pageNo':"1",
    'pageSize':"100",   # 单页最大100条
    'rid':"",
    'threadId':""
}

def main(song_id):
    try:
        # 动态更新资源ID
        data['rid']=f"R_SO_4_{song_id}"
        data['threadId']=f"R_SO_4_{song_id}"

        # 加密参数
        encrypted_data = {
            "params": get_params(data),
            "encSecKey": get_encSeKey()
        }

        # 发送请求
        resp=requests.post(url,data=encrypted_data)
        print(f'请求状态{resp.status_code}')
        if resp.status_code==200:
            print('开始爬取音乐评论...')
            pageSource=resp.json()

            # 解析当前页评论
            comment_list=pageSource['data']['comments']
            if not comment_list:
                print("\n没有更多评论了")
                return

            ensure_output_dir()
            save_comments(comment_list,song_id)
        else:
            print('请求失败，请检查是否被反爬等等')
    except KeyError as e:
        print(f"\n数据解析失败，缺少字段：{e}")
        print("可能是网易云接口格式更新")

if __name__ == '__main__':
    song_id='2082229673'    # 修改为你要爬取的歌曲ID
    main(song_id)


