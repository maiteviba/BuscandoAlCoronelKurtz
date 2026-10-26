
## Se inicializan las variables globales de obstáculos ##
EMPTY_ROOM = "."
SOLDADO = "M"
EXIT = "E"
PRECIPICIO = "P"
CORONEL_KURTZ = "CK"
COORDENADAS_INICIALES = (0,0)

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
      
      
      # Qué contiene la habitación
      self.casilla = Room

      # Aspecto para visualizar
      self.aspecto = EMPTY_ROOM
    
    def __str__(self) :
        return self.aspecto

class Creencias_Room:

    def __init__(self, visitada:bool, segura:bool, 
                 posible_precipicio:bool, posible_soldado:bool, posible_salida:bool):
        
        self.visitada = visitada
        self.segura = segura #Si se sabe que no hay un precipicio o salodado en esa casilla.
        
        self.posible_precipicio = posible_precipicio
        self.posible_soldado = posible_soldado
        self.posible_salida = posible_salida
        
        self.aspecto = "."

    def __str__(self) :
        return self.aspecto                  