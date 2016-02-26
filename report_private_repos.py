#!/usr/bin/env python
"""
    Report on private repos.

    By default, outputs csv format file of private repos in org.
"""

import argparse
import logging
import csv
import sys

from client import get_github3_client

logger = logging.getLogger(__name__)
exit_code = 0

HEADERS = (
    'Repo Name',
    'Create Date',
    'Updated',
    'Hook Count',
    'Admin Teams',
    'users if no teams',
    )


def _iter_length(i):
    # ONLY CALL FOR FINITE ITERABLES!!!!!
    return sum(1 for _ in i)


def get_admin_teams(repo):
    admin_teams = []
    for t in repo.iter_teams():
        if t.permission in ('admin',) and t.name <> u'Core':
            # Core always has admin access, no useful info
            admin_teams.append(t.name)
    return admin_teams


def get_admin_contributors(repo):
    admin_contributors = []
    user_contributors = []
    for t in repo.iter_contributors():
        if t.type not in ('User',):
            logger.info("%s is %s for %s", t.login, t.type, repo.full_name)
        if t.type in ('Admin',):
            admin_contributors.append(t.login)
        elif t.type in ('Users',):
            user_contributors.append(t.login)
    if len(admin_contributors) is 0 and len(user_contributors) > 0:
        admin_contributors.append('USERS:')
        admin_contributors.extend(user_contributors)
    return admin_contributors


def output_repo(repo, cvs_file, short_names=True):
    forked = True if repo.parent else False
    if forked:
        logger.info("Private repo '%s' forked from '%s'",
                repo.full_name, repo.parent.full_name)
    hook_count = _iter_length(repo.iter_hooks())
    contributor_count = None
    teams_with_admin_permissions = get_admin_teams(repo)
    members_with_admin_permissions = []
    if len(teams_with_admin_permissions) == 0:
        members_with_admin_permissions = get_admin_contributors(repo)
    # Google docs spreadsheets can't deal with date/time very well, so
    # just output the dates.
    create_date = repo.created_at.strftime("%Y-%m-%d")
    last_change_date = repo.updated_at.strftime("%Y-%m-%d")
    row = {}
    row['Repo Name'] = repo.name if short_names else repo.full_name
    row['Create Date'] = create_date
    row['Updated'] = last_change_date
    row['Hook Count'] = hook_count
    row['Admin Teams'] = ' '.join(teams_with_admin_permissions)
    row['users if no teams'] = ' '.join(members_with_admin_permissions)
    cvs_file.writerow(row)


def show_private_repos(gh, orgs, cvs_file, short_names=True):
    for org in orgs:
        o = gh.organization(org)
        for r in o.iter_repos(type='private'):
            output_repo(r, cvs_file)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', '-o', help="csv destination (STDOUT)",
            type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--debug', help="include github3 output",
                        action='store_true')
    parser.add_argument('--short-names', help="only use short name of repo",
            action='store_true')
    parser.add_argument("orgs", nargs='*', default=['mozilla', ],
                        help='github organizations to check (defaults to mozilla)')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('github3').setLevel(logging.DEBUG)
    gh = get_github3_client()
    csv_out = csv.DictWriter(args.output, HEADERS)
    csv_out.writeheader()
    show_private_repos(gh, args.orgs, csv_out, args.short_names)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    logging.getLogger('github3').setLevel(logging.WARNING)
    main()
    raise SystemExit(exit_code)
