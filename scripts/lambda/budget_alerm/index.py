import urllib.request
import json
import os

discord_webhook_url = os.environ['NOTIFY_DISCORD_URL']

message  = {
    "username": "AWS",
    "embeds": [
        {
            "title": "AWS予算アラート通知",
            "description": "",
            "url": "",
            "color": 15105570,
            "fields": []
        }
    ]
}

def handler(event, context):
    
    # for test 
    print(event)
    
    sns_message = str(event['Records'][0]["Sns"]["Message"])
    text = [text.replace("[1]","") for text in sns_message.split("\n") if ":" in text]
    descriptions = [text.replace("[1]","") for text in sns_message.split("\n") if ":" not in text]
    
    description = ''
    for tex in descriptions:
        description += tex + '\n'
    
    fields = {}
    for tex in text[:-1]:
        kv = tex.split(':')
        if '>' in kv[1]:
            kv[1] = kv[1].replace('>', '\>')
            
        elem = {
            "name": ':small_blue_diamond:'+kv[0].strip(),
            'value': kv[1].strip(),
            "inline": True
        }
        message["embeds"][0]["fields"].append(elem)
    
    message["embeds"][0]["description"] = description
    message["embeds"][0]["url"] = text[-1].replace(" ","")
    

    data = json.dumps(message).encode("utf-8")
    
    request = urllib.request.Request(
        url = discord_webhook_url,
        data = data,
        headers = {"User-Agent": "lambda/python", "Content-Type" : "application/json"},
        method = 'POST'
    )
    
    with urllib.request.urlopen(request) as response:
        return response.read()