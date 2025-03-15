from le_arquivo import ler_arquivo_dados
from random import randint, sample, random, choice, uniform, choices
from time import time
from copy import deepcopy
import argparse
import csv
from pathlib import Path
from tabulate import tabulate

# na população inicial, todo cliente tem sua demanda suprida
def cria_populacao_inicial(n_populacao, clientes, depositos, n_depositos, n_clientes):
    populacao = set()

    while len(populacao) < n_populacao:
        cromossomo = [[0] * n_depositos for _ in range(n_clientes)]
        depositos_usados = set()
        capacidade_restante = [deposito['capacidade'] for deposito in depositos]

        for i in range(n_clientes):
            c = clientes[i]
            demanda_cliente = c['demanda']
            custos_atendimento = c['custos_alocacao']

            while demanda_cliente > 0:
                custos_validos = []
                todos_custos = []
                
                for j in range(n_depositos):
                    custo_construcao = 0 if j in depositos_usados else depositos[j]['custo_construcao']
                    custos = custos_atendimento[j] + custo_construcao

                    if capacidade_restante[j] > 0:
                        custos_validos.append((custos, j))
                    todos_custos.append((custos, j))

                if len(custos_validos) > 0:
                    custos_validos.sort(key=lambda x: x[0])
                    melhor_deposito = choice(custos_validos[:2])[1]
                    quantidade_alocada = min(demanda_cliente, capacidade_restante[melhor_deposito])
                else:
                    todos_custos.sort(key=lambda x: x[0])
                    melhor_deposito = choice(todos_custos[:2])[1]
                    quantidade_alocada = demanda_cliente

                cromossomo[i][melhor_deposito] += quantidade_alocada
                capacidade_restante[melhor_deposito] -= quantidade_alocada
                demanda_cliente -= quantidade_alocada
                depositos_usados.add(melhor_deposito)

        
        populacao.add(tuple(map(tuple, cromossomo)))

    return [[list(c) for c in cromossomo] for cromossomo in populacao]


# a avaliação não penaliza clientes não atendidos 
# porque o crossover apenas troca a configuração de depósitos que atendem a um cliente sorteado
def avaliar_cromossomo(cromossomo, depositos, clientes, n_clientes, n_depositos, custo_max, capacidade_max):
    custo_total = 0
    penalizacao = 0
    dep_excedidos = 0
    deposito_aberto = [0] * n_depositos

    for i in range(n_clientes):
        demanda = clientes[i]['demanda']
        custos = clientes[i]['custos_alocacao']

        for j in range(n_depositos):
            if cromossomo[i][j] > 0:
                custo_total += custos[j] * cromossomo[i][j]/demanda
                deposito_aberto[j] = 1

    for i in range(n_depositos):
        custo_total += deposito_aberto[i] * depositos[i]['custo_construcao']
    
        recursos_providos = 0
        for j in range(n_clientes):
            recursos_providos += cromossomo[j][i]
        
        dif_recursos = recursos_providos - depositos[i]['capacidade']

        if dif_recursos > 0:
            penalizacao += dif_recursos
            dep_excedidos += 1

    custo_normalizado = custo_total / custo_max if custo_max > 0 else 0
    penalizacao_normalizada = penalizacao / capacidade_max if capacidade_max > 0 else 0

    fitness = -(custo_normalizado + 10 * penalizacao_normalizada)

    return {
        'fitness': fitness,
        'fo': custo_total,
        'dep_excedidos': dep_excedidos,
    }

# croossover por linha em dois pontos
# a parte superior e inferior do pai 1 e a parte intermediária do pai 2
def crossover(pai1, pai2, n_clientes):
    corte1 = randint(1, n_clientes // 3)
    corte2 = randint(2 * n_clientes // 3, n_clientes - 1)
    
    pai1_copia = deepcopy(pai1)
    pai2_copia = deepcopy(pai2)

    filho = pai1_copia[:corte1] + pai2_copia[corte1:corte2] + pai1_copia[corte2:]
   
    return filho

# escolhe um cliente aleatório
# escolhe um depósito que o supria em x unidades para fechar
# distribui as x unidades aleatoriamente entre os depósitos que o atendiam, se existiam
# se aquele era o único depósito que o atendia, escolhe um novo para migrar a demanda
def encerrar_atendimento_cliente(cromossomo, n_clientes, n_depositos):
    cliente_idx = randint(0, n_clientes - 1)
    
    depositos_atuais = [i for i, valor in enumerate(cromossomo[cliente_idx]) if valor > 0]
    
    deposito_a_fechar = choice(depositos_atuais)
    demanda_a_fechar = cromossomo[cliente_idx][deposito_a_fechar]
    
    cromossomo[cliente_idx][deposito_a_fechar] = 0
    
    outros_depositos = [dep for dep in depositos_atuais if dep != deposito_a_fechar]
    if len(outros_depositos) > 0:
        demanda_restante = int(demanda_a_fechar)
        while demanda_restante > 0:
            deposito_destino = choice(outros_depositos)
            quantidade_a_adicionar = randint(1, demanda_restante)
            cromossomo[cliente_idx][deposito_destino] += quantidade_a_adicionar
            demanda_restante -= quantidade_a_adicionar
    else:
        depositos_nao_usados = [i for i in range(n_depositos) if i != deposito_a_fechar]
        deposito_novo = choice(depositos_nao_usados)
        cromossomo[cliente_idx][deposito_novo] += demanda_a_fechar

    return cromossomo

# escolhe um cliente aleatório
# escolhe um depósito que supre esse cliente em x unidades
# redistribui uma proporção de x a um novo depósito
def novo_atendimento_cliente(cromossomo, n_clientes, n_depositos):
    cliente_idx = randint(0, n_clientes - 1)
    depositos_usados = [i for i, valor in enumerate(cromossomo[cliente_idx]) if valor > 0]

    deposito_antigo = choice(depositos_usados)
    
    depositos_nao_usados = [i for i in range(n_depositos) if i not in depositos_usados]

    if len(depositos_nao_usados) > 0:
        deposito_novo = choice(depositos_nao_usados)
    else:
        deposito_novo = randint(0, n_depositos - 1)

        while deposito_antigo == deposito_antigo:
            deposito_novo = randint(0, n_depositos - 1)

    demanda_antiga = cromossomo[cliente_idx][deposito_antigo]
    proporcao = uniform(0.1, 0.5)
    demanda_transferida = int(proporcao * demanda_antiga)

    cromossomo[cliente_idx][deposito_antigo] -= demanda_transferida
    cromossomo[cliente_idx][deposito_novo] += demanda_transferida

    return cromossomo

# escolhe um cliente aleatório
# escolhe dois depósitos desse cliente e troca seus valores
def trocar_depositos_cliente(cromossomo, n_clientes, n_depositos):
    cliente_idx = randint(0, n_clientes - 1)
    deposito1_idx = randint(0, n_depositos - 1)
    deposito2_idx = randint(0, n_depositos - 1)

    while cromossomo[cliente_idx][deposito1_idx] == cromossomo[cliente_idx][deposito2_idx]:
        deposito2_idx = randint(0, n_depositos - 1)
    
    aux = cromossomo[cliente_idx][deposito1_idx]
    cromossomo[cliente_idx][deposito1_idx] = cromossomo[cliente_idx][deposito2_idx]
    cromossomo[cliente_idx][deposito2_idx] = aux

    return cromossomo

# decide aleatoriamente um modo de mutar o cromossomo dentre os acima
def mutar(cromossomo, n_clientes, n_depositos):
    sorteio = random()

    if sorteio < 1/3:
        cromossomo = novo_atendimento_cliente(cromossomo, n_clientes, n_depositos)
    elif sorteio < 2/3:
        cromossomo = encerrar_atendimento_cliente(cromossomo, n_clientes, n_depositos)
    else: 
        cromossomo = trocar_depositos_cliente(cromossomo, n_clientes, n_depositos)

    return cromossomo

# seleciona n_torneio cromossomos aleatoriamente
# obtem o melhor deles de acordo com o fitness para ser um pai
def selecao_pais_por_torneio(populacao, avaliacoes, n_torneio, n_populacao):
    candidatos = sample(range(n_populacao), n_torneio)

    melhor_indice = candidatos[0]
    melhor_avaliacao = avaliacoes[melhor_indice]['fitness']

    for i in range(1, n_torneio):
        if avaliacoes[candidatos[i]]['fitness'] > melhor_avaliacao:
            melhor_indice = candidatos[i]
            melhor_avaliacao = avaliacoes[candidatos[i]]['fitness']

    return populacao[melhor_indice], melhor_indice


# mantém os 10 melhores indivíduos para a próxima geração
# sorteia os demais 40 indivíduos
def selecao_populacao_por_elitismo(populacao, avaliacoes, n_populacao, prop_elitismo):
    n_elite = int(prop_elitismo * n_populacao)
    individuos_ordenados = sorted(zip(populacao, avaliacoes), key=lambda x: x[1]['fitness'], reverse=True)
    
    elite_populacao = [individuo[0] for individuo in individuos_ordenados[:n_elite]]
    elite_avaliacoes = [individuo[1] for individuo in individuos_ordenados[:n_elite]]
    
    restante_populacao = [individuo[0] for individuo in individuos_ordenados[n_elite:]]
    restante_avaliacoes = [individuo[1] for individuo in individuos_ordenados[n_elite:]]
    
    num_restante = n_populacao - n_elite
    selecionados_restante = choices(list(zip(restante_populacao, restante_avaliacoes)), k=num_restante)
    
    nova_populacao_restante = [individuo[0] for individuo in selecionados_restante]
    novas_avaliacoes_restante = [individuo[1] for individuo in selecionados_restante]

    nova_populacao = elite_populacao + nova_populacao_restante
    novas_avaliacoes = elite_avaliacoes + novas_avaliacoes_restante
    
    return nova_populacao, novas_avaliacoes


def algoritmo_genetico(n_depositos, n_clientes, depositos, clientes, n_populacao, n_torneio, prob_mutacao, prob_crossover, tempo_max, prop_elitismo):
    inicio = time()
    # dados para normalização do fitness
    custo_construcao_max = sum(d['custo_construcao'] for d in depositos)
    custo_alocacao_max = sum(custos[j] for c in clientes for j, custos in enumerate([c['custos_alocacao']]))
    custo_max = custo_construcao_max + custo_alocacao_max
    capacidade_max = sum(d['capacidade'] for d in depositos)

    populacao = cria_populacao_inicial(n_populacao, clientes, depositos, n_depositos, n_clientes)
    avaliacoes = [avaliar_cromossomo(cromossomo, depositos, clientes, n_clientes, n_depositos, custo_max, capacidade_max) for cromossomo in populacao]


    while time() - inicio < tempo_max:
        filhos_gerados = []
        avaliacoes_filhos = []
        
        for _ in range(n_populacao // 2):
            pai1, indice_pai1 = selecao_pais_por_torneio(populacao, avaliacoes, n_torneio, n_populacao) 
            avaliacoes_aux = deepcopy(avaliacoes)
            avaliacoes_aux[indice_pai1]['fitness'] = float('-inf')
            pai2, _ = selecao_pais_por_torneio(populacao, avaliacoes_aux, n_torneio, n_populacao)
            
            if random() < prob_crossover:
                filho1 = crossover(pai1, pai2, n_clientes)
                filho2 = crossover(pai2, pai1, n_clientes)
    
                if random() < prob_mutacao:
                    filho1 = mutar(filho1, n_clientes, n_depositos)
                if random() < prob_mutacao:
                    filho2 = mutar(filho2, n_clientes, n_depositos)

                filhos_gerados.append(filho1)
                filhos_gerados.append(filho2)

                avaliacoes_filhos.append(avaliar_cromossomo(filho1, depositos, clientes, n_clientes, n_depositos, custo_max, capacidade_max))
                avaliacoes_filhos.append(avaliar_cromossomo(filho2, depositos, clientes, n_clientes, n_depositos, custo_max, capacidade_max))

        populacao_expandida = populacao + filhos_gerados
        avaliacoes_expandida = avaliacoes + avaliacoes_filhos
        
        populacao, avaliacoes = selecao_populacao_por_elitismo(populacao_expandida, avaliacoes_expandida, n_populacao, prop_elitismo)
        
    melhor_indice = -1
    menor_dep_excedidos = float('inf')
    melhor_fitness = float('-inf')
    melhor_fo = float('inf')
    excedidos =  float('inf')

    for i, avaliacao in enumerate(avaliacoes):
        if (avaliacao['dep_excedidos'] < menor_dep_excedidos or
           (avaliacao['dep_excedidos'] == menor_dep_excedidos and avaliacao['fitness'] > melhor_fitness)):
            menor_dep_excedidos = avaliacao['dep_excedidos']
            melhor_fitness = avaliacao['fitness']
            melhor_indice = i
            melhor_fo = avaliacao['fo']
            excedidos = avaliacao['dep_excedidos']

    print("Acabei o genético")

    return populacao[melhor_indice], melhor_fo, excedidos


def salva_melhor_solucao(melhor_solucao, melhor_fo, melhor_dep_excedidos, arquivo):
    with open(arquivo, 'w') as f:
        f.write(f"Melhor Solução:\n\n")

        table = tabulate(melhor_solucao, tablefmt="grid", numalign="right", stralign="right")
        f.write(table + "\n\n")

        f.write(f"F.O. desta Solução: {melhor_fo}\n\n")
        f.write(f"Depósitos excedidos desta Solução: {melhor_dep_excedidos}\n\n")
    print(f"Solução salva com sucesso em '{arquivo}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Executar o algoritmo genético com os parâmetros fornecidos.")
    parser.add_argument("--arquivo", required=True, help="Nome do arquivo de dados.")
    parser.add_argument("--prop_elitismo", type=float, default=0.1, help="Proporção de elitismo.")
    parser.add_argument("--n_populacao", type=int, default=200, help="Tamanho da população.")
    parser.add_argument("--n_torneio", type=int, default=20, help="Número de participantes no torneio.")
    parser.add_argument("--prob_crossover", type=float, default=1.0, help="Probabilidade de crossover.")
    parser.add_argument("--prob_mutacao", type=float, default=0.4, help="Probabilidade de mutação.")
    parser.add_argument("--n_rep", type=int, default=10, help="Número de repetições.")
    parser.add_argument("--csv_output", required=True, help="Arquivo CSV para salvar os resultados.")

    args = parser.parse_args()

    dados = ler_arquivo_dados(args.arquivo)
    n_depositos = dados['n_depositos']
    n_clientes = dados['n_clientes']
    depositos = dados['depositos']
    clientes = dados['clientes']

    tempo_max = 0.0375 * n_depositos * n_clientes

    soma_fo = 0
    rodadas_ok = 0

    melhor_solucao = None
    melhor_fo = float('inf')
    melhor_dep_excedidos = None

    for _ in range(args.n_rep):
        solucao, fo, excedidos = algoritmo_genetico(
            n_depositos, n_clientes, depositos, clientes,
            args.n_populacao, args.n_torneio,
            args.prob_mutacao, args.prob_crossover,
            tempo_max, args.prop_elitismo
        )

        if excedidos == 0:
            soma_fo += fo
            rodadas_ok += 1

            if fo < melhor_fo:
                melhor_solucao = solucao
                melhor_fo = fo
                melhor_dep_excedidos = excedidos

    nome_arquivo_saida = f"melhor_genetico_{args.arquivo}"
    salva_melhor_solucao(melhor_solucao, melhor_fo, melhor_dep_excedidos, nome_arquivo_saida)

    media = soma_fo / rodadas_ok if rodadas_ok > 0 else 0

    csv_path = Path(args.csv_output)
    existe_csv = csv_path.exists()

    with open(csv_path, mode='a', newline='') as csvfile:
        fieldnames = [
            "programa", "arquivo", "prop_elitismo", "n_populacao", "n_torneio",
            "prob_crossover", "prob_mutacao", "tempo_max", "n_rep", "melhor_resultado",
            "media_resultados", "rodadas_ok"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not existe_csv:
            writer.writeheader()

        writer.writerow({
            "programa": "genetico.py",
            "arquivo": args.arquivo,
            "prop_elitismo": args.prop_elitismo,
            "n_populacao": args.n_populacao,
            "n_torneio": args.n_torneio,
            "prob_crossover": args.prob_crossover,
            "prob_mutacao": args.prob_mutacao,
            "tempo_max": tempo_max,
            "n_rep": args.n_rep,
            "melhor_resultado": melhor_fo,
            "media_resultados": media,
            "rodadas_ok": rodadas_ok
        })
