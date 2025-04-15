<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class EnsureSuperAdmin
{
    public function handle(Request $request, Closure $next)
    {
        dd('Middleware executed');

        if (!Auth::check() || !Auth::user()->roles->contains('name', 'Super Admin')) {
            abort(403, 'Unauthorized action.');
        }

        return $next($request);
    }
}
