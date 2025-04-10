# ScopeWatch Project Structure

This document provides an overview of the ScopeWatch project's file and directory structure, helping developers navigate and understand the codebase organization.

## Directory Structure

```
scopewatch/
├── apps/                      # Django applications directory
│   ├── audits/                # Audit management application
│   ├── certification_bodies/  # Certification bodies application
│   ├── consultants/           # Consultants application
│   ├── management/            # Management commands application
│   │   └── commands/          # Django management commands
│   ├── organizations/         # Organizations application
│   ├── public/                # Public-facing application
│   └── utils/                 # Utility modules
├── backups/                   # Backup directory
│   ├── db/                    # Database backups
│   └── migrations/            # Migration backups
├── docs/                      # Documentation files
│   ├── migration_management.md
│   ├── project_structure.md   # This file
│   └── system_architecture_overview.md
├── htmlcov/                   # Coverage reports
├── logs/                      # Log files
├── scopewatch/                # Core Django project directory
│   ├── settings.py            # Main settings file
│   ├── dev_settings.py        # Development settings
│   ├── test_settings.py       # Test settings
│   ├── urls.py                # URL configuration
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
├── scripts/                   # Utility scripts directory
│   ├── migrations/            # Migration-related scripts
│   └── utils/                 # General utility scripts
├── templates/                 # Global templates directory
├── manage.py                  # Django management script
├── requirements.txt           # Production dependencies
└── requirements-dev.txt       # Development dependencies
```

## Key Components

### Applications (`apps/`)

The `apps/` directory contains all Django applications used in the project:

- **audits**: For managing audit processes, findings, and evidence
- **certification_bodies**: For certification body management and auditor assignments
- **consultants**: For consultant and consultancy firm management
- **management**: Contains Django management commands
- **organizations**: For organization management and certification tracking
- **public**: Public-facing components like certificate verification
- **utils**: Shared utility functions and helpers

### Core Project (`scopewatch/`)

The `scopewatch/` directory contains the Django project configuration files:

- **settings.py**: Main Django settings
- **urls.py**: Main URL routing configuration
- **wsgi.py/asgi.py**: Web server gateway interfaces

### Scripts (`scripts/`)

The `scripts/` directory contains utility scripts separated by purpose:

- **migrations/**: Scripts for managing and fixing migrations
- **utils/**: General utility scripts for development and maintenance

### Backups (`backups/`)

The `backups/` directory is organized into:

- **db/**: Database backup files
- **migrations/**: Migration backup files

## Development Workflow

For information on the development workflow, please refer to the [DEVELOPMENT.md](../DEVELOPMENT.md) file in the project root.