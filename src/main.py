from os.path import join, dirname
from dotenv import load_dotenv

from api.getData import getReposData
from utils.generateCSV import generateReposCSV
from utils.generateCSV import generatePrsCsv
from api.getData import getPRsData


def main():
    dotenv_path = join(dirname(dirname(__file__)), '.env')

    load_dotenv(dotenv_path)

    print('Getting pullrequests data...')
    prs = getPRsData()

    print('Generating pullrequests csv...')
    generatePrsCsv(prs, 'prs')
    print('Done')


if __name__ == "__main__":
    main()
