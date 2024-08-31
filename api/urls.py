from django.urls import path,include,re_path
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, EmployeeViewSet


router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]