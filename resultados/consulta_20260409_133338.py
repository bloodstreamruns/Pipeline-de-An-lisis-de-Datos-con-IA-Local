resultado = df.groupby('departamento')['salario_anual'] \
              .agg(['mean', 'min', 'max']) \
              .nlargest(3, 'mean') \
              .reset_index() \
              .to_string(index=False)