from geopy.distance import geodesic

class AgenteBuscador:
    """
    Agente encargado de buscar alternativas que se ajusten al tiempo y dinero del usuario.
    """
    def planificar_visita(self, origen, museos, presupuesto_max, tiempo_max):
        """
        Selecciona un conjunto óptimo de museos basándose en restricciones.
        Utiliza un enfoque voraz (greedy) para maximizar la cantidad de visitas.
        """
        if not museos:
            return []

        # Ordenar museos por distancia al origen para empezar por lo más cercano
        for m in museos:
            m['dist_origen'] = geodesic((origen['lat'], origen['lng']), (m['lat'], m['lng'])).meters
        
        museos_ordenados = sorted(museos, key=lambda x: x['dist_origen'])
        
        seleccionados = []
        presupuesto_gastado = 0
        tiempo_gastado = 0
        posicion_actual = origen
        
        for m in museos_ordenados:
            # Estimación de traslado: 20 km/h (promedio urbano)
            distancia = geodesic((posicion_actual['lat'], posicion_actual['lng']), (m['lat'], m['lng'])).meters
            tiempo_traslado_hrs = (distancia / 1000) / 18  # 18 km/h
            costo_traslado = 2.0  # Costo base de trufi/micro
            
            nuevo_presupuesto = presupuesto_gastado + m['precio'] + costo_traslado
            nuevo_tiempo = tiempo_gastado + m['tiempoEstimado'] + tiempo_traslado_hrs
            
            if nuevo_presupuesto <= presupuesto_max and nuevo_tiempo <= tiempo_max:
                seleccionados.append(m)
                presupuesto_gastado = nuevo_presupuesto
                tiempo_gastado = nuevo_tiempo
                posicion_actual = m
            
        return seleccionados

