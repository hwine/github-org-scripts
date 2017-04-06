#!/usr/bin/env python

import requests

from client import get_github3_client


def report_repos(repo_list, msg):
    print "Found %d repos with %s." % (len(repo_list), msg)
    for r in repo_list:
        print r

if __name__ == '__main__':
    gh = get_github3_client()
    headers = {
        'Accept': 'application/vnd.github.drax-preview+json',
    }

    # Divvy up into repositories that have/do not have a LICENSE file.
    mpl_repos = []
    good_repos = []
    bad_repos = []
    gpl_repos = []

    org_name = 'mozilla'
    repos = gh.organization(org_name).repositories(type='sources')
    for repo in repos:
        repo_name = repo.name
        license_url = 'https://api.github.com/repos/%s/%s' % (org_name,
                                                              repo_name)

        resp = requests.get(license_url, headers=headers)
        repo_data = resp.json()

        try:
            license_type = repo_data[u'license'][u'key']
            if license_type == 'mpl-2.0':
                mpl_repos.append(repo.full_name)
            elif 'gpl' in license_type:
                gpl_repos.append(repo.full_name)
            else:
                good_repos.append(repo.full_name)
        except (KeyError, TypeError):
            # any kind of reference error to the license means there
            # is not a license defined (at least not in a way that
            # github understands)
            bad_repos.append(repo.full_name)

    report_repos(mpl_repos, "an MPL license")
    report_repos(gpl_repos, "some sort of GPL license")
    report_repos(good_repos, "a license")
    report_repos(bad_repos, "NO License")
