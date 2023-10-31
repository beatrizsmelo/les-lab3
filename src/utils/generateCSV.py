import csv

def generateRepositoriesCsv(json, filename):
    headersRepo = [
        'nameWithOwner',
        'mergedPRs',
        'closedPRs'
    ]

    print("Generating " + filename + " CSV...")
    with open(filename + '.csv', 'x') as f:
        writer = csv.writer(f)

        writer.writerow(headersRepo)

        for repo in json:
            if repo['mergedPRs'] + repo['closedPRs'] >= 100:
                writer.writerow([
                    repo['nameWithOwner'],
                    repo['mergedPRs'],
                    repo['closedPRs']
                ])


def generatePullRequestsCsv(json, filename):
    headersRepo = [
        'repo',
        'owner',
        'filesCount',
        'updatedAt',
        'createdAt',
        'closedAt',
        'mergedAt',
        'description',
        'reviews'
        'participants',
        'comments',
    ]

    print("Generating " + filename + " CSV...")
    with open('./src/data/' + filename + '.csv', 'x') as f:
        writer = csv.writer(f)

        writer.writerow(headersRepo)

        for prData in json:
            writer.writerow([
                    prData['repo'],
                    prData['owner'],
                    prData['filesCount'],
                    prData['updatedAt'],
                    prData['createdAt'],
                    prData['closedAt'],
                    prData['mergedAt'],
                    prData['description'],
                    prData['reviews'],
                    prData['participants'],
                    prData['comments'],
            ])
