from config import *
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api import audio
from vk_api.utils import get_random_id
from Levenshtein import jaro
def get_params(s:str):
    login,password,*ids=s.split()
    new_ids=[]
    for id in ids:
        if id not in new_ids:
            new_ids.append(id)
    print(new_ids)
    return login,password,new_ids

def get_common_audios(login:str,password:str,*ids):
    #пока только для 2 акков
    #добавить lru_cache
    vk_session = vk_api.VkApi(
    login, password,
    app_id=app_id, scope=scope)
    vk_session.auth()
    #vk=vk_session.get_api()
    vkaudio=audio.VkAudio(vk_session)
    users_track_list=[]
    for id in ids:
        user_track_list=set([track['artist']+'-'+track['title'] for track in vkaudio.get_iter(id)])
        print("I'm not dead")
        users_track_list.append(user_track_list)
    shares=[len(i) for i in users_track_list]
    common_audios_lst=set()
    while(len(users_track_list)>1):
        common_audios_lst=set()
        users_track_list.sort(key=lambda x:len(x))
        for i in users_track_list[0]:
            for j in users_track_list[1]:
                if jaro(i,j)>0.75:
                    common_audios_lst.add(i)
        users_track_list.pop(0)
        print("I'm not dead")
        users_track_list[0]=common_audios_lst
    print("_______________________")
    print(common_audios_lst)
    shares=[len(common_audios_lst)/i for i in shares.copy()]
    returnable_text=''
    for i in common_audios_lst:
        returnable_text+=(i+'\n')
    returnable_text+="Процент общих песен\n"
    for i in shares:
        returnable_text+=(str(round(100*i,2))+r'% ')
    return returnable_text[:-1]
def main():
    vk_session = vk_api.VkApi(token=group_token)
    longpoll = VkBotLongPoll(vk_session, client_id)
    vk = vk_session.get_api()

    for e in longpoll.listen():
        print(e.type)
        if e.type == VkBotEventType.MESSAGE_NEW:
            login,password,ids=get_params(e.obj.text)
            our_msg=get_common_audios(login,password,*ids)
            for i in range(0,len(our_msg),4000):
                vk.messages.send(
                                 peer_id=e.obj.from_id,
                                 random_id=get_random_id(),
                                 message=our_msg[i:i+min(4000,len(our_msg)-i)]
                                )

if __name__=='__main__':
    main()