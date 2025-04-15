<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class CertificationBodyController extends Controller
{
    public function index()
    {
        return view('certification_body.dashboard');
    }
}
