# MasterCook

Este es un proyecto de ...

## Frontend con React

```bash

...

```

## Backend con FastAPI

Para que el backend funcione bien hay que tener primero el .venv, que contiene todas las librerias que usara python y luego correr el backend (importante una ves el tengas el .venv con las dependencias puedes directamente activar el backend siempre y cuando tengas el .venv activo)

```bash
# 1. Crear un .venv y activarlo
python3 -m venv .venv

source .venv/bin/activate

## En Windows sería:

source .venv\Scripts\activate

# 2. Instalar dependencias en el .venv

pip install -r requirements.txt

# 3. Correr el backend
uvicorn main:app --reload
```
