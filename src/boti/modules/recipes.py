# modules/recipes.py — Recetario con SQLite

import sqlite3
from config import DB_PATH

RECETAS_INICIALES = [
    (
        "Tortilla española",
        "4 huevos, 3 patatas medianas, 1 cebolla, aceite de oliva, sal",
        "1. Pela y corta las patatas en láminas finas.\n"
        "2. Fríe las patatas con la cebolla a fuego medio hasta que estén blandas (15 min).\n"
        "3. Escurre el aceite. Bate los huevos con sal y mezcla con las patatas.\n"
        "4. Cuaja en sartén a fuego medio-bajo tapada (4 min).\n"
        "5. Da la vuelta con un plato y cuaja 3 min más.",
        "huevo, patata, española, tradicional",
    ),
    (
        "Pasta al pesto",
        "200g pasta, 1 manojo de albahaca, 2 dientes de ajo, "
        "30g piñones, 50g parmesano, 60ml aceite de oliva, sal",
        "1. Cuece la pasta en agua salada según el paquete.\n"
        "2. Tritura albahaca, ajo, piñones y parmesano.\n"
        "3. Añade aceite poco a poco hasta obtener una salsa homogénea.\n"
        "4. Mezcla con la pasta escurrida y sirve.",
        "pasta, italiana, rápida, albahaca",
    ),
    (
        "Gazpacho",
        "1kg tomates maduros, 1 pepino, 1 pimiento rojo, "
        "1 diente de ajo, 4 cdas aceite de oliva, 2 cdas vinagre, sal",
        "1. Trocea todos los vegetales.\n"
        "2. Bate con batidora hasta obtener crema fina.\n"
        "3. Añade aceite, vinagre y sal. Prueba y ajusta.\n"
        "4. Cuela si quieres textura más fina.\n"
        "5. Refrigera mínimo 1 hora antes de servir.",
        "tomate, fría, verano, vegetariana, sin cocción",
    ),
    (
        "Arroz con leche",
        "200g arroz, 1L leche, 150g azúcar, 1 rama canela, "
        "piel de limón, canela en polvo",
        "1. Pon la leche a calentar con la canela y la piel de limón.\n"
        "2. Cuando hierva añade el arroz y baja el fuego.\n"
        "3. Cocina 30-35 min removiendo frecuentemente.\n"
        "4. Añade el azúcar en los últimos 5 min.\n"
        "5. Sirve frío con canela en polvo por encima.",
        "postre, dulce, leche, arroz, tradicional",
    ),
    (
        "Lentejas con verduras",
        "300g lentejas, 1 zanahoria, 1 puerro, 1 patata, "
        "2 dientes de ajo, 1 hoja de laurel, pimentón, aceite, sal",
        "1. Pica todas las verduras en trozos medianos.\n"
        "2. Sofríe ajo, puerro y zanahoria en aceite 5 min.\n"
        "3. Añade las lentejas, la patata, el laurel y pimentón.\n"
        "4. Cubre con agua y cocina 35-40 min a fuego medio.\n"
        "5. Ajusta de sal antes de servir.",
        "legumbre, cuchara, invierno, económica, vegetariana",
    ),
]


def _conexion():
    return sqlite3.connect(DB_PATH)


def inicializar():
    """Crea la tabla y carga recetas iniciales si está vacía."""
    con = _conexion()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL,
            ingredientes TEXT,
            pasos        TEXT,
            etiquetas    TEXT,
            creada       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("SELECT COUNT(*) FROM recetas")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO recetas (nombre, ingredientes, pasos, etiquetas) VALUES (?,?,?,?)",
            RECETAS_INICIALES,
        )
    con.commit()
    con.close()


# ── Comandos ──────────────────────────────────────────────────────────────────

def buscar(texto: str) -> str:
    """Busca recetas por nombre, ingredientes o etiquetas."""
    IGNORAR = {"receta", "de", "la", "el", "un", "una", "para", "con",
               "cómo", "hacer", "hago", "preparo", "cocinar", "plato",
               "cómo", "se", "hace"}

    palabras = [p for p in texto.lower().split()
                if p not in IGNORAR and len(p) > 2]

    con = _conexion()
    cur = con.cursor()

    if not palabras:
        cur.execute("SELECT nombre, ingredientes, pasos FROM recetas LIMIT 3")
    else:
        cond = " OR ".join(
            ["nombre LIKE ? OR ingredientes LIKE ? OR etiquetas LIKE ?"] * len(palabras)
        )
        vals = [v for p in palabras for v in (f"%{p}%", f"%{p}%", f"%{p}%")]
        cur.execute(f"SELECT nombre, ingredientes, pasos FROM recetas WHERE {cond} LIMIT 3", vals)

    filas = cur.fetchall()
    con.close()

    if not filas:
        return (f"No encontré ninguna receta con «{texto}».\n"
                "Prueba con otro ingrediente o escribe «mis recetas» para ver todas.")

    if len(filas) == 1:
        return _formato_receta(*filas[0])

    opciones = "\n".join(f"  {i+1}. {f[0]}" for i, f in enumerate(filas))
    return f"Encontré varias recetas:\n{opciones}\n\nEscribe el nombre exacto para verla completa."


def listar() -> str:
    """Devuelve la lista completa de recetas."""
    con = _conexion()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, etiquetas FROM recetas ORDER BY nombre")
    filas = cur.fetchall()
    con.close()

    if not filas:
        return "No hay recetas guardadas aún. Prueba «nueva receta» para añadir una."

    lineas = ["📚 Recetario completo:\n"]
    for fid, nombre, etiquetas in filas:
        tag = f" — {etiquetas}" if etiquetas else ""
        lineas.append(f"  {fid}. {nombre}{tag}")
    return "\n".join(lineas)


def añadir_interactivo() -> str:
    """Mensaje guía para añadir una receta paso a paso desde la UI."""
    return (
        "Para añadir una receta escribe en este formato:\n\n"
        "nueva receta\n"
        "nombre: Nombre del plato\n"
        "ingredientes: ingrediente1, ingrediente2...\n"
        "pasos: 1. Paso uno. 2. Paso dos...\n"
        "etiquetas: pasta, italiana, rápida"
    )


def guardar_desde_texto(texto: str) -> str:
    """Parsea y guarda una receta desde texto con formato nombre/ingredientes/pasos."""
    lineas = {l.split(":", 1)[0].strip().lower(): l.split(":", 1)[1].strip()
              for l in texto.splitlines() if ":" in l}

    nombre       = lineas.get("nombre", "")
    ingredientes = lineas.get("ingredientes", "")
    pasos        = lineas.get("pasos", "")
    etiquetas    = lineas.get("etiquetas", "")

    if not nombre or not pasos:
        return "Faltan datos. Necesito al menos «nombre» y «pasos»."

    con = _conexion()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO recetas (nombre, ingredientes, pasos, etiquetas) VALUES (?,?,?,?)",
        (nombre, ingredientes, pasos, etiquetas),
    )
    con.commit()
    con.close()
    return f"✅ Receta «{nombre}» guardada correctamente."


# ── Formato ───────────────────────────────────────────────────────────────────

def _formato_receta(nombre: str, ingredientes: str, pasos: str) -> str:
    return (
        f"🍳 {nombre}\n\n"
        f"Ingredientes:\n{ingredientes}\n\n"
        f"Preparación:\n{pasos}"
    )