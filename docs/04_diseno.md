# Diseño del Sistema

## Introducción

Este documento describe la arquitectura interna del simulador de Sistemas P y las decisiones de diseño adoptadas durante el desarrollo.

El objetivo principal es construir una arquitectura modular, extensible y fácilmente mantenible que permita representar Sistemas P de transición normalizados a tres membranas.

---

# Arquitectura General

El sistema se dividirá en varios componentes independientes:

```text
Sistema P
│
├── Membranas
│   ├── Membrana 1
│   ├── Membrana 2
│   └── Membrana 3
│
├── Reglas
│
├── Configuraciones
│
├── Motor de Simulación
│
├── Cargador JSON
│
└── Interfaz Gráfica
```

Cada componente tendrá una responsabilidad claramente definida.

---

# Estructura del Proyecto

```text
src/
│
├── models/
│   ├── membrane.py
│   ├── rule.py
│   ├── produced_object.py
│   ├── configuration.py
│   └── psystem.py
│
├── simulator/
│   └── simulator.py
│
├── parser/
│   └── json_loader.py
│
├──ui/
│   └── streamlit_app.py
├── examples/
│
└── main.py
```

---

# Modelo de Membrana

## Responsabilidad

Representar una región delimitada por una membrana.

Cada membrana almacenará:

* Su identificador.
* Referencia a la membrana padre.
* Lista de membranas hijas.
* Multiconjunto de objetos.

## Clase Membrane

```python
class Membrane:
```

### Atributos

```python
id: int
parent: Membrane | None
children: list[Membrane]
objects: Counter[str]
```

### Funcionalidades

* Añadir objetos.
* Eliminar objetos.
* Consultar multiplicidades.
* Comprobar disponibilidad de objetos.

---

# Modelo de Producción

## ProducedObject

Representa un objeto generado por una regla.

Permite especificar tanto el símbolo generado como su destino.

### Clase ProducedObject

```python
class ProducedObject:
```

### Atributos

```python
symbol: str
count: int
target: str
```

### Valores posibles para target

```text
here
out
in_2
in_3
```

---

# Modelo de Regla

## Responsabilidad

Representar una regla de evolución o comunicación.

Las reglas se almacenarán asociadas a una membrana concreta.

### Clase Rule

```python
class Rule:
```

### Atributos

```python
id: str

membrane_id: int

lhs: Counter[str]

rhs: list[ProducedObject]
```

### Ejemplo

Regla:

```text
ab -> c(out)d
```

Representación interna:

```python
lhs = {
    "a": 1,
    "b": 1
}

rhs = [
    ProducedObject("c", 1, "out"),
    ProducedObject("d", 1, "here")
]
```

---

# Modelo de Configuración

## Responsabilidad

Representar el estado completo del sistema en un instante dado.

### Clase Configuration

```python
class Configuration:
```

### Atributos

```python
membranes: dict[int, Membrane]

step: int
```

Una configuración contendrá:

* El contenido de cada membrana.
* El número de paso de simulación.

---

# Modelo del Sistema P

## Responsabilidad

Representar una instancia completa de un Sistema P.

### Clase PSystem

```python
class PSystem:
```

### Atributos

```python
alphabet: set[str]

membranes: dict[int, Membrane]

rules: dict[int, list[Rule]]

output_membrane: int

seed: int | None
```

### Funcionalidades

* Acceso a membranas.
* Acceso a reglas.
* Validación estructural.
* Gestión global del sistema.

---

# Cargador JSON

## Responsabilidad

Convertir un fichero JSON en una instancia de PSystem.

### Clase JsonLoader

```python
class JsonLoader:
```

### Funcionalidades

* Leer fichero JSON.
* Validar estructura.
* Crear membranas.
* Crear reglas.
* Construir el sistema completo.

---

# Motor de Simulación

## Responsabilidad

Ejecutar la evolución del sistema.

### Clase Simulator

```python
class Simulator:

    current_configuration: Configuration

    history: list[Configuration]
    mode: SimulationMode
```

### Funcionalidades

```python
step()

run()

is_halted()

get_history()
```

## Modelo de Modo de simulación

```python
from enum import Enum

class SimulationMode(Enum):
    SEQUENTIAL = "sequential"
    MAXIMAL_PARALLEL = "maximal_parallel"
```
---

# Aplicación de Reglas

## Detección de reglas aplicables

Una regla será aplicable cuando:

```text
lhs ⊆ multiconjunto_actual
```

considerando las multiplicidades de todos los símbolos.

---

## Consumo de objetos

Durante un paso de simulación los objetos consumidos quedarán reservados.

No podrán reutilizarse para activar otras reglas dentro del mismo paso.

---

## Producción de objetos

Los objetos generados no aparecerán inmediatamente.

Primero se acumularán en estructuras temporales.

Una vez finalizado el paso completo:

1. Se consumen los objetos.
2. Se aplican todos los movimientos.
3. Se incorporan los nuevos objetos.

Este comportamiento reproduce la semántica habitual de los Sistemas P de transición.

---

# Máximo Paralelismo

El simulador utilizará el modo máximamente paralelo.

Para cada membrana:

1. Se localizan las reglas aplicables.
2. Se selecciona un conjunto de reglas compatible.
3. Se aplican tantas reglas como sea posible sin reutilizar objetos.
4. El conjunto resultante debe ser no extensible.

El proceso finaliza cuando ya no es posible aplicar ninguna regla adicional.

---

# Condición de Parada

Una computación finalizará cuando:

* Ninguna regla sea aplicable en ninguna membrana.

En ese momento el sistema habrá alcanzado una configuración de parada.

---

# Futuras Extensiones

La arquitectura propuesta permitirá incorporar posteriormente:

* Prioridades.
* Catalizadores.
* Reglas de disolución.
* Membranas activas.
* Polarizaciones.
* Sistemas P tisulares.
* Sistemas P neuronales.

Sin necesidad de modificar la estructura principal del simulador.

# Modos de simulación

El simulador soportará dos estrategias de ejecución:

## Sequential

Las reglas se aplican una a una.

Su principal finalidad será la depuración y validación del comportamiento interno.

## Maximal Parallel

Las reglas se aplican siguiendo la semántica máximamente paralela de los Sistemas P.

Este será el modo de ejecución principal del simulador.


# Algoritmo de Máximo Paralelismo

## Introducción

Los Sistemas P de transición se caracterizan por la aplicación paralela de reglas dentro de cada paso de computación.

En lugar de aplicar una única regla por transición, el sistema debe aplicar simultáneamente tantas reglas como sea posible utilizando los objetos disponibles en cada membrana.

Este criterio recibe el nombre de ejecución máximamente paralela.

---

## Objetivo

Durante cada paso de simulación se deberá construir un conjunto de reglas aplicadas que cumpla las siguientes condiciones:

* Todas las reglas seleccionadas deben ser aplicables.
* Ningún objeto puede consumirse más veces de las disponibles.
* El conjunto resultante debe ser no extensible.
* No debe existir ninguna regla adicional que pueda añadirse utilizando los objetos restantes.

---

## Concepto de Reserva de Objetos

Durante la construcción del conjunto de reglas aplicadas, los objetos consumidos quedarán reservados.

Por ejemplo, si una membrana contiene:

```text
a² b¹
```

y se aplica la regla:

```text
ab → c
```

entonces quedará disponible:

```text
a¹
```

para el resto de selecciones del mismo paso.

Los objetos ya reservados no podrán reutilizarse.

---

## Procedimiento General

Para cada membrana:

### Paso 1

Copiar el multiconjunto actual de objetos.

```text
objetos_disponibles = objetos_membrana
```

---

### Paso 2

Buscar todas las reglas aplicables utilizando únicamente los objetos todavía disponibles.

---

### Paso 3

Seleccionar una regla aplicable.

---

### Paso 4

Reservar los objetos consumidos por dicha regla.

```text
objetos_disponibles -= lhs
```

---

### Paso 5

Registrar la aplicación de la regla.

---

### Paso 6

Repetir el proceso hasta que no exista ninguna regla adicional aplicable.

---

### Paso 7

Ejecutar simultáneamente todas las reglas seleccionadas.

---

## Producción Diferida

Los objetos generados no se incorporarán inmediatamente al sistema.

Todos los productos de las reglas se almacenarán temporalmente.

Por ejemplo:

```text
Regla 1:
a → b

Regla 2:
b → c
```

Si inicialmente existe un único objeto:

```text
a
```

solamente podrá aplicarse la primera regla.

El objeto:

```text
b
```

no estará disponible hasta la siguiente transición.

Esta restricción reproduce la semántica estándar de los Sistemas P de transición.

---

## Comunicación entre Membranas

Los objetos enviados mediante:

```text
out
```

o

```text
in_j
```

también se almacenarán temporalmente.

Los movimientos entre membranas se efectuarán únicamente al finalizar el paso completo.

Esto garantiza que todas las reglas trabajen sobre la misma configuración inicial.

---

## Estrategia de Selección

Los Sistemas P son modelos inherentemente no deterministas.

Por tanto, cuando existan varias reglas aplicables simultáneamente, el simulador podrá seleccionar cualquiera de ellas.

La primera versión utilizará una estrategia aleatoria controlada.

Esta decisión permite aproximarse mejor al comportamiento teórico del modelo.

---

## Ejemplo

Supongamos una membrana con:

```text
a² b¹
```

y las reglas:

```text
r1: ab → c

r2: a → d
```

Proceso:

```text
Estado inicial:
a² b¹

Aplicar r1:
consume a¹ b¹

Disponible:
a¹

Aplicar r2:
consume a¹

Disponible:
∅
```

Conjunto de reglas aplicado:

```text
{r1, r2}
```

Producción final:

```text
c¹ d¹
```

---

## Condición de Finalización

La selección termina cuando no existe ninguna regla aplicable utilizando los objetos aún disponibles.

En ese momento el conjunto de reglas construido es máximamente paralelo para dicha membrana.

Tras realizar este proceso en todas las membranas, se ejecuta la transición global del sistema.


## Reproducibilidad

Aunque la selección de reglas es no determinista desde el punto de vista teórico, el simulador permitirá fijar una semilla de ejecución.

La semilla se utilizará para inicializar el generador de números aleatorios empleado durante la selección de reglas.

Ejemplo:

```json
{
  "seed": 42
}
```