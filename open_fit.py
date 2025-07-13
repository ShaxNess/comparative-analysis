import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Legge il file CSV
df = pd.read_csv("benchmark_results100.csv")
print(df)

df_c = pd.read_csv("costanti_stimate100.csv")
print("\nCostanti stimate:")
print(df_c)

get_c = lambda nome: float(df_c.loc[df_c["Nome costante"] == nome, "Valore"].values[0])

c_elastic  = get_c("c_elastic_avg")
c_funnel   = get_c("c_funnel_avg")
c_uniform  = get_c("c_uniform_avg")

c_elastic_max  = get_c("c_elastic_max")
c_funnel_max   = get_c("c_funnel_max")
c_uniform_max  = get_c("c_uniform_max")

inv_delta  = df["1/delta"].values
log_inv    = np.log(inv_delta)   
log_inv_sq  = log_inv ** 2

elastic_fit  = c_elastic  * log_inv
funnel_fit   = c_funnel   * log_inv
uniform_fit  = c_uniform  * log_inv

elastic_fit_max  = c_elastic_max  * log_inv
funnel_fit_max   = c_funnel_max   * log_inv_sq
uniform_fit_max  = c_uniform_max  * inv_delta

# Grafico probe medi (ammortizzati)
plt.figure()
plt.plot(df["1/delta"], df["elastic_avg"], label="Elastic - average probes", color="blue")
plt.plot(inv_delta, elastic_fit, linestyle="--", label="Elastic - fit", color="blue")
plt.plot(df["1/delta"], df["funnel_avg"], label="Funnel - average probes", color="green")
plt.plot(inv_delta, funnel_fit, linestyle="--", label="Funnel - fit", color="green")
plt.plot(df["1/delta"], df["uniform_avg"], label="Uniform - average probes", color="red")
plt.plot(inv_delta, uniform_fit, linestyle="--", label="Uniform - fit", color="red")
plt.xlabel("1 / delta")
plt.ylabel("Numero medio di probe")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig("graficoAvg.pdf", format="pdf", bbox_inches="tight")
plt.show()


# Grafico probe massimi (worst case)
plt.figure()
plt.plot(df["1/delta"], df["elastic_max"], label="Elastic - worst-case probes", color="blue")
plt.plot(inv_delta, elastic_fit_max, ls="--", label="Elastic - fit", color="blue")
plt.plot(df["1/delta"], df["funnel_max"], label="Funnel - worst-case probes", color="green")
plt.plot(inv_delta, funnel_fit_max, ls="--", label="Funnel - fit", color="green")
plt.plot(df["1/delta"], df["uniform_max"], label="Uniform - worst-case probes", color="red")
plt.plot(inv_delta, uniform_fit_max, ls="--",  label="Uniform - fit", color="red")
plt.xlabel("1 / delta")
plt.ylabel("Numero massimo di probe")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.savefig("graficoMax.pdf", format="pdf", bbox_inches="tight")
plt.show()



