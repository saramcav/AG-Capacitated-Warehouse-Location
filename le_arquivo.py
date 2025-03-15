def ler_arquivo_dados(caminho_arquivo):
    dados = {
        "n_depositos": -1,
        "n_clientes": -1,
        "depositos": [],
        "clientes": []
    }
    
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            linhas = arquivo.readlines()
        
        dados["n_depositos"], dados["n_clientes"] = map(int, linhas[0].split())
        
        for i in range(1, dados["n_depositos"] + 1):
            capacidade, custo_construcao = map(float, linhas[i].split())
            dados["depositos"].append({"capacidade": capacidade, "custo_construcao": custo_construcao})
        
        linha_atual = dados["n_depositos"] + 1
        for _ in range(dados["n_clientes"]):
            demanda = int(linhas[linha_atual].strip())
            linha_atual += 1
            
            custos_alocacao = []
            while len(custos_alocacao) < dados["n_depositos"]:
                custos_alocacao.extend(map(float, linhas[linha_atual].split()))
                linha_atual += 1
            
            dados["clientes"].append({"demanda": demanda, "custos_alocacao": custos_alocacao})
        
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return None
    
    return dados



