import parte2 as p2
import random

EMPTY_ROOM = "."
SOLDADO = "M"
SALIDA = "S"
CORONEL_KURTZ = "CK"
FUEGO = "F"
PINCHOS = "P"
DARDOS = "D"
COORDENADAS_INICIALES = (0,0)


## Dimensiones del palacio ##
DIM_X = 6
DIM_Y = 6
N = DIM_X*DIM_Y
       

def Initialize_Palace() -> list[list]:
    """
    Función para crear el tablero y posicionar sus elementos 
    Args:
        None
    
    Returns:
        palace(list[list]): tablero creado
    """
   
    # Se crea el tablero
    palace = [[[] for i in range(DIM_Y)] for j in range(DIM_X)]
    trampas = [FUEGO, PINCHOS, DARDOS]
    otras_celdas = [SOLDADO, SALIDA, CORONEL_KURTZ]

    coordenadas_trampas = []


    # Se seleccionan de forma aleatoria las posiciones de los elementos que compondrán el tablero
    for trampa in trampas:   
        
        while True:
            coordx = random.randint(0, DIM_X-1)
            coordy = random.randint(0, DIM_Y-1)
            
            if (coordx, coordy) != COORDENADAS_INICIALES:
                palace[coordx][coordy].append(trampa)
                coordenadas_trampas.append((coordx, coordy))
                break
    
    for celda in otras_celdas:
        
        while True:
            x = random.randint(0, DIM_X-1)
            y = random.randint(0, DIM_Y-1)

            if (x,y) not in coordenadas_trampas and (x,y) != COORDENADAS_INICIALES:
                palace[x][y].append(celda)
                break

    return palace

def Create_Palace(palace: list[list]) -> p2.Palace:
    """
    Función que crea los objetos necesarios para el programa. 
    Args:
        palace(list[list]): tablero con las posiciones correspondoentes de cada elemento 
    
    Returns:
        (Palace): tablero final
    """
   
    # Se crea una matriz para convertirla en el objeto palacio
    tablero = [[None for i in range(DIM_Y)] for j in range(DIM_X)]

    # Se recorre el tablero inicial
    for i in range(DIM_X):
      for j in range(DIM_Y):
         
        # Se crea la habitación
        room = p2.casillas2(palace[i][j])
         
        ### Se comprueban sus preceptos ###
        coordenadas_vecinas = []

        # Arriba
        if i > 0:
            coordenadas_vecinas.append((i-1, j))
        else:
           room.preceptos[5] = True
        
        # Abajo
        if i < DIM_X-1:
            coordenadas_vecinas.append((i+1, j))
        else:
           room.preceptos[6] = True

        # Izquierda
        if j > 0:
            coordenadas_vecinas.append((i, j-1))
        else:
           room.preceptos[8] = True

        # Derecha
        if j < DIM_Y-1:
            coordenadas_vecinas.append((i, j+1))
        else:
           room.preceptos[7] = True
        
        # La coordenada actual, también tiene un estímulo si contiene alguna casilla "especial"
        coordenadas_vecinas.append((i,j))

        # Otros elementos 
        for cx, cy in coordenadas_vecinas:
            casilla = palace[cx][cy]
             
            if FUEGO in casilla:
                room.preceptos[0] = True
            if PINCHOS in casilla:
                room.preceptos[1] = True
            if DARDOS in casilla:
                room.preceptos[2] = True
            if SOLDADO in casilla:
                room.preceptos[3] = True
            if SALIDA in casilla:
                room.preceptos[4] = True

        # Se añade la habitación al tablero  
        tablero[i][j] = room  
    
    # Se retorna el palacio creado
    return p2.Palace(tablero) 

def mapa_prior()->list[list]:
    """
    Función que crea los tableros
    """
    tablero = [[1/(N-1) for i in range(DIM_Y)] for j in range(DIM_X)]
    x, y = COORDENADAS_INICIALES
    tablero[x][y] = 0.0
    return tablero

def Create_Agente()->p2.Capitan_Willard:
    """
    Función que crea el agente
    """

    fuego = mapa_prior()
    pinchos = mapa_prior()
    dardos = mapa_prior()

    militar = mapa_prior()
    salida = mapa_prior()
    
    return p2.Capitan_Willard(COORDENADAS_INICIALES, 
                           fuego, pinchos, dardos, 
                           militar, salida)

if __name__ == "__main__":
   
    palace = Initialize_Palace()
    palace = Create_Palace(palace)

    CW = Create_Agente()

    while True:
        modo = input("Elija el modo en el que quiere guiar el agente\n "
        "-Guiado por usted (YO)\n "
        "-Guiado por el algoritmo (ALGORITMO)\n ").strip().upper()
        if modo == "YO":
            p2.busqueda_usuario(CW, palace)
            break
        if modo == "ALGORITMO":
            p2.busqueda_logica(CW, palace)
            break
        else:
            print("Vuelva a intentarlo, escriba YO o ALGORITMO")


