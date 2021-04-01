import HabiticaAPI.SendQueue as SendQueue
import HabiticaAPI.Profile as Profile
import HabiticaAPI.Group as Group
import time


# todo add docstrings
# todo test functions
# todo check environment state of habitica (disable development functions)


class Account:
    def __init__(self, data: dict, user_id: str, api_token: str):
        self.__data = {'acc': self}
        self.__data.update(data)
        x_client = "%s-%s" % (self.__data['author_uid'], self.__data['application_name'])
        self.send = SendQueue.SendQueue(self.__data, {"x-client": x_client, "x-api-user": user_id, "x-api-key": api_token})
        self.__data['send'] = self.send
        self.user_id = user_id
        self.api_token = api_token
        self.profile = Profile.Profile(self.__data, self.user_id)

    def __delete__(self, instance):
        if self.send.sender.is_alive():
            if self.__data['print_status_info']:
                print(len(self.send.queue), "requests pending...")
            self.send.sender.join()

    @property
    def objects(self):
        if self.__data['objects']['appVersion'] == '':
            self.send.refresh_objects('')
        return self.__data['objects']

    @property
    def party(self):
        return Group.Group(self.__data, self.profile['party']['_id'])

    def ProfileList(self, ids: list):
        return Profile.ProfileList(self.__data, ids)

    def get_profile_by_id(self, user_id):
        return Profile.Profile(self.__data, user_id)


    # function implementations
    def challenge_clone(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/challenges/%s/clone' % challenge_id, queued, callback)

    def challenge_create(self, group: int, name: str, short_name: str, summary: str = None, description: str = None,
                         prize: int = None, official: bool = None, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/challenges', queued, callback, {
            'challenge': {
                'group': group,
                'name': name,
                'short_name': short_name,
                'summary': summary,
                'description': description,
                'prize': prize
            },
            'official': official
        })

    def challenge_delete(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/challenges/%s' % challenge_id, queued, callback)

    def challenge_export_csv(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/challenges/%s/export/csv' % challenge_id, queued, callback)

    def challenge_get(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/challenges/%s' % challenge_id, queued, callback)

    def challenges_get_for_group(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/challenges/groups/%s' % group_id, queued, callback)

    def challenges_get_for_user(self, page: int, member: str, owned: str, search: str, categories: str,
                                queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/challenges/user?page=%d&member=%s&owned=%s&search=%s&categories=%s' % (
            page, member, owned, search, categories), queued, callback)

    def challenge_join(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/challenges/%s/join' % challenge_id, queued, callback)

    def challenge_leave(self, challenge_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/challenges/%s/leave' % challenge_id, queued, callback)

    def challenge_select_winner(self, challenge_id: str, winner_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/challenges/%s/selectWinner/%s' % (challenge_id, winner_id), queued, callback)

    def challenge_update(self, challenge_id: str, name: str = None, summary: str = None, description: str = None,
                         queued: bool = True, callback: object = None):
        data = {}
        if name:
            data['name'] = name
        if summary:
            data['summary'] = name
        if description:
            data['description'] = name
        return self.send('put', 'api/v3/challenges/%s' % challenge_id, queued, data, callback)

    def challenge_member_get_process(self, challenge_id: str, user_id: str, queued: bool = True,
                                     callback: object = None):
        return self.send('get', 'api/v3/challenges/%s/members/%s' % (challenge_id, user_id), queued, callback)

    def challenge_get_members(self, challenge_id: str, last_id: str = None, limit: int = None,
                              include_tasks: bool = None, include_all_public_fields: bool = None, queued: bool = True,
                              callback: object = None):
        query = 'api/v3/challenges/%s/members'
        params = []
        if last_id:
            params.append("lastId=%s" % last_id)
        if limit:
            params.append("limit=%d" % limit)
        if include_tasks:
            params.append("includeTasks=%s" % str(include_tasks).lower())
        if include_all_public_fields:
            params.append("includeAllPublicFields=%s" % str(include_all_public_fields).lower())
        if params:
            query += "?" + "&".join(params)
        return self.send('get', query % challenge_id, queued, callback)

    def chat_group_msg_clear_flags(self, group_id: str, chat_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/chat/%s/clearflags' % (group_id, chat_id), queued, callback)

    def chat_group_msg_delete(self, group_id: str, chat_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/groups/%s/chat/%s?previousMsg=%s' % (
        group_id, chat_id, self.groups[group_id]['chat'][0]['id']),
                         queued, callback)

    def chat_group_msg_flag(self, group_id: str, chat_id: str, comment: str = None, queued: bool = True,
                            callback: object = None):
        data = {'comment': comment} if comment else None
        return self.send('post', 'api/v3/groups/%s/chat/%s/flag' % (group_id, chat_id), queued, data, callback)

    def chat_group_msg_get(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/groups/%s/chat' % group_id, queued, callback)

    def chat_group_msg_like(self, group_id: str, chat_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/chat/%s/like' % (group_id, chat_id), queued, callback)

    def chat_group_all_mark_read(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/chat/seen' % group_id, queued, callback)

    def coupons_generate(self, event: str, count: int, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/coupons/generate/%s?count=%d' % (event, count), queued, callback)

    def coupons_get_csv(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/coupons', queued, callback)

    def coupon_redeem(self, code: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/coupons/enter/%s' % code, queued, callback)

    def coupon_validate(self, code: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/coupons/validate/%s' % code, queued, callback)

    def cron_run(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/cron', queued, callback)

    def export_userdata_json(self, queued: bool = True, callback: object = None):
        return self.send('get', 'export/userdata.json', queued, callback)

    def export_userdata_xml(self, queued: bool = True, callback: object = None):
        return self.send('get', 'export/userdata.xml', queued, callback)

    def export_private_messages_html(self, queued: bool = True, callback: object = None):
        return self.send('get', 'export/inbox.html', queued, callback)

    def export_tasks_history_csv(self, queued: bool = True, callback: object = None):
        return self.send('get', 'export/history.csv', queued, callback)

    def export_render_user_avatar_png(self, uuid: str, queued: bool = True, callback: object = None):
        return self.send('get', 'export/avatar-%s.png' % uuid, queued, callback)

    def export_render_user_avater_html(self, uuid: str, queued: bool = True, callback: object = None):
        return self.send('get', 'export/avatar-%s.html' % uuid, queued, callback)

    def development_user_add_hourglass(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/debug/add-hourglass', queued, callback)

    def development_user_add_ten_gems(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/debug/add-ten-gems', queued, callback)

    def development_artificially_accelerate_quest_progress(self, queued: bool = True, callback: object = None):
        return self.send('get', 'post', queued, callback)

    def development_set_inventory(self, gear, special, pets, mounts, eggs, hatching_potions, food, quests,
                                  queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/debug/modify-inventory', queued, callback, {
            'gear': gear,
            'special': special,
            'pets': pets,
            'mounts': mounts,
            'eggs': eggs,
            'hatchingPotions': hatching_potions,
            'food': food,
            'quests': quests
        })

    def development_set_last_cron(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/debug/set-cron', queued, callback)

    def development_make_admin(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/debug/make-admin', queued, callback)

    def group_manager_add(self, group_id: str, user_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/add-manager' % group_id, queued, {'managerId': user_id}, callback)

    def group_create_plan(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/create-plan', queued, callback)

    def group_create(self, name: str, grouptype: str, privacy: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups', queued, callback, {
            'name': name,
            'type': grouptype,
            'privacy': privacy
        })

    def group_get_plans(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/group-plans', queued, callback)

    def group_get(self, group_id, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/groups/%s' % group_id, queued, callback)

    def group_invite_users(self, group_id: str, emails: list = None, uuids: list = None, queued: bool = True,
                           callback: object = None):
        data = {}
        if emails is not None:
            data['emails'] = emails
        if uuids is not None:
            data['uuids'] = uuids
        return self.send('post', 'api/v3/groups/%s/invite' % group_id, queued, data, callback)

    def group_join(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/join' % group_id, queued, callback)

    def group_leave(self, group_id: str, keep: str, keep_challenges: str = None, queued: bool = True,
                    callback: object = None):
        data = {'keepChallenges': keep_challenges} if keep_challenges else None
        return self.send('post', 'api/v3/groups/%s/leave?keep=%s' % (group_id, keep), queued, data, callback)

    def group_invite_reject(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/reject-invite' % group_id, queued, callback)

    def group_remove_manager(self, group_id: str, user_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/remove-manager' % group_id, queued, {'managerId': user_id}, callback)

    def group_remove_member(self, group_id: str, user_id: str, message: str, queued: bool = True,
                            callback: object = None):
        return self.send('post', 'api/v3/groups/%s/removeMember/%s?message=%s' % (group_id, user_id, message), queued,
                         callback)

    def group_update(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('put', 'api/v3/groups/%s' % group_id, queued, callback)

    def group_get_invites(self, group_id: str, last_id: str = None, limit: int = None,
                          include_all_public_fields: bool = None, queued: bool = True, callback: object = None):
        query = 'api/v3/groups/%s/invites'
        params = []
        if last_id:
            params.append("lastId=%s" % last_id)
        if limit:
            params.append("limit=%d" % limit)
        if include_all_public_fields:
            params.append("includeAllPublicFields=%s" % str(include_all_public_fields).lower())
        if params:
            query += "?" + "&".join(params)
        return self.send('get', query % group_id, queued, callback)

    def group_get_members(self, group_id: str, last_id: str = None, limit: int = None, include_tasks: bool = None,
                          include_all_public_fields: bool = None, queued: bool = True, callback: object = None):
        query = 'api/v3/groups/%s/members'
        params = []
        if last_id:
            params.append("lastId=%s" % last_id)
        if limit:
            params.append("limit=%d" % limit)
        if include_tasks:
            params.append("includeTasks=%s" % str(include_tasks).lower())
        if include_all_public_fields:
            params.append("includeAllPublicFields=%s" % str(include_all_public_fields).lower())
        if params:
            query += "?" + "&".join(params)
        return self.send('get', query % group_id, queued, callback)

    def hall_get_all_heroes(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/hall/heroes', queued, callback)

    def hall_get_all_patrons(self, page: int = None, queued: bool = True, callback: object = None):
        query = 'api/v3/hall/patrons'
        if page is not None:
            query += "?page=%d" % page
        return self.send('get', query, queued, callback)

    def hall_get_user(self, user_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/hall/heroes/%s' % user_id, queued, callback)

    def hall_update_user(self, user_id: str, queued: bool = True, callback: object = None):
        return self.send('put', 'api/v3/hall/heroes/%s' % user_id, queued, callback)

    def inbox_get_messages(self, page: int, conversation_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/inbox/messages?page=%d&conversation=%s' % (page, conversation_id), queued,
                         callback)

    def user_get_groups(self, grouptypes: [str], paginate: str = None, page: int = None, queued: bool = True,
                        callback: object = None):
        query = 'api/v3/groups?type=%s' % ','.join(grouptypes)
        if paginate is not None:
            query += '&paginate=%s' % paginate
        if page is not None:
            query += '&page=%d' % page
        return self.send('get', query, queued, callback)

    def user_get_profile(self, user_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/members/%s' % user_id, queued, callback)

    def user_get_achievements(self, user_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/members/%s/achievements' % user_id, queued, callback)

    def user_get_objections_to_interaction(self, user_id: str, interaction: str, queued: bool = True,
                                           callback: object = None):
        return self.send('get', 'api/v3/members/%s/objections/%s' % (user_id, interaction), queued, callback)

    def user_send_gem_gift(self, message: str, user_id: str, amount: int, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/members/transfer-gems', queued, callback, {
            'message': message,
            'toUserId': user_id,
            'gemAmount': amount
        })

    def user_send_private_message(self, message: str, user_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/members/send-private-message', queued, callback, {
            'message': message,
            'toUserId': user_id
        })

    def meta_get_paths_for_model(self, model: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/models/%s/paths' % model, queued, callback)

    def news_bailey_allow_latest_announcement_to_be_read_later(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/news/tell-me-later', queued, callback)

    def news_bailey_get_latest_announcement(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/news', queued, callback)

    def news_bailey_get_latest_announcements(self, page: int = None, queued: bool = True, callback: object = None):
        query = 'api/v3/news'
        if page is not None:
            query += "?page=%d" % page
        return self.send('get', query, queued, callback)

    def news_bailey_mark_latest_as_read(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v4/news/read', queued, callback)

    def news_post_create(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v4/news', queued, callback)

    def news_post_delete(self, post_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v4/news/%s' % post_id, queued, callback)

    def news_post_get(self, post_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v4/news/%s' % post_id, queued, callback)

    def news_post_update(self, post_id: str, queued: bool = True, callback: object = None):
        return self.send('put', 'api/v4/news/' % post_id, queued, callback)

    def notifications_mark_multiple_as_read(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/notifications/read', queued, callback)

    def notifications_mark_multiple_as_seen(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/notifications/see', queued, callback)

    def notification_mark_as_read(self, notification_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/notifications/%s/read' % notification_id, queued, callback)

    def notification_mark_as_seen(self, notification_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/notifications/%s/see' % notification_id, queued, callback)

    def quest_abort_current(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/abort' % group_id, queued, callback)

    def quest_accept_pending(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/accept' % group_id, queued, callback)

    def quest_cancel_inactive_quest(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/cancel' % group_id, queued, callback)

    def quest_force_start_pending_quest(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/force-start' % group_id, queued, callback)

    def quest_invite_group(self, group_id: str, quest_key: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/invite/%s' % (group_id, quest_key), queued, callback)

    def quest_leave(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/leave' % group_id, queued, callback)

    def quest_reject(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/groups/%s/quests/reject' % group_id, queued, callback)

    def api_get_status(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/status', queued, callback)

    def tag_create(self, name: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tags', queued, {'name': name}, callback)

    def tag_delete(self, tag_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/tags/%s' % tag_id, queued, callback)

    def tag_get(self, tag_id: str, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/tags/%s' % tag_id, queued, callback)

    def tags_get_all(self, queued: bool = True, callback: object = None):
        return self.send('get', 'api/v3/tags', queued, callback)

    def tag_reorder(self, tag_id: str, position_to: int, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/reorder-tags', queued, callback, {
            'tagId': tag_id,
            'to': position_to
        })

    def tag_update(self, tag_id: str, name: str, queued: bool = True, callback: object = None):
        return self.send('put', 'api/v3/tags/%s' % tag_id, queued, {'name': name}, callback)

    def task_add_tag(self, task_id: str, tag_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/%s/tags/%s' % (task_id, tag_id), queued, callback)

    def task_add_item(self, task_id: str, text: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/%s/checklist' % task_id, queued, callback, {'text': text})

    def task_approve_user_assigned(self, task_id: str, user_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/%s/approve/%s' % (task_id, user_id), queued, callback)

    def task_of_group_assign_to_user(self, task_id: str, user_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/%s/assign/%s' % (task_id, user_id), queued, callback)

    def task_create_for_challenge(self, challenge_id: str, text: str, tasktype: str, attribute: str = None,
                                  collapse_check_list: bool = False, notes: str = None, date: str = None,
                                  priority: float = 1, reminders: [dict] = None, frequency: str = 'weekly',
                                  repeat: {str: False} = True, every_x: int = None, streak: int = 0,
                                  days_of_month: [int] = None, weeks_of_month: [int] = None, start_date: str = None,
                                  up: bool = True, down: bool = True, value: int = 0, queued: bool = True,
                                  callback: object = None):
        data = {'text': text, 'type': type}
        if attribute and attribute in ["str", "int", "per", "con"]:
            data['attribute'] = attribute
        if collapse_check_list:
            data['collapseChecklist'] = True
        if notes:
            data['notes'] = notes
        if date and tasktype == 'todo':
            data['date'] = date
        if priority and priority in [0.1, 1.5, 2]:
            data['priority'] = priority
        if reminders:
            data['reminders'] = reminders
        if frequency and tasktype == 'daily' and frequency in ["daily", "weekly", "monthly", "yearly"]:
            data['frequency'] = frequency
        if repeat and type(repeat) == dict and data.get('frequency', None) in ["weekly", "monthly"]:
            data['repeat'] = repeat
        if every_x and data.get('frequency', False) == 'daily':
            data['everyX'] = every_x
        if streak:
            data['streak'] = streak
        if days_of_month and tasktype == 'daily':
            data['daysOfMonth'] = days_of_month
        if weeks_of_month and tasktype == 'daily':
            data['weeksOfMonth'] = weeks_of_month
        if start_date and tasktype == 'daily':
            data['startDate'] = start_date
        if not up and tasktype == 'habit':
            data['up'] = False
        if not down and tasktype == 'habit':
            data['down'] = False
        if value and tasktype == 'reward':
            data['value'] = value

        return self.send('post', 'api/v3/tasks/challenge/%s' % challenge_id, queued, data, callback)

    def task_create_for_group(self, group_id: str, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/group/%s' % group_id, queued, callback)

    def task_create_for_user(self, text: str, tasktype: str, tags: [str] = None, checklist: list = None,
                             alias: str = None, attribute: str = None,
                             collapse_check_list: bool = False, notes: str = None, date: str = None,
                             priority: float = 1, reminders: [dict] = None, frequency: str = 'weekly',
                             repeat: {str: False} = True, every_x: int = None, streak: int = 0,
                             days_of_month: [int] = None, weeks_of_month: [int] = None, start_date: str = None,
                             up: bool = True, down: bool = True, value: int = 0, queued: bool = True,
                             callback: object = None):
        data = {'text': text, 'type': tasktype}
        if tags:
            data['tags'] = tags
        if alias:
            data['alias'] = alias
        if attribute and attribute in ["str", "int", "per", "con"]:
            data['attribute'] = attribute
        if collapse_check_list:
            data['collapseChecklist'] = True
        if notes:
            data['notes'] = notes
        if date and tasktype == 'todo':
            data['date'] = date
        if priority and priority in [0.1, 1.5, 2]:
            data['priority'] = priority
        if reminders:
            data['reminders'] = reminders
        if tasktype == 'daily' and frequency in ["daily", "weekly", "monthly", "yearly"]:
            data['frequency'] = frequency
        if repeat and type(repeat) == dict and data.get('frequency', None) in ["weekly", "monthly"]:
            data['repeat'] = repeat
        if every_x and data.get('frequency', False):
            data['everyX'] = every_x
        if streak:
            data['streak'] = streak
        if days_of_month and tasktype == 'daily':
            data['daysOfMonth'] = days_of_month
        if weeks_of_month and tasktype == 'daily':
            data['weeksOfMonth'] = weeks_of_month
        if start_date and tasktype == 'daily':
            data['startDate'] = start_date
        if not up and tasktype == 'habit':
            data['up'] = False
        if not down and tasktype == 'habit':
            data['down'] = False
        if value and tasktype == 'reward':
            data['value'] = value
        if checklist:
            data['checklist'] = checklist

        return self.send('post', 'api/v3/tasks/user', queued, callback, data)

    def task_delete_item(self, task_id: str, item_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/tasks/%s/checklist/%s' % (task_id, item_id), queued, callback)

    def task_delete_tag(self, task_id: str, tag_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/tasks/%s/tags/%s' % (task_id, tag_id), queued, callback)

    def task_delete(self, task_id: str, queued: bool = True, callback: object = None):
        return self.send('delete', 'api/v3/tasks/%s' % task_id, queued, callback)

    def task_delete_completed_todos(self, queued: bool = True, callback: object = None):
        return self.send('post', 'api/v3/tasks/clearCompletedTodos', queued, callback)

    def challenge_get_tasks(self, challenge_id: str, tasktype: str = None, queued: bool = True,
                            callback: object = None):
        query = 'api/v3/tasks/challenge/%s'
        if tasktype:
            query += "?type=%s" % tasktype
        return self.send('get', query % challenge_id, queued, callback)
# def funcname(self, funcargs, queued: bool = True):
#     return self.send('get', 'url', queued, callback: object = None, callback)
