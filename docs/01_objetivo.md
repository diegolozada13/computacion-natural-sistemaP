# Objetivo del Proyecto

## Introducción

Los Sistemas P constituyen un modelo de computación bioinspirado propuesto por Gheorghe Păun a finales de los años noventa dentro del área de la computación con membranas. Estos sistemas abstraen el comportamiento de las células eucariotas mediante una estructura jerárquica de membranas que delimitan regiones donde evolucionan y se comunican distintos objetos siguiendo reglas formales de transformación.

Los Sistemas P destacan por su naturaleza paralela, distribuida y no determinista, permitiendo modelar procesos computacionales inspirados en fenómenos biológicos. Debido a ello, representan una de las ramas más relevantes de la Computación Natural Bioinspirada.

## Objetivo General

El objetivo principal de este proyecto es diseñar e implementar un simulador de Sistemas P de transición normalizados a tres membranas utilizando Python.

El simulador deberá permitir definir la estructura de membranas, los multiconjuntos iniciales de objetos y las reglas de evolución y comunicación asociadas a cada región, reproduciendo el comportamiento descrito por la definición formal de los Sistemas P de transición.

## Objetivos Específicos

Para alcanzar el objetivo general se plantean los siguientes objetivos específicos:

* Implementar una representación interna de la estructura jerárquica de tres membranas.
* Implementar la gestión de multiconjuntos de objetos presentes en cada región del sistema.
* Diseñar un mecanismo para representar reglas de evolución sobre multiconjuntos.
* Implementar reglas de comunicación entre membranas mediante direccionamiento hacia regiones internas y externas.
* Simular la evolución del sistema a través de sucesivas configuraciones.
* Implementar el modo de ejecución máximamente paralelo propio de los Sistemas P de transición.
* Detectar automáticamente las configuraciones de parada cuando no existan reglas aplicables.
* Mostrar de forma clara la evolución de las configuraciones generadas durante una computación.

## Alcance del Proyecto

El proyecto se centrará exclusivamente en los Sistemas P de transición con estructura fija de tres membranas.

La implementación incluirá:

* Objetos representados mediante multiconjuntos.
* Reglas de evolución.
* Reglas de comunicación entre membranas.
* Configuración inicial del sistema.
* Simulación paso a paso.
* Ejecución completa hasta alcanzar una configuración de parada.
* Aplicación de reglas en modo máximamente paralelo.
- Simulación en modo máximamente paralelo.
- Simulación secuencial para depuración y validación.
- Interfaz visual para la ejecución y visualización de configuraciones.

Con el fin de mantener un alcance adecuado para el desarrollo del proyecto, no se implementarán variantes más avanzadas de los Sistemas P.

## Exclusiones

Quedan fuera del alcance de esta primera versión:

* Sistemas P con membranas activas.
* Sistemas P con polarizaciones.
* Reglas de disolución de membranas.
* Reglas de división de membranas.
* Catalizadores.
* Sistemas P tisulares.
* Sistemas P con impulsos neuronales.
* Otras extensiones especializadas descritas en la literatura.

## Tecnologías Utilizadas

La implementación se realizará utilizando:

* Python 3 como lenguaje principal.
* Estructuras de datos orientadas a objetos.
* Bibliotecas estándar de Python para la representación y manipulación de multiconjuntos.
- Streamlit (interfaz gráfica)

## Resultado Esperado

Como resultado final se espera obtener una herramienta capaz de ejecutar simulaciones de Sistemas P de transición normalizados a tres membranas, permitiendo observar la evolución de los objetos a través de las distintas regiones del sistema y verificar el funcionamiento de las reglas definidas por el usuario.

Además, la arquitectura desarrollada deberá facilitar futuras ampliaciones que permitan incorporar nuevas variantes de Sistemas P o mecanismos computacionales bioinspirados relacionados.
