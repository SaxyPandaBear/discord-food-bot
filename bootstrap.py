# Purpose of this script is to read
# environment variables, in order to
# create the auths.py file, and the 
# subreddits.txt file necessary to run
# the app.
# This is mainly to bootstrap for 
# Heroku deployments
# Usage: python bootstrap.py --commit
# '--commit': add the --commit in order to
#             actually write the file out
#             to disk.
import os
import sys


dry_run = True
auths_file_name = "auths.py"
subs_file_name = "subreddits.txt"


def main():
    # Read os.environ in order to get all of the 
    # necessary environment variables:
    # 1. SUBREDDITS -> comma delimited list of subreddits
    # 2. REDDIT_CLIENT_ID
    # 3. REDDIT_CLIENT_SECRET
    # 4. DISCORD_TOKEN
    if "SUBREDDITS" not in os.environ or \
        "REDDIT_CLIENT_ID" not in os.environ or \
        "REDDIT_CLIENT_SECRET" not in os.environ or \
        "DISCORD_TOKEN" not in os.environ:
        print('Missing required parameters to bootstrap application')
        sys.exit(1)
    else:
        subreddits = os.environ["SUBREDDITS"]
        client_id = os.environ["REDDIT_CLIENT_ID"]
        client_secret = os.environ["REDDIT_CLIENT_SECRET"]
        discord_token = os.environ["DISCORD_TOKEN"]

        if dry_run:
            print('Detected dry-run mode. Will not persist data to disk.')
        # Write the data out to its respective locations
        write_data_to_auth(client_id, client_secret, discord_token)
        write_data_to_subs(subreddits)


def write_data_to_auth(client_id, client_secret, discord_token):
    if not dry_run:
        with open(auths_file_name, 'w') as f:
            f.write(f"reddit_client_id = '{client_id}'\n")
            f.write(f"reddit_client_secret = '{client_secret}'\n")
            f.write(f"discord_token = '{discord_token}'")
        print(f"Wrote data out to {auths_file_name}")
    else:
        print(f'Would have written {client_secret}, {client_secret}, {discord_token} to {auths_file_name}')


# take the comma delimited subreddits and output
# them to the subreddits file
def write_data_to_subs(subreddits_str: str):
    subs = subreddits_str.split(',')
    if not dry_run:
        with open(subs_file_name, 'w') as f:
            for sub in subs:
                f.write(sub + '\n')
        print(f"Wrote data out to {subs_file_name}")
    else:
        print(f"Would have written {subs} to {subs_file_name}")


if __name__ == '__main__':
    if '--commit' in sys.argv:
        dry_run = False
    main()
