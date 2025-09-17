import tkinter as tk
from itertools import product
import re


def parse_formula(formula): 
    stack = [[]]  # pilha de listas; começa com a lista principal
    current = ''

    for char in formula:
        if char == '(':
            if current:
                stack[-1].append(current)
                current = ''
            new_list = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif char == ')':
            if current:
                stack[-1].append(current)
                current = ''
            stack.pop()
        else: 
            current += char

    if current:
        stack[-1].append(current)

    return stack[0]

def substituir_implicacoes(expr):   
    padrao = re.compile(r'(.*)→(.*)')
    while True:
        nova_expr = padrao.sub(r'not \1 or \2', expr)
        if nova_expr == expr:
            break
        expr = nova_expr
    return expr

def substituir_bicondicional(expr): 
    return re.sub(r'(.*)↔(.*)', r'\1 == \2', expr)

def traduzir_expressao(expr):       
    expr = expr.replace("¬", " not ")
    expr = expr.replace("∧", " and ")
    expr = expr.replace("V", " or ")
    expr = substituir_implicacoes(expr)
    expr = substituir_bicondicional(expr)

    return expr

def extrair_variaveis(expr): 
    return sorted(set(filter(lambda c: c in "pqrst", expr))) #'lambda' é uma função de uma linha só, ou seja, a função "c" vai ser extrair as variáveis "pqrst" da expressão caso haja.

def resolve_expr(structure, father_structure=None): 
    final_structure = []
    for i, piece in enumerate(structure):
        if isinstance(piece, str):
            if piece.find('→') == 0:
                # Continua implicação com item anterior
                piece = f'{final_structure.pop(i-1)} {piece}'
            final_structure.append(traduzir_expressao(piece))
        elif isinstance(piece, list):
            # print(structure)
            # Recursivamente resolve sublistas
            father_structure = '(' + ''.join(resolve_expr(piece, final_structure)) + ')'
            final_structure.append(father_structure)
        # print(final_structure)
    return ''.join(final_structure)

#Interface e Funções de UI

def gerar_tabela_verdade(): 
    entrada = entrada_expr.get() #Pega o texto digitado pelo usuário no campo de entrada da interface Tkinter.
    saida_text.delete("1.0", tk.END)
    
    if not entrada:
        saida_text.insert(tk.END, "Enter a logical expression.")
        return
    
    try:
        expr_python = resolve_expr(parse_formula(entrada))
        variaveis = extrair_variaveis(entrada)
        combinacoes = list(product([True, False], repeat=len(variaveis))) #biblioteca intertools product faz todas as combinações

        cabecalho = " | ".join(variaveis) + " | Output\n"
        saida_text.insert(tk.END, cabecalho)
        saida_text.insert(tk.END, "-" * len(cabecalho) + "\n")

        for valores in combinacoes:
            contexto = dict(zip(variaveis, valores))
            resultado = eval(expr_python, {}, contexto)
            linha = " | ".join(['V' if contexto[v] else 'F' for v in variaveis])
            linha += " | " + ("V" if resultado else "F") + "\n"
            saida_text.insert(tk.END, linha)
    
    except Exception as e:
        saida_text.insert(tk.END, f"Erro: {e}")

def adicionar_texto(valor): 
    entrada_expr.insert(tk.END, valor)

def clear(): 
    entrada_expr.delete(0, tk.END)


janela = tk.Tk()
janela.title("Truth Table Generator")

# Campo de entrada
entrada_expr = tk.Entry(janela, width=50, font=("Arial", 14))
entrada_expr.pack(pady=10)

# Botões da calculadora lógica
botoes = [
    ["p", "q", "r", "s", "t"],
    ["¬", "∧", "V", "→", "↔"],
    ["(", ")", "Clear", "Generate"]
]

for linha in botoes:
    frame = tk.Frame(janela)
    frame.pack()
    for btn in linha:
        if btn == "Clear":
            tk.Button(frame, text=btn, width=10, command=clear).pack(side=tk.LEFT, padx=2, pady=2)
        elif btn == "Generate":
            tk.Button(frame, text=btn, width=15, bg="green", fg="white", command=gerar_tabela_verdade).pack(side=tk.LEFT, padx=2, pady=2)
        else:
            tk.Button(frame, text=btn, width=5, command=lambda b=btn: adicionar_texto(b)).pack(side=tk.LEFT, padx=2, pady=2)

# Área de saída
saida_text = tk.Text(janela, height=15, width=60)
saida_text.pack(pady=10)

# Inicia a interface
janela.mainloop()
