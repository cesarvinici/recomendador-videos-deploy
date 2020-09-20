from get_data import *
from ml_utils import *
import time
import os
import re
import pandas as pd
from threading import Thread
from requests_html import HTMLSession
from DAO.database import Database


queries = ["machine+learning", "data+science"]

def update_db():
    try:
        database = Database()
        for query in queries:
            
            for page in range(1,4):
                print(query, page)
                search_page = download_search_page(query, page)
                video_list = parse_search_page(search_page)
                df_videos = pd.DataFrame(video_list)
                for video in df_videos['link'].unique():
                    if database.get_by_link(video):
                        print("Já cadastrado no banco: {}".format(video))
                        continue
                    video_json_data = parse_video_page(video)
                    if(not video_json_data):
                        continue
                    
                    p = compute_prediction(video_json_data)

                    video_id = video
                    data_front = {"title": video_json_data['title'], "score": float(p), "video_id": video_id, "thumbnail": video_json_data['thumbnail']}
                    data_front['update_time'] = time.time_ns()

                    print(video_id, json.dumps(data_front))
                    database.save_recomendation(data_front)
    except Exception as identifier:
        # os.remove("novos_videos.json")
        print(identifier)
        raise Exception('Internal Server Error')
    return True

def add_single_video(youtube_link):
    pattern = r'(\/watch.*)'
   
    try:
        database = Database()
        video_id = re.split(pattern, youtube_link)[1]
        
        if database.get_by_link(video_id):
            print("Já cadastrado no banco: {}".format(video_id))
            return False
        video_json_data = parse_video_page(video_id)
        if(not video_json_data):
            return False

        p = compute_prediction(video_json_data)

        video_id = video_id
        data_front = {"title": video_json_data['title'], "score": float(p), "video_id": video_id, "thumbnail": video_json_data['thumbnail']}
        data_front['update_time'] = time.time_ns()
        database.save_recomendation(data_front, 1)
    except Exception as err:
        return False
    
    return True