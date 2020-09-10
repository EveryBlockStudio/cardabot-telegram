import json

with open('language_options.json', 'r') as f:
    json_data = json.load(f)

for chat_id in json_data.keys():
    lang = json_data[chat_id]

    with open('chats/'+chat_id+'.json', 'w') as f:
        json_obj = {}
        json_obj['chat_id'] = chat_id
        json_obj['language'] = lang
        json_obj['default_pool'] = 'EBS'
        json.dump(json_obj, f)
