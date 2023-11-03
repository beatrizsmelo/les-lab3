from os import environ
import requests
import time
from pandas import read_csv
from datetime import datetime

MAX_RETRIES = 3  # Define o número máximo de tentativas para erros temporários

def getRepositoriesData():
    token = environ.get('ACCESS_TOKEN1')
    after = 'null'
    hasNextPage = True
    data = []
    
    while len(data) < 400:
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
        total_prs = row.mergedPRs + row.closedPRs
        if total_prs < 100:
            print(f"Skipping {row.nameWithOwner} as it has only {total_prs} PRs (merged + closed).")
            continue    
                
        print("\nGetting PRs data for repo: %s" % row.nameWithOwner)

        after = 'null'
        hasNextPage = True
        repoName = row.nameWithOwner.split('/')[1]
        repoOwnerName = row.nameWithOwner.split('/')[0]
        pr_count = 0
        retries = 0  # Contador de tentativas


        while hasNextPage and pr_count < 100:
            fetch_count = min(100 - pr_count, 50)  # Assuming GitHub API lets us fetch 50 at a time
            try:
                query = """
                {{
                    repository(owner: "{owner}", name: "{name}") {{
                        pullRequests(states: [MERGED, CLOSED], first: {fetch_count}, after: {after}) {{
                            nodes {{
                                id
                                files {{
                                    totalCount
                                }}
                                updatedAt
                                createdAt
                                closedAt
                                mergedAt
                                body
                                reviews {{
                                    totalCount
                                }}
                                participants {{
                                    totalCount
                                }}
                                comments {{
                                    totalCount
                                }}
                                additions
                                deletions                        
                            }}
                            pageInfo {{
                                endCursor
                                hasNextPage
                            }}
                        }}
                    }}
                }}
                """.format(owner=repoOwnerName, name=repoName, fetch_count=fetch_count, after=after)

                url = 'https://api.github.com/graphql'
                json_data = {'query': query}
                headers = {'Authorization': 'Bearer %s' % tokens[tokenIndex]}

                print(f'\nFetching pull requests {pr_count + 1} to {pr_count + fetch_count}...')
                responsePayload = requests.post(url=url, json=json_data, headers=headers)

                if responsePayload.status_code == 200:
                    print('Fetched with success!')
                    response = responsePayload.json()

                    hasNextPage = response['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
                    after = '"%s"' % response['data']['repository']['pullRequests']['pageInfo']['endCursor']

                    for prData in response['data']['repository']['pullRequests']['nodes']:
                        created_at = datetime.fromisoformat(prData['createdAt'].replace('Z', '+00:00'))
                        closed_or_merged_at = prData['mergedAt'] or prData['closedAt']
                        if closed_or_merged_at:
                            closed_or_merged_at = datetime.fromisoformat(closed_or_merged_at.replace('Z', '+00:00'))
                            difference = closed_or_merged_at - created_at

                            if difference.total_seconds() > 3600:  # 1 hour
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
                                    'additions': prData['additions'],
                                    'deletions': prData['deletions']
                                })
                                pr_count += 1
                    retries = 0  # Reset the retries counter after successful fetch

                elif responsePayload.status_code == 502:
                    print("Server error (502), retrying...")
                    retries += 1
                    if retries >= MAX_RETRIES:
                        print("Max retries reached, skipping to next repository.")
                        break
                    time.sleep(10)  # Esperando um pouco para tentar novamente

                elif responsePayload.status_code == 401:
                    print("Authentication error (401), switching token or aborting...")
                    tokenIndex = 0 if tokenIndex == 1 else 1  # Try to switch tokens
                    if not tokens[tokenIndex]:  # If there are no valid tokens left, skip to the next repository
                        print("No valid tokens available, skipping to next repository.")
                        break

                else:
                    print(f"Unhandled HTTP error {responsePayload.status_code}, skipping to next repository.")
                    break

            except Exception as e:
                print(f"Exception occurred: {e}")
                break  # Exit the current repository loop and move to the next one

            time.sleep(5)

        print(f"Finished fetching data for {row.nameWithOwner}. Pull requests collected.")
        #{pr_count} 

    return data

if __name__ == "__main__":
    repositories = getRepositoriesData()
    pull_requests = getPullRequestsData()
    print(f"Collected data for {len(pull_requests)} pull requests from multiple repositories.")
