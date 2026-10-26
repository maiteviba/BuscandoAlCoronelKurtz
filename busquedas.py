from agente import Capitan_Willard
from entorno import Rooms, Creencias_Room, Palace
from collections import deque
import re

## Se inicializan las variables globales de obstáculos ##
EMPTY_ROOM = "."
SOLDADO = "M"
EXIT = "E"
PRECIPICIO = "P"
CORONEL_KURTZ = "CK"
COORDENADAS_INICIALES = (0,0)

LISTA = [SOLDADO, EXIT, CORONEL_KURTZ, PRECIPICIO, PRECIPICIO]

coordenadas_precipicios = []
coordenadas_soldado = []
coordenadas_salida = []

## Dimensiones del palacio ##
DIM_X = 6
DIM_Y = 6


def elegir_celda_exploracion(CW:Capitan_Willard):
    """
    Función que retorna la próxima celda a explorar
    Args:
        - CW (Capitan_Willard): agente de búsqueda
    Returns:
        - (tuple): Las coordenadas de la siguiente habitación a explorar
    """

    x, y = CW.ubicacion

    if not CW.frontera:
        return None
    
    
    objetivo = None
    menor_distancia = float("inf")

    for (fx, fy) in CW.frontera:
        distancia = abs(fx-x) + abs(fy-y)
        if distancia < menor_distancia:
            menor_distancia = distancia
            objetivo = (fx, fy)

    return objetivo

def busqueda_anchura (CW:Capitan_Willard, inicio: tuple, objetivo_actual:tuple):
    """
    Función que realiza la búsqueda por anchura para encontrar un camino seguro desde la posición
    actual hasta la celda objetivo.
    Esta búsqueda se realiza únicamente sobre las casillas que el agente considera que no atraviesan peligros.
    
    Params:
        - CW (Capitan_Willard): agente
        - inicio (tuple): coordenadas de inicio
        - objetivo_actual (tuple): coordenadas del objetivo
    Returns:
        - (list): lista de coordenadas que representa ek camino desde el inicio hacia el objetivo.
        - None: en caso de que no exista un camino seguro
    """

    # Inicializamos la cola para poder ejecutar el BFS, 
    # además de un set de las habitaciones que se han visitado 
    # y un diccionario para poder a continuación calcular la ruta
    cola = deque([inicio])
    habitaciones_visitadas = {inicio}
    ruta_padres = {inicio: None}

    # Mientras la cola no se quede vacía se exploran todas las posibles rutas desde 
    # la habitación actual para encontrar la ruta a la habitación 'objetivo'
    while cola:
        actual = cola.popleft() # Se actualiza el actual

        # En caso de que ya se haya encontrado el objetivo, se calcula la ruta
        if actual == objetivo_actual:
            camino = []
            while actual is not None:
                camino.append(actual)
                actual = ruta_padres[actual]
            return camino[::-1]
        
        # En caso contrario, se van añadiendo los vecinos seguros que no han sido visitados
        x, y = actual
        for vx, vy in CW.vecinos_seguros(x, y):
            if (vx,vy) not in habitaciones_visitadas:
                habitaciones_visitadas.add((vx,vy))
                ruta_padres[(vx,vy)] = (x,y)
                cola.append((vx,vy))
    
    # En caso de que no se haya encontrado ninguna ruta, significa que ya no hay caminos seguros.
    return None

def ir_salida(CW:Capitan_Willard):

    """
    Función que lleva al agante desde su posición actual hacia la salida usando búsqueda en anchura.
    Reconstruyendo el camino hasta la salida, desplazándose paso a paso desde su ubicación actual.

    Params:
        - CW(Capitan_Willard): agente

    Returns:
        - None
    """
    
    inicio = CW.ubicacion
    salida = CW.salida

    # Se vuelve a usar bfs para salir del palacio

    cola = deque([inicio])
    habitaciones_visitadas = {inicio}
    ruta_padres = {inicio: None}

    while cola:
        actual = cola.popleft() # Se actualiza el actual

        # En caso de que ya se haya encontrado el objetivo, se calcula la ruta
        if actual == salida:
            break
        
        # En caso contrario, se van añadiendo los vecinos seguros que no han sido visitados
        x, y = actual
        for vx, vy in CW.vecinos_seguros(x, y):
            if (vx,vy) not in habitaciones_visitadas:
                habitaciones_visitadas.add((vx,vy))
                ruta_padres[(vx,vy)] = (x,y)
                cola.append((vx,vy))
    
    if salida not in ruta_padres:
        print("No es posible volver a la salida de manera segura")
        return
    
    camino = []
    actual = salida
    while actual is not None:
        camino.append(actual)
        actual=ruta_padres[actual]
    camino.reverse()

    for vx, vy in camino:
        
        x, y = CW.ubicacion
        CW.tablero[x][y].aspecto = "."

        CW.ubicacion = (vx, vy)
        CW.tablero[vx][vy].aspecto = "CW"
        print(CW)
    
    print("El agente ha conseguido su objetivo y ha saldio con el Coronel Kurtz")

def tirar_granada (CW: Capitan_Willard):
    """
    Función que lanza la granada al soldado
    Params:
        - CW(Capitan_Willard): agente
    Returns:
        - None
    """

    sx, sy= CW.soldado
    x, y = CW.ubicacion

    if 0<= abs(sx-x) <= 1 and  0<= abs(sy-y) <= 1:
        print("Soldado muerto")
        CW.granada = 0
        CW.soldado_muerto = True
        CW.soldado = None
        CW.tablero[sx][sy].segura = True
        CW.tablero[sx][sy].posible_soldado = False
        

def algoritmo_agente_logico(CW:Capitan_Willard, palace:Palace):
    """
    Función del agente lógico para conseguir el objetivo
    Params:
        - CW (Capitan_Willard): agente
        - palace (Palace): entorno
    Returns:
        - None
    """

    while not CW.final:

        px, py = CW.ubicacion
        CW.tablero[px][py].aspecto = "CW"

        if palace.tablero[px][py].casilla == PRECIPICIO:
            print("Agente muerto!")
            break

        CW.actualizar_casillas(palace.tablero[px][py])
        CW.deduccion_precipicio(palace)
        soldado = CW.deduccion_soldado(palace)
        CW.actualizar_frontera()

        print(CW)

        if soldado or CW.soldado is not None:
            tirar_granada(CW)
            print(CW)

        if palace.tablero[px][py].casilla == EXIT and CW.ck:
            CW.final = True
            print("El agente ha logrado su objetivo, ha salido con el Coronel Kurtz")
            break
        
        # En caso de que se sepa donde está la salida y ya se encuentre con el Coronel:
        if CW.ck and CW.salida is not None:
            ir_salida(CW)
            break

        ## Observo hacia donde avanzar:
        siguiente_habitacion = elegir_celda_exploracion(CW)

        if siguiente_habitacion is None:
            print("La frontera está vacía, no es posible seguir avanzando")
            break

        ruta = busqueda_anchura(CW, CW.ubicacion, siguiente_habitacion)
            
        if ruta is None or len(ruta)<2:
            CW.frontera.discard(siguiente_habitacion)
            print("La frontera está vacía y no se puede encontrar una ruta segura")
            break
        
        CW.tablero[px][py].aspecto = "✓"
        CW.ubicacion = ruta[1]
        

def mostrar_tablero (CW: Capitan_Willard, palacio:Palace):
    """
    Función para mostrarle el tablero al usuario
    """

    print("--------LEYENDA--------\n" \
    "CW: Capitán Willard\n" \
    "✓: casilla explorada\n" \
    ".: Casilla sin explorar\n" \
    "□: Casilla en frontera\n" \
    "E: Salida\n" \
    "P?: Posible_precipicio\n" \
    "S?: Posible soldado\n" \
    "P!: Precipicio seguro\n" \
    "S!: Soldado seguro\n")

    tablero_conocimientos = CW.tablero
    visitadas = CW.visitados
    frontera = CW.frontera

    tablero_pintar = [["." for i in range(DIM_Y)] for j in range(DIM_X)]

    for i in range(len(tablero_pintar)):
        for j in range(len(tablero_pintar[i])):

            if (i, j) in frontera:
                tablero_pintar[i][j] = "□"
            elif (i,j) in visitadas:
                tablero_pintar[i][j] = "✓"
            elif palacio.tablero[i][j].casilla == EXIT:
                tablero_pintar[i][j] = "E"
            elif (i,j) in CW.precipicios:
                tablero_pintar[i][j] = "P!"
            elif (i,j) == CW.soldado:
                tablero_pintar[i][j] = "S!"
    
    for vx, vy in visitadas:
        vecinos = CW.coger_coord_vecinas(palacio.tablero[vx][vy],vx, vy)
        seguros = CW.vecinos_seguros(vx, vy)

        for i, j in vecinos:
            if (i,j) not in seguros:
                if tablero_conocimientos[i][j].posible_precipicio and tablero_conocimientos[i][j].posible_soldado:
                    pass
                elif tablero_conocimientos[i][j].posible_precipicio:
                    tablero_pintar[i][j] = "P?"
                elif tablero_conocimientos[i][j].posible_soldado:
                    tablero_pintar[i][j] = "S?"



    for fx, fy in frontera:
        vecinos = CW.coger_coord_vecinas(palacio.tablero[fx][fy],fx, fy)
        seguros = CW.vecinos_seguros(fx, fy)

        for i, j in vecinos:
            if (i,j) not in seguros:
                if tablero_conocimientos[i][j].posible_precipicio and tablero_conocimientos[i][j].posible_soldado:
                    pass
                elif tablero_conocimientos[i][j].posible_precipicio:
                    tablero_pintar[i][j] = "P?"
                elif tablero_conocimientos[i][j].posible_precipicio:
                    tablero_pintar[i][j] = "S?"

    for fila in tablero_pintar:
        print(fila) 

            
def limpiar_coordenadas (coordenadas:str)->tuple:
    """
    Función auxiliar para obtener a través de regex las coordenadas elegidas por el usuario
    Params:
        - coordenadas (str): input del usuario
    Returns:
        - (tuple): coordenadas ya en forma de tupla para continuar con el algoritmo.
    """

    pattern = re.compile(r"\((\d+)\s*,\s*(\d+)\)")
    busqueda = pattern.match(coordenadas)

    if busqueda:
        return (int(busqueda.group(1)), int(busqueda.group(2)))
    return None


def busqueda_usuario(CW:Capitan_Willard, palace:Palace):
    """
    Función que se ejevuta cuando es el ususario el que guía al agente en la toma de decisiones

    Params:
        - CW (Capitan_Willard): agente
        - palace (Palace): entorno
    Returns:
        - None
    """
    
    while not CW.final:

        px, py = CW.ubicacion

        if palace.tablero[px][py].casilla in [PRECIPICIO, SOLDADO]:
            print("☠️ --- Ha muerto --- ☠️")
            print("Se acaba la aprtida...")
            break

        CW.tablero[px][py].aspecto = "CW"

        CW.actualizar_casillas(palace.tablero[px][py])
        CW.deduccion_precipicio(palace)
        soldado = CW.deduccion_soldado(palace)
        CW.actualizar_frontera()

        if CW.ck:
            print("Se ha encontrado al Coronel Kurtz")

        mostrar_tablero(CW, palace)

        if palace.tablero[px][py].casilla == EXIT and CW.ck:
            CW.final = True
            print("El agente ha logrado su objetivo, ha salido con el Coronel Kurtz")
            break

        if soldado:
            print("SOLDADO ENCONTRADO!")
            while True:
                bomba = input("¿Quieres lanzarle la bomba? (SI/NO): ")
                if bomba == "SI": 
                    tirar_granada(CW)
                    print("AAAAA")
                    print("💣BUM💣")
                    palace.tablero[px][py].casilla = EMPTY_ROOM
                    mostrar_tablero(CW, palace)
                    break

                elif bomba == "NO":
                    print("No se ataca al soldado...")
                    break
                else:
                    print("Respuesta no válida. Escriba SI o NO")
                                   
        print("Frontera: ")
        for i, j in CW.frontera:
            print(f"({i}, {j})")
        
        if len(CW.frontera)<1:
            print("Frontera vacía, no es posible continuar de manera segura")
            break

        CW.tablero[px][py].aspecto = "."
        
        match = False
        while not match:
            coordenadas = input("Elija a que casilla se quiere desplazar (x,y): ")
            coordenadas=limpiar_coordenadas(coordenadas)
            if coordenadas in CW.frontera:
                match = True
        
        CW.ubicacion = coordenadas
        