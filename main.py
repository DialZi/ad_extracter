from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException, LDAPBindError
import os
import csv
import json
import re

HATE_DOCKER = True # Don't forget create file .env, if hate docker :)
with open('.env', 'r') as fh:
    vars_dict = dict(
        tuple(line.strip().split('=', 1)) for line in fh.readlines() if not line.startswith('#')
    )
# print(vars_dict)
AD_USERNAME = vars_dict['AD_USERNAME'] if HATE_DOCKER else os.getenv('AD_USERNAME')
AD_DOMAIN = vars_dict['AD_DOMAIN'] if HATE_DOCKER else os.getenv('AD_DOMAIN')
AD_PASSWORD = vars_dict['AD_PASSWORD'] if HATE_DOCKER else os.getenv('AD_PASSWORD')
AD_HOST = vars_dict['AD_HOST'] if HATE_DOCKER else os.getenv('AD_HOST')
AD_PORT = vars_dict['AD_PORT'] if HATE_DOCKER else os.getenv('AD_PORT')
AD_SEARCH = vars_dict['AD_SEARCH'] if HATE_DOCKER else os.getenv('AD_SEARCH')


# Choose attributes for extracting
ATTRIBUTES = ['sAMAccountName', 'cn','mail','memberOf', 'distinguishedName'] 
# Search filters
SEARCHED_FILTERS = '(objectClass=user)'
# Highlight groups
HIGHLIGHT_GROUPS = ['Blocked']


def connect_ldap_server():
    try:
        server = Server(AD_HOST, port=int(AD_PORT), use_ssl=True, get_info=ALL)
        upn = "{}@{}".format(AD_USERNAME, AD_DOMAIN)
        conn = Connection(server, user=upn, password=AD_PASSWORD, auto_bind='NONE', version=3,
                                            authentication='SIMPLE', client_strategy='SYNC', auto_referrals=False,
                                            check_names=True, read_only=True, lazy=False, raise_exceptions=False)
        bind_response = conn.bind() # Returns True or False
        if bind_response:
            print('Binded')
        else:
            print('not Binded')
        return conn
    except LDAPBindError as e:
        connection = e


def get_ldap_users():
    search_base = AD_SEARCH
    search_filter = SEARCHED_FILTERS
    ldap_conn = connect_ldap_server()
    try:

        ldap_conn.search(search_base=search_base,
                         search_filter=search_filter,
                         search_scope=SUBTREE,
                         attributes=ATTRIBUTES)
        results = ldap_conn
    except LDAPException as e:
        results = e
    return results


users = get_ldap_users()
f = csv.writer(open("users.csv", "w"))
f.writerow(ATTRIBUTES + HIGHLIGHT_GROUPS)
for user in users.entries:
    row = []
    row_HIGHLIGHT_GROUPS = {}
    for g in HIGHLIGHT_GROUPS:
        row_HIGHLIGHT_GROUPS.update({g: "False"})
    for attribute in ATTRIBUTES:
        if attribute == 'memberOf' or attribute == 'distinguishedName':
            all_gropus = set()
            for row_item in user.entry_attributes_as_dict[attribute]:
                all_gropus.update(re.findall(r'CN=([^,]*)', row_item))
                all_gropus.update(re.findall(r'OU=([^,]*)', row_item))
            for g in HIGHLIGHT_GROUPS:
                if g in all_gropus:
                    row_HIGHLIGHT_GROUPS.update({g: "True"})
            
        col = ', '.join(user.entry_attributes_as_dict[attribute])
        re_AD_SEARCH = str(AD_SEARCH) + '[,]?'
        col = re.sub(re_AD_SEARCH, '', col)
        col = re.sub("[],]?$", '', col)
        row.append(col)
    f.writerow(row + list(row_HIGHLIGHT_GROUPS.values()))