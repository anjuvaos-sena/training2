from django.test import TestCase
from app_convocatorias.models import Convocatoria
from app_convocatorias.views import _datos_convocatoria
from django.contrib.auth.models import User, Group

class ConvocatoriaTestCase(TestCase):
    def test_crear_convocatoria(self):
        convocatoria = Convocatoria.objects.create(
            titulo = "Curso de Python Avanzado",
            area = "Tecnología",
            descripcion = "Capacitación en desarrollo backend",
            fecha_inicio = "2026-10-01",
            fecha_final = "2026-10-15",
            ciudad = "Bogotá",
            cupos_totales = 30,
        )
        self.assertEqual(convocatoria.titulo, "Curso de Python Avanzado")
        self.assertEqual(convocatoria.cupos_asignados, 0)
        self.assertEqual(convocatoria.estado, "Borrador")

    def test_rechazar_convocatoria_sin_titulo(self):
        datos = {
            'titulo': '',
            'area': 'Tecnología',
            'descripcion': 'Prueba incompletitud',
            'fecha_inicio': '2026-10-01',
            'fecha_final': '2026-10-15',
            'ciudad': 'Medellín',
            'cupos_totales': '20',
        }

        campos, fecha_inicio, fecha_final, cupos_totales, errores = (
            _datos_convocatoria(None, datos)
        )

        self.assertEqual(campos['titulo'], '')
        self.assertEqual(fecha_inicio.isoformat(), '2026-10-01')
        self.assertEqual(fecha_final.isoformat(), '2026-10-15')
        self.assertEqual(cupos_totales, 20)
        self.assertEqual(errores['titulo'], 'Este campo es obligatorio.')
        self.assertEqual(Convocatoria.objects.count(), 0)