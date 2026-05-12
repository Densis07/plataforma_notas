import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect("notas.db")
c = conn.cursor()

print("🔎 Verificando base de datos...\n")

# Listar tablas
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = c.fetchall()
print("Tablas encontradas:", tablas)

# Verificar contenido de Materias
print("\n📚 Materias registradas:")
try:
    c.execute("SELECT * FROM Materias;")
    for fila in c.fetchall():
        print(fila)
except Exception as e:
    print("⚠️ Error al consultar Materias:", e)

# Verificar contenido de Estudiantes
print("\n👨‍🎓 Estudiantes registrados:")
try:
    c.execute("SELECT * FROM Estudiantes;")
    for fila in c.fetchall():
        print(fila)
except Exception as e:
    print("⚠️ Error al consultar Estudiantes:", e)

# Verificar contenido de Docentes
print("\n👩‍🏫 Docentes registrados:")
try:
    c.execute("SELECT * FROM Docentes;")
    for fila in c.fetchall():
        print(fila)
except Exception as e:
    print("⚠️ Error al consultar Docentes:", e)

# Verificar si hay notas
print("\n📝 Notas registradas:")
try:
    c.execute("SELECT * FROM Notas;")
    for fila in c.fetchall():
        print(fila)
except Exception as e:
    print("⚠️ Error al consultar Notas:", e)

conn.close()
print("\n✅ Verificación completada.")
