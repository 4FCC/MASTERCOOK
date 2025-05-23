# MasterCook – Microservicio Modular con FastAPI + Docker

Este proyecto es una plataforma modular construida con microservicios en FastAPI y Docker, orientada a la gestión de usuarios, reservas y talleres gastronómicos.

## Levantar el Proyecto

```
# Iniciar todos los contenedores
docker-compose up --build
```

```
# Apagar todo y eliminar volúmenes persistentes
docker-compose down -v
```

```
# Borrar imágenes, redes y contenedores (CUIDADO)
docker system prune -a
```

## Notas Importantes

- Los Dockerfile y la configuración de docker-compose ya están completamente funcionales.
- No modificar configuraciones de red, puertos ni dependencias internas sin coordinación.
- Si hay cambios en la base de datos, recuerda actualizar también los scripts de inicialización.
