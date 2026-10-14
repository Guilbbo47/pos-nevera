# POS Nevera - Sistema de Caja y Stock para Asociación

Aplicación web móvil para gestionar el stock y las ventas de productos de una nevera/asociación.

## Características

- Escaneo de códigos de barras con la cámara del móvil
- Gestión de productos (nombre, código de barras, precio, stock)
- Caja registradora: añade productos escaneando, modifica cantidades y cobra
- Descuento automático de stock al confirmar la venta
- Historial de ventas
- Interfaz optimizada para móvil
- Varias personas pueden usarla a la vez (conectada a la red)

## Requisitos

- Python 3.9+
- Cámara en el móvil (para escanear)

## Instalación

```bash
cd pos_nevera
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Abre en el móvil: `http://IP_DEL_ORDENADOR:8000`

**Importante para la cámara:**
- En móvil real necesitas HTTPS o localhost. Para pruebas locales funciona.
- Si lo despliegas, usa un servicio con HTTPS (Render, Railway, etc.).

## Uso

1. **Productos**: Añade productos con su código de barras, precio y stock.
2. **Vender**: Apunta la cámara al código → se añade al ticket → Cobrar.
3. **Historial**: Consulta las últimas ventas.

## Notas

- La base de datos es SQLite (`pos_nevera.db`). Se crea automáticamente.
- Para uso en producción con varias personas, considera desplegarlo en un servidor (Render.com tiene plan gratuito).
- El escáner usa `html5-qrcode` (funciona en Chrome y Safari móviles modernos).

## Estructura

- `main.py` → Backend FastAPI + API
- `templates/index.html` → Interfaz completa
- `requirements.txt` → Dependencias
