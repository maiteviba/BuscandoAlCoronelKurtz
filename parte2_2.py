import random

VACIA = "|   |"
SEGURA = "| R |"
ISLA = "| I |"
ORILLA_FINAL ="| E |"
POSICION = "|CWCK|"

acciones = {"up": (-1,0), "down":(1,0), 
            "left":(0,-1), "right":(0,1)}
DIMX = 7
DIMY = 6

class Entorno():

    def __init__(self, tablero:list[list], inicio:tuple, salida:tuple, islas:list, corriente: dict):
        
        self.tablero = tablero
        self.inicio = inicio
        self.salida = salida
        self.islas = set(islas)
        self.corriente = corriente       
    
class Agente():

    def __init__(self, inicio:tuple, entorno, politica):
        
        self.estado = inicio
        self.entorno = entorno
        self.politica = politica
        self.terminado = False

    def elegir_siguiente(self, transiciones:list):
        """
        Función que elige de forma aleatoria el sigiuente estado utilizando muestreo aleatorio.
        Params:
            - self
            - transiciones(list): lista de los posibles estados siguientes con su probabilidad ascociada
        Returns:
            - (tuple): siguiente esatdo
        """

        r = random.random()
        acum = 0.0

        for p, s2 in transiciones:
            acum += p
            if r <= acum:
                return s2
        
        return transiciones[-1][1]

    def simular_partida(self, max_pasos=200):
        """ 
        Función que simula una partida completa del agente siguiendo una política fija dentro del entorno
        hasta alcanzar la casilla final o por el contrario superar el número máximo de pasos impuesto.
        Params:
            - self
            - max_pasos(int): número máximo de pasos a realizar
        Returns:
            - (tuple): (trayectoria seguida, 
                        secuencia de acciones realizadas,
                        recompensa final obtenida,
                        cantidad de acciones realizadas,
                        booleano que indica si el estado final es terminal o no)
        
            """

        entorno = self.entorno
        estado = self.estado
        trayectoria = [estado]
        acciones = []
        recompensa_total = 0

        for _ in range(max_pasos):

            if es_terminal(estado, entorno):
                break

            accion = self.politica[estado]
            if accion is None:
                break

            trans = transicion(estado, accion, entorno)
            siguiente = self.elegir_siguiente(trans)
            r = recompensas(estado, siguiente, accion, entorno)

            recompensa_total+=r
            acciones.append(accion)
            trayectoria.append(siguiente)

            estado = siguiente
        
        return (trayectoria, acciones, recompensa_total, len(acciones), es_terminal(estado, entorno))



        
def transicion(estado:tuple, accion: str, entorno:Entorno)->list:
    """
    Función que devuelve una lista de las probabilidades y las coordenadas de la dirección a las que se le asocia
    Params:
        - estado(tuple): lugar en el que se encuentra el agente
        - accion(str): accion que va a tomar el agente
        - entorno(Entorno): entorno en el que trabaja
    Returns:
        - (list): lista de todas las posibilidades asociada a sus probabilidades
    """
    if es_terminal(estado, entorno):
        return [(1.0, estado)]
    
    x, y = estado
    acx, acy = acciones[accion]

    # Hacia abajo:
    abx, aby = acciones["down"]


    movimientos = []

    p_Down = entorno.corriente[y]

    # Movimiento que se quiere hacer
    mx, my = x+acx, y+acy
    if not (0<= mx <DIMX and 0<= my <DIMY) or (mx, my) in entorno.islas:
        return [(1.0, (x,y))]

    # En caso de que empuje la corriente hacia abajo
    bx, by = x+abx, y+aby
    if not (0<= bx <DIMX and 0<= by <DIMY) or (bx, by) in entorno.islas:
        bx, by = x, y
    
    if accion == "down":
        movimientos.append((1.0, (mx, my)))
    else:
        movimientos.append((p_Down, (bx, by)))
        movimientos.append((1-p_Down, (mx, my)))
    
    return movimientos

def recompensas(s:tuple, s2:tuple, a:str, entorno:Entorno)->int:
    """
    Función que calcula la recompensa de la acción realizada
    R(s, a, s').
    Params:
        - s(tuple): estado en el que se encuentra
        - s2(tuple): estado al que se dirige del cual se quiere saber la recompensa
        - a(str): acción que realiza
        - entorno(Entorono): espacio sobre el que trabaja el agente
    Returns:
        - (int): valor de la recompensa
    """

    if s2 == entorno.salida:
        return 100
    elif s2 in entorno.islas:
        return -100
    else:
        return -1

def es_terminal(estado:tuple, entorno: Entorno)->bool:
    """
    Función que devuelve un booleano en función de si
    el estado que analiza es un estado terminal o no.
    Params:
        - estado(tuple): estado que hay que estudiar
        - entorno(Entorno): entorno sobre el que se trabaja
    Returns:
        - (bool): especificando si se trata de un estado terminal ono 
    """
    if estado == entorno.salida or estado in entorno.islas:
        return True    
    return False

def value_iteration(entorno, gamma=0.9, epsilon=1e-4):
    """
    Obtiene la política óptima y el valor esperado
    Params:
        - gamma(float)
        - epsilon(float): valor de convergencia
        - entorno(Entorno)
    Returns:
        - V(dict): diccionario de valores esperados
        - politica(dict): diccionario con la política de movimiento
    """

    estados = [(i,j) for i in range(DIMX) for j in range(DIMY)]
    # Valor de la función de tomar la acción
    V = {}
    # Mejor política a seguir en cada casilla
    politica = {}
    for estado in estados:        
        V[estado] = 0.0
        politica[estado] = None

    while True:
        delta = 0.0

        # Se recorren todos los estados
        for s in estados:

            # En caso de que se trate de un estado terminal, su mejor política es no moverse
            if es_terminal(s, entorno):
                politica[s] = None
                continue
        
            mejor_val = -float("inf")
            accion_mejor = None

            # Se exploran todas las acciones que se pueden realizar
            for a in list(acciones.keys()):
                q = 0.0
                # Se estudian las transiciones, la recompensa final que aporta condicionado por su probabilidad y el factor gamma
                for p, s2 in transicion(s, a, entorno):
                    r = recompensas(s, s2, a, entorno)
                    q += p*(r+gamma * V[s2])
                
                # En caso de que sea la acción con mayor recompensa, se almacena
                if q > mejor_val:
                    mejor_val = q
                    accion_mejor = a
            
            # Se actualizan los valores
            delta = max(delta, abs(mejor_val- V[s]))
            V[s] = mejor_val
            politica[s] = accion_mejor

        # Utilizamos delta como condición de parada, siendo delta la cantidad que cambia el valor desde su mejor valor al actual
        # En caso de que este sea menor que epsilon (un valor muy pequeño), significa que apenas hay cambio y que por lo tanto, se ha encontrado el camino óptimo.
        # Condición de parada por convergencia
        if delta < epsilon:
            break
    
    return V, politica
    

    
    