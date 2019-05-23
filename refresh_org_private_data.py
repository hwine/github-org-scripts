#!/usr/bin/env python
# coding: utf-8

# In[6]:


import time
import yaml
import github3
print github3.__version__
script_dir = '~/repos/github-org-scripts/'
#get_ipython().system('git --git-dir $script_dir/.git status -sbu no')

import os
org_name = os.environ["ORG"]

# In[3]:


#cd $script_dir


# In[4]:


from client import get_github3_client
gh = get_github3_client()


# In[80]:


# fix broken datetime api
import datetime


# In[5]:


# get or refresh data
try:
    org.refresh(conditional=True)
except NameError:
    org = gh.organization(org_name)

owners = list(org.members(role='admin'))
members = list(org.members(role='members'))
teams = list(org.teams())
private_repos = list(org.repositories(type='private'))


# In[81]:


# build the snapshot - basics first
snapshot = {
    'organization': org.name,
    'last_modified': org.last_modified,
    'last_snapshot_update':  datetime.datetime.now(github3.utils.UTC()),
    'owners': [x.login for x in owners],
    'members': [x.login for x in members],
}

# teams and their members
snapshot['team'] = { x.name: [y.login for y in x.members()] for x in teams}


# That's it for the simple data. For each private repo, we have to go through the repo to the members to the user to find their permission for that repo.

# In[82]:


def get_permissions(iter):
    """ Return list of tuples (id, perms)"""
    tups = []
    for agent in iter():
        if 'login' in agent.as_dict():
            # Users have login
            name = agent.login
        else:
            # Teams don't have login - name instead
            name = agent.name  # assume team
        perm = extract_permissions(agent)
        tups.append((name, perm))
    return tups


# We have the ugly type of polymorphism here -- permissions are stored differently depending on agent type:
#   - a team has a single valued string: 'permission' (value: 'admin', 'push', 'pull')
#   - a user in a contributor context does not have a value
#   - otherwise a user has a dictionary: 'permissions', with a boolean for each of the permission values
#  
# Compounding that, those attributes are only materialized on the object only if it appears in the underlying json data (which is mirrored to a dict). That is a contributor permission is not 'None', it is 'AttributeError'.
# 
# Lets normalize everything into the single valued string format, as those value form a strict hierarchy.

# In[83]:


permission_values = ('admin', 'push', 'pull')
def extract_permissions(agent):
    permission = None
    if 'permission' in agent.as_dict():
        permission = agent.permission
    elif 'permissions' in agent.as_dict():
        # pick highest value
        for p in permission_values:
            if agent.permissions[p]:
                permission = p
                break
    return permission


# In[86]:


# not all repositories will have an event history
def get_last_event_time(repo):
    when = None
    try:
        when = r.events().next().created_at
    except StopIteration:
        pass
    return when


# In[87]:


# N.B. "contributors" never have permissions, but grab them as possible contact points
p_repos = []
for r in private_repos:
    p_repos.append({
        'name': r.name,
        'updated_at': r.updated_at,
        'latest_event': get_last_event_time(r),
        'collaborators_perm': get_permissions(r.collaborators),
        'contributors_perm': get_permissions(r.contributors),
        'team_perm': get_permissions(r.teams),
        })
snapshot['private_repos'] = p_repos


# In[88]:


# Time to save it
with open('./private_repo_membership.yaml', 'w') as f:
    yaml.safe_dump(snapshot, f, default_flow_style=False, explicit_start=True)

