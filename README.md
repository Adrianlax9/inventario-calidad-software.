# Inventario CUN — evaluación de calidad

Proyecto académico de Adrián Fernando Cuevas Osorio. CUN, Calidad del Software 54461, docente Alexander Calderón Martínez. Entrega: 8 de noviembre de 2026. 

## Ejecutar

Requisito: Python 3.10 o superior con SQLite (incluido en la distribución habitual). No hay paquetes externos. Descomprimir y abrir una terminal en esta carpeta:

```sh
python app.py
```

Abrir http://127.0.0.1:8000 en un navegador. En Windows también puede usarse `py app.py`. Detener con Ctrl+C. Los datos se guardan en `inventario.sqlite3` en la carpeta de ejecución. No compartir esa base si contiene información privada. La variable opcional `INVENTARIO_DB` cambia la ruta de la base. Si el puerto 8000 está ocupado, cerrar el otro servicio antes de iniciar.

Funciones: registrar producto con SKU único, listar productos y aplicar movimientos positivos o negativos sin permitir stock negativo. No incluye eliminación, modificación de nombres, precios, usuarios o historial.

## Repetir las dos pruebas reales

Con el servidor normal detenido o iniciado, desde esta carpeta:

```sh
python tests/run_tests.py
```

El programa crea un servidor independiente en un puerto libre y una base temporal. CP01 es una prueba funcional con ocho verificaciones; CP02 es una prueba de rendimiento local con 10 calentamientos y 200 consultas secuenciales de un cliente sobre una fila. Devuelve un error si no se cumplen las expectativas. Sobrescribe los archivos `resultados.json`, `servidor.log` y `ejecucion.txt`.

Resultados originales: 8/8 verificaciones, 200/200 respuestas correctas, p95 25,83 ms. El umbral de 100 ms fue fijado para el ejercicio. Los tiempos varían por equipo. Ver `evidencias/resultados.json` para versión de Python, fecha UTC, datos esperados y obtenidos, y 200 muestras originales. El percentil usa rango más próximo, posición 190. 

## Archivos

- `app.py`: servidor HTTP y operaciones SQLite.
- `index.html`: interfaz accesible por navegador.
- `tests/run_tests.py`: dos casos automatizados y cálculo de tres métricas.
- `evidencias/`: resultados, log, resumen y capturas originales.
- `MATRIZ_REQUISITOS.md`: trazabilidad a la guía.

## Publicar en GitHub

Publicación pendiente; no existe un enlace remoto de esta entrega. Crear un repositorio vacío en la cuenta propia, sin README automático. Esta carpeta incluye un repositorio Git local con un commit. Desde ella, ejecutar los comandos siguientes sustituyendo la dirección por la URL REAL proporcionada por GitHub:

```sh
git remote add origin URL_REAL_DEL_REPOSITORIO
git push -u origin main
```

Si Git solicita autenticación, completarla con la cuenta propia. No guardar contraseñas ni tokens en archivos. Alternativa: GitHub Desktop → Add local repository → Publish repository. Si un descompresor no conserva `.git`, ejecutar `git init -b main`, `git add .` y `git commit -m "Entrega de inventario y pruebas reales"` antes de configurar el remoto. Comprobar desde una ventana sin sesión que el docente pueda consultar el código y las evidencias. Insertar la URL auténtica en el informe.

## Límites

Prototipo local sin autenticación, roles, HTTPS ni auditoría. `http.server` no está recomendado para producción. No se ha probado concurrencia, grandes volúmenes, restauración o seguridad completa. No usar como inventario operativo sin ampliar controles y pruebas. La modalidad individual difiere de los grupos de 3–5 solicitados; no se declara aprobación docente.

Fuentes técnicas: documentación oficial de Python, https://docs.python.org/3/library/http.server.html, https://docs.python.org/3/library/sqlite3.html y https://docs.python.org/3/library/time.html.
