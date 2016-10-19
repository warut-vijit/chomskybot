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
    # print("Finished")


def get_members():
    global members
    response = requests.get("https://api.groupme.com/v3/groups/" + groupid + "?token=" + token).json()['response']['members']
    newmembers = {}
    for member in response:
        newmembers[member['nickname']] = member['id']
    if len(newmembers) < len(members) and not perms['kick']: #Member was removed
        for member in members:
            if member not in newmembers:
                requests.post("https://api.groupme.com/v3/groups/" + groupid + "/members/add?token="+token+"&nickname="+member+"&user_id="+members[member])
                post_message('User ' + member + " has been re-added in compliance with group policy.")
    else:
        members = newmembers
    #  print members


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
    global members
    if 'promote' in text:
        # print(members.keys())
        print text[8:] in members
        if text[8:] in members and text[8:] not in mods:
            mods.append(text[8:])
            post_message('User '+text[8:]+' has been appointed as moderator')
    elif 'perms' in text:
        substr = text[6:].split(' ')
        if 'list' in text:
            permstr = 'Permissions are:'
            for perm in perms:
                permstr += '\n    '+perm+': '+str(perms[perm])
            post_message(permstr)
        elif substr[0] in perms:
            if substr[1].lower() in ['true', 't', '1']:
                perms[substr[0]] = True
                post_message('Permission '+substr[0]+' has been changed to TRUE')
            elif substr[1].lower() in ['false', 'f', '0']:
                perms[substr[0]] = False
                post_message('Permission '+substr[0]+' has been changed to FALSE')
        else:
            post_message(substr[0]+' is not a valid permission for this group')
    elif 'kick' in text:
        if text[5:] in members and text[5:] != owner:
            requests.post("https://api.groupme.com/v3/groups/"+groupid+"/members/"+members[text[5:]]+"/remove?token="+token)
            members.remove(text[5:])
            post_message('User '+text[5:]+" has been removed.")
    elif 'help' in text:
        help_display()
    elif 'demote' in text:
        if text[7:] in mods:
            mods.pop(text[7:])
            post_message('User '+text[7:]+' has been demoted from moderator')
    elif 'members' in text:
        memstr = 'Members of this group are: '
        for member in members:
            memstr += member
        post_message(memstr)
    elif 'search' in text:
        query = text[7:]
        searchrequest = requests.get('https://en.wikipedia.org/w/api.php?action=opensearch&search='+query+'&limit=1&namespace=0&format=json').json()
        post_message('Here is what I found about '+query+': '+json.dumps(searchrequest))


def process_as_mod(text):
    if 'help' in text:
        help_display()
    elif 'kick' in text:
        if text[5:] in members and text[5:] != owner and text[5:] not in mods:
            requests.post("https://api.groupme.com/v3/groups/"+groupid+"/members/"+members[text[5:]]+"/remove?token="+token)
            members.pop(text[5:])
            post_message('User '+text[5:]+" has been removed.")
    elif 'members' in text:
        memstr = 'Members of this group are: '
        for member in members:
            memstr += member
        post_message(memstr)
    elif 'search' in text:
        query = text[7:]
        searchrequest = requests.get('https://en.wikipedia.org/w/api.php?action=opensearch&search='+query+'&limit=1&namespace=0&format=json').json()
        post_message('Here is what I found about '+query+': '+json.dumps(searchrequest))


def process_as_member(text):
    if 'help' in text:
        help_display()
    elif 'members' in text:
        memstr = 'Members of this group are: '
        for member in members:
            memstr += member
        post_message(memstr)
    elif 'search' in text:
        query = text[7:]
        searchrequest = requests.get('https://en.wikipedia.org/w/api.php?action=opensearch&search='+query+'&limit=1&namespace=0&format=json').json()
        post_message('Here is what I found about '+query+': '+json.dumps(searchrequest))


def help_display():
    modstring = ''
    for moderator in mods:
        modstring += moderator+", "
    post_message('Version: ChomskyBot v1.0.0.\nOwner: ' + owner + "\nMods: " + modstring + "\nOwner functions: promote, help, demote, kick, perms, members, search\nMod functions: help, kick, members, search\nMember functions: help, members, search")


# post_message("I am ChomskyBot v1.0.0. I am here to ensure that this chat runs smoothly.")
# Runtime calls
while True:
    get_members()
    get_last_message()
    time.sleep(1)
    # print("Updated at "+time.asctime())
