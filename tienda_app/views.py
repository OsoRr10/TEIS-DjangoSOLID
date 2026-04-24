import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from .domain.logic import CalculadorImpuestos
from .infra.factories import PaymentFactory
from .models import Libro, Inventario, Orden
from .services import CompraService


# ─── TUTORIAL 01: FBV Spaghetti (evidencia del punto de partida) ──────────────
def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)
    if request.method == 'POST':
        inventario = Inventario.objects.get(libro=libro)
        if inventario.cantidad > 0:
            total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
            with open("pagos_manuales.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Pago FBV: ${total}\n")
            inventario.cantidad -= 1
            inventario.save()
            Orden.objects.create(libro=libro, total=total)
            return HttpResponse(f"Compra exitosa: {libro.titulo}")
        return HttpResponse("Sin stock", status=400)
    total_estimado = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
    return render(request, 'tienda_app/compra_rapida.html', {
        'libro': libro, 'total': total_estimado
    })


# ─── TUTORIAL 01→02: CBV final (usa Factory desde Tutorial 02) ────────────────
class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un 'Portero': recibe la petición y delega al servicio.
    """
    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()  # Factory Method (Tutorial 02)
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(request, self.template_name, {
                'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                'total': total,
            })
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)