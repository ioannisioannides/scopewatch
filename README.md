![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/ioannisioannides/scopewatch?utm_source=oss&utm_medium=github&utm_campaign=ioannisioannides%2Fscopewatch&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

# Scopewatch

Scopewatch is an open-source platform for managing compliance and certifications. It unites organizations, certifying bodies, and auditors in a privacy-first workflow, fostering trust, accountability, and transparency.

## Why Scopewatch?

- **Centralized Compliance:** Manage multiple frameworks in one place.
- **Transparency & Trust:** Provide public verification of certificates and audits.
- **Privacy by Design:** Collect minimal personal data; keep sensitive info secure.
- **Open-Source Collaboration:** Encourage community contributions and improvements.

## System Architecture

Scopewatch connects multiple stakeholders in the compliance ecosystem:

- **Organizations** seeking certifications
- **Certification Bodies** conducting audits and issuing certificates
- **Auditors** gathering evidence and generating findings
- **Consultants** assisting organizations with compliance
- **Public Users** who can verify certificates

For a detailed overview of the system architecture, please see the [System Architecture Overview](docs/system_architecture_overview.md).

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (`virtualenv` or `venv`)

### Automated Setup (Recommended)

We provide an automated setup script for quickly preparing your development environment:

```bash
# Clone the repository
git clone https://github.com/ioannisioannides/scopewatch.git
cd scopewatch

# Run the setup script
./setup_dev_environment.py
```

The script will:
1. Check for required dependencies
2. Create a virtual environment
3. Install required packages
4. Set up a `.env` file
5. Run database migrations
6. Offer to create a superuser

### Manual Setup

If you prefer to set up manually, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ioannisioannides/scopewatch.git
   cd scopewatch
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Using virtualenv
   virtualenv .venv

   # On Windows
   .\.venv\Scripts\activate

   # On Unix/MacOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Set Up Environment Variables**
   ```bash
   # Copy the example .env file
   cp .env.example .env

   # Edit the .env file with your settings
   ```

5. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Development Server

```bash
python manage.py runserver
```

Access the application at http://127.0.0.1:8000/ and the admin interface at http://127.0.0.1:8000/admin/

## Development Guidelines

### Project Structure

The project follows an organized structure to maintain clarity and separation of concerns:

- `apps/` - Django applications organized by domain
  - `audits/` - Audit management
  - `certification_bodies/` - Certification bodies and auditors
  - `consultants/` - Consultant management
  - `management/` - Management commands application
  - `organizations/` - Organization management
  - `public/` - Public certificate verification portal
  - `utils/` - Shared utility modules
- `backups/` - Database and migration backups
  - `db/` - Database backup files
  - `migrations/` - Migration backup files
- `docs/` - Project documentation
- `scripts/` - Utility scripts
  - `migrations/` - Migration management scripts
  - `utils/` - General utility scripts
- `scopewatch/` - Core project settings
- `templates/` - HTML templates

For more detailed information about the project structure, see our [Project Structure Documentation](docs/project_structure.md).

### Running Tests

```bash
# Run all tests
pytest

# Generate coverage report
pytest --cov=apps
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Run linting
pylint apps

# Format code
black apps
isort apps
```

## Deployment

For production deployment, please ensure:

1. Set `DEBUG=False` in your environment
2. Provide a secure `DJANGO_SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain name
4. Configure PostgreSQL database settings
5. Set up proper web server (Nginx, Apache, etc.)

See our [deployment guide](docs/deployment.md) for more detailed instructions (coming soon).

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

For major changes, please [open an issue](../../issues) first to discuss your proposed modifications.

## License

This project is licensed under the terms of the license included in the [LICENSE](LICENSE) file.

## Contact

For questions or support, please open an issue on the GitHub repository.
