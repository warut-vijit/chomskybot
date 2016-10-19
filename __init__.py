import requests
import time

token = "<TOKEN HERE>"
botid = "<BOTID HERE>"
groupid = "<GROUPID HERE>"


owner = "<CHAT OWNER NAME>"
mods = []
members = {}
perms = {'kick': False, 'add': True, 'censor': False}
triggers = []


def post_message(message):
    message = message.replace(' ', '+')
    requests.post("https://api.groupme.com/v3/bots/post?bot_id="+botid+"&text="+message)
    print("Finished")


def get_members():
    global members
    response = requests.get("https://api.groupme.com/v3/groups/" + groupid + "?token=" + token).json()['response']['members']
    for member in response:
        members[member['nickname']] = member['id']
    print members


def get_last_message():
    response = requests.get("https://api.groupme.com/v3/groups/"+groupid+"?token="+token).json()['response']['messages']['preview']
    postername = response['nickname']
    text = response['text']
    if perms['censor']:
        if any([word.lower() in triggers for word in text.split(' ')]):
            post_message('Profanity has been detected. Warning issued for user '+postername)
    if text[:2] == 'CB':
        text = text[3:]
        if postername == owner:
            process_as_owner(text)
        elif postername in mods:
            process_as_mod(text)
        else:
            process_as_member(text)


def process_as_owner(text):
    if 'promote' in text:
        print(members.keys())
        if text[8:] in members and text[8:] not in mods:
            mods.append(text[8:])
            post_message('User '+text[8:]+' has been appointed as moderator')
    elif 'kick' in text:
        if text[5:] in members and text[5:] != owner:
            requests.post("https://api.groupme.com/v3/groups/"+groupid+"/members/"+members[text[5:]]+"/remove?token="+token)
            post_message('User '+members[text[5:]]+" has been removed.")
    elif 'help' in text:
        help_display()
    elif 'demote' in text:
        if text[7:] in mods:
            mods.remove(text[7:])
            post_message('User '+text[7:]+' has been demoted from moderator')
    elif 'perms' in text:
        substr = text[6:].split(' ')
        if substr[0] in perms:
            if substr[1].lower() in ['true', 't', '1']:
                perms[substr[0]] = True
                post_message('Permission '+substr[0]+' has been changed to TRUE')
            elif substr[1].lower() in ['false', 'f', '0']:
                perms[substr[0]] = False
                post_message('Permission '+substr[0]+' has been changed to FALSE')
        else:
            post_message(substr[0]+' is not a valid permission for this group')


def process_as_mod(text):
    if 'help' in text:
        help_display()
    elif 'kick' in text:
        if text[5:] in members and text[5:] != owner and text[5:] not in mods:
            requests.post("https://api.groupme.com/v3/groups/"+groupid+"/members/"+members[text[5:]]+"/remove?token="+token)
            post_message('User '+members[text[5:]]+" has been removed.")


def process_as_member(text):
    if 'help' in text:
        help_display()


def help_display():
    modstring = reduce(lambda x, y: x + ", " + y, mods) if len(mods)>0 else ' '
    post_message('Version: ChomskyBot v1.0.0.\nOwner: ' + owner + "\nMods: " + modstring + "\nOwner functions: promote, help, demote\nMod functions: help, kick\nMember functions: help")


# post_message("I am ChomskyBot v1.0.0. I am here to ensure that this chat runs smoothly.")
# Runtime calls
get_members()
while True:
    get_last_message()
    time.sleep(5)
    print("Updated at "+time.asctime())
