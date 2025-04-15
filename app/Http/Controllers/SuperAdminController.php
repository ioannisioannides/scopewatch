<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class SuperAdminController extends Controller
{
    public function index()
    {
        $users = User::with('roles')->get();
        return view('superadmin.dashboard', compact('users'));
    }
}
