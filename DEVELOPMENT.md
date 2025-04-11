# Scopewatch Development Guide

This guide explains how to set up your development environment for working on the Scopewatch project.

## Getting Started

### Option 1: Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/scopewatch.git
   cd scopewatch
   ```

2. **Create a branch for your changes**:
   ```bash
   # Create a new branch from development
   git checkout development
   git pull
   git checkout -b feature/your-feature-name
   ```

3. **Start the development environment**:
   ```bash
   # Build and start the Docker containers
   docker-compose up -d
   ```

4. **Access the application**:
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

### Option 2: Local Setup

1. **Set up the Python environment**:
   ```bash
   # Run the setup script
   python setup_dev_environment.py
   ```

2. **Activate the virtual environment**:
   ```bash
   # On Windows:
   .\.venv\Scripts\activate

   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Development Workflow

1. **Create a feature branch from development**:
   ```bash
   git checkout development
   git pull
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and run tests**:
   ```bash
   # Run tests
   pytest

   # Run linting
   pylint --rcfile=pylintrc $(git ls-files '*.py')
   ```

3. **Commit and push your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   git push -u origin feature/your-feature-name
   ```

4. **Create a Pull Request** to merge your changes into the `development` branch:
   - Go to the GitHub repository
   - Click "Pull Requests" > "New Pull Request"
   - Set the base branch to `development` and the compare branch to your feature branch
   - Add a description of your changes
   - Submit the Pull Request

## Project Structure

We've organized the project structure to improve maintainability:

### Key Directories

- `apps/` - Django applications organized by domain functionality
- `scripts/` - Utility scripts for development and maintenance
  - `migrations/` - Scripts for managing database migrations
  - `utils/` - General utility scripts
- `backups/` - Organized backup storage
  - `db/` - Database backups
  - `migrations/` - Migration backups
- `docs/` - Project documentation

### Working with Management Commands

Django management commands are centralized in the `apps/management/commands/` directory. Common commands include:

```bash
# Optimize SQLite database
python manage.py optimize_sqlite --all

# Backup SQLite database
python manage.py backup_sqlite

# Create or update a superuser
python manage.py create_or_update_superuser
```

For more details on the project structure, refer to the [Project Structure Documentation](docs/project_structure.md).

## Database Migrations

When making changes to models:

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Environment Variables

Copy `.env.example` to `.env` and update the values as needed for your local development.

## Code Quality

Before submitting a PR, ensure:
- All tests pass
- No linting errors
- Code is formatted according to project conventions

## Production Release Process

1. Changes are merged into `development` branch
2. Tests and CI checks pass on `development` branch
3. Create a PR from `development` to `main`
4. After approval, code is merged to `main`
5. GitHub Actions automatically deploy to production
