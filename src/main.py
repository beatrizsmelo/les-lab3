from os.path import join, dirname
from dotenv import load_dotenv

from api.getData import getPullRequestsData, getRepositoriesData
from utils.generateCSV import generateRepositoriesCsv, generatePullRequestsCsv


def main():
    # Carregando variáveis de ambiente
    dotenv_path = join(dirname(dirname(__file__)), '.env')
    load_dotenv(dotenv_path)

    # Buscando repositórios    
    print('\nGetting repositories data...')
    repos = getRepositoriesData()
    
    # Gerando CSV de repositórios
    print('\nGenerating repositories csv...')
    generateRepositoriesCsv(repos, './src/data/repos')

    # Buscando pull requests
    print('\nGetting pull requests data...')
    prs = getPullRequestsData()

    # Gerando CSV de pull requests
    print('\nGenerating pull requests csv...')
    generatePullRequestsCsv(prs, './src/data/prs')
    
    print('\nDone!')

if __name__ == "__main__":
    main()
