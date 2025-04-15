<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Models\User;
use App\Models\Role;
use App\Models\Group;

class ExampleTest extends TestCase
{
    /**
     * Test that true is true.
     */
    public function testThatTrueIsTrue(): void
    {
        $this->assertTrue(true);
    }

    /**
     * Test User model has a name attribute.
     */
    public function testUserHasNameAttribute(): void
    {
        $user = new User(['name' => 'John Doe']);
        $this->assertEquals('John Doe', $user->name);
    }

    /**
     * Test Role model has a name attribute.
     */
    public function testRoleHasNameAttribute(): void
    {
        $role = new Role(['name' => 'Admin']);
        $this->assertEquals('Admin', $role->name);
    }

    /**
     * Test Group model has a description attribute.
     */
    public function testGroupHasDescriptionAttribute(): void
    {
        $group = new Group(['description' => 'Test Group']);
        $this->assertEquals('Test Group', $group->description);
    }
}
