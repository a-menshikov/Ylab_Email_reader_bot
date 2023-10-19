from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from ninja import Router

from email_service.service import ServiceEmailDomain
from email_service.schemas import EmailDomainList

service_router = Router(tags=['Почтовый сервис'])

domain_service = ServiceEmailDomain()


@service_router.get(
    '',
    response={HTTPStatus.OK: EmailDomainList},
    summary='Доступные почтовые сервисы',
)
async def get_services(request: HttpRequest) -> HttpResponse:
    """Получить список почтовых сервисов."""
    data = await domain_service.get_domain_list()
    return EmailDomainList(services=data)
