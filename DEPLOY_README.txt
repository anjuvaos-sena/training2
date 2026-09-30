DESPLIEGUE EN RENDER GRATUITO MEDIANTE DOCKER

Requisitos
----------
- El proyecto debe estar en un repositorio GitHub accesible desde Render.
- Una base PostgreSQL persistente con una URL de conexion compatible con
  dj-database-url. Puede ser un servicio PostgreSQL gratuito externo; revisa
  sus limites y politica de retencion antes de usarlo en produccion.
- Un proyecto Supabase con un bucket de Storage y credenciales S3.
- Una clave SECRET_KEY larga, aleatoria y privada.

Genera una clave desde una terminal con:
python -c "import secrets; print(secrets.token_urlsafe(64))"
Guarda el resultado directamente como SECRET_KEY en Render; no lo agregues al
repositorio.

1. Preparar PostgreSQL
----------------------
1. Crea una base de datos PostgreSQL en un proveedor que permita el nivel
   gratuito y que admita conexiones desde Render.
2. Copia su URL PostgreSQL completa (postgres:// o postgresql://). No la
   publiques ni la guardes en el repositorio.
3. Verifica los limites de almacenamiento, conexiones, expiracion y copias de
   seguridad del proveedor. Render gratuito no conserva una SQLite incluida
   en el contenedor.

2. Preparar los archivos de Supabase
------------------------------------
1. En Supabase, crea un bucket llamado media (o el nombre que usaras abajo).
2. Habilita acceso/lectura publica si la aplicacion debe mostrar los PDF a
   cualquier visitante. Para documentos privados, define politicas de acceso
   apropiadas y prueba el acceso firmado; no hagas publico un bucket sensible.
3. En la configuracion S3 de Storage, genera una access key y una secret key
   con permisos sobre el bucket.
4. El endpoint S3 tiene este formato:
   https://<project-ref>.supabase.co/storage/v1/s3
   No uses la URL de la API REST ni la URL publica del bucket como endpoint.
5. Conserva el project ref, endpoint, access key y secret key. La secret key
   solo se introduce como variable secreta en Render.

3. Crear el servicio web
------------------------
1. Sube los cambios del proyecto a GitHub, incluyendo Dockerfile y
   .dockerignore. No subas .env, claves, la base SQLite ni archivos privados.
2. Inicia sesion en Render y elige New > Web Service; conecta el repositorio.
3. Selecciona el branch a desplegar y el runtime Docker. Deja Dockerfile Path
   como ./Dockerfile y Docker Context Directory como . (raiz del proyecto).
4. Elige la instancia Free. No configures Build Command ni Start Command: el
   Dockerfile ya instala dependencias, recopila estaticos, aplica migraciones y
   ejecuta Gunicorn.
5. Antes de crear el servicio, agrega las variables del siguiente paso.

4. Configurar variables de entorno
----------------------------------
Configura estos valores en Environment del servicio Render:

- DEBUG = False
- SECRET_KEY = una cadena aleatoria larga, unica y secreta
- DATABASE_URL = URL de PostgreSQL del paso 1
- SUPABASE_ENDPOINT = https://<project-ref>.supabase.co/storage/v1/s3
- SUPABASE_ACCESS_KEY = access key S3 de Supabase
- SUPABASE_SECRET_KEY = secret key S3 de Supabase
- SUPABASE_BUCKET = media (o el nombre real del bucket)

No agregues comillas alrededor de los valores. Marca como secretos SECRET_KEY,
DATABASE_URL, SUPABASE_ACCESS_KEY y SUPABASE_SECRET_KEY. Render proporciona
RENDER_EXTERNAL_HOSTNAME automaticamente; Django lo usa para ALLOWED_HOSTS y
CSRF_TRUSTED_ORIGINS. Si se usa un dominio personalizado, agregalo tambien a
ALLOWED_HOSTS y agrega su origen https:// a CSRF_TRUSTED_ORIGINS.

La aplicacion no iniciara si falta SECRET_KEY, DATABASE_URL o alguna de las
credenciales S3 obligatorias. Esto evita una instalacion que pierda datos al
reiniciar el servicio.

5. Desplegar y verificar
------------------------
1. Crea el Web Service. Render construira la imagen desde el Dockerfile.
2. Abre Events/Logs y espera a que termine el build y el despliegue. En el
   primer arranque se aplican las migraciones y Gunicorn escucha en PORT.
3. Abre la URL *.onrender.com asignada al servicio. La primera solicitud puede
   tardar porque las instancias gratuitas pueden suspenderse cuando no reciben
   trafico.
4. Prueba inicio de sesion, formularios y carga/descarga de PDF. Comprueba en
   PostgreSQL que los registros sobreviven un redeploy y en Supabase que los
   archivos siguen disponibles.
5. Crea el superusuario desde la consola del servicio Render (Shell), si el
   plan ofrece Shell, ejecutando:
   python manage.py createsuperuser
   Si no hay Shell disponible, ejecuta ese comando localmente con las mismas
   variables apuntando a DATABASE_URL y al entorno de produccion. No uses la
   base SQLite local para crear el usuario.

Notas operativas
----------------
- Cada despliegue vuelve a ejecutar migrate. No borres ni reemplaces la base
  PostgreSQL al desplegar.
- El sistema de archivos del servicio gratuito es efimero. No uses media/ ni
  db.sqlite3 como almacenamiento de produccion.
- El backend de correo actual es de consola; los correos no se entregan a
  destinatarios. Si el sistema necesita enviar correos, configura un proveedor
  SMTP y adapta MAILERS en pr_eni/settings.py con sus credenciales privadas.
- Render gratuito tiene limites y condiciones que pueden cambiar. Revisa los
  limites vigentes de Render, del proveedor PostgreSQL y de Supabase.
- Para diagnosticos, revisa los logs del build y del runtime en Render. Errores
  que indican una variable obligatoria faltante se corrigen en Environment y
  requieren un nuevo deploy.