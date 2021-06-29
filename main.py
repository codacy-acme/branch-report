#!/usr/bin/env python3
import argparse
import requests
import json
import time
import csv



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
    return repositories['data']

   

def getRepositoryBranchMetrics(baseurl, provider, organization, repository, branchname, token):
    if token == None:
        raise Exception('api-token needs to be defined')
    headers = {
        'Accept': 'application/json',
        'api-token': token
    }
    url = '%s/api/v3/organizations/%s/%s/repositories/%s/branches?search=%s'%(baseurl,provider, organization, repository, branchname)
    b = requests.get(url, headers=headers)
    branches = json.loads(b.text)
    for branch in branches['data']:
        if(branch['name'] == branchname):
            print('\t[Branch] %s - Exists on repository %s and is %s'%(branch['name'],repository,('Active' if branch['isEnabled'] else 'Inactive')))        
            return ('Active' if branch['isEnabled'] else 'Inactive')
    
    print('\t[Branch] %s - Doesn\'t exit on repo %s'%(branchname,repository))
    
    return "Inexistent"

def generateCSV(report, filename):
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['repository','repositoryId','coverage-main','branch','branchStatus'])
            for item in report:
                writer.writerow([item['repository'],item['repositoryId'],item['coverage-main'],item['branch'],item['branchStatus']])
    except BaseException as e:
        print('BaseException:', filename)
        print(e)
    else:
        print('File written successfully!')

def main():
    print('Welcome to Codacy Branch Report')
    parser = argparse.ArgumentParser(description='Codacy Engine Helper')
    parser.add_argument('--token', dest='token', default=None, help='the api-token to be used on the REST API', required=True)
    parser.add_argument('--baseurl', dest='baseurl', default='https://app.codacy.com', help='codacy server address (ignore if cloud)')
    parser.add_argument('--provider', dest='provider', default=None, help='git provider', required=True)
    parser.add_argument('--organization', dest='organization', default=None, help='organization id', required=True)
    parser.add_argument('--branches', dest='branches', default='main,develop', help='branches to validate', required=False)
    parser.add_argument('--output', dest='output', help="name of file to write", required=False, default=None)
    args = parser.parse_args()
    branches = args.branches.split(',')
    repositories = listRepositories(args.baseurl, args.provider, args.organization, args.token)
    report = []
    for repo in repositories:
        print('[Repository %s] %s (coverage:%s)'%(repo['repository']['repositoryId'],repo['repository']['name'], (repo['coverage']['coveragePercentage'] if ('coverage' in repo and 'coveragePercentage' in repo['coverage'] != None) else '-' )))
        for branch in branches:
            branchStatus = getRepositoryBranchMetrics(args.baseurl, args.provider, args.organization, repo['repository']['name'], branch, args.token)
            report.append({
                "repository": repo['repository']['name'],
                "repositoryId": repo['repository']['repositoryId'],
                "coverage-main": repo['coverage']['coveragePercentage'] if ('coverage' in repo and 'coveragePercentage' in repo['coverage'] != None) else '-' ,
                "branch": branch,
                "branchStatus": branchStatus
                
            })
        time.sleep(0.5)
    if(args.output != None):
        generateCSV(report, args.output)
    else:
        print(report)
main()