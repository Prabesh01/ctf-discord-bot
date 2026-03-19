import os
import json
from pathlib import Path
from time import sleep
import re
from dotenv import load_dotenv
import requests

BASE_DIR = Path(__file__).resolve().parent
token_expired_file=BASE_DIR / 'token.expired'
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

session_file=BASE_DIR / 'htb_session.json'
session_data=json.loads(session_file.read_text())
session_data=session_data['message'] if 'message' in session_data else session_data

headers={
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Authorization":"Bearer "+session_data["access_token"]
}


def send_log(msg, track_file):
     print(msg)
     if not os.path.exists(track_file):
         r=requests.post(os.getenv("token_expired_notif_webhook"),data={"content":"htb share - "+msg})
         with open(track_file,'w') as f: pass

def get_challenge_info(htb_challenge_name,i=0):
    print(f"--> {htb_challenge_name}")
    match=re.findall('^(.*?)\(',htb_challenge_name)
    htb_challenge_name= match[0].strip() if match else htb_challenge_name.strip()
    try:
        r=requests.get(
            f"https://labs.hackthebox.com/api/v4/challenge/info/{htb_challenge_name}",
            headers=headers
            ).json()
        if os.path.exists(token_expired_file): 
            requests.post(os.getenv("token_expired_notif_webhook"),data={"content":"htb share - working!"})
            os.remove(token_expired_file)
        return r
    except:
        if i:
            send_log(f"Token expired!", token_expired_file)
            return None
        else:
            print("Token expired! Refreshing..")
            try:
                r=requests.post(
                    "https://labs.hackthebox.com/api/v4/login/refresh",
                    json={"refresh_token":session_data['refresh_token']},
                    headers=headers
                    ).json()['message']
                session_data['access_token']=r['access_token']
                session_data['refresh_token']=r['refresh_token']
                with open(session_file,'w') as f:
                    f.write(json.dumps(session_data))
                headers['Authorization']="Bearer "+session_data['access_token']
                return get_challenge_info(htb_challenge_name,1)
            except Exception as e:
                print(e)
                send_log(f"Token expired!", token_expired_file)
                return None                

def main():
    get_ch_name=requests.get(os.environ.get('conan_bot_api_url'), headers={"X-API-Key":os.environ.get('conan_bot_api_key')})
    if get_ch_name.status_code!=200:
        print("couldn't get challenge name from conan api")
        return
    htb_challnge_name=get_ch_name.text
    r=get_challenge_info(htb_challnge_name)
    if not r: return

    ch=r['challenge']
    if not ch['docker_ip']:
        # spawn the challenge
        print("Spawnning challenge..")
        spawn_r=requests.post('https://labs.hackthebox.com/api/v4/challenge/start', headers=headers, data={"challenge_id":ch['id']})
        print(spawn_r.json()['message'])
        if spawn_r.status_code!=200: return

        for i in range(5):
            sleep(20)
            print(f"Checking challenge status.. {i}")
            r=get_challenge_info(htb_challnge_name)
            ch=r['challenge']

            if ch['docker_ip']:
                url=f"http://{ch['docker_ip']}:{ch['docker_ports'][0]}"
                print(url)
                
                # post to conan api
                rr=requests.post(os.environ.get('conan_bot_api_url'), data={"url": url}, headers={"X-API-Key":os.environ.get('conan_bot_api_key')})
                print(rr.status_code)                
                break
    else:
        print("Challenge is already up!")


main()
