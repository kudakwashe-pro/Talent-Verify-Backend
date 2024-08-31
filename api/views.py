from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
import pandas as pd
import logging
from .models import Company, Employee
from .serializers import CompanySerializer, EmployeeSerializer

logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Save a new company instance."""
        serializer.save()

    @action(methods=["post"], detail=False)
    def upload_companies(self, request):
        """Upload companies from a file (CSV, Excel, TXT)."""
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        try:
            # Determine the file type and read the data accordingly
            if file.name.endswith(".csv"):
                data = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                data = pd.read_excel(file)
            elif file.name.endswith(".txt"):
                data = pd.read_csv(file, sep="\t")
            else:
                return Response(
                    {"error": "File format not supported."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if DataFrame is empty
            if data.empty:
                return Response(
                    {"error": "The uploaded file is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            required_fields = ["name", "registration_date", "registration_number", "address", "contact_person", "departments", "number_of_employees", "contact_phone", "email"]
            companies_to_create = []

            # Iterate through the uploaded data
            for _, row in data.iterrows():
                # Check for required fields
                missing_fields = [field for field in required_fields if field not in row]
                if missing_fields:
                    return Response(
                        {"error": f"Missing required fields: {', '.join(missing_fields)}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Create a Company instance
                companies_to_create.append(
                    Company(
                        name=row["name"],
                        registration_date=row["registration_date"],
                        registration_number=row["registration_number"],
                        address=row["address"],
                        contact_person=row["contact_person"],
                        departments=row.get("departments", {}),
                        number_of_employees=row["number_of_employees"],
                        contact_phone=row["contact_phone"],
                        email=row["email"],
                    )
                )

            # Bulk create companies if any are valid
            if companies_to_create:
                Company.objects.bulk_create(companies_to_create)

            return Response(
                {
                    "message": f"{len(companies_to_create)} companies uploaded successfully!"
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error("Error processing file: %s", str(e))
            return Response(
                {"error": "An error occurred during file processing."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Save a new employee instance."""
        serializer.save()

    @action(methods=["post"], detail=False)
    def upload_employees(self, request):
        """Upload employees from a file (CSV, Excel, TXT)."""
        if "file" not in request.FILES:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]
        try:
            # Determine the file type and read the data accordingly
            if file.name.endswith(".csv"):
                data = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                data = pd.read_excel(file)
            elif file.name.endswith(".txt"):
                data = pd.read_csv(file, sep="\t")
            else:
                return Response(
                    {"error": "File format not supported."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if DataFrame is empty
            if data.empty:
                return Response(
                    {"error": "The uploaded file is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            required_fields = ["company_name", "employee_name", "employee_id"]
            employees_to_create = []
            existing_employee_ids = set(
                Employee.objects.values_list("employee_id", flat=True)
            )

            # Iterate through the uploaded data
            for _, row in data.iterrows():
                # Check for required fields
                missing_fields = [field for field in required_fields if field not in row]
                if missing_fields:
                    return Response(
                        {"error": f"Missing required fields: {', '.join(missing_fields)}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate required values
                if pd.isnull(row.get("employee_id")) or pd.isnull(row.get("company_name")):
                    logger.warning(f"Missing required values in row: {row}. Skipping.")
                    continue

                # Check if the company exists
                try:
                    company = Company.objects.get(name=row["company_name"])
                except Company.DoesNotExist:
                    return Response(
                        {"error": f"Company '{row['company_name']}' not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Check for duplicate employee IDs
                if row["employee_id"] in existing_employee_ids:
                    logger.warning(
                        f"Duplicate employee ID '{row['employee_id']}' found. Skipping."
                    )
                    continue  # Skip adding this employee

                # Create an Employee instance
                employees_to_create.append(
                    Employee(
                        company=company,
                        name=row["employee_name"],
                        employee_id=row["employee_id"],
                        department=row.get("department"),
                        role=row.get("role"),
                        date_started=row.get("date_started"),
                        date_left=row.get("date_left"),
                        duties=row.get("duties"),
                    )
                )

            # Bulk create employees if any are valid
            if employees_to_create:
                Employee.objects.bulk_create(employees_to_create)

            return Response(
                {
                    "message": f"{len(employees_to_create)} employees uploaded successfully!"
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error("Error processing file: %s", str(e))
            return Response(
                {"error": "An error occurred during file processing."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )