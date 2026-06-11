# Plan de Trabajo

## Fase 1 - Análisis y Diseño

### Documentación

* [x] Definir el objetivo del proyecto.
* [x] Resumir la teoría necesaria sobre Sistemas P.
* [x] Definir requisitos funcionales y no funcionales.
* [x] Diseñar la arquitectura del simulador.
* [x] Definir el algoritmo de máximo paralelismo.

---

## Fase 2 - Modelado del Dominio

### Modelos

* [ ] Implementar clase `Membrane`.
* [ ] Implementar clase `ProducedObject`.
* [ ] Implementar clase `Rule`.
* [ ] Implementar clase `Configuration`.
* [ ] Implementar clase `PSystem`.
* [ ] Implementar enum `SimulationMode`.

### Validaciones

* [ ] Validar estructura de membranas.
* [ ] Validar reglas.
* [ ] Validar destinos de comunicación.

---

## Fase 3 - Carga de Sistemas P

### Parser JSON

* [ ] Implementar `JsonLoader`.
* [ ] Cargar membranas.
* [ ] Cargar multiconjuntos.
* [ ] Cargar reglas.
* [ ] Cargar configuración general.
* [ ] Validar ficheros JSON inválidos.

---

## Fase 4 - Motor de Simulación

### Funcionalidad básica

* [ ] Detectar reglas aplicables.
* [ ] Aplicar reglas de evolución.
* [ ] Aplicar reglas de comunicación.
* [ ] Gestionar producción diferida.
* [ ] Gestionar movimientos entre membranas.

### Modo Sequential

* [ ] Implementar ejecución secuencial.
* [ ] Implementar avance paso a paso.
* [ ] Implementar ejecución completa.

### Modo Maximal Parallel

* [ ] Implementar reserva de objetos.
* [ ] Implementar selección de reglas.
* [ ] Implementar conjunto no extensible.
* [ ] Implementar ejecución máximamente paralela.

### Gestión de simulaciones

* [ ] Detectar configuraciones de parada.
* [ ] Gestionar historial de configuraciones.
* [ ] Implementar reproducibilidad mediante semilla.

---

## Fase 5 - Ejemplos

### Sistemas de prueba

* [ ] Crear ejemplo básico de evolución.
* [ ] Crear ejemplo con comunicación entre membranas.
* [ ] Crear ejemplo con reglas cooperativas.
* [ ] Crear ejemplo con máximo paralelismo.
* [ ] Reproducir al menos un ejemplo visto en clase.

---

## Fase 6 - Interfaz Gráfica

### Streamlit

* [ ] Crear interfaz base.
* [ ] Mostrar estructura de membranas.
* [ ] Mostrar multiconjuntos.
* [ ] Mostrar reglas del sistema.
* [ ] Ejecutar un paso.
* [ ] Ejecutar simulación completa.
* [ ] Mostrar historial de configuraciones.

---

## Fase 7 - Pruebas

### Tests

* [ ] Test de membranas.
* [ ] Test de reglas.
* [ ] Test del cargador JSON.
* [ ] Test de simulación secuencial.
* [ ] Test de máximo paralelismo.

### Validación

* [ ] Comparar resultados con ejemplos teóricos.
* [ ] Verificar reproducibilidad mediante semilla.
* [ ] Verificar condiciones de parada.

---

## Fase 8 - Entrega

### Documentación

* [ ] Revisar documentación técnica.
* [ ] Añadir capturas de la interfaz.
* [ ] Redactar memoria final.

### Proyecto

* [ ] Revisar código.
* [ ] Limpiar repositorio.
* [ ] Preparar versión de entrega.
