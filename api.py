import copy
import redis
from flask import Flask,Response,jsonify

# encoding:utf-8
import io  
import sys  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 

app = Flask(__name__)

returnModule  = {"comment":"",
                 "nickName":"",
                 "songName":"",
                 "songId":"",
                 "likeCount":0,
                 "singer":""
                }

redis_cli        = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True, db=2)  
redis_cli_simple = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True, db=1)  

@app.route('/get_comment')
def get_comment():

        re_dict       = copy.deepcopy(returnModule)
        randomKey     = redis_cli.randomkey()
        randomCommentList = redis_cli.get(randomKey).split("|")
        re_dict["likeCount"] = randomCommentList[0]
        re_dict["nickName"]  = randomCommentList[1]
        re_dict["comment"]   = randomCommentList[2]
        re_dict["songName"]  = randomCommentList[3]
        re_dict["singer"]    = randomCommentList[4]
        re_dict["songId"]    = randomKey.split("_")[0]
        response = Response(json.dumps(re_dict), mimetype = 'application/json')    
        response.headers.add('Server','python flask')  
        print(re_dict)
        return response


if __name__ == "__main__":

        app.run(host="127.0.0.1", port=8888, debug = True)
