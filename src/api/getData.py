from os import environ
import requests
import time
from pandas import read_csv

def getRepositoriesData():
    token = environ.get('ACCESS_TOKEN1')
    after = 'null'
    hasNextPage = True
    data = []

    while len(data) < 200:
        query = f"""
        {{
            search (query: "stars:>100", type: REPOSITORY, first: 10, after: {after}) {{
                pageInfo {{
                    startCursor
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    ... on Repository {{
                        nameWithOwner
                        mergedPRs: pullRequests(states:MERGED) {{
                            totalCount
                        }}
                        closedPRs: pullRequests(states:CLOSED) {{
                            totalCount
                        }}
                    }}
                }}
            }}
        }}
        """

        url = 'https://api.github.com/graphql'
        json_data = {'query': query}
        headers = {'Authorization': f'Bearer {token}'}

        try:
            print('\nFetching repository...')
            response = requests.post(url=url, json=json_data, headers=headers).json()
            
            if 'errors' in response or 'data' not in response:
                print('Found error or empty data in response. Skipping...')
                break

            hasNextPage = response['data']['search']['pageInfo']['hasNextPage']
            after = f'"{response["data"]["search"]["pageInfo"]["endCursor"]}"'

            for repoData in response['data']['search']['nodes']:
                data.append({
                    'nameWithOwner': repoData['nameWithOwner'],
                    'mergedPRs': repoData['mergedPRs']['totalCount'],
                    'closedPRs': repoData['closedPRs']['totalCount'],
                })
            
            print('Fetched with success!')

        except (requests.RequestException, ValueError):
            # Network error or invalid JSON error
            print("Error fetching data. Skipping to next repository...")
            break

    return data


def getPullRequestsData():
    tokens = [environ.get('ACCESS_TOKEN1'), environ.get('ACCESS_TOKEN2')]
    csv_path = './src/data/repos.csv'
    repos_df = read_csv(csv_path)
    data = []
    tokenIndex = 0


    for index, row in repos_df.iterrows():
        print("\nGetting PRs data for repo: %s" % row.nameWithOwner)

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

                print('\nFetching a pull request...')
                responsePayload = requests.post(url=url, json=json, headers=headers)

                if responsePayload.status_code == 200:
                    print('Fetched with success!')
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
