"""
from django.test import TestCase
from .models import PropuestaCapacitacion
from django.contrib.auth.models import User, Group

class PropuestaCapacitacionIntegracionTestCase(TestCase):
    def test_realizar_propuesta_capacitacion(self):
        # Precondiciones
        # Existe una cuenta de usuario registrada en el sistema.
        # El usuario se encuentra autenticado con sesión activa.
        self.grupo = Group.objects.create(name='Instructores')
        self.usuario = User.objects.create_user(username='usuario', password='usuario123')
        self.usuario.groups.add(self.grupo)
        self.client.login(username='usuario', password='usuario123')


        # El usuario envía una solicitud de acceso (solicitud HTTP GET) a la ruta encargada del registro de propuestas de capacitación.
        respuesta = self.client.get('/propuestas/crear/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'app_inscripciones/app_propuestas_form.html')

        # El usuario completa los campos con la información requerida y presiona el botón de envío (solicitud HTTP POST a la ruta de guardado).
        datos_propuesta = {
            'titulo': 'Propuesta de Capacitación en Django ciclo 3 Pruebas y Despliegue',
            'objetivo': 'Capacitar a desarrolladores web en el framework Django',
            'justificacion': 'Demanda creciente de desarrolladores Django en el mercado laboral',
        }
        respuesta_post = self.client.post('/propuestas/crear/', datos_propuesta)

        # Los datos recibidos del formulario se usan para crear un nuevo objeto PropuestaCapacitacion en la base de datos.
        self.assertEqual(PropuestaCapacitacion.objects.count(), 1)
        propuesta_creada = PropuestaCapacitacion.objects.first()
        self.assertEqual(propuesta_creada.titulo, 'Propuesta de Capacitación en Django')
        self.assertEqual(propuesta_creada.descripcion, 'Capacitación para desarrolladores web')
        
"""   