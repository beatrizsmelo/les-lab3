from os.path import join, dirname
from dotenv import load_dotenv

from api.getData import getPullRequestsData, getRepositoriesData
from utils.generateCSV import generateRepositoriesCsv, generatePullRequestsCsv


def main():
    # Carregando variáveis de ambiente
    dotenv_path = join(dirname(dirname(__file__)), '.env')
    load_dotenv(dotenv_path)

    # Buscando repositórios    
    print('Getting repositories data...')
    repos = getRepositoriesData()
    
    # Gerando CSV de repositórios
    print('Generating repositories csv...')
    generateRepositoriesCsv(repos, 'repos')

    # Buscando pull requests
    print('Getting pull requests data...')
    prs = getPullRequestsData()

    # Gerando CSV de pull requests
    print('Generating pull requests csv...')
    generatePullRequestsCsv(prs, 'prs')
    
    print('Done')

if __name__ == "__main__":
    main()
