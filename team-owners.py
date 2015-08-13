#!/usr/bin/env python
import urllib

import requests

from client import get_token

def get_all_responses(url, headers):
    """ Get all response by following next links """
    # first, get all teams, so we can find team id
    resp = requests.get(url, headers=headers)
    payload = resp.json()
    # get rest of pages
    while True:
        try:
            next_url = resp.links['next']['url']
        except KeyError:
            break
        resp = requests.get(next_url, headers=headers)
        payload.extend(resp.json())
    return payload


if __name__ == '__main__':
    headers = {
        'Accept': 'application/vnd.github.ironman-preview+json',
        'Authorization': 'token %s' % get_token()
    }
    # first, get all teams, so we can find team id
    list_teams_url = 'https://api.github.com/orgs/%s/teams' % 'mozilla'
    teams = get_all_responses(list_teams_url, headers=headers)
    this_team = [x for x in teams if x['name'] == 'quality']
    if not this_team:
        raise SystemExit('No such team')
    elif len(this_team) > 1:
        raise SystemExit('Too many matches')
    team_id = this_team[0]['id']

    # we want maintainers of group
    params = {'role': 'maintainer'}

    team_maintainers_url = '%s?%s' % (
        'https://api.github.com/teams/%s/members' % team_id,
        urllib.urlencode(params)
    )
    resp = requests.get(team_maintainers_url, headers=headers)

    team_maintainers = resp.json()
    email_targets = []
    if team_maintainers:
        print 'The following are maintainers:'
        for a in team_maintainers:
            print a['login']
            email_targets.append(a['login'])
    else:
        print 'No maintainers yet, members are:'
        team_members_url = 'https://api.github.com/teams/%s/members' % team_id
        team_members = get_all_responses(team_members_url, headers=headers)
        for a in team_members:
            print a['login']
            email_targets.append(a['login'])
    # get email address now
    no_email_addr = []
    print "The emails you need are:"
    for user_login in email_targets:
        user_url = 'https://api.github.com/users/%s' % user_login
        resp = requests.get(user_url, headers=headers)
        user_info = resp.json()
        email = user_info.get('email', '')
        if email:
            print "%s," % email,
        else:
            no_email_addr.append(user_login)
    print
    if no_email_addr:
        print "You may need to research these github user names further:"
        print ' '.join(no_email_addr)
