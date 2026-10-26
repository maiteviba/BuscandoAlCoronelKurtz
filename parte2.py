import re
import matplotlib.pyplot as plt
import numpy as np


EMPTY_ROOM = "."
SOLDADO = "M"
SALIDA = "S"
CORONEL_KURTZ = "CK"
FUEGO = "F"
PINCHOS = "P"
DARDOS = "D"

RIESGOS = [SOLDADO, FUEGO, PINCHOS, DARDOS]

## Dimensiones del palacio ##
DIM_X = 6
DIM_Y = 6
N = DIM_X*DIM_Y


class Palace:

    def __init__(self, tablero:list):      
      self.tablero=tablero


class casillas2:

    def __init__ (self, casilla: str):    

        # [eF?, eP?, eD?, eM?, eS?, P_arriba?, P_abajo?, P_derecha?, P_izquierda?, G?]
        self.preceptos = [False]*10
        self.casilla = casilla # Lista de símbolos de esa celda
    

class Capitan_Willard:

    def __init__ (self, ubicacion:tuple, 
                  fuego, pinchos, dardos, 
                  soldado, salida):

        
        self.ubicacion = ubicacion
        self.visitados = set()
        self.frontera = set()
        self.bloqueadas = set()
        self.riesgo_asumido = 0.2

        self.fuego = fuego
        self.pinchos = pinchos
        self.dardos = dardos
        self.soldado = soldado
        self.salida = salida
        
        self.ck = False # Indica si el Capitán Willard está o no con el Coronel 
        self.granada = 1
        self.final = False
        self.posi_soldado = None
        self.camino = [ubicacion]

     
    def vecinos_no_visitados (self, x:int, y:int)->list:
        """
        Función que devuleve una lista con las coordenadas de las celdas adyacentes que aún no hayan sido visitadas
        
        Params:
            - x(int): coordenada x
            - y(int): coordenada y
        Returns:
            - (list): lista de coordenadas
        """

        vecinos = []
        movimientos = [(-1,0), (1,0), (0,-1), (0,1)]

        for mx, my in movimientos:
            vx, vy = x+mx, y+my
            if 0<= vx < DIM_X and 0<= vy < DIM_Y:
                if (vx, vy) not in self.visitados:
                    vecinos.append((vx,vy))
        return vecinos

    def coger_coord_vecinas (self, casilla_actual:casillas2, coord_x:int, coord_y:int) ->list:
        """
        Función que guarda y retorna las coordenadas de las casillas adyacentes a la dada. 
        Args:
            - casilla_actual(Rooms): habitación de la que se buscan las vecinas
            - coord_x(int): coordenada x
            - coord_y(int): coordenada y
        
        Returns:
            coordenadas_vecians (list): lista de coordenadas vecinas
        """
        coordenadas_vecinas = []

        # Arriba
        if not casilla_actual.preceptos[5]:
            coordenadas_vecinas.append((coord_x-1, coord_y))
        # Abajo
        if not casilla_actual.preceptos[6]:
            coordenadas_vecinas.append((coord_x+1, coord_y))
        # Izquierda
        if not casilla_actual.preceptos[8]:
            coordenadas_vecinas.append((coord_x, coord_y-1))
        # Derecha
        if not casilla_actual.preceptos[7]:
            coordenadas_vecinas.append((coord_x, coord_y+1))

        return coordenadas_vecinas


    def riesgo_total(self, i:int, j:int)-> float:
        """
        Función que devuelve el riesgo total asociado a una casilla
        Params:
            - self: agente
            - i(int): coordenada x de la habitación
            - j(int): coordenada y de la habitación
        Returns:
            - (float): valor del riesgo de la casilla
        """
        return (self.fuego[i][j] + self.pinchos[i][j] + self.dardos[i][j] + self.soldado[i][j])

    def max_probabilidad_salida (self)->tuple:
        """
        Función que obtiene las coordenadas de la casilla con la probabilidad más alta
        de ser la salida
        Params:
            - self
        Returns:
            - (tuple): tupla con las coordenadas de la casilla obtenida      
        """

        # Inicialización de variables
        mapa = self.salida
        max_prob = 0.0
        casilla = None

        # Búsqueda de la casilla
        for i in range(DIM_X):
            for j in range(DIM_Y):
                prob_casilla = mapa[i][j]

                if prob_casilla > max_prob:
                    max_prob = prob_casilla
                    casilla = (i,j)
        
        return casilla

    def distancia_manhattan (self, coordenadas:tuple, objetivo:tuple) -> float:
        """
        Función que calcula la distancia Manhattan entre dos casillas
        Params:
            -self
            - coordenadas(tuple): coordenadas de la casilla en la que está
            - objetivo(tuple): coordenadas de la casilla a la que se quiere llegar
        Returns:
            - (float): valor de la distancia entre ambas casillas
        """
        # Coordenadas casilla actual
        x, y = coordenadas
        # Coordenadas casilla objetivo
        ox, oy = objetivo

        return abs(ox-x) + abs(oy-y)

    def calculo_heuristica (self, x:int, y:int) -> float:
        """
        Función que calcula la heurística de la casilla que se proporcionan las coordenadas.
        
        Si aún no está con ck -> se minimiza el riesgo.
        Si el agente ya está con ck -> se busca ir hacia la salida.
        
        Params:
            - x(int): coordenada x
            - y(int): coordenada y
        Returns:
            - (float): heurística de la casilla
        """

        if not self.ck:
            return self.riesgo_total(x, y)
        
        else:
            objetivo = self.max_probabilidad_salida()
            
            if objetivo is None:
                return self.riesgo_total(x, y)

            distancia_objetivo = self.distancia_manhattan((x,y), objetivo)
            ox, oy = objetivo
            prob_salida = self.salida[ox][oy]
            
            return distancia_objetivo * (1-prob_salida)


    def valorar_soldado (self):
        """
        Función que identifica si se ha encontrado la posición del soldado o no.
        Params:
            -self: agente
        Returns
            - None
        """
        self.posi_soldado = None
        
        for i in range(DIM_X):
            for j in range(DIM_Y):
                # Tomamos un valor que no sea muy estricto
                if self.soldado[i][j] > 0.9:
                    self.posi_soldado = (i, j)    

    def tirar_granada (self, palacio:Palace, x:int, y:int)->None:
        """
        Función cuya utilidad es lanzar la granada, puede ser un comando mandado por el agente o el usuario.
        Params:
            -self
            - palacio(Palace): entorno de juego
            - x(int): coordenada x a la que se tira
            - y(int): coordenada y a la que se tira la granada
        Returns:
            - None
        """

        sx, sy= self.posi_soldado
        px, py = self.ubicacion
        
        # Se comprueba que hayan granadas suficientes para realizar el tiro
        if self.granada>0:

            # En caso de que la distancia no sea uno
            if max(abs(x-px), abs(y-py)) !=1:
                print("La granada no ha dado al objetivo, demasiado lejos.")
                self.granada = 0
                return

            # En caso de que sí se haya dado al soldado
            if (x,y) == (sx,sy) and (sx,sy) is not None:
                print("Soldado muerto")
                self.granada = 0
                palacio.tablero[sx][sy].preceptos[9] = True
                for i in range (DIM_X):
                    for j in range(DIM_Y):
                        self.soldado[i][j] = 0.0
                self.posi_soldado = None
                return
             
            # En caso contrario
            else:
                print("Se ha fallado en el tiro")
                self.granada = 0
                return 
        else:
            print("No es posible lanzar la granada, no hay suficientes.")
            return


    def actualizar_frontera(self):
        """
        Función que recalcula la frontera del agente
        Params: 
            -self: agente
        Returns:
            -None
        """

        frontera = set()

        # Se filtran las casillas por los vecinos de los visitados que no hayan sido visitados
        for x, y in self.visitados:            
            movimientos = [(-1,0), (1,0), (0,-1), (0,1)]
            for mx, my in movimientos:
                vx, vy = x+mx, y+my
                if 0<= vx < DIM_X and 0<= vy < DIM_Y:
                    if (vx, vy) not in self.visitados:
                        frontera.add((vx,vy))
        
        self.frontera = frontera


    def actualizar_creencias (self, actual: casillas2, x:int, y:int)->None:
        """
        Función que evalúa las probabilidades de riesgos y modifica los 
        valores de las casillas vecinas a la actual.
        
        Params:
            - self: agente
            - actual(casillas2): habitacíon actual del palacio de juego
            - x(int): coordenada x de la casilla
            - y(int): coordenada y de la casilla
        
        Returns:
            - None
        """

        coord_vecinas = self.coger_coord_vecinas(actual, x, y)
        
        # A parte de a los vecinos, también se actualiza el valor de la propia casilla, pues si no recibe ningún precepto, 
        # significa que no contiene ninguna de las trampas y si lo recibe, hay que cambiar su probabilidad
        coord_vecinas.append((x,y))
        preceptos = {"fuego":0, "pinchos": 1, "dardos":2, "soldado":3, "salida":4}

        self.visitados.add((x,y))

        for precepto, indice_precepto in preceptos.items():

            # Se coge el atributo con la función getattr
            mapa = getattr(self, precepto)
            
            if not actual.preceptos[indice_precepto]:

                # En este caso, se pone la celda a 0, por el valor que toma el liklihood, 
                # que es 0 en caso de que no se perciba el estímulo en la celda
                
                for vx, vy in coord_vecinas:      
                    mapa[vx][vy] = 0.0            
            
            else:
                # Por el contrario, en caso de que sí que se perciba el estímulo, el likelihood es 1, 
                # y por lo tanto, hay que actualizar el valor de la casilla
                for i in range(DIM_X):
                    for j in range(DIM_Y):
                        # Solo actualizamos el valor de aquellas casillas cuyo likelihood es 0, 
                        # puesto que el prior de las casillas cuyo likelihood es 1 es el posterior sin normalizar, que se realizará a continuación.
                        if (i,j) not in coord_vecinas:                    
                            mapa[i][j] = 0.0
            
            
            # A continuación, se normalizan los valores del tablero:
            total = sum(sum(fila) for fila in mapa)

            if total>0:
                for i in range(DIM_X):
                    for j in range(DIM_Y):
                        mapa[i][j] /= total

    def greedy_explorar(self)->tuple:
        """
        Función que obtiene utilizando el algoritmo greedy, la mejor casilla a la que avanzar
        en función de la heurística.
        Params:
            - self: agente
        Returns:
            -(tuple): tupla con las coordenadas de la casilla con mejor heurística
        """
        
        # Se comienza por filtar los candidatos por el riesgo que el agente está dispuesto a 
        # asumir para elegir la siguiente casilla
        if not self.frontera:
            return None
        
        candidatos = []
        for x, y in self.frontera:
            riesgo = self.riesgo_total(x, y)
            if riesgo <= self.riesgo_asumido:
                candidatos.append((x,y))

        # En el caso de que no haya un riesgo lo suficientemente pequeño como para que lo asuma el agente...
        if not candidatos:
            return None
                
        mejor_casilla = None
        mejor_heuristica = float("inf")

        for x, y in candidatos:
            heuristica = self.calculo_heuristica(x, y)

            if heuristica< mejor_heuristica:
                mejor_heuristica = heuristica
                mejor_casilla = (x,y)

        return mejor_casilla

    def greedy_salida(self)->tuple:
        """
        Función que obtiene utilizando el algoritmo greedy, la mejor casilla a la que avanzar, para volver a la salida
        en función de la heurística.
        Params:
            - self: agente
        Returns:
            -(tuple): tupla con las coordenadas de la casilla con mejor heurística
        """

        objetivo = self.max_probabilidad_salida()
        if objetivo is None:
            return None
        
        px, py = self.ubicacion
        dist_actual = self.distancia_manhattan((px,py), objetivo)

        candidatos = []
        for x, y in self.frontera:
            
            if (x,y) in self.bloqueadas:
                continue

            riesgo = self.riesgo_total(x, y)
            if riesgo > self.riesgo_asumido:
                continue
            
            if self.distancia_manhattan((x,y), objetivo) < dist_actual:
                candidatos.append((x,y))

        # En el caso de que no haya un riesgo lo suficientemente pequeño como para que lo asuma el agente...
        if not candidatos:
            return None
                
        mejor_casilla = None
        mejor_distancia = float("inf")

        for casilla in candidatos:
            distancia = self.distancia_manhattan(casilla, objetivo)

            if distancia< mejor_distancia:
                mejor_distancia = distancia
                mejor_casilla = casilla

        return mejor_casilla

    def greedy(self):
        """
        Función que lleva a calcular dos tipos distntos de greedy, dependiendo de si se ha encontrado
        al coronel o no.
        Params:
            - self
        Returns:
            - (tuple): tupla que contiene las coordenadas de la casilla objetivo en el momento.
        """

        if not self.ck:
            return self.greedy_explorar()
        return self.greedy_salida()


def mostrar_heatmap_color(mapa, titulo):
    
    plt.figure(figsize=(5,5))
    plt.imshow(mapa, cmap="viridis", interpolation="nearest")
    plt.colorbar(label="Probabilidad")
    plt.title(titulo)
    plt.show()

def mostrar_tableros (CW:Capitan_Willard):
    
    print("Mapas de probabilidades... ")

    riesgo = np.array([[CW.riesgo_total(i,j) for j in range(DIM_Y)]for i in range(DIM_X)])
    mostrar_heatmap_color(riesgo, "Riesgo total")
    mostrar_heatmap_color(CW.soldado, "Probabilidad de soldado")
    mostrar_heatmap_color(CW.salida, "Probabilidad de salida")

def hay_riesgo(celda:list)->bool:
    """
    Función que determina si en esa celda hay riesgo o no.
    Params:
        - celdas(list): lista de contenido de la celda
    Returns:
        -(bool): booleano que asigna si hay riesgo o no.
    """

    for elem in celda:
        for riesgo in RIESGOS:
            if elem == riesgo:
                return True
    return False



def busqueda_logica(CW: Capitan_Willard, palacio: Palace):
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
        
        # Se comprueba que no esté en una casilla "especial"
        if hay_riesgo(palacio.tablero[px][py].casilla):
            print("Agente muerto!")
            break

        if CORONEL_KURTZ in palacio.tablero[px][py].casilla and not CW.ck:
            CW.ck = True
            print("Se ha encontrado al Coronel Kurtz!!")
        
        if SALIDA in palacio.tablero[px][py].casilla:
            print("salida encontrada")

        # ACtualización lógica bayesiana
        CW.actualizar_creencias(palacio.tablero[px][py], px, py)
        CW.actualizar_frontera()
        CW.valorar_soldado()

        mostrar_tableros(CW)

        # Lanzar granada
        if CW.posi_soldado:
            sx, sy = CW.posi_soldado
            if max(abs(sx-px),abs(sy-py)) == 1:
                CW.tirar_granada(palacio, sx, sy)

        # Si se cumplen las condiciones de finalización
        if SALIDA in palacio.tablero[px][py].casilla and CW.ck:
            CW.final = True
            print("El agente ha logrado su objetivo, ha salido con el Coronel Kurtz")
            break
        

        ## Observo hacia donde avanzar:
        siguiente_habitacion = CW.greedy()

        if siguiente_habitacion is None:
            if CW.camino: 
                if CW.ck:
                    CW.bloqueadas.add(CW.ubicacion)
                CW.ubicacion = CW.camino.pop()
                print("No hay nuevas casillas en la frontera, retrocediendo a: ", CW.ubicacion)
                continue
            else:
                print("La frontera está vacía y no es posible retroceder.")
                break

        # Se avanza a la siguiente casilla
        CW.camino.append(CW.ubicacion)
        CW.ubicacion = siguiente_habitacion

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

def busqueda_usuario(CW:Capitan_Willard, palacio:Palace):
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
        
        # Comprueban casillas especiales
        if hay_riesgo(palacio.tablero[px][py].casilla):
            print("☠️ --- Ha muerto --- ☠️")
            print("Se acaba la aprtida...")
            break
        
        if CORONEL_KURTZ in palacio.tablero[px][py].casilla:
            CW.ck = True
            print("Se ha encontrado al Coronel Kurtz!!")

        # Actualiza conocimientos
        CW.actualizar_creencias(palacio.tablero[px][py], px, py)
        CW.actualizar_frontera()
        CW.valorar_soldado()

        mostrar_tableros(CW)

        # Soldado lanzar granada
        if CW.posi_soldado is not None:
            sx, sy = CW.posi_soldado
            print("SOLDADO ENCONTRADO!")
            print(f"Usted se encuentra en la casilla ({px}, {py}) y el soldado en la casilla ({sx}, {sy})")
            while True:
                bomba = input("¿Quieres lanzarle la bomba? (SI/NO): ")
                
                if bomba == "SI": 
                    
                    coordenadas = input("¿A qué casilla contigua a su ubicación quiere tirar la granada")
                    x, y = limpiar_coordenadas(coordenadas)                    
                    CW.tirar_granada(palacio, x, y)
                    print("AAAAA")
                    print("💣BUM💣")
                    mostrar_tableros(CW)
                    break

                elif bomba == "NO":
                    print("No se ataca al soldado...")
                    break
                else:
                    print("Respuesta no válida. Escriba SI o NO")

        if SALIDA in palacio.tablero[px][py].casilla and CW.ck:
            CW.final = True
            print("El agente ha logrado su objetivo, ha salido con el Coronel Kurtz")
            break
                                         
        print("Frontera: ")
        for i, j in CW.frontera:
            print(f"({i}, {j})")

        print("Camino recorrido: ")
        print(CW.camino)
        
        ## Observo hacia donde avanzar:
        siguiente_habitacion = CW.greedy()
        if siguiente_habitacion is not None:
            print(f"Se recomiendo avanzar hacia: {siguiente_habitacion}")
        else:
            print(f"Frontera vacía, no es posible continuar, pero se puede retroceder a {CW.camino[-1]} o finalizar el juego.")


        while True:
            coordenadas = input("Elija a que casilla se quiere desplazar (x,y) o acabar la partida (S): ")
            if coordenadas.strip().upper() == "S":
                print("Saliendo de la partida...")
                return
            else:
                coordenadas=limpiar_coordenadas(coordenadas)
                if coordenadas is None:
                    print("Formato no válido, use (x,y) o S")
                    continue
                else:
                    break
        
        CW.ubicacion = coordenadas
        CW.camino.append(CW.ubicacion)
        
        
 