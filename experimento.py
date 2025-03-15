import subprocess

arquivos = ["cap61.txt", "cap62.txt", "cap63.txt", "cap64.txt", "cap82.txt", "cap124.txt", "cap133.txt", "capa.txt"]

def executar_genetico(arquivo):
    comando = [
        "python", "genetico.py",
        "--arquivo", arquivo,
        "--prop_elitismo", "0.1", 
        "--n_populacao", "200",  
        "--n_torneio", "20",     
        "--prob_crossover", "1.0", 
        "--prob_mutacao", "0.4", 
        "--n_rep", "10",         
        "--csv_output", "resultados_genetico.csv"
    ]

    subprocess.run(comando, check=True)


def executar_simulated_annealing(arquivo):
    calculate_initial_t = "0" if arquivo == "capa.txt" else "1"
    
    comando = [
        "python", "sa.py",
        "--input_file", arquivo,
        "--beta", "2",
        "--gama", "0.95",
        "--t0", "100",
        "--cooling_rate", "0.91",
        "--t_final", "1e-5",
        "--n_rep", "10",
        "--csv_output", "resultados_sa.csv",
        "--calculate_initial_t", calculate_initial_t
    ]
    
    subprocess.run(comando, check=True)


if __name__ == "__main__":
    for arquivo in arquivos:
        executar_genetico(arquivo)
        executar_simulated_annealing(arquivo)
