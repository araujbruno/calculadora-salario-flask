# app.py
from flask import Flask, render_template, request

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = ''  # ou remova se quiser abrir geral
    return response

# Tabela INSS 2025 (valores oficiais atualizados)
def calcular_inss(salario_bruto):
    faixas = [
        (1412.00, 0.075),
        (2666.68, 0.09),
        (4000.03, 0.12),
        (7786.02, 0.14)
    ]
    inss = 0.0
    limite_anterior = 0.0
    for limite, aliquota in faixas:
        if salario_bruto > limite:
            inss += (limite - limite_anterior) * aliquota
            limite_anterior = limite
        else:
            inss += (salario_bruto - limite_anterior) * aliquota
            break
    return inss

# Tabela IRRF 2025 (valores oficiais atualizados)
def calcular_irrf(salario_bruto, inss, dependentes):
    base_calculo = salario_bruto - inss - (dependentes * 189.59)
    if base_calculo <= 2259.20:
        return 0.0
    elif base_calculo <= 2826.65:
        return base_calculo * 0.075 - 169.44
    elif base_calculo <= 3751.05:
        return base_calculo * 0.15 - 381.44
    elif base_calculo <= 4664.68:
        return base_calculo * 0.225 - 662.77
    else:
        return base_calculo * 0.275 - 896.00

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        try:
            salario = float(request.form['salario'])
            dependentes = int(request.form['dependentes'])
            outros = float(request.form['outros']) if request.form['outros'] else 0.0
            inss = calcular_inss(salario)
            irrf = calcular_irrf(salario, inss, dependentes)
            liquido = salario - inss - irrf - outros
            resultado = {
                'bruto': salario,
                'dependentes': dependentes,
                'inss': round(inss, 2),
                'irrf': round(irrf, 2),
                'outros': round(outros, 2),
                'liquido': round(liquido, 2)
            }
        except ValueError:
            resultado = 'Erro: valores inválidos.'

    return render_template('index.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
