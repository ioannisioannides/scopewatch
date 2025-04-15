<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## ScopeWatch

ScopeWatch is a Laravel-based application designed to manage certifications, audits, and compliance workflows. The application is now located in the root directory of this repository.

## Features
- User registration and login.
- Role-based access control (RBAC).
- Group management for Certification Bodies, Organizations, and Consulting Firms.
- Certification and audit workflows.
- Public certification search interface.

## Setup Instructions
1. Install dependencies:
   ```bash
   composer install
   npm install
   ```
2. Set up the environment file:
   ```bash
   cp .env.example .env
   ```
3. Generate the application key:
   ```bash
   php artisan key:generate
   ```
4. Run migrations and seed the database:
   ```bash
   php artisan migrate --seed
   ```
5. Start the development server:
   ```bash
   php artisan serve
   ```

## Folder Structure
- `app/`: Contains the core application logic.
- `bootstrap/`: Handles application bootstrapping.
- `config/`: Configuration files.
- `database/`: Migrations, seeders, and database files.
- `public/`: Publicly accessible files.
- `resources/`: Views, CSS, and JavaScript assets.
- `routes/`: Application routes.
- `storage/`: Logs, cache, and other storage.
- `tests/`: Unit and feature tests.
- `vendor/`: Composer dependencies.

## Future Enhancements
- Integration with external systems.
- Advanced analytics and dashboards.
- Multi-language support.

## License
This project is licensed under the MIT License.
