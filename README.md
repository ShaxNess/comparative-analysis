# comparative-analysis
La repository presenta l'implementazione di tre algoritmi: uniform_probing, elastic_hashing, funnel_hashing. Inoltre è presente un benchmark di confronto tra le performance dei tre in termini di numero di probes per inserimento nel caso peggiore e nel caso ammortizzato.
Il codice di Funnel ed Elastic Hashing è stato modificato partendo dal codice già realizzato da sternma https://github.com/sternma/optopenhash
Per vedere direttamente i confronti utilizza open_fit.py con i csv presenti in repository. 
Per eseguire confronti personalizzati modifica il benchmark con il numero di inserimenti e di delta desiderati, i valori max e min di delta e il numero di run per delta.
