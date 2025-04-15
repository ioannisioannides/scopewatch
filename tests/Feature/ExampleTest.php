<?php

namespace Tests\Feature;

use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * Test the home page returns a successful response.
     */
    public function testHomePageReturnsSuccessfulResponse(): void
    {
        $response = $this->get('/');
        $response->assertStatus(200);
        $response->assertSee('Welcome'); // Check if the page contains 'Welcome'
    }

    /**
     * Test the dashboard page requires authentication.
     */
    public function testDashboardRequiresAuthentication(): void
    {
        $response = $this->get('/dashboard');
        $response->assertRedirect('/login'); // Ensure unauthenticated users are redirected to login
    }

    /**
     * Test an authenticated user can access the dashboard.
     */
    public function testAuthenticatedUserCanAccessDashboard(): void
    {
        $user = \App\Models\User::factory()->create();

        $response = $this->actingAs($user)->get('/dashboard');
        $response->assertStatus(200);
        $response->assertSee('Dashboard'); // Check if the page contains 'Dashboard'
    }
}
