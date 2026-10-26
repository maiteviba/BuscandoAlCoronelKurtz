from entorno import Palace, Rooms, Creencias_Room

## Se inicializan las variables globales de obstáculos ##
EXIT = "E"
CORONEL_KURTZ = "CK"

## Dimensiones del palacio ##
DIM_X = 6
DIM_Y = 6


class Capitan_Willard:

    def __init__ (self, ubicacion:tuple, tablero:list[list[Creencias_Room]]):

        self.tablero = tablero
        
        self.ubicacion = ubicacion
        self.visitados = set()
        self.frontera = set()

        self.precipicios = set() # Variable que contabiliza la cantidad de precipicios encontrados
        
        self.ck = False # Indica si el Capitán Willard está o no con el Coronel 
        
        self.granada = 1 # Cantidad de granadas que tiene el Capitán
        self.soldado = None
        self.soldado_muerto = False
        
        self.final = False
        self.salida = None

    def __str__(self):
        
        salida=""
        for fila in self.tablero:
           salida+= " ".join(str(room) for room in fila) + "\n"
        return salida
    
    
    def vecinos_seguros(self, x:int, y:int)->list:
        """
        Función que retorna una lista de coordenadas de los vecios seguros de la habitación actual
        
        Params:
            - self
            - x (int): coordenada x de la casilla
            - y(int); coordenada y de la casilla
            - palacio (Palace): tablero de juego
        Returns:
            - (list): lista de coordenadas vecinas segura
        """

        seguros = []
        movimientos = [(-1,0), (1,0), (0,-1), (0,1)]

        for mx, my in movimientos:
            vx, vy = x+mx, y+my
            if 0<= vx < DIM_X and 0<= vy < DIM_Y:
                if self.tablero[vx][vy].segura:
                    seguros.append((vx,vy))

        return seguros
    
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
                if not self.tablero[vx][vy].visitada:
                    vecinos.append((vx,vy))
        return vecinos

    def coger_coord_vecinas (self, casilla_actual:Rooms, coord_x:int, coord_y:int) ->list:
        """
        Función que guarda y retorna las coordenadas de las casillas adyacentes a la dada. 
        Args:
            casilla_actual(Rooms): habitación de la que se buscan las vecinas
            coord_x (int)
            coord_y (int)
        
        Returns:
            coordenadas_vecians (list): lista de coordenadas vecinas
        """
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

    def actualizar_casillas (self, casilla_actual:Rooms)->None:
        """
        Función que actualiza las creencias del agente en base a lo que se sabe de la actual. 
        Args:
            casilla_actual(Rooms): habitación de la que se buscan las vecinas
       
        Returns:
            None
        """

        coord_x, coord_y = self.ubicacion

        ## Se actualiza la casilla sobre la que estamos
        habitacion = self.tablero[coord_x][coord_y]
        
        habitacion.visitada = True
        habitacion.segura = True
        habitacion.posible_soldado = False
        habitacion.posible_precipicio = False
        
        
        # Se guardan las coordenadas de las casillas visitadas y se saca de frontera
        self.visitados.add((coord_x,coord_y))
        self.frontera.discard((coord_x,coord_y))


        if casilla_actual.casilla == CORONEL_KURTZ:
            self.ck = True
        if casilla_actual.casilla == EXIT:
            self.salida = (coord_x, coord_y)

        coordenadas_vecinas = self.coger_coord_vecinas(casilla_actual, coord_x, coord_y)
        
        # Se filtran los vecinos que no hayan sido visitados y que no sean seguros (evitando sobreescrituras)
        vecinos = [self.tablero[x][y] for x, y in coordenadas_vecinas 
                   if not self.tablero[x][y].visitada]
                            

        # Actualización debido a ausencia de los preceptos
        if not casilla_actual.brisa:
            for vecino in vecinos:
                vecino.posible_precipicio = False
                
        if not casilla_actual.ronquido:
            for vecino in vecinos:
                vecino.posible_soldado = False
                        
        if not casilla_actual.brisa and not casilla_actual.ronquido:
            for vecino in vecinos:
                vecino.segura = True
                            
        # En caso de que haya resplandor, se puede decir que puede estar cerca de la salida
        if casilla_actual.resplandor:
            for vecino in vecinos:
                vecino.posible_salida = True
                               
    def actualizar_frontera(self):

        for x, y in self.visitados:
            vecinos = []
            movimientos = [(-1,0), (1,0), (0,-1), (0,1)]
            for mx, my in movimientos:
                vx, vy = x+mx, y+my
                if 0<= vx < DIM_X and 0<= vy < DIM_Y:
                    if self.tablero[vx][vy].segura:
                        vecinos.append((vx,vy))

            for vx, vy in vecinos:
                vecino = self.tablero[vx][vy]
                if not vecino.visitada:
                    self.frontera.add((vx,vy))

    def deduccion_precipicio(self, palacio_completo:Palace)->None:
        """
        Función que deduce la posición de los precipicios en función del conocimiento sobre el entorno. 
        Args:
            palacio_compelto (Palace): palacio del juego con toda su información
       
        Returns:
            None
        """

        conjuntos_brisa = []

        visitadas = self.visitados

        # Se estudian paso a paso las casillas vecinas de las celdas visitadas
        for x, y in visitadas:        

            posibles = []
            no_visitados = self.vecinos_no_visitados(x,y)

            for vx,vy in no_visitados:
                if self.tablero[vx][vy].posible_precipicio:
                    posibles.append((vx,vy))

            if len(posibles)>0:
                conjuntos_brisa.append(set(posibles))
            
            if len(conjuntos_brisa)<2:
                return
            
            interseccion = set.intersection(*conjuntos_brisa)

            if len(interseccion) == 1:
                px,py = interseccion.pop()
                self.tablero[px][py].aspecto = "P!"
                self.tablero[px][py].segura = False
                self.tablero[px][py].posible_precipicio = False
                self.precipicios.add((px,py))
                      
    def deduccion_soldado (self, palacio_completo:Palace)->bool:
        """
        Función que deduce la posición del soldado en función del conocimiento sobre el entorno. 
        Args:
            palacio_compelto (Palace): palacio del juego con toda su información
       
        Returns:
            None
        """

        visitadas = self.visitados
        
        # Se estudian paso a paso las casillas vecinas de las celdas visitadas
        for x, y in visitadas:            
            casilla = palacio_completo.tablero[x][y]
            vecinos = self.coger_coord_vecinas(casilla, x, y)
            
            # En caso de que la casilla vecina tenga el precepto de ronquido
            if casilla.ronquido:
                
                # Se seleccionan los vecinos que no hayan sido visitados, que no contengan soldados.
                vecinos = [(self.tablero[i][j], i, j) for i,j in vecinos 
                   if not self.tablero[i][j].visitada 
                   and self.tablero[i][j].posible_soldado]
                
                # En caso de que sólamente uno de los vecinos pueda contener un soldado significa que seguramente lo sea
                if len(vecinos)==1:
                    vecinos[0][0].aspecto = "S!"
                    vecinos[0][0].segura = False

                    self.soldado = (vecinos[0][1], vecinos[0][2])


                    # Debido a que hay un único soldado, significa que el resto no lo serán y
                    # por lo tanto se actualiza el conocimiento del resto del entorno
                    for fila in self.tablero:
                        for celda in fila:
                            if celda is not vecinos[0][0]:
                                celda.posible_soldado=False
                    
                    return True
        return False
    