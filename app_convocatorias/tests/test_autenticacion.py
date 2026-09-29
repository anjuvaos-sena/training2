from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class AutenticacionViewTestCase(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

    def crear_usuario(self, username, group_name=None):
        user = User.objects.create_user(username=username, password='clave-segura')
        if group_name:
            group = Group.objects.create(name=group_name)
            user.groups.add(group)
        return user

    def test_get_login_renderiza_formulario(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_autenticacion/login.html')
        self.assertContains(response, 'Iniciar sesión')

    def test_login_rechaza_credenciales_invalidas(self):
        response = self.client.post(
            self.login_url,
            {'username': 'usuario-inexistente', 'password': 'incorrecta'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app_autenticacion/login.html')
        self.assertContains(response, 'El usuario o la contrasena no son validos.')

    def test_login_redirige_administrador(self):
        self.crear_usuario('admin', 'Administradores')

        response = self.client.post(
            self.login_url,
            {'username': ' admin ', 'password': 'clave-segura'},
        )

        self.assertRedirects(response, reverse('app_convocatorias:gestionar_convocatorias'))

    def test_login_redirige_instructor(self):
        self.crear_usuario('instructor', 'Instructores')

        response = self.client.post(
            self.login_url,
            {'username': 'instructor', 'password': 'clave-segura'},
        )

        self.assertRedirects(response, reverse('app_inscripciones:capacitaciones_publicadas'))

    def test_login_redirige_a_login_si_no_tiene_grupo(self):
        self.crear_usuario('sin-grupo')

        response = self.client.post(
            self.login_url,
            {'username': 'sin-grupo', 'password': 'clave-segura'},
        )

        self.assertRedirects(response, self.login_url)

    def test_logout_cierra_sesion_y_redirige_al_login(self):
        self.crear_usuario('usuario-activo')
        self.client.login(username='usuario-activo', password='clave-segura')

        response = self.client.get(self.logout_url)

        self.assertRedirects(response, self.login_url)
        self.assertNotIn('_auth_user_id', self.client.session)