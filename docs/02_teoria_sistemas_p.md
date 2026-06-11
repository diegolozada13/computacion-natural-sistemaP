# Fundamentos Teóricos de los Sistemas P

## Introducción

Los Sistemas P son modelos de computación bioinspirados pertenecientes al campo de la Computación Natural. Fueron propuestos por Gheorghe Păun en 1998 y están inspirados en la organización y funcionamiento de las células eucariotas.

La idea principal consiste en representar una célula mediante una estructura jerárquica de membranas que delimitan distintas regiones. En cada región existen objetos que evolucionan y se comunican siguiendo reglas formales, simulando de manera abstracta los procesos bioquímicos que tienen lugar en una célula real.

Los Sistemas P destacan por ser modelos de computación paralelos, distribuidos y no deterministas.

---

# Multiconjuntos

La información dentro de un Sistema P se representa mediante multiconjuntos.

A diferencia de los conjuntos tradicionales, en un multiconjunto un mismo elemento puede aparecer varias veces.

Por ejemplo:

```text
aabbbcc
```

representa el multiconjunto:

```text
a² b³ c²
```

En la implementación del simulador, cada región almacenará un multiconjunto de objetos que representará el estado interno de dicha membrana.

---

# Estructura de Membranas

Un Sistema P está formado por una estructura jerárquica de membranas anidadas.

Cada membrana delimita una región de trabajo independiente donde existen objetos y reglas propias.

Para este proyecto se utilizará una estructura fija normalizada de tres membranas:

```text
[1 [2 [3]3 ]2 ]1
```

donde:

* La membrana 1 representa la membrana externa o piel.
* La membrana 2 se encuentra contenida en la membrana 1.
* La membrana 3 se encuentra contenida en la membrana 2.

Cada región posee su propio multiconjunto de objetos y su propio conjunto de reglas.

---

# Sistemas P de Transición

Los Sistemas P de transición constituyen la variante más básica y extendida de los Sistemas P.

Formalmente, un Sistema P de transición puede definirse mediante:

Π = (O, μ, w₁, ..., wₘ, R₁, ..., Rₘ)

donde:

* O es el alfabeto de objetos.
* μ es la estructura de membranas.
* wᵢ es el multiconjunto inicial de la región i.
* Rᵢ es el conjunto de reglas asociadas a la región i.

La ejecución del sistema consiste en la aplicación sucesiva de reglas sobre los objetos presentes en las distintas regiones.

---

# Reglas de Evolución

Las reglas de evolución permiten transformar objetos dentro de una misma región.

Su forma general es:

```text
u → v
```

donde:

* u representa los objetos consumidos.
* v representa los objetos generados.

Ejemplos:

```text
a → b
ab → c
aa → bc
```

Una regla solamente puede aplicarse cuando todos los objetos necesarios aparecen en el multiconjunto de la región correspondiente.

---

# Reglas Cooperativas

El miembro izquierdo de una regla puede contener más de un objeto.

Por ejemplo:

```text
ab → c
```

Esta regla consume simultáneamente un objeto `a` y un objeto `b`.

Las reglas cuyo antecedente contiene más de un símbolo reciben el nombre de reglas cooperativas.

Su presencia incrementa significativamente la capacidad computacional del sistema.

---

# Reglas de Comunicación

Además de evolucionar, los objetos pueden desplazarse entre regiones.

Para ello se utilizan reglas de comunicación.

## Comunicación hacia la membrana padre

```text
a → (b, out)
```

La regla consume un objeto `a` de la región actual y envía un objeto `b` a la membrana que la contiene.

---

## Comunicación hacia una membrana interna

```text
a → (b, in_3)
```

La regla consume un objeto `a` y envía un objeto `b` a la membrana 3.

---

## Comunicación local

```text
a → b
```

Los objetos permanecen dentro de la misma región.

---

# Configuraciones

Una configuración representa el estado completo del sistema en un instante determinado.

Puede representarse como:

```text
(μ, M₁, M₂, M₃)
```

donde:

* μ representa la estructura de membranas.
* M₁, M₂ y M₃ representan los multiconjuntos presentes en cada región.

La ejecución del sistema consiste en una secuencia de configuraciones obtenidas mediante la aplicación de reglas.

---

# Máximo Paralelismo

Una de las características fundamentales de los Sistemas P es el paralelismo.

En este proyecto se utilizará el modo de ejecución máximamente paralelo.

Bajo este criterio, en cada paso de computación deben aplicarse simultáneamente tantas reglas como sea posible.

Esto implica que:

* Una regla puede aplicarse varias veces si existen suficientes objetos.
* Varias reglas pueden ejecutarse simultáneamente.
* Ninguna regla adicional debe poder añadirse a la ejecución sin consumir objetos que ya han sido utilizados.

El conjunto de reglas aplicadas en un paso debe ser no extensible.

---

# Configuración de Parada

La computación finaliza cuando no existe ninguna regla aplicable en ninguna de las membranas del sistema.

La última configuración alcanzada recibe el nombre de configuración final o configuración de parada.

El resultado de la computación se obtiene a partir de dicha configuración final.

---

# Alcance Teórico del Proyecto

El simulador desarrollado implementará exclusivamente Sistemas P de transición con:

* Tres membranas.
* Reglas de evolución.
* Reglas de comunicación.
* Multiconjuntos de objetos.
* Ejecución máximamente paralela.

No se incluirán otras variantes avanzadas de los Sistemas P como membranas activas, polarizaciones, división de membranas, sistemas tisulares o sistemas neuronales.
