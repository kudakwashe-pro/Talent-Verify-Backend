from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, EmployeeViewSet
from .views import upload_employees

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'employees', EmployeeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('employees/upload/', EmployeeViewSet.as_view({'post': 'upload_bulk'}), name='upload-bulk-employees'),
    path('employees/upload/', upload_employees),

]