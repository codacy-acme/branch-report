#!/usr/bin/env python3
import argparse
import requests
import json



#TODO: paginate instead of requesting 10000 repos
def listRepositories(baseurl, provider, organization, token):
    if token == None:
        raise Exception('api-token needs to be defined')
    headers = {
        'Accept': 'application/json',
        'api-token': token
    }
    url = '%s/api/v3/analysis/organizations/%s/%s/repositories?limit=10000'%(baseurl,provider, organization)
    r = requests.get(url, headers=headers)
    repositories = json.loads(r.text)
    for repository in repositories['data']:
        #print(repository)
        print('[%s] %s (%s coverage)'%(repository['repository']['repositoryId'],repository['repository']['name'], (repository['coverage']['coveragePercentage'] if ('coverage' in repository and 'coveragePercentage' in repository['coverage'] != None) else '-' )))
    return repositories['data']


def listRepositoryBranches(baseurl, provider, organization, repository, token):
    url = '%s/api/v3/organizations/%s/%s/repositories/%s/branches?limit=10000'%(baseurl,provider, organization, repository)
    return

def main():
    print('Welcome to Codacy Branch Report')
    parser = argparse.ArgumentParser(description='Codacy Engine Helper')
    parser.add_argument('--token', dest='token', default=None, help='the api-token to be used on the REST API', required=True)
    parser.add_argument('--baseurl', dest='baseurl', default='https://app.codacy.com', help='codacy server address (ignore if cloud)')
    parser.add_argument('--provider', dest='provider', default=None, help='git provider', required=True)
    parser.add_argument('--organization', dest='organization', default=None, help='organization id', required=True)
    args = parser.parse_args()

    listRepositories(args.baseurl, args.provider, args.organization, args.token)

main()