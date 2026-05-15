# sistema-club-360

## Requisitos

*Dependencias de la app para poder correr. Instalar antes de clonar el repo.*

- python (3.10+)
- pip
- node.js
- npm

## Setup del proyecto

**Backend**
 1. Preparar el entorno virtual de flask
    
        cd backend
        python -m venv venv
    
        source venv/bin/activate (Linux/Mac)
        venv\Scripts\Activate.ps1 (Windows PowerShell)

        pip install -r requirements.txt 
    
3. Levantar el backend, corre en http://localhost:5000

        python run.py
    
**Frontend**
1. Preparar el entorno del front (seleccionar React + JavaScript)

        cd frontend
        npm install
   
3. Levantar el frontend, corre en http://localhost:5173/

        npm run dev


**La página de prueba está en http://localhost:5173/items**

## Contexto

Dentro del proyecto se separa backend y frontend.

En el **backend** está la base de datos que en flask se gestiona con SQLAlchemy (en vez de SQL, las consultas se hacen con streams que manejan las tablas como objetos).
En models.py se ponen las clases que representan las tablas. Dentro de cada clase se hacen distintas consultas según el dato que se desee recuperar.
En routes.py se encuentra la lógica, funciones y las URLs que las disparan.

> [!IMPORTANT]
> MODELOS ➡️ QUERYS REUSABLES
> 
> RUTAS ➡️ LOGICA Y ALGORITMOS

(ambos archivos deberían ser carpetas en realidad, con archivos con el nombre de la clase que modelan)

En el **frontend** el _main.jxs_ redirige a las distintas rutas que el frontend sabe representar, éstas se encuentran en la carpeta pages, que tiene un archivo por página monolítica, pero todas las páginas pueden tener por ejemplo un Header, éste tipo de elementos reutilizables van en una carpeta components.

## App de Prueba
*Tendría que ser borrada ésta sección cuando ya estemos desarrollando todo*

Está armada una paqueña app de prueba que tiene la conexión **base de datos -> backend -> frontend.**

La base de datos es mínima:

    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

    INSERT INTO items (name) VALUES ('Apple');
    INSERT INTO items (name) VALUES ('Banana');
    INSERT INTO items (name) VALUES ('Orange');

En models.py se hace una simple consulta que recupera todos los datos
En routes.py se dispara la consulta asociándola con la ruta /items

En el front, se asocia esa misma ruta con la página ItemsPage para renderizar.

**SOBRE LA BASE DE DATOS:** La que clonan ahora es de prueba nomás, después cuando nos pongamos de acuerdo cada uno debería tener la suya local y agregarla al .gitignore para que los cambios de cada uno no rompan las pruebas del resto

## Esqueleto

    sistema-club-360 // root
    ├── backend
    │   ├── app
    │   │   ├── config.py
    │   │   ├── _init_.py
    │   │   ├── models.py // representación en POO de la base de datos + las consultas asociadas a cada tabla
    │   │   ├── _pycache_
    │   │   └── routes.py // la lógica de la aplicación con sus rutas asociadas
    │   ├── instance
    │   │   └── database.db // base de datos -> tiene que ser reemplazada y puesta en .gitignore
    │   ├── requirements.txt
    │   └── run.py
    ├── frontend
    │   ├── eslint.config.js
    │   ├── index.html // NO TOCAR
    │   ├── package.json
    │   ├── package-lock.json
    │   ├── public // carpeta para logo de la app en el navegador
    │   ├── README.md
    │   ├── src
    │   │   ├── assets 
    │   │   │   ├── images // imágenes que se muestren dentro de la página
    │   │   │   └── styles // todos los archivos .css
    │   │   ├── components // componentes jsx reutilizables
    │   │   ├── index.css
    │   │   ├── main.jsx // NO TOCAR
    │   │   ├── pages // archivos para cada página de la app
    │   │   │   └── ItemsPage.jsx
    │   │   └── routes
    │   │       └── AppRoutes.jsx // un solo archivo que tiene todas las rutas que la app debe reocnocer
    │   └── vite.config.js
    └── README.md
