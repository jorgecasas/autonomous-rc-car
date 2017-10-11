# Autonomous RC Car

El objetivo de este proyecto es construir un vehículo autónomo (un coche radio control que conduzca sólo), mediante OpenCV y Tensorflow, utilizando una Raspberry Pi y su cámara. En este repositorio puedes encontrar todo el código que vaya utilizando.

Puedes encontrar más información en mi blog https://jorgecasas.github.io, donde se va detallando todos los pasos necesarios.

* [Coche RC autónomo - Índice de contenidos](https://jorgecasas.github.io/2017/08/22/autonomous-rc-car-construyendo-un-coche-autonomo)
* [Github - jorgecasas/autonomous-rc-car](https://github.com/jorgecasas/autonomous-rc-car)


## Scripts y código compartido

En el directorio **scripts** puedes encontrar los ficheros con el código compartido. Los principales para el vehículo autónomo son:

* **Servidor `server.py`**: Servidor que controlará y realizará los procesos requeridos para la conducción autónoma (procesado de imágenes y datos de los sensores, red neuronal, control de servos para la conducción, etcétera). Durante fase de desarrollo puede utilizarse en nuestro ordenador de desarrollo, para luego pasar a ejecutarse en la propia Raspberry Pi que controlará el vehículo
* **Cliente `client.py`**: Este código se ejecutará integramente en la Raspberry Pi, obteniendo y enviando datos de los sensores (cámara y sensor ultrasónico) al servidor (`server.py`)

Otros ficheros contienen partes luego utilizados en estos otros scripts principales, y pueden servir de ejemplo para probar diferentes conceptos. Son los mismos que se utilizan y comentan en cada post que voy escribiendo sobre el proyecto [Coche RC autónomo](https://jorgecasas.github.io/2017/08/22/autonomous-rc-car-construyendo-un-coche-autonomo) en mi blog (como puede ser el utilizar la cámara de la Raspberry, configurar el sensor de ultrasonidos o crear un semáforo con Arduino)
