import yaml
from collections import Counter

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.Loader)

print(Counter([user['login_location'] for user in data['users']]))
