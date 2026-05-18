import os
def ensure_output_dir():
    """确保output文件夹存在"""
    if not os.path.exists('output'):
        os.makedirs('output')


def save_comments(comment_list,song_id):
    """将评论保存到本地文本文件"""
    filename = f"output/歌曲_{song_id}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        for index, comment in enumerate(comment_list, start=1):
            content=comment['content']
            name=comment['user']['nickname']
            f.write(f'[{index}]{name}:{content}\n')
        print(f'评论已保存至 {filename}')
        print(f'共爬取{len(comment_list)}条评论')

