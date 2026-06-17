from geopy.distance import geodesic

class AgenteBuscador:
    """
    Agente encargado de buscar alternativas que se ajusten al tiempo y dinero del usuario.
    """
    def planificar_visita(self, origen, museos, presupuesto_max, tiempo_max):
        """
        Selecciona un conjunto óptimo de museos basándose en restricciones.
        Utiliza un enfoque dinámico de 'Vecino más Cercano' asegurando el retorno.
        """
        if not museos:
            return []

        seleccionados = []
        presupuesto_gastado = 0
        tiempo_gastado = 0
        posicion_actual = origen
        
        # Parámetros realistas para Cochabamba
        VELOCIDAD_KMH = 15.0  # Tráfico urbano lento
        COSTO_TRANSPORTE = 3.0  # Precio actual Trufi
        
        # Lista de museos aún no visitados
        pendientes = list(museos)
        
        while pendientes:
            # Encontrar el museo más cercano a la posición actual
            mejor_museo = None
            mejor_distancia = float('inf')
            
            for m in pendientes:
                dist = geodesic((posicion_actual['lat'], posicion_actual['lng']), (m['lat'], m['lng'])).meters
                if dist < mejor_distancia:
                    mejor_distancia = dist
                    mejor_museo = m
            
            if not mejor_museo:
                break
                
            # Calcular tiempos y costos para ESTE museo
            tiempo_traslado_hrs = (mejor_distancia / 1000) / VELOCIDAD_KMH
            
            # Verificar si podemos visitar este museo Y LUEGO REGRESAR al origen
            distancia_retorno = geodesic((mejor_museo['lat'], mejor_museo['lng']), (origen['lat'], origen['lng'])).meters
            tiempo_retorno_hrs = (distancia_retorno / 1000) / VELOCIDAD_KMH
            
            nuevo_presupuesto = presupuesto_gastado + mejor_museo['precio'] + COSTO_TRANSPORTE
            # Tiempo: ya gastado + traslado + estancia en el museo + tiempo de regreso (margen de seguridad)
            tiempo_con_visita_y_regreso = tiempo_gastado + tiempo_traslado_hrs + mejor_museo['tiempoEstimado'] + tiempo_retorno_hrs
            
            if nuevo_presupuesto <= presupuesto_max and tiempo_con_visita_y_regreso <= tiempo_max:
                # Es viable visitar este museo
                seleccionados.append(mejor_museo)
                presupuesto_gastado += mejor_museo['precio'] + COSTO_TRANSPORTE
                tiempo_gastado += tiempo_traslado_hrs + mejor_museo['tiempoEstimado']
                posicion_actual = {'lat': mejor_museo['lat'], 'lng': mejor_museo['lng']}
                pendientes.remove(mejor_museo)
            else:
                # Este museo es inalcanzable, pero quizás otro más cercano/barato/rápido sí lo sea?
                pendientes.remove(mejor_museo)
            
        return seleccionados

