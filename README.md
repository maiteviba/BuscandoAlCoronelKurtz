# Proyecto Final:

## Buscando al Coronel Kurtz

Este repositorio contiene el código desarrollado para el proyecto final de la asignatura de Fundamentos de la Inteligencia Artificial de 2º iMAT.

El objetivo es diseñar un agente (el Capitán Willard) capaz de moverse por un entorno parcialmente observable, encontrar al coronel Kurtz y salir con él de forma segura. El proyecto se divide en tres partes:

1. Agente lógico que deduce la posición de los precipicios y del soldado a partir de los perceptos y explora el palacio mediante búsqueda en anchura (BFS)
2. Agente que utiliza inferencia bayesiana para estimar la probabilidad de cada peligro y la representa con mapas de calor
3. Cruce del río modelado como un proceso de decisión de Markov (MDP) y resuelto con Value Iteration


## Estructura del proyecto

Parte 1:

- `kurtz.py`: archivo principal de la parte 1
- `agente.py`: clase del agente y sus acciones
- `busquedas.py`: deducción de peligros y búsqueda del camino
- `entorno.py`: clases del palacio y de las habitaciones

Parte 2:

- `palacio.py`: archivo principal de la parte 2.1
- `parte2.py`: inferencia bayesiana, mapas de probabilidad y toma de decisiones
- `river_mdp.py`: archivo principal de la parte 2.2
- `parte2_2.py`: definición del MDP y algoritmo de Value Iteration

Otros:

- `memoria.pdf`: informe final del proyecto
- `requirements.txt`: librerías necesarias


## Ejecución

Cada parte se ejecuta desde su archivo principal:

python kurtz.py
python palacio.py
python river_mdp.py

En las partes 1 y 2.1 se puede elegir entre guiar al agente manualmente (YO) o dejar que decida el algoritmo (ALGORITMO).


## Requisitos

Para ejecutar el código es necesario tener instalado Python 3 y las siguientes librerías:

numpy
matplotlib
