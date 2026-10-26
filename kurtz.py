import random
from entorno import Palace, Rooms, Creencias_Room
from agente import Capitan_Willard
from busquedas import busqueda_usuario, algoritmo_agente_logico

## Se inicializan las variables globales de obstáculos ##
EMPTY_ROOM = "."
SOLDADO = "M"
EXIT = "E"
PRECIPICIO = "P"
CORONEL_KURTZ = "CK"
COORDENADAS_INICIALES = (0,0)

LISTA = [SOLDADO, EXIT, CORONEL_KURTZ, PRECIPICIO, PRECIPICIO, PRECIPICIO]

coordenadas_precipicios = []
coordenadas_soldado = []
coordenadas_salida = []

## Dimensiones del palacio ##
DIM_X = 6
DIM_Y = 6

       
def Initialize_Palace() -> list[list]:
    """
    Función para crear el tablero y posicionar sus elementos 
    Args:
        None
    
    Returns:
        palace(list[list]): tablero creado
    """
   
    # Se crea el tablero
    palace = [[EMPTY_ROOM for i in range(DIM_Y)] for j in range(DIM_X)]
    
    # Se seleccionan de forma aleatoria las posiciones de los elementos que compondrán el tablero
    for element in LISTA:   
        stop=False
        
        while not stop:
            coordx = random.randint(0, DIM_X-1)
            coordy = random.randint(0, DIM_Y-1)

            if palace[coordx][coordy] == EMPTY_ROOM and not (coordx== COORDENADAS_INICIALES[0] and coordy==COORDENADAS_INICIALES[1]):
                palace[coordx][coordy] = element
                stop=True
    return palace

def Create_Palace(palace: list[list]) -> Palace:
    """
    Función que crea los objetos necesarios para el programa. 
    Args:
        palace(list[list]): tablero con las posiciones correspondoentes de cada elemento 
    
    Returns:
        (Palace): tablero final
    """
   
    # Se crea una matriz para convertirla en el objeto palacio
    tablero = [[None for i in range(DIM_Y)] for j in range(DIM_X)]
    elementos = [SOLDADO, EXIT, PRECIPICIO]

    # Se recorre el tablero inicial
    for i in range(DIM_X):
      for j in range(DIM_Y):
         
        # Se crea la habitación
        room = Rooms(palace[i][j])
         
        ### Se comprueban sus preceptos ###
        coordenadas_vecinas = []

        # Arriba
        if i > 0:
            coordenadas_vecinas.append((i-1, j))
        else:
           room.arriba = True
        
        # Abajo
        if i < DIM_X-1:
            coordenadas_vecinas.append((i+1, j))
        else:
           room.abajo = True

        # Izquierda
        if j > 0:
            coordenadas_vecinas.append((i, j-1))
        else:
           room.izquierda = True

        # Derecha
        if j < DIM_Y-1:
            coordenadas_vecinas.append((i, j+1))
        else:
           room.derecha = True

        # Otros elementos 
        for cx, cy in coordenadas_vecinas:
            casilla = palace[cx][cy]

            if casilla in elementos:                
                if casilla == SOLDADO:
                    room.ronquido = True
                if casilla == EXIT:
                    room.resplandor = True
                if casilla == PRECIPICIO:
                    room.brisa = True 
        if room.casilla == EXIT:
            room.resplandor = True
        # Se añade la habitación al tablero  
        tablero[i][j] = room  
    
    # Se retorna el palacio creado
    return Palace(tablero) 

def Create_Agente()->Capitan_Willard:
    """
    Función que crea el agente
    """
    tablero = [[None for i in range(DIM_Y)] for j in range(DIM_X)]

    for i in range(DIM_X):
      for j in range(DIM_Y):
        
        room = Creencias_Room(False, False, True, True, False)
        tablero[i][j] = room
        
    return Capitan_Willard(COORDENADAS_INICIALES, tablero)



if __name__ == "__main__":
   
    palace = Initialize_Palace()
    palace = Create_Palace(palace)

    CW = Create_Agente()

    while True:
        modo = input("Elija el modo en el que quiere guiar el agente\n "
        "-Guiado por usted (YO)\n "
        "-Guiado por el algoritmo (ALGORITMO)\n ").strip().upper()
        if modo == "YO":
            busqueda_usuario(CW, palace)
            break
        if modo == "ALGORITMO":
            algoritmo_agente_logico(CW, palace)
            break
        else:
            print("Vuelva a intentarlo, escriba YO o ALGORITMO")


