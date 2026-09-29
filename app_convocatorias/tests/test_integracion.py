from django.test import TestCase
from app_convocatorias.models import Convocatoria
from django.contrib.auth.models import User, Group


class ConvocatoriaIntegracionTestCase(TestCase):
    def setUp(self):
        #Precondiciones
        #Existe una cuenta de administrador registrada en el sistema.
        #El usuario se encuentra autenticado con sesión activa de administrador.
        self.grupo = Group.objects.create(name='Administradores')
        self.usuario_admin = User.objects.create_user(username='admin', password='admin123')
        self.usuario_admin.groups.add(self.grupo)
        self.client.login(username='admin', password='admin123')

    def test_crear_convocatoria_integracion(self):
        #El administrador envía una solicitud de acceso (solicitud HTTP GET) a la ruta encargada del registro de convocatorias.
        #Verificación: El sistema procesa la solicitud en la vista correspondiente, confirma la sesión del usuario y responde enviando la plantilla HTML con el formulario de registro limpio.
        respuesta = self.client.get('/convocatorias/crear/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'app_convocatorias/app_convocatorias_form.html')

        #El administrador completa los campos con la información requerida y presiona el botón de envío (solicitud HTTP POST a la ruta de guardado
        #Verificación: La vista recibe la información, valida que todos los datos recibidos sean correctos y completos, y le indica al modelo de datos que registre la información.
        
        datos_convocatoria = {
            'titulo': 'Curso Python Avanzado',
            'area': 'Tecnología',
            'descripcion': 'Capacitación en desarrollo backend',
            'fecha_inicio': '2026-10-01',
            'fecha_final': '2026-10-15',  # Nombre del campo según tu vista
            'ciudad': 'Bogotá',
            'cupos_totales': '30',
        }
        #Se envian los datos de la convocatoria mediante una solicitud POST a la ruta de creación de convocatorias.
        respuesta_post = self.client.post('/convocatorias/crear/', datos_convocatoria)
        #Los datos recibidos del formulario se usan para crear un nuevo objeto Convocatoria en la base de datos.
        self.assertEqual(Convocatoria.objects.count(), 1)
        convocatoria_creada = Convocatoria.objects.first()
        self.assertEqual(convocatoria_creada.titulo, 'Curso Python Avanzado')
        self.assertEqual(convocatoria_creada.area, 'Tecnología')

        self.assertEqual(convocatoria_creada.estado, 'Borrador')
        self.assertEqual(convocatoria_creada.cupos_asignados, 0)
        self.assertEqual(respuesta_post.status_code, 302)
        self.assertRedirects(respuesta_post, '/convocatorias/')
        respuesta_dashboard = self.client.get('/convocatorias/')
        self.assertContains(respuesta_dashboard, 'Curso Python Avanzado')

    def test_rechazar_convocatoria_con_titulo_vacio(self):
        datos_convocatoria = {
            'titulo': '',
            'area': 'Tecnología',
            'descripcion': 'Prueba incompletitud',
            'fecha_inicio': '2026-10-01',
            'fecha_final': '2026-10-15',
            'ciudad': 'Medellín',
            'cupos_totales': '20',
        }

        respuesta = self.client.post('/convocatorias/crear/', datos_convocatoria)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(
            respuesta,
            'app_convocatorias/app_convocatorias_form.html',
        )
        self.assertContains(respuesta, 'Revisa el formulario.')
        self.assertContains(respuesta, 'Este campo es obligatorio.')
        self.assertContains(respuesta, 'id="titulo"')
        self.assertEqual(Convocatoria.objects.count(), 0)