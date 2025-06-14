from flask import Flask, render_template, request
import random
import math

app = Flask(__name__)

COORDENADAS = {
    'Jiloyork': (19.916012, -99.580580),
    'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844),
    'Guadalajara': (20.677754472859146, -103.34625354877137),
    'Monterrey': (25.69161110159454, -100.321838480256),
    'QuintanaRoo': (21.163111924844458, -86.80231502121464),
    'Michoacan': (19.701400113725654, -101.20829680213464),
    'Aguascalientes': (21.87641043660486, -102.26438663286967),
    'CDMX': (19.432713075976878, -99.13318344772986),
    'QRO': (20.59719437542255, -100.38667040246602)
}

def distancia(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def evalua_ruta(ruta, coord):
    total = sum(distancia(coord[ruta[i]], coord[ruta[i+1]]) for i in range(len(ruta)-1))
    total += distancia(coord[ruta[-1]], coord[ruta[0]])
    return total

def generar_vecinos(ruta):
    vecinos = []
    for _ in range(5):
        nuevo_vecino = ruta[:]
        i, j = random.sample(range(len(ruta)), 2)
        nuevo_vecino[i], nuevo_vecino[j] = nuevo_vecino[j], nuevo_vecino[i]
        vecinos.append(nuevo_vecino)
    return vecinos

def busqueda_tabu(ruta_inicial, coord, max_iteraciones=100, memoria_tabu_tamano=10):
    estado_actual = ruta_inicial[:]
    mejor_estado = estado_actual[:]
    memoria_tabu = []

    for _ in range(max_iteraciones):
        vecinos = generar_vecinos(estado_actual)
        vecinos_validos = [ruta for ruta in vecinos if ruta not in memoria_tabu]
        if not vecinos_validos:
            continue
        estado_nuevo = min(vecinos_validos, key=lambda ruta: evalua_ruta(ruta, coord))
        if evalua_ruta(estado_nuevo, coord) < evalua_ruta(mejor_estado, coord):
            mejor_estado = estado_nuevo[:]
        estado_actual = estado_nuevo[:]
        memoria_tabu.append(estado_actual)
        if len(memoria_tabu) > memoria_tabu_tamano:
            memoria_tabu.pop(0)
    return mejor_estado

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        temp_inicial = float(request.form.get('temp_inicial'))
        temp_minima = float(request.form.get('temp_minima'))
        velocidad = float(request.form.get('velocidad'))
        num_iteraciones = int(request.form.get('num_iteraciones'))
        tamano_lista_tabu = int(request.form.get('tamano_lista_tabu'))

        # Crear ruta inicial excluyendo origen y destino, y luego armar ruta con origen al inicio y destino al final
        ciudades_ruta = list(COORDENADAS.keys())
        ciudades_ruta.remove(origen)
        ciudades_ruta.remove(destino)
        random.shuffle(ciudades_ruta)
        ruta_inicial = [origen] + ciudades_ruta + [destino]

        mejor_ruta = busqueda_tabu(
            ruta_inicial, COORDENADAS,
            max_iteraciones=num_iteraciones,
            memoria_tabu_tamano=tamano_lista_tabu
        )
        distancia_total = evalua_ruta(mejor_ruta, COORDENADAS)
        resultado = {
            'ruta': mejor_ruta,
            'distancia': distancia_total,
            'temp_inicial': temp_inicial,
            'temp_minima': temp_minima,
            'velocidad': velocidad,
            'num_iteraciones': num_iteraciones,
            'tamano_lista_tabu': tamano_lista_tabu
        }

    return render_template('index.html', ciudades=COORDENADAS.keys(), resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)
