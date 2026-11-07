"""Inventario académico local. Python 3.10+, sin dependencias externas."""
import json
import os
import sqlite3
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DB = os.environ.get('INVENTARIO_DB', 'inventario.sqlite3')

@contextmanager
def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS productos (sku TEXT PRIMARY KEY, nombre TEXT NOT NULL, cantidad INTEGER NOT NULL CHECK(cantidad>=0))')
    try:
        with db:
            yield db
    finally:
        db.close()

class Handler(BaseHTTPRequestHandler):
    def send(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            body = Path(__file__).with_name('index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/productos':
            with connect() as db:
                rows = db.execute('SELECT sku,nombre,cantidad FROM productos ORDER BY sku').fetchall()
            self.send(200, [dict(zip(('sku','nombre','cantidad'), r)) for r in rows])
        else:
            self.send(404, {'error':'Ruta no encontrada'})

    def do_POST(self):
        if self.path not in ('/api/productos', '/api/movimientos'):
            return self.send(404, {'error':'Ruta no encontrada'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                raise ValueError('Solicitud vacía o demasiado grande')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Se requiere un objeto JSON')
            sku = data.get('sku', '')
            if not isinstance(sku, str) or not 1 <= len(sku.strip()) <= 30:
                raise ValueError('SKU requerido, máximo 30 caracteres')
            sku = sku.strip()
            with connect() as db:
                if self.path == '/api/productos':
                    name, qty = data.get('nombre'), data.get('cantidad')
                    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
                        raise ValueError('Nombre requerido, máximo 100 caracteres')
                    if type(qty) is not int or qty < 0:
                        raise ValueError('Cantidad debe ser un entero no negativo')
                    db.execute('INSERT INTO productos VALUES (?,?,?)', (sku, name.strip(), qty))
                    return self.send(201, {'mensaje':'Producto registrado', 'sku':sku})
                delta = data.get('cambio')
                if type(delta) is not int or delta == 0:
                    raise ValueError('Cambio debe ser un entero distinto de cero')
                cur = db.execute('UPDATE productos SET cantidad=cantidad+? WHERE sku=? AND cantidad+?>=0', (delta,sku,delta))
                if cur.rowcount != 1:
                    raise ValueError('Producto inexistente o stock insuficiente')
            self.send(200, {'mensaje':'Movimiento registrado'})
        except sqlite3.IntegrityError:
            self.send(409, {'error':'SKU duplicado o cantidad inválida'})
        except (ValueError, TypeError, json.JSONDecodeError) as err:
            self.send(400, {'error':str(err)})

def make_server(port=8000):
    with connect():
        pass
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)

if __name__ == '__main__':
    print('Inventario disponible en http://127.0.0.1:8000', flush=True)
    make_server().serve_forever()
