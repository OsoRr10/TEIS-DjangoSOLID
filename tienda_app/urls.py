from django.urls import path
from .api.views import CompraAPIView
from .views import CompraView, compra_rapida_fbv

urlpatterns = [
    # Tutorial 01 - FBV (evidencia spaghetti)
    path('compra-fbv/<int:libro_id>/', compra_rapida_fbv, name='compra_fbv'),

    # Tutorial 01→02 - CBV limpia con Factory
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),

    # Tutorial 03 - API REST
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]