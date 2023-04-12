import pandas as pd
from datetime import timedelta

# Carrega o arquivo CSV em um DataFrame do Pandas
prs = pd.read_csv('./src/data/prs.csv')

# Converte as colunas de data/hora para objetos datetime do Pandas
date_cols = ['updatedAt', 'createdAt', 'closedAt', 'mergedAt']
prs[date_cols] = prs[date_cols].apply(pd.to_datetime)

# Calcula a diferença entre a data de criação e de merge ou close
prs['time_to_merge_or_close'] = prs[['createdAt', 'mergedAt', 'closedAt']].apply(
    lambda x: (x['mergedAt'] - x['createdAt']) if pd.notnull(x['mergedAt']) else (x['closedAt'] - x['createdAt']),
    axis=1
)

# Filtra o DataFrame para incluir apenas PRs com pelo menos uma revisão e que levaram pelo menos uma hora para serem concluídos
filtered_prs = prs[(prs['reviews'] > 0) & (prs['time_to_merge_or_close'] >= timedelta(hours=1))]

# Salva o DataFrame filtrado em um novo arquivo CSV
filtered_prs.to_csv('filteredPRs.csv', index=False)
