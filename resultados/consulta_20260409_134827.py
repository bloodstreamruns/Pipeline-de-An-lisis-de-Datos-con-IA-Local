resultado = df.groupby('departamento')['salario_anual'] \
              .agg(promedio=('salario_anual', 'mean'),
                   minimo=('salario_anual', 'min'),
                   maximo=('salario_anual', 'max')) \
              .nlargest(3, 'promedio') \
              .to_string()