
import os
import getpass
import requests

# Evaluacion Parcial N° 2 - CUY6142
# Sistema de geolocalizacion con GraphHopper

URL_BASE = "https://graphhopper.com/api/1"


def obtener_ubicacion(nombre, api_key):
    """Obtiene las coordenadas de un lugar mediante GraphHopper."""

    respuesta = requests.get(
        f"{URL_BASE}/geocode",
        params={
            "q": nombre,
            "locale": "es",
            "limit": 1,
            "key": api_key
        },
        timeout=20
    )

    respuesta.raise_for_status()
    resultados = respuesta.json().get("hits", [])

    if not resultados:
        raise ValueError(
            f"No se encontro la ubicacion: {nombre}"
        )

    return resultados[0]["point"]


def calcular_ruta(origen, destino, api_key):
    """Consulta una ruta con instrucciones en espanol."""

    inicio = obtener_ubicacion(origen, api_key)
    fin = obtener_ubicacion(destino, api_key)

    parametros = [
        ("point", f"{inicio['lat']},{inicio['lng']}"),
        ("point", f"{fin['lat']},{fin['lng']}"),
        ("profile", "car"),
        ("locale", "es"),
        ("instructions", "true"),
        ("calc_points", "true"),
        ("points_encoded", "false"),
        ("key", api_key)
    ]

    respuesta = requests.get(
        f"{URL_BASE}/route",
        params=parametros,
        timeout=30
    )

    respuesta.raise_for_status()
    datos = respuesta.json()

    rutas = datos.get("paths", [])

    if not rutas:
        raise ValueError(
            "No se encontro una ruta disponible."
        )

    return rutas[0]


def mostrar_resultado(origen, destino, ruta):
    """Muestra distancia, tiempo e instrucciones del viaje."""

    distancia_km = ruta["distance"] / 1000
    tiempo_min = ruta["time"] / 60000

    print("\n======================================")
    print("          RESULTADO DEL VIAJE")
    print("======================================")

    print(f"Origen: {origen}")
    print(f"Destino: {destino}")
    print(f"Distancia total: {distancia_km:.2f} km")
    print(f"Tiempo estimado: {tiempo_min:.2f} minutos")

    print("\n======================================")
    print("       INSTRUCCIONES DEL VIAJE")
    print("======================================")

    instrucciones = ruta.get("instructions", [])

    if not instrucciones:
        print(
            "La API no devolvio instrucciones "
            "para este recorrido."
        )
        return

    for numero, paso in enumerate(instrucciones, start=1):
        descripcion = paso.get(
            "text", "Continue por la ruta indicada"
        )

        distancia_metros = paso.get("distance", 0)
        distancia_paso_km = distancia_metros / 1000

        tiempo_paso_min = paso.get("time", 0) / 60000

        print(f"\nPaso {numero}: {descripcion}")
        print(
            f"  Distancia: {distancia_paso_km:.2f} km"
        )
        print(
            f"  Tiempo: {tiempo_paso_min:.2f} minutos"
        )

    print("\n======================================")
    print("       FIN DEL RECORRIDO")
    print("======================================")


def main():
    print("======================================")
    print("    SISTEMA DE RUTAS - GRAPHHOPPER")
    print("======================================")
    print("Evaluacion N° 2 - DUOC UC")
    print("Idioma: Espanol")
    print("Modo de transporte: Automovil")

    api_key = os.getenv("GRAPHHOPPER_API_KEY", "").strip()

    if not api_key:
        api_key = getpass.getpass(
            "\nIngrese su API Key de GraphHopper: "
        ).strip()

    if not api_key:
        print("Error: debe proporcionar una API Key.")
        return

    while True:
        print("\n--------------------------------------")
        print("       PLANIFICADOR DE VIAJES")
        print("--------------------------------------")
        print("Escriba 's' o 'salir' para finalizar.")

        origen = input(
            "\nIngrese el lugar de origen: "
        ).strip()

        if origen.lower() in ("s", "salir"):
            break

        destino = input(
            "Ingrese el lugar de destino: "
        ).strip()

        if destino.lower() in ("s", "salir"):
            break

        if not origen or not destino:
            print(
                "\nError: debe ingresar ambos lugares."
            )
            continue

        try:
            print("\nConsultando la ruta en GraphHopper...")

            ruta = calcular_ruta(
                origen, destino, api_key
            )

            mostrar_resultado(
                origen, destino, ruta
            )

        except requests.HTTPError as error:
            print(
                f"\nError HTTP de GraphHopper: {error}"
            )

            if error.response is not None:
                print(
                    "Detalle del servidor:",
                    error.response.text[:500]
                )

        except requests.RequestException as error:
            print(
                f"\nError de conexion: {error}"
            )

        except (ValueError, KeyError, TypeError) as error:
            print(
                f"\nNo fue posible calcular la ruta: {error}"
            )

    print("\n======================================")
    print("   PROGRAMA FINALIZADO CORRECTAMENTE")
    print("======================================")
    print("Gracias por utilizar GraphHopper.")


if __name__ == "__main__":
    main()
