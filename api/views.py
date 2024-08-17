from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser
from .models import Company, Employee
from .serializers import CompanySerializer, EmployeeSerializer
import pandas as pd
from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.decorators import api_view,APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Company, Employee
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self, request):
          
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response(status=status.HTTP_400_BAD_REQUEST)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Handle single employee creation
        return super().create(request, *args, **kwargs)

    def upload_bulk(self, request):
        # Handle bulk upload from file
        file = request.FILES['file']
        file_path = default_storage.save(file.name, file)
        data = pd.read_excel(file_path)  # Using pandas to read Excel file

        for _, row in data.iterrows():
            Employee.objects.create(
                company_id=row['company_id'],
                name=row['name'],
                employee_id=row['employee_id'],
                department=row['department'],
                role=row['role'],
                date_started=row['date_started'],
                date_left=row['date_left'],
                duties=row['duties']
            )

        return Response({"success": "Employees uploaded successfully."}, status=201)
    
#@api_view(['POST'])
#def register(request):
#    username = request.data.get('username')
#    password = request.data.get('password')
#
#    if User.objects.filter(username=username).exists():
#        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
#
#    user = User.objects.create_user(username=username, password=password)
#    Token.objects.create(user=user)

#@api_view(['POST'])
#def login(request):
#    username = request.data.get('username')
#    password = request.data.get('password')
#    user = authenticate(username=username, password=password)
#
#    if user is not None:
#        token, created = Token.objects.get_or_create(user=user)
#        return Response({'token': token.key}, status=status.HTTP_200_OK)
#    return Response({'error': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_employees(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    elif file.name.endswith('.txt'):
        data = pd.read_csv(file, sep='\t')
    else:
        return Response({'error': 'File format not supported.'}, status=status.HTTP_400_BAD_REQUEST)

    for _, row in data.iterrows():
        Employee.objects.create(
            company=Company.objects.get(name=row['company_name']),
            name=row['employee_name'],
            employee_id=row['employee_id'],
            department=row['department'],
            role=row['role'],
            date_started=row['date_started'],
            date_left=row.get('date_left'),
            duties=row['duties']
        )

    return Response({'message': 'Employees uploaded successfully!'}, status=status.HTTP_201_CREATED)