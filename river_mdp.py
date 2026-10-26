import random
import parte2_2 as p2

VACIA = "|   |"
SEGURA = "| R |"
ISLA = "| I |"
ORILLA_FINAL ="| E |"
POSICION = "|CWCK|"


DIMX = 7
DIMY = 6



def crear_tablero()->tuple:
    """
    Función que crea el tablero:
    Params:
        - None
    Returns:
        - (tuple): tablero, coordenadas de inicio, coordenadas de salida, localización de las islas
    """
    tablero = [[SEGURA for i in range(DIMY)] for j in range(DIMX)]
    
    ix, iy = (random.randint(0,5), 0)
    sx, sy = (random.randint(0,5), 5)

    for i in range(DIMX):
        tablero[i][0] = VACIA
        tablero[i][DIMY-1] = VACIA
        
    tablero[ix][iy] = POSICION
    tablero[sx][sy] = ORILLA_FINAL
    
    islas = []
    for i in range(2):
        while True:             
            x = random.randint(0, DIMX-1)
            y = random.randint(0, DIMY-1)

            if tablero[x][y] == SEGURA:
                if tablero[x][y] != ISLA:
                    tablero[x][y] = ISLA
                    islas.append((x,y))
                    break

    return (tablero, (ix,iy), (sx, sy), islas)

def mostrar_tablero(tablero):
    """
    Función auxiliar para mostrar el tablero
    """
    for fila in tablero:
        print(" ".join(fila))

def calcular_corriente():
    """
    Función que calcula la carriente en cada columna
    Params:
        - None
    Returns:
        - (dict): diccionario con las corrientes correspondientes a cada columna
    """
    
    corriente = {}
    for i in range(DIMY):
        if i==0 or i==DIMY-1:
            corriente[i] = 0.0
        else:
            corriente[i] = river_strenght()
    return corriente

def river_strenght():
    """
    Función que genera un número aleatorio que es la fuerza de la corriente del río
    Params:
        - self
    Returns:
        - número aleatorio de la corriente
    """
    return round(random.uniform(0.06,0.94), 1)  


def mostrar_tablero_con_ruta (trayectoria:list[tuple], inicio:tuple, salida:tuple):
    """
    Función que muestra la ruta tomada por el agente en el entorno.
    """
    
    tablero = [["." for _ in range(DIMY)] for _ in range(DIMX)]

    anterior = None
    acciones = {(-1,0):"↑",(1,0):"↓",
            (0,-1):"←",(0,1):"→"}
    
    for x, y in trayectoria:
        if anterior is not None:
            if ((x-anterior[0]),(y-anterior[1])) in acciones.keys():
                tablero[anterior[0]][anterior[1]] = acciones[(x-anterior[0]),(y-anterior[1])]
        anterior = (x,y)
    tablero[inicio[0]][inicio[1]] = "CW"
    tablero[salida[0]][salida[1]] = "E"
    mostrar_tablero(tablero)

def mostrar_politica (politica:dict, inicio:tuple, salida:tuple, env:p2.Entorno)->None:
    """
    Función que muestra el resultado obtenido por las políticas óptimas.
    Params:
        - politica(dict): diccionario de la política óptima calculada mediante Value Iteration
        - salida(tuple): tupla con las coordenadas de la salida
        - inicio(tuple): tupla con coordenadas de inicio
        - env (p2.Entorno): entorno en el que se trabaja
    Returns:
        - None
    """
    tablero = [["." for _ in range(DIMY)] for _ in range(DIMX)]
    mapa = {"up":"↑","down":"↓","left":"←","right":"→"}
    for i in range(len(tablero)):
        for j in range(len(tablero[i])):
            a = politica[(i,j)]
            if (i, j) == salida:
                tablero[i][j] = "S"
            elif (i, j) == entrada:
                tablero[i][j] = "CWCK"
            elif (i, j) in env.islas:
                tablero[i][j] = "I"
            else:
                tablero[i][j] = mapa[a]
    mostrar_tablero(tablero)
                


if __name__ == "__main__":
    
    tablero, entrada, salida, islas = crear_tablero()
    corriente = calcular_corriente()
    entorno = p2.Entorno(tablero, entrada, salida, islas, corriente)

    V, politica = p2.value_iteration(entorno)
    print("Mostrando política...\n")
    mostrar_politica(politica, entrada, salida, entorno )

    agente = p2.Agente(entrada, entorno, politica)

    trayectoria, acciones, recompensa, n_acciones, es_terminal = agente.simular_partida()

    print(f"La recompensa total ha sido: {recompensa}")
    print(f"La trayectoria seguida ha sido:\n{trayectoria}")
    mostrar_tablero_con_ruta(trayectoria, entrada, salida)