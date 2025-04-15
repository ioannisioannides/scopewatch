<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\SuperAdminController;
use App\Http\Controllers\CertificationBodyController;

Route::get('/', function () {
    return view('welcome');
});

// Authentication Routes
Route::get('/register', [AuthController::class, 'showRegistrationForm'])->name('register');
Route::post('/register', [AuthController::class, 'register']);
Route::get('/login', [AuthController::class, 'showLoginForm'])->name('login');
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

// Dashboard Route
Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard')->middleware('auth');

// Super Admin Dashboard Route
Route::get('/super-admin/dashboard', [SuperAdminController::class, 'index'])->name('super-admin.dashboard')->middleware(['auth', 'superadmin']);

// Certification Body Dashboard Route
Route::get('/certification-body/dashboard', [CertificationBodyController::class, 'index'])->name('certification-body.dashboard')->middleware(['auth', 'certbodyadmin']);
