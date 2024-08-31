# Backend Documentation

## API Endpoints

### Authentication

- **Login**: `POST /api-token-auth/`
  - **Body**: 
    ```json
    { "username": "your_username", "password": "your_password" }
    ```
  - **Response**: 
    ```json
    { "token": "your_token" }
    ```

### Companies

- **Fetch Companies**: `GET /api/companies/`
- **Create Company**: `POST /api/companies/`
  - **Body**: 
    ```json
    { "name": "Company Name" }
    ```

### Employees

- **Fetch Employees**: `GET /api/employees/`
- **Create Employee**: `POST /api/employees/`
  - **Body**: 
    ```json
    { "name": "Employee Name", "company": "Company ID" }
    ```
- **Upload Employees**: `POST /api/employees/upload/`
  - **Body**: FormData containing the file to upload.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
