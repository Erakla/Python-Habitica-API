from HabiticaAPI.Client import Account
import json
from threading import Thread
import requests

def savefile(filename: str, data, is_json: bool = True, cls=None):
    with open('manual_usage_data/'+filename, "wt") as file:
        if is_json:
            file.write(json.dumps(data, indent="\t"))
        else:
            file.write(data)
    return data

def cast_spell(acc: Account, skill, times, target_id=''):
    url = 'https://habitica.com/api/v3/user/class/cast/%s' % skill
    if target_id:
        url += "?targetId=%s" % target_id
    for i in range(times):
        Thread(target=requests.post, kwargs={"url": url, "headers": acc.send.header}).start()

def determine_best_valued_task(acc: Account):
    tasks = acc.send('get', 'api/v3/tasks/user', False)
    taskvalue = 0
    taskid = ''

    # find best task
    for task in tasks:
        if task['value'] > taskvalue:
            taskvalue = task['value']
            taskid = task['id']
    if taskvalue < 0: taskvalue = 0
    return taskid, taskvalue

def determine_best_rogue_spell(acc: Account, profile, objects, user_id):
    equip_for_stat(acc, 'per', profile, objects)
    per = acc.user_get_profile(user_id, False)['data']['stats']['per']

    _, taskvalue = determine_best_valued_task(acc)

    # pickPocket
    Bonus = (taskvalue + 1) + (per * 0.5)
    Gold = 25 * Bonus / (Bonus + 75)
    print("Taschendiebstahl: %d Gold" % Gold)

    equip_for_stat(acc, 'str', profile, objects)
    str = acc.user_get_profile(user_id, False)['stats']['str']

    # backStab
    Bonus = (taskvalue + 1) + (str * 0.5)
    XP = 75 * Bonus / (Bonus + 50)
    Gold = 18 * Bonus / (Bonus + 75)
    print("Überraschungsangriff: %d Gold, %d XP" % (Gold, XP))

def equip_for_stat(acc: Account, stat, profile, objects):
    own_gear = profile['items']['gear']['owned']
    con_gear = objects['gear']['flat']
    best_items = {}
    equiped = 0
    for key in own_gear:
        if con_gear[key][stat] > best_items.get(con_gear[key]['type'], ('', 0))[1]:
            best_items[con_gear[key]['type']] = (key, con_gear[key][stat])
    for type in best_items:
        key = best_items[type][0]
        if key != profile['items']['gear']['equipped'].get(type, ''):
            profile['items'].update(acc.send('post', 'api/v3/user/equip/equipped/%s' % key, False))
            equiped += 1
    return equiped