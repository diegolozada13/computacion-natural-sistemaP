# Requisitos del Sistema

## Introducción

Este documento define los requisitos funcionales y no funcionales que deberá cumplir el simulador de Sistemas P desarrollado en este proyecto.

El objetivo es establecer de forma precisa el comportamiento esperado del sistema antes de comenzar la implementación.

---

# Requisitos Funcionales

## RF-01: Definición de membranas

El sistema deberá permitir representar una estructura fija de tres membranas anidadas.

La estructura utilizada será:

```text
[1 [2 [3]3 ]2 ]1
```

Cada membrana deberá conocer:

* Su identificador.
* Su membrana padre.
* Sus membranas hijas.
* Los objetos presentes en su región.

---

## RF-02: Gestión de multiconjuntos

Cada membrana deberá almacenar un multiconjunto de objetos.

El sistema deberá permitir:

* Añadir objetos.
* Eliminar objetos.
* Consultar multiplicidades.
* Comprobar disponibilidad de objetos.

Ejemplo:

```text
aabbbc
```

equivale a:

```text
a² b³ c¹
```

---

## RF-03: Definición de reglas

El sistema deberá permitir definir reglas asociadas a una membrana concreta.

Cada regla tendrá:

* Un antecedente (objetos consumidos).
* Un consecuente (objetos producidos).
* Un tipo de comunicación.

Ejemplo:

```text
ab -> c
```

---

## RF-04: Reglas cooperativas

El sistema deberá soportar reglas cooperativas.

Ejemplos válidos:

```text
ab -> c

aa -> bc

abc -> d
```

Una regla cooperativa solamente podrá ejecutarse cuando todos los objetos requeridos estén presentes en la región correspondiente.

---

## RF-05: Reglas de evolución

El sistema deberá soportar reglas de evolución local.

Ejemplos:

```text
a -> b

ab -> cd
```

Los objetos generados permanecerán en la misma región donde se ejecutó la regla.

---

## RF-06: Reglas de comunicación hacia fuera

El sistema deberá soportar comunicación hacia la membrana padre.

Ejemplos:

```text
a -> (b, out)

ab -> (c, out)d
```

Los objetos marcados como `out` deberán transferirse a la membrana inmediatamente superior.

---

## RF-07: Reglas de comunicación hacia dentro

El sistema deberá soportar comunicación hacia membranas hijas.

Ejemplos:

```text
a -> (b, in_2)

ab -> (c, in_3)d
```

Los objetos enviados deberán aparecer en la membrana destino al finalizar el paso de computación.

---

## RF-08: Aplicabilidad de reglas

El sistema deberá determinar automáticamente si una regla es aplicable.

Una regla será aplicable cuando:

* Todos los objetos del antecedente estén presentes.
* Existan suficientes multiplicidades para satisfacer el consumo requerido.

---

## RF-09: Simulación paso a paso

El simulador deberá permitir ejecutar una única transición del sistema.

La ejecución de un paso deberá producir una nueva configuración.

---

## RF-10: Simulación completa

El simulador deberá permitir ejecutar automáticamente el sistema hasta alcanzar una configuración de parada.

---

## RF-11: Máximo paralelismo

El simulador deberá implementar el modo máximamente paralelo.

En cada transición:

* Se aplicará un conjunto no extensible de reglas.
* Los objetos consumidos no podrán reutilizarse durante el mismo paso.
* Se maximizará el aprovechamiento de los objetos disponibles.

---

## RF-12: Configuración de parada

La simulación deberá finalizar cuando no exista ninguna regla aplicable en ninguna membrana.

---

## RF-13: Visualización de configuraciones

El sistema deberá mostrar el contenido de cada membrana durante la ejecución.

Ejemplo:

```text
Paso 0

Membrana 1: {}
Membrana 2: {a:2,b:1}
Membrana 3: {c:3}
```

---

## RF-14: Modo de ejecución

El simulador deberá soportar los siguientes modos de ejecución:

- Sequential
- Maximal Parallel

El modo Maximal Parallel será el modo de ejecución por defecto.

---

## RF-15: Interfaz visual

El simulador deberá proporcionar una interfaz gráfica que permita:

- Cargar sistemas P desde ficheros JSON.
- Visualizar el contenido de cada membrana.
- Ejecutar un único paso de simulación.
- Ejecutar la simulación completa.
- Consultar el historial de configuraciones.

---

## RF-16: Reproducibilidad

El simulador deberá permitir fijar una semilla de ejecución para controlar los procesos aleatorios utilizados durante la selección de reglas.

Cuando se utilice la misma semilla y la misma configuración inicial, el simulador deberá producir exactamente la misma secuencia de configuraciones.

Si no se especifica ninguna semilla, el simulador podrá utilizar una semilla generada automáticamente.

---

# Formato de Entrada

Los sistemas P se definirán mediante ficheros JSON.

Cada regla tendrá:

* `id`: identificador textual.
* `membrane`: membrana donde se aplica.
* `lhs`: multiconjunto consumido.
* `rhs`: lista de objetos producidos.
* `target`: destino de cada objeto producido.

Los destinos válidos son:

* `here`: el objeto permanece en la misma membrana.
* `out`: el objeto se envía a la membrana padre.
* `in_2`: el objeto se envía a la membrana 2 si esta es hija directa de la membrana actual.
* `in_3`: el objeto se envía a la membrana 3 si esta es hija directa de la membrana actual.

## Restricciones sobre comunicación

La comunicación deberá respetar la estructura jerárquica de membranas.

La operación `out` solamente será válida si existe una membrana padre.

La operación `in_j` solamente será válida si la membrana destino es hija directa de la membrana actual.

Por tanto:

* La membrana 1 puede enviar objetos a la membrana 2.
* La membrana 2 puede enviar objetos a la membrana 3 o hacia la membrana 1 mediante `out`.
* La membrana 3 únicamente puede enviar objetos hacia la membrana 2 mediante `out`.

No se permitirá enviar objetos directamente desde la membrana 1 a la membrana 3.

## Ejemplo

```json
{
  "seed": 42,
  "alphabet": ["a", "b", "c", "d"],
  "membranes": {
    "1": {
      "objects": {}
    },
    "2": {
      "objects": {
        "a": 2,
        "b": 1
      }
    },
    "3": {
      "objects": {
        "c": 3
      }
    }
  },
  "rules": [
    {
      "id": "r1",
      "membrane": 2,
      "lhs": {
        "a": 1,
        "b": 1
      },
      "rhs": [
        {
          "object": "c",
          "count": 1,
          "target": "here"
        }
      ]
    },
    {
      "id": "r2",
      "membrane": 3,
      "lhs": {
        "c": 1
      },
      "rhs": [
        {
          "object": "d",
          "count": 1,
          "target": "out"
        }
      ]
    },
    {
      "id": "r3",
      "membrane": 1,
      "lhs": {
        "d": 1
      },
      "rhs": [
        {
          "object": "a",
          "count": 1,
          "target": "in_2"
        }
      ]
    }
  ],
  "output_membrane": 1,
  "max_steps": 50
}
```

---

# Requisitos No Funcionales

## RNF-01: Lenguaje

La implementación se desarrollará en Python 3.

---

## RNF-02: Modularidad

La arquitectura deberá estar basada en componentes independientes.

Como mínimo deberán existir módulos para:

* Membranas.
* Reglas.
* Configuraciones.
* Simulación.

---

## RNF-03: Extensibilidad

La arquitectura deberá facilitar futuras ampliaciones para incorporar:

* Prioridades.
* Catalizadores.
* Disolución de membranas.
* Membranas activas.

---

## RNF-04: Legibilidad

El código deberá incluir:

* Tipado estático cuando sea posible.
* Comentarios relevantes.
* Nombres descriptivos.

---

# Exclusiones

La primera versión del simulador no incluirá:

* Catalizadores.
* Prioridades entre reglas.
* Disolución de membranas.
* Membranas activas.
* Polarizaciones.
* Sistemas tisulares.
* Sistemas P neuronales.

Estas características podrán añadirse en futuras versiones sin modificar la arquitectura principal.
