from django.urls import path
from ninja import NinjaAPI

from api.v1.mail import service_router
from api.v1.user import user_router

api = NinjaAPI(
    title='Email Bot API',
    description='API for Email Bot',
)

api.add_router('/user', user_router)
api.add_router('/email-domain', service_router)

urlpatterns = [
    path('', api.urls),
]
