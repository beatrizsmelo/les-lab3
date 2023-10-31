from pandas import read_csv, notnull, to_datetime
from datetime import timedelta

# Carrega 'prs.csv' em um DataFrame do Pandas
prs = read_csv('./src/data/prs.csv')

# Converte colunas de data/hora em objetos datetime do Pandas
date_cols = ['updatedAt', 'createdAt', 'closedAt', 'mergedAt']
prs[date_cols] = prs[date_cols].apply(to_datetime)

# Calcula a diferença entre a data de criação e a de merge/close dos PRs
prs['time_to_merge_or_close'] = prs[['createdAt', 'mergedAt', 'closedAt']].apply(
    lambda x: (x['mergedAt'] - x['createdAt']) if notnull(x['mergedAt']) else (x['closedAt'] - x['createdAt']),
    axis=1
)

# Filtra o DataFrame para manter somente PRs com no mínimo UMA REVISAO e que levaram no mínimo UMA HORA para serem concluídos
filtered_prs = prs[(prs['reviews'] > 0) & (prs['time_to_merge_or_close'] >= timedelta(hours=1))]

# Salva o DataFrame filtrado em um novo arquivo 'filteredPRs.csv'
filtered_prs.to_csv('filteredPRs.csv', index=False)
