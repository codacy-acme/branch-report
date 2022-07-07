#!/usr/bin/env python3
import argparse
import requests
import json
import time
import csv


# TODO: paginate instead of requesting 10000 repos
def listRepositories(baseurl, provider, organization, token):
    if token == None:
        raise Exception('api-token needs to be defined')
    headers = {
        'Accept': 'application/json',
        'api-token': token
    }
    url = '%s/api/v3/analysis/organizations/%s/%s/repositories?limit=10000' % (
        baseurl, provider, organization)
    r = requests.get(url, headers=headers)
    repositories = json.loads(r.text)
    return repositories['data']


def getRepositoryBranchMetrics(baseurl, provider, organization, repository, token):
    result = []
    cursor = 1
    hasNextPage = True
    if token == None:
        raise Exception('api-token needs to be defined')
    headers = {
        'Accept': 'application/json',
        'api-token': token
    }
    while hasNextPage:
        url = '%s/api/v3/organizations/%s/%s/repositories/%s/branches?limit=100&cursor=%s' % (
            baseurl, provider, organization, repository, cursor)
        b = requests.get(url, headers=headers)
        branches = json.loads(b.text)
        hasNextPage = 'cursor' in branches['pagination']
        for branch in branches['data']:
            print('\t[Branch] %s - Exists on repository %s and is %s' %
                  (branch['name'], repository, ('Active' if branch['isEnabled'] else 'Inactive')))
            result.append({'name': branch['name'], 'status': (
                'Active' if branch['isEnabled'] else 'Inactive')})
        cursor += 1

    return result


def generateCSV(report, filename):
    try:
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['repository', 'repositoryId',
                            'coverage-main', 'branch', 'branchStatus'])
            for item in report:
                writer.writerow([item['repository'], item['repositoryId'],
                                item['coverage-main'], item['branch'], item['branchStatus']])
    except BaseException as e:
        print('BaseException:', filename)
        print(e)
    else:
        print('File written successfully!')

def showMetrics(token,baseurl,provider,organization,repos,output):
    reposToInclude = (repos == None)
    report = []
    listRepos=[]
    reposWithCoverage = 0
    totalCoverage = 0
    totalProjects = 0
    repositories = listRepositories(
            baseurl, provider, organization, token)
    if not reposToInclude:
        listRepos = repos.split(',')
    for repo in repositories:
        if reposToInclude or repo['repository']['name'] in listRepos:
            totalProjects+=1
            print('[Repository %s] %s (coverage:%s)' % (repo['repository']['repositoryId'], repo['repository']['name'], (repo['coverage']
                ['coveragePercentage'] if ('coverage' in repo and 'coveragePercentage' in repo['coverage'] != None) else '-')))
            branches = getRepositoryBranchMetrics(
                baseurl, provider, organization, repo['repository']['name'], token)
            for branch in branches:
                report.append({
                    "repository": repo['repository']['name'],
                    "repositoryId": repo['repository']['repositoryId'],
                    "coverage-main": repo['coverage']['coveragePercentage'] if ('coverage' in repo and 'coveragePercentage' in repo['coverage'] != None) else '-',
                    "branch": branch['name'],
                    "branchStatus": branch['status']
                })
            if ('coverage' in repo and 'coveragePercentage' in repo['coverage'] != None):
                reposWithCoverage += 1
                totalCoverage += repo['coverage']['coveragePercentage']
            time.sleep(0.5)
    if(output != None):
        generateCSV(report, output)
    else:
        print('\n############### Report with all Repositories #########')
        print(report)
    print('\nTotal projects: %s, with coverage: %s'%(totalProjects,reposWithCoverage))
    print('Average coverage per repo with coverage: %s'%(totalCoverage/reposWithCoverage))

def main():
    print('Welcome to Codacy Branch Report\n')
    parser = argparse.ArgumentParser(description='Codacy Engine Helper')
    parser.add_argument('--token', dest='token', default=None,
                        help='the api-token to be used on the REST API', required=True)
    parser.add_argument('--baseurl', dest='baseurl', default='https://app.codacy.com',
                        help='codacy server address (ignore if cloud)')
    parser.add_argument('--provider', dest='provider',
                        default=None, help='git provider', required=True)
    parser.add_argument('--organization', dest='organization',
                        default=None, help='organization id', required=True)
    parser.add_argument('--repos', dest='repos',
                        default=None, help='list of repositories to be included', required=False)
    parser.add_argument('--output', dest='output',
                        help="name of file to write", required=False, default=None)
    args = parser.parse_args()
    ##can be used to select specific branches##
    # parser.add_argument('--branches', dest='branches', default=None, help='branches to validate', required=False)
    # branches = args.branches.split(',')

    showMetrics(args.token,args.baseurl,args.provider,args.organization,args.repos,args.output)
    
main()
