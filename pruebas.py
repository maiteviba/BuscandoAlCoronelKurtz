import random

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


class Palace:

    def __init__(self, tablero:list):      
      self.tablero=tablero

    def __str__(self):
        
        salida=""
        for fila in self.tablero:
           salida+= " ".join(str(room) for room in fila) + "\n"
        return salida

class Rooms:

    def __init__(self, Room:str):
      
      # Perceptos
      self.brisa = False
      self.ronquido = False
      self.resplandor = False
      
      # Paredes
      self.arriba = False
      self.abajo = False
      self.derecha = False
      self.izquierda = False
      
      self.grito = False

      # Qué contiene la habitación
      self.casilla = Room

      # Aspecto para mostrar
      self.aspecto = EMPTY_ROOM
    
    def __str__(self) :
        return self.aspecto

class Creencias_Room:

    def __init__(self, visitada:bool, segura:bool, 
                 posible_precipicio:bool, posible_soldado:bool, posible_salida:bool, 
                 descartada:bool):
        
        self.visitada = visitada
        self.segura = segura #Si se sabe que no hay un precipicio o salodado en esa casilla.
        
        self.posible_precipicio = posible_precipicio
        self.posible_soldado = posible_soldado
        self.posible_salida = posible_salida

        self.descartada = descartada
        
        self.aspecto = "."

    def __str__(self) :
        return self.aspecto

class Capitan_Willard:

    def __init__ (self, ubicacion:tuple, tablero:list[list[Creencias_Room]]):

        self.tablero = tablero
        
        self.ubicacion = ubicacion
        self.visitados = []
        
        self.ck = False # Indica si el Capitán Willard está o no con el Coronel 
        self.granada = 1 # Cantidad de granadas que tiene el Capitán
        self.soldado_muerto = False

    def __str__(self):
        
        salida=""
        for fila in self.tablero:
           salida+= " ".join(str(room) for room in fila) + "\n"
        return salida
    
    def coger_coord_vecinas (self, casilla_actual:Rooms, coord_x:int, coord_y:int) ->list:

        coordenadas_vecinas = []

        if not casilla_actual.arriba:
            coordenadas_vecinas.append((coord_x-1, coord_y))
        if not casilla_actual.abajo:
            coordenadas_vecinas.append((coord_x+1, coord_y))
        if not casilla_actual.izquierda:
            coordenadas_vecinas.append((coord_x, coord_y-1))
        if not casilla_actual.derecha:
            coordenadas_vecinas.append((coord_x, coord_y+1))

        return coordenadas_vecinas

    def actualizar_casillas (self, casilla_actual:Rooms):

        coord_x, coord_y = self.ubicacion

        ## Se actualiza la casilla sobre la que estamos

        # Tengo que hacerlo en algún momento pero no estoy segura de cuando
        # self.tablero[coord_x][coord_y].aspecto = "CW" 
        
        self.tablero[coord_x][coord_y].visitada = True
        self.tablero[coord_x][coord_y].segura = True
        self.tablero[coord_x][coord_y].posible_soldado = False
        self.tablero[coord_x][coord_y].posible_precipicio = False

        self.visitados.append((coord_x,coord_y))

        if casilla_actual.casilla == CORONEL_KURTZ:
            self.ck = True

        coordenadas_vecinas = self.coger_coord_vecinas(casilla_actual, coord_x, coord_y)
        
        # Se filtran los vecinos que no hayan sido visitados y que no sean seguros (evitando sobreescrituras)
        vecinos = [self.tablero[x][y] for x, y in coordenadas_vecinas 
                   if not self.tablero[x][y].visitada]
                    

        # Actualización debido a ausencia de los preceptos
        if not casilla_actual.brisa:
            for vecino in vecinos:
                vecino.posible_precipicio = False
                vecino.aspecto ="."

        if not casilla_actual.ronquido:
            for vecino in vecinos:
                vecino.posible_soldado = False
                vecino.aspecto ="."
        
        if not casilla_actual.brisa and not casilla_actual.ronquido:
            for vecino in vecinos:
                vecino.segura = True
                vecino.posible_soldado = False
                vecino.posible_precipicio = False
                vecino.aspecto ="."
        

        # Actualización por presencia de los preceptos, 
            # además, ha de cumplir que el vecino no se sepa aún que es una celda segura
        if casilla_actual.brisa:
            for vecino in vecinos:
                vecino.posible_precipicio = True
                vecino.aspecto ="P?"

        if casilla_actual.ronquido:
            for vecino in vecinos:
                vecino.posible_soldado = True
                vecino.aspecto ="M?"
    
        # En caso de que haya resplandor, se puede decir que puede estar cerca de la salida
        if casilla_actual.resplandor:
            for vecino in vecinos:
                vecino.posible_salida = True
                vecino.aspecto ="E?"

    def deduccion_precipicio(self, palacio_completo:Palace):
        
        visitadas = self.visitados

        for x, y in visitadas:            
            casilla = palacio_completo.tablero[x][y]
            vecinos = self.coger_coord_vecinas(casilla, x, y)
            
            if casilla.brisa:
                vecinos = [self.tablero[i][j] for i,j in vecinos 
                   if not self.tablero[i][j].visitada and self.tablero[i][j].posible_precipicio]
                
                if len(vecinos)==1:
                    vecinos[0].aspecto = "P!"

    def deduccion_soldado (self, palacio_completo:Palace):

        visitadas = self.visitados

        for x, y in visitadas:            
            casilla = palacio_completo.tablero[x][y]
            vecinos = self.coger_coord_vecinas(casilla, x, y)
            
            if casilla.ronquido:
                vecinos = [self.tablero[i][j] for i,j in vecinos 
                   if not self.tablero[i][j].visitada and self.tablero[i][j].posible_soldado]
                
                if len(vecinos)==1:
                    vecinos[0].aspecto = "S!"



            


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
    palace[0][1] = "P"
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

    tablero = [[None for i in range(DIM_Y)] for j in range(DIM_X)]

    for i in range(DIM_X):
      for j in range(DIM_Y):
        
        room = Creencias_Room(False, False, True, True, False, False)
        tablero[i][j] = room
        
    return Capitan_Willard(COORDENADAS_INICIALES, tablero)



if __name__ == "__main__":
   
    # palace = Initialize_Palace()
    palace = [['.', '.', 'M', '.', '.', '.'], ['.', '.','.','.','.','.'], ['.','.','.','E','P', '.'],
              ['.','.','.','.','P','.'], ['.','CK','.','P','.','.'], ['.','.','.','.','.','.']]
    palace = Create_Palace(palace)

    CW = Create_Agente()

    CW.actualizar_casillas(palace.tablero[0][0])
    print(palace)
    print(CW.tablero[0][1].posible_precipicio)
    

    CW.ubicacion = (0,1)
    CW.actualizar_casillas(palace.tablero[0][1])
    print(CW.tablero[0][2].posible_soldado)
    print(CW.tablero[0][0].posible_soldado)
    print(CW.tablero[0][1].posible_soldado)
    print(CW.tablero[1][1].posible_soldado)
    print("\n")
    CW.ubicacion = (1,0)
    CW.actualizar_casillas(palace.tablero[1][0])
    print(CW.tablero[1][0].posible_soldado)
    print(CW.tablero[2][0].posible_soldado)
    print(CW.tablero[0][0].posible_soldado)
    print(CW.tablero[1][1].posible_soldado)
    print("\n")
    CW.ubicacion = (1,1)
    CW.actualizar_casillas(palace.tablero[1][1])
    print(CW.tablero[0][1].posible_soldado)
    print(CW.tablero[1][0].posible_soldado)
    print(CW.tablero[1][2].posible_soldado)
    print(CW.tablero[2][1].posible_soldado)
    print("\n")
    CW.ubicacion = (1,2)
    CW.actualizar_casillas(palace.tablero[1][2])
    print(CW.tablero[0][2].posible_soldado)
    print(CW.tablero[1][1].posible_soldado)
    print(CW.tablero[1][3].posible_soldado)
    print(CW.tablero[2][2].posible_soldado)
    print("\n")