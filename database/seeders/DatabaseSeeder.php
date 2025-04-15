<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Role;
use App\Models\Group;
use Illuminate\Support\Facades\Hash;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // Seed roles
        $roles = ['Admin', 'Auditor', 'Consultant', 'Organization Admin', 'Organization Manager'];
        foreach ($roles as $role) {
            Role::create(['name' => $role]);
        }

        // Seed groups
        $groups = [
            ['name' => 'Certification Body', 'type' => 'certification_body'],
            ['name' => 'Organization', 'type' => 'organization'],
            ['name' => 'Consulting Firm', 'type' => 'consulting_firm'],
        ];
        foreach ($groups as $group) {
            Group::create($group);
        }

        // Update the existing user instead of creating a duplicate
        $user = User::updateOrCreate(
            ['email' => 'test@example.com'],
            [
                'name' => 'Super Admin User',
                'password' => Hash::make('password123'),
            ]
        );

        // Ensure Super Admin role exists
        $superAdminRole = Role::firstOrCreate(['name' => 'Super Admin']);

        // Assign Super Admin role to the user
        if ($user) {
            $user->roles()->syncWithoutDetaching([$superAdminRole->id]);
        }

        // Ensure Certification Body Admin role exists
        $certBodyAdminRole = Role::firstOrCreate(['name' => 'Certification Body Admin']);

        // Create a Certification Body Admin user
        $certBodyAdminUser = User::updateOrCreate(
            ['email' => 'certbodyadmin@example.com'],
            [
                'name' => 'Certification Body Admin',
                'password' => Hash::make('password123'),
            ]
        );

        // Assign Certification Body Admin role to the user
        if ($certBodyAdminUser) {
            $certBodyAdminUser->roles()->syncWithoutDetaching([$certBodyAdminRole->id]);
        }
    }
}
