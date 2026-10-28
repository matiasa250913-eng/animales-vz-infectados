import random
import sys
import pygame

# Animales vs Infectados — versión reorganizada y mejorada
# Instala Pygame con: pip install pygame

pygame.init()
pygame.display.set_caption("Animales vs Infectados")

INFO = pygame.display.Info()
ANCHO = INFO.current_w if INFO.current_w > 0 else 900
ALTO = INFO.current_h if INFO.current_h > 0 else 600
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
reloj = pygame.time.Clock()

FILAS, COLUMNAS = 3, 7
TAM_CASILLA = max(44, min(int(ALTO * 0.16), int(ANCHO * 0.105)))
INICIO_X = int(ANCHO * 0.08)
INICIO_Y = int(ALTO * 0.32)
ANCHO_TABLERO = COLUMNAS * TAM_CASILLA
ALTO_TABLERO = FILAS * TAM_CASILLA

# Colores
PASTO = (34, 139, 34)
PASTO_OSCURO = (0, 100, 0)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (70, 130, 180)
AZUL_CLARO = (135, 206, 235)
AMARILLO = (218, 165, 32)
ROJO = (220, 45, 45)
GRIS = (75, 80, 88)
VERDE = (70, 180, 90)

fuente = pygame.font.Font(None, max(24, int(ALTO * 0.045)))
fuente_grande = pygame.font.Font(None, max(36, int(ALTO * 0.075)))
fuente_pequena = pygame.font.Font(None, max(20, int(ALTO * 0.032)))


def texto(superficie, mensaje, tipografia, color, posicion, centrado=False):
    imagen = tipografia.render(str(mensaje), True, color)
    rect = imagen.get_rect()
    if centrado:
        rect.center = posicion
    else:
        rect.topleft = posicion
    superficie.blit(imagen, rect)


def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))


class Unidad:
    def __init__(self, fila, columna, tipo):
        self.fila = fila
        self.columna = columna
        self.tipo = tipo
        self.x = INICIO_X + columna * TAM_CASILLA + TAM_CASILLA // 2
        self.y = INICIO_Y + fila * TAM_CASILLA + TAM_CASILLA // 2
        self.ultimo = pygame.time.get_ticks()
        self.vida = 100

    def dibujar(self, superficie):
        color = AZUL if self.tipo == "Cientifico" else VERDE
        radio = int(TAM_CASILLA * 0.31)
        pygame.draw.circle(superficie, color, (int(self.x), int(self.y)), radio)
        letra = "C" if self.tipo == "Cientifico" else "D"
        texto(superficie, letra, fuente, BLANCO, (self.x, self.y), centrado=True)


class Infectado:
    def __init__(self, fila):
        self.fila = fila
        self.x = ANCHO + TAM_CASILLA
        self.y = INICIO_Y + fila * TAM_CASILLA + TAM_CASILLA // 2
        self.velocidad = max(18, TAM_CASILLA * 0.42)
        self.vida = 60
        self.ultimo_movimiento = pygame.time.get_ticks()

    def actualizar(self, dt):
        self.x -= self.velocidad * dt

    def dibujar(self, superficie):
        radio = int(TAM_CASILLA * 0.29)
        pygame.draw.circle(superficie, ROJO, (int(self.x), int(self.y)), radio)
        texto(superficie, "I", fuente, BLANCO, (self.x, self.y), centrado=True)


class Proyectil:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidad = TAM_CASILLA * 5.0
        self.daño = 20
        self.radio = max(4, int(TAM_CASILLA * 0.07))

    def actualizar(self, dt):
        self.x += self.velocidad * dt

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, AZUL_CLARO, (int(self.x), int(self.y)), self.radio)


class Moneda:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.creada = pygame.time.get_ticks()
        self.rect = pygame.Rect(
            int(x - TAM_CASILLA * 0.18),
            int(y - TAM_CASILLA * 0.18),
            int(TAM_CASILLA * 0.36),
            int(TAM_CASILLA * 0.36),
        )

    def dibujar(self, superficie):
        pygame.draw.circle(
            superficie, AMARILLO, (int(self.x), int(self.y)),
            max(7, int(TAM_CASILLA * 0.17))
        )
        texto(superficie, "$", fuente_pequena, NEGRO, (self.x, self.y), centrado=True)


def reiniciar():
    return {
        "dinero": 150,
        "tipo_seleccionado": None,
        "unidades": [],
        "infectados": [],
        "proyectiles": [],
        "monedas": [],
        "ultimo_spawn": pygame.time.get_ticks(),
        "jugando": True,
        "resultado": None,
    }


estado = reiniciar()


def celda_desde_posicion(pos):
    mx, my = pos
    if not (INICIO_X <= mx < INICIO_X + ANCHO_TABLERO and
            INICIO_Y <= my < INICIO_Y + ALTO_TABLERO):
        return None
    columna = (mx - INICIO_X) // TAM_CASILLA
    fila = (my - INICIO_Y) // TAM_CASILLA
    return int(fila), int(columna)


def dibujar_tablero(superficie):
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            x = INICIO_X + columna * TAM_CASILLA
            y = INICIO_Y + fila * TAM_CASILLA
            color = PASTO if (fila + columna) % 2 == 0 else PASTO_OSCURO
            pygame.draw.rect(superficie, color, (x, y, TAM_CASILLA, TAM_CASILLA))
            pygame.draw.rect(superficie, (20, 70, 25), (x, y, TAM_CASILLA, TAM_CASILLA), 1)


def dibujar_interfaz(superficie, juego):
    texto(superficie, "ANIMALES VS INFECTADOS", fuente_grande, BLANCO,
          (ANCHO // 2, int(ALTO * 0.08)), centrado=True)
    texto(superficie, f"Fondos: ${juego['dinero']}", fuente, BLANCO,
          (INICIO_X, int(ALTO * 0.19)))

    ancho_boton = int(ANCHO * 0.23)
    alto_boton = max(44, int(ALTO * 0.09))
    y_boton = int(ALTO * 0.19)
    boton_c = pygame.Rect(int(ANCHO * 0.48), y_boton, ancho_boton, alto_boton)
    boton_d = pygame.Rect(int(ANCHO * 0.73), y_boton, ancho_boton, alto_boton)

    color_c = AZUL if juego["tipo_seleccionado"] != "Cientifico" else (35, 85, 150)
    color_d = VERDE if juego["tipo_seleccionado"] != "Defensor" else (25, 120, 45)
    pygame.draw.rect(superficie, color_c, boton_c, border_radius=10)
    pygame.draw.rect(superficie, color_d, boton_d, border_radius=10)
    texto(superficie, "Científico $50", fuente_pequena, BLANCO,
          boton_c.center, centrado=True)
    texto(superficie, "Defensor $100", fuente_pequena, BLANCO,
          boton_d.center, centrado=True)
    return boton_c, boton_d


def actualizar(juego, dt):
    ahora = pygame.time.get_ticks()

    # Los científicos generan monedas; los defensores disparan a los infectados de su fila.
    for unidad in juego["unidades"]:
        if unidad.tipo == "Cientifico" and ahora - unidad.ultimo >= 5000:
            juego["monedas"].append(Moneda(unidad.x, unidad.y - TAM_CASILLA * 0.28))
            unidad.ultimo = ahora
        elif unidad.tipo == "Defensor" and ahora - unidad.ultimo >= 1100:
            if any(i.fila == unidad.fila and i.x > unidad.x for i in juego["infectados"]):
                juego["proyectiles"].append(
                    Proyectil(unidad.x + TAM_CASILLA * 0.25, unidad.y)
                )
                unidad.ultimo = ahora

    if ahora - juego["ultimo_spawn"] >= 4000:
        juego["infectados"].append(Infectado(random.randrange(FILAS)))
        juego["ultimo_spawn"] = ahora

    for infectado in juego["infectados"]:
        infectado.actualizar(dt)
        if infectado.x < INICIO_X:
            juego["resultado"] = "¡Los infectados llegaron al refugio!"
            juego["jugando"] = False

    for proyectil in juego["proyectiles"][:]:
        proyectil.actualizar(dt)
        if proyectil.x > ANCHO:
            juego["proyectiles"].remove(proyectil)
            continue
        for infectado in juego["infectados"][:]:
            if infectado.fila == round((infectado.y - INICIO_Y - TAM_CASILLA / 2) / TAM_CASILLA):
                distancia = ((proyectil.x - infectado.x) ** 2 +
                             (proyectil.y - infectado.y) ** 2) ** 0.5
                if distancia < TAM_CASILLA * 0.30:
                    infectado.vida -= proyectil.daño
                    if proyectil in juego["proyectiles"]:
                        juego["proyectiles"].remove(proyectil)
                    if infectado.vida <= 0 and infectado in juego["infectados"]:
                        juego["infectados"].remove(infectado)
                        juego["dinero"] += 25
                    break

    for moneda in juego["monedas"][:]:
        if ahora - moneda.creada > 9000:
            juego["monedas"].remove(moneda)

    # Victoria de supervivencia: aguanta 90 segundos.
    if ahora - juego["inicio"] >= 90000:
        juego["resultado"] = "¡Victoria! ¡Defendiste el refugio!"
        juego["jugando"] = False


estado["inicio"] = pygame.time.get_ticks()

while True:
    dt = reloj.tick(60) / 1000.0

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not estado["jugando"]:
                estado = reiniciar()
                estado["inicio"] = pygame.time.get_ticks()
                continue

            boton_c, boton_d = dibujar_interfaz(pantalla, estado)
            pos = evento.pos

            if boton_c.collidepoint(pos):
                estado["tipo_seleccionado"] = "Cientifico"
            elif boton_d.collidepoint(pos):
                estado["tipo_seleccionado"] = "Defensor"
            else:
                # Recoger monedas.
                moneda_recogida = False
                for moneda in estado["monedas"][:]:
                    if moneda.rect.collidepoint(pos):
                        estado["dinero"] += 25
                        estado["monedas"].remove(moneda)
                        moneda_recogida = True
                        break

                celda = celda_desde_posicion(pos)
                if celda and estado["tipo_seleccionado"] and not moneda_recogida:
                    fila, columna = celda
                    ocupada = any(u.fila == fila and u.columna == columna
                                  for u in estado["unidades"])
                    coste = 50 if estado["tipo_seleccionado"] == "Cientifico" else 100
                    if not ocupada and estado["dinero"] >= coste:
                        estado["dinero"] -= coste
                        estado["unidades"].append(
                            Unidad(fila, columna, estado["tipo_seleccionado"])
                        )
                    estado["tipo_seleccionado"] = None

    pantalla.fill(NEGRO)
    boton_c, boton_d = dibujar_interfaz(pantalla, estado)
    dibujar_tablero(pantalla)

    # Actualizar y dibujar monedas, sin dibujarlas dos veces.
    if estado["jugando"]:
        ahora = pygame.time.get_ticks()
        for unidad in estado["unidades"]:
            unidad.dibujar(pantalla)
        for infectado in estado["infectados"]:
            infectado.dibujar(pantalla)
        for proyectil in estado["proyectiles"]:
            proyectil.dibujar(pantalla)
        for moneda in estado["monedas"]:
            moneda.dibujar(pantalla)

        # Actualización de lógica.
        actualizar(estado, dt)

        # Indicaciones de juego.
        texto(pantalla, "Elige una unidad y toca una casilla. Toca las monedas para recogerlas.",
              fuente_pequena, BLANCO, (INICIO_X, INICIO_Y + ALTO_TABLERO + 12))
        texto(pantalla, "ESC: salir", fuente_pequena, BLANCO,
              (ANCHO - int(ANCHO * 0.14), ALTO - int(ALTO * 0.07)))
    else:
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((0, 0, 0, 180))
        pantalla.blit(capa, (0, 0))
        texto(pantalla, estado["resultado"] or "Fin del juego",
              fuente_grande, BLANCO, (ANCHO // 2, ALTO // 2 - 35), centrado=True)
        texto(pantalla, "Toca la pantalla para volver a jugar",
              fuente, BLANCO, (ANCHO // 2, ALTO // 2 + 30), centrado=True)

    pygame.display.flip()
