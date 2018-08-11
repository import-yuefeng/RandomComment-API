

import time
import AES
import requests
import redis
import datetime
import re
import requests.exceptions


class Netmusic(object):


    def __init__(self):
        self.requ_date    = {"song":{"totalnum":"", "list":[{}]}}
        self.top_list_all = {
                        0: ['云音乐新歌榜', '/discover/toplist?id=3779629'],
                        1: ['云音乐热歌榜', '/discover/toplist?id=3778678'],
                        2: ['网易原创歌曲榜', '/discover/toplist?id=2884035'],
                        3: ['云音乐飙升榜', '/discover/toplist?id=19723756'],
                        4: ['云音乐电音榜', '/discover/toplist?id=10520166'],
                        5: ['UK排行榜周榜', '/discover/toplist?id=180106'],
                        6: ['美国Billboard周榜', '/discover/toplist?id=60198'],
                        7: ['KTV嗨榜', '/discover/toplist?id=21845217'],
                        8: ['iTunes榜', '/discover/toplist?id=11641012'],
                        9: ['Hit FM Top榜', '/discover/toplist?id=120001'],
                        10: ['日本Oricon周榜', '/discover/toplist?id=60131'],
                        11: ['韩国Melon排行榜周榜', '/discover/toplist?id=3733003'],
                        12: ['韩国Mnet排行榜周榜', '/discover/toplist?id=60255'],
                        13: ['韩国Melon原声周榜', '/discover/toplist?id=46772709'],
                        14: ['中国TOP排行榜(港台榜)', '/discover/toplist?id=112504'],
                        15: ['中国TOP排行榜(内地榜)', '/discover/toplist?id=64016'],
                        16: ['香港电台中文歌曲龙虎榜', '/discover/toplist?id=10169002'],
                        17: ['华语金曲榜', '/discover/toplist?id=4395559'],
                        18: ['中国嘻哈榜', '/discover/toplist?id=1899724'],
                        19: ['法国 NRJ EuroHot 30周榜', '/discover/toplist?id=27135204'],
                        20: ['台湾Hito排行榜', '/discover/toplist?id=112463'],
                        21: ['Beatport全球电子舞曲榜', '/discover/toplist?id=3812895']
                        }


        self.comment_url  = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_%s?csrf_token="

        self.session      = requests.session()
        self.headers      = {
                            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
                            'Referer':'http://music.163.com/',
                            'Content-Type':'application/x-www-form-urlencoded'
                            }
        self.play_default = "{\"ids\":\"[%s]\",\"br\":%s\
                            ,\"csrf_token\":\"\"}"

        self.r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True, db=2)  

        self.br    = "128000"


    def top_songlist(self, song_id=''):
        """
        这是用来下载top_songlist的热门排行版的方法
        """
        # if song_id != '':
        #     for item in song_id:
        #         try:
        #             url = 'http://music.163.com' + item
        #             connection = requests.get(url = url,
        #                                       headers=self.headers,
        #                                       )
        #         except:
        #             print("[-]Error -> top_songlist")
        #             continue
        #         else:
        #             connection.encoding = 'UTF-8'
        #             songids = re.findall(r'/song\?id=(\d+)', connection.text)
        #             songids = set(songids)
        #             if songids == []:
        #                 continue
        #             print("list(songids) = ", list(songids))
        #             self.requests_comment(music_ids=list(songids))
        # else:
        for item in self.top_list_all:
            try:
                url = 'http://music.163.com' + self.top_list_all[item][1]
                connection = requests.get(url = url,
                                          headers=self.headers,
                                          )
                print(self.top_list_all[item][1])
            except:
                print("[-]Error -> top_songlist")
                continue
            else:

                connection.encoding = 'UTF-8'
                songids = re.findall(r'/song\?id=(\d+)', connection.text)
                songids = set(songids)
                if songids == []:
                    continue
                print("list(songids) = ", list(songids))
                self.requests_comment(music_ids=list(songids))



    def User_SongList(self):
        """
        这是用于获取用户热门歌单的歌曲地址的方法
        """
        for offset in range(0, 1190, 35):
            try:
                print(offset)
                connection = requests.get(url = "http://music.163.com" + \
                                          "/discover/playlist" + \
                                          "?order=hot&cat=%E5%85%A8%E9%83%A8&limit=35&offset={}".format(offset),
                                          headers=self.headers,
                                          )
            except:
                print("[-]Error -> User_SongList")
                continue
            else:
                connection.encoding = 'UTF-8'
                SongList_Id         = re.findall(r'/playlist\?id=(\d+)', \
                                                 connection.text)
                Set_SongList_Id     = set(SongList_Id)
                if Set_SongList_Id == []:
                    continue
                print("list(Set_SongList_Id) = ", list(Set_SongList_Id))
                return self.top_songlist(list(Set_SongList_Id))

    def requ_comment(self, music_id, proxies=""):
        try:
            print("music_id = ", music_id)
            self.post_data = AES.encrypted_request(self.play_default %(music_id, self.br))
            if proxies == "":
                resp = self.session.post(url=self.comment_url %(music_id), data=self.post_data, headers=self.headers)
            else:
                try:
                    resp = self.session.post(url=self.comment_url %(music_id), data=self.post_data, headers=self.headers, proxies=proxies, timeout=35)
                except requests.exceptions.ConnectionError:
                    print("requests.exceptions.ConnectionError")
                    self.requ_comment(music_id, self.Get_Ip())
                except requests.exceptions.ReadTimeout:
                    print("requests.exceptions.ReadTimeout")
                    self.requ_comment(music_id, self.Get_Ip())
            try:resp = resp.json()
            except:
                print("[-]Have Error")
            count = 1
            try:
                url    = "http://music.163.com/api/song/detail?ids=[%s]" %(music_id)
                respa  = self.session.get(url, headers=self.headers).json()
            except:
                self.requ_comment(music_id)
            else:
                songName = respa["songs"][0]["name"]
                artists  = respa["songs"][0]["artists"][0]["name"]

                if self.r.get(str(music_id) + "_" + str(count)) != None:
                    return 0
                else:
                    for num in range(len(resp["hotComments"])):
                        like              = resp["hotComments"][num]["likedCount"]
                        username          = resp["hotComments"][num]['user']["nickname"]
                        comment_content   = resp["hotComments"][num]["content"]
                        # if len(comment_content)<=50 and int(like)>1000:
                        self.r.set(str(music_id) + "_" + str(count), str(like)+"|"+username+"|"+comment_content+"|"+songName+"|"+artists)
                        print(str(music_id) + "_" + str(count), str(like)+"|"+username+"|"+comment_content+"|"+songName+"|"+artists)
                        print(str(music_id) + "_" + str(count))
                        count += 1

        except requests.exceptions.ConnectionError:
            print("[-]Trying Get_Ip")
            proxies = self.Get_Ip()
            self.requ_comment(music_id, proxies)



    def requests_comment(self, music_ids, proxies=''):
        for music_id in music_ids:
            self.requ_comment(music_id)


    def Get_Ip(self):
        proxies  = str(requests.get(url="").text)
        proxies  = {"http":"http://" + str(proxies)[:-1], "https":"https://" + str(proxies)[:-1]}
        return proxies


if __name__ == '__main__':
    
    test = Netmusic()
    test.top_songlist()
    # print(test.requests_comment("66282"))
    # print(test.User_SongList())
