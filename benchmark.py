from elastic_hashing import ElasticHashTableSHA256
from funnel_hashing import FunnelHashTableSHA256
from uniform_probing import UniformHashingSHA256
import numpy as np
import csv

def estimate_constant(f_theory, y_exp):
    f_arr = np.array(f_theory)
    y_arr = np.array(y_exp)
    c = np.dot(f_arr, y_arr) / np.dot(f_arr, f_arr)  # Least squares, np dot fa il prodotto scalare
    return c

def averaged_benchmark(table_class, n, delta, num_runs=5, run_id_start=1):
    avg_list = []
    max_list = []
    for i in range(num_runs):
        run_id = run_id_start + i
        result = benchmark_probes(table_class, n, delta, run_id=run_id)
        avg_list.append(result["avg"])
        max_list.append(result["max"])
    return {
        "avg": sum(avg_list) / num_runs,
        "max": sum(max_list) / num_runs,
    }, run_id_start + num_runs  # ritorna il dizionario con la media e il massimo dei probe, e l'ID per il prossimo run


def benchmark_probes(table_class, n, delta, info = False, run_id=1):
    prefix = str(run_id).zfill(4)
    base_keys = [f"key{i}" for i in range(1, n + 1)]
    keys = [f"{prefix} {k}" for k in base_keys] 
    
    values = [f"value{i}" for i in range(n)]
    capacity = int(n / (1 - delta)) + 1
    table = table_class(capacity=capacity, delta=delta, random_seed=run_id) #random_seed per garantire replicabilità per salt elastic e funnel 

    probe_list = []

    for k, v in zip(keys, values):
        table.insert(k, v)
        probe_list.append(table.probes)

    if (info):
        print("capacità: ", capacity)
        maxx = max(probe_list)
        avg = sum(probe_list) / n
        print("max tentativi per questi " + str(n) +" inserimenti:", maxx)
        print("avg tentativi per questi " + str(n) +" inserimenti:", avg)

    return {
        "max": max(probe_list), #restituisco il numero massimo di probe fatti in un singolo inserimento, tra tutti gli n inserimenti eseguiti (caso peggiore)
        "avg": sum(probe_list) / n, #restituisco il numero medio di probe effettuati per inserimento (complessità ammortizzata)
        "prefix": str(run_id).zfill(4)
    } 

# Lista dei delta e numero fisso di inserimenti
n = 100000 #numero inserimenti
n_delta_points = 50  # numero di delta da testare
delta_start = 0.5
delta_end = 0.0005
delta_values = list(np.geomspace(delta_start, delta_end, n_delta_points)) #lista di delta da testare
results = {}
prefixes = {}

num_runs = 100 # Numero di esecuzioni per ogni delta per ridurre la varianza
run_id_counter = 1


for delta in delta_values:
    print(f"Testing delta = {delta}")

    r_elastic, run_id_counter = averaged_benchmark(ElasticHashTableSHA256, n, delta, num_runs, run_id_counter)
    r_funnel, run_id_counter = averaged_benchmark(FunnelHashTableSHA256, n, delta, num_runs, run_id_counter)
    r_uniform, run_id_counter = averaged_benchmark(UniformHashingSHA256, n, delta, num_runs, run_id_counter)

    results[delta] = {
        "elastic_avg": r_elastic["avg"],
        "elastic_max": r_elastic["max"],
        "funnel_avg": r_funnel["avg"],
        "funnel_max": r_funnel["max"],
        "uniform_avg": r_uniform["avg"],
        "uniform_max": r_uniform["max"]
    }

# Dati per fitting (calcolo della costante)
inv_deltas = [1/d for d in delta_values]
log_inv_deltas = [np.log(1/d) for d in delta_values] #logaritmo naturale di 1/delta
log2_inv_deltas = [np.log(1/d)**2 for d in delta_values]

elastic_avg = [results[d]["elastic_avg"] for d in delta_values]
c_elastic_avg = estimate_constant(log_inv_deltas, elastic_avg)

funnel_avg = [results[d]["funnel_avg"] for d in delta_values]
c_funnel_avg = estimate_constant(log_inv_deltas, funnel_avg)

uniform_avg = [results[d]["uniform_avg"] for d in delta_values]
c_uniform_avg = estimate_constant(log_inv_deltas, uniform_avg)

elastic_max = [results[d]["elastic_max"] for d in delta_values]
c_elastic_max = estimate_constant(log_inv_deltas, elastic_max)

funnel_max = [results[d]["funnel_max"] for d in delta_values]
c_funnel_max = estimate_constant(log2_inv_deltas, funnel_max)

uniform_max = [results[d]["uniform_max"] for d in delta_values]
c_uniform_max = estimate_constant(inv_deltas, uniform_max)

costanti = [
    ("c_elastic_avg", c_elastic_avg),
    ("c_funnel_avg", c_funnel_avg),
    ("c_uniform_avg", c_uniform_avg),
    ("c_elastic_max", c_elastic_max),
    ("c_funnel_max", c_funnel_max),
    ("c_uniform_max", c_uniform_max)
]


with open("benchmark_results100.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "delta", "1/delta", 
        "elastic_avg", "elastic_max", 
        "funnel_avg", "funnel_max", 
        "uniform_avg", "uniform_max"
    ])

    for delta in delta_values:
        inv_d = 1 / delta
        r = results[delta]
        writer.writerow([
            delta, inv_d,
            r["elastic_avg"], r["elastic_max"],
            r["funnel_avg"], r["funnel_max"],
            r["uniform_avg"], r["uniform_max"]
        ])

with open("costanti_stimate100.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Nome costante", "Valore"])
    for nome, valore in costanti:
        writer.writerow([nome, f"{valore:.6f}"])
