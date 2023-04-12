import os
import requests
from os.path import join, dirname
from datetime import datetime
import time
import pandas as pd

def getReposData():
    token = os.environ.get('ACCESS_TOKEN')
    after = 'null'
    hasNextPage = True
    data = []

    while hasNextPage:
        query = """
        {
            search (query: "stars:>100", type: REPOSITORY, first: 10, after: %s) {
                pageInfo {
                    startCursor
                    hasNextPage
                    endCursor
                }
                nodes {
                    ... on Repository {
                        nameWithOwner
                        mergedPRs: pullRequests(states:MERGED) {
                            totalCount
                        }
                        closedPRs: pullRequests(states:CLOSED) {
                            totalCount
                        }
                    }
                }
            }
        }
        """ % after

        url = 'https://api.github.com/graphql'
        json = {'query': query}
        headers = {'Authorization': 'Bearer %s' % token}

        response = requests.post(url=url, json=json, headers=headers).json()

        hasNextPage = response['data']['search']['pageInfo']['hasNextPage'] if response['data']['search']['pageInfo']['hasNextPage'] else False
        after = '"%s"' % response['data']['search']['pageInfo']['endCursor']

        for repoData in response['data']['search']['nodes']:
            data.append({
                'nameWithOwner': repoData['nameWithOwner'],
                'mergedPRs': repoData['mergedPRs']['totalCount'],
                'closedPRs': repoData['closedPRs']['totalCount'],
            })

    return data


def getPRsData():
    tokens = [os.environ.get('ACCESS_TOKEN1'), os.environ.get('ACCESS_TOKEN2')]
    csv_path = './src/data/repos.csv'
    repos_df = pd.read_csv(csv_path)
    data = []
    tokenIndex = 0

    start_time = time.time()

    for index, row in repos_df.iterrows():
        print("Getting PRs data for repo: %s" % row.nameWithOwner)

        after = 'null'
        hasNextPage = True
        repoName = row.nameWithOwner.split('/')[0]
        repoOwnerName = row.nameWithOwner.split('/')[1]

        while hasNextPage:
            try:
                query = """
                    query {
                        repository(owner: "%s", name: "%s") {
                            pullRequests(states: [MERGED, CLOSED], first: 40, after: %s) {
                                nodes {
                                    id
                                    files {
                                        totalCount
                                    }
                                    updatedAt
                                    createdAt
                                    closedAt
                                    mergedAt
                                    body
                                    reviews {
                                        totalCount
                                    }
                                    participants {
                                        totalCount
                                    }
                                    comments {
                                        totalCount
                                    }
                                }
                                pageInfo {
                                    endCursor
                                    hasNextPage
                                }
                            }
                        }
                    }
                """ % (repoName, repoOwnerName, after)

                url = 'https://api.github.com/graphql'
                json = {'query': query}
                headers = {'Authorization': 'Bearer %s' % tokens[tokenIndex]}

                responsePayload = requests.post(url=url, json=json, headers=headers)

                if responsePayload.status_code == 200:
                    response = responsePayload.json()

                    if 'errors' in response:
                        for error in response['errors']:
                            print(f"GraphQL error: {error['message']}")

                    else:
                        hasNextPage = response['data']['repository']['pullRequests']['pageInfo']['hasNextPage'] if response['data']['repository']['pullRequests']['pageInfo']['hasNextPage'] else False
                        after = '"%s"' % response['data']['repository']['pullRequests']['pageInfo']['endCursor']

                        for prData in response['data']['repository']['pullRequests']['nodes']:
                                data.append({
                                    'id': prData['id'],
                                    'repo': repoName,
                                    'owner': repoOwnerName,
                                    'filesCount': prData['files']['totalCount'],
                                    'updatedAt': prData['updatedAt'],
                                    'createdAt': prData['createdAt'],
                                    'closedAt': prData['closedAt'],
                                    'mergedAt': prData['mergedAt'],
                                    'description': len(prData['body']),
                                    'reviews': prData['reviews']['totalCount'],
                                    'participants': prData['participants']['totalCount'],
                                    'comments': prData['comments']['totalCount'],
                                })

                        tokenIndex = 0 if tokenIndex == 1 else 1
                        time.sleep(5)
                else:
                    print(f"HTTP error {responsePayload.status_code}")
                    tokenIndex = 0 if tokenIndex == 1 else 1
            
            except Exception as e:
                print(f"Exception: {e}")
                tokenIndex = 0 if tokenIndex == 1 else 1
                time.sleep(5)

        print(f"Finished fetching data for {row.nameWithOwner}.")
        time.sleep(1)
    
    return data
