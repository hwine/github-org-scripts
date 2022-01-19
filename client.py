from datetime import datetime
import os
import time

from github3 import login


CREDENTIALS_FILE = ".credentials"


def get_token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
    if not token:
        raise KeyError(
            """ERROR - GitHub token must be provided via environment"""
            """ variable "GITHUB_TOKEN" or "GITHUB_PAT"."""
            """ Please delete any old ".credentials" file."""
        )
    return token


# get_token()


def get_github3_client():
    token = get_token()
    gh = login(token=token)
    return gh


# keep the most recently fetched rates object, so it can be inspected after a
# rate limit response occurs
rates = {}


def sleep_if_rate_limited(gh, verbose=False, min: int = 1):
    global rates
    rates = gh.rate_limit()

    if rates["resources"]["search"]["remaining"] <= min:
        reset_epoch = rates["resources"]["search"]["reset"]

        reset_dt, now = datetime.utcfromtimestamp(reset_epoch), datetime.utcnow()

        if reset_dt > now:
            sleep_secs = (reset_dt - now).seconds + 1

            if verbose:
                print(
                    (
                        "sleeping for",
                        sleep_secs,
                        "got rate limit",
                        rates["resources"]["search"],
                    )
                )

            time.sleep(sleep_secs)
