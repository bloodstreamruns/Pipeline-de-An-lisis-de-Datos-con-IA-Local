resultado = df.groupby('departamento')['salario_anual']\
    .agg(['mean', 'min', 'max'])\
    .sort_values(by='mean', ascending=False)\
    .head(3)\
    .to_string()