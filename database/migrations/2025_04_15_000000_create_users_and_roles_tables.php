<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUsersAndRolesTables extends Migration
{
    public function up()
    {
        // Create roles table
        if (!Schema::hasTable('roles')) {
            Schema::create('roles', function (Blueprint $table) {
                $table->id();
                $table->string('name'); // e.g., Admin, Auditor, Consultant
                $table->timestamps();
            });
        }

        // Create users table
        if (!Schema::hasTable('users')) {
            Schema::create('users', function (Blueprint $table) {
                $table->id();
                $table->string('name');
                $table->string('email')->unique();
                $table->timestamp('email_verified_at')->nullable();
                $table->string('password');
                $table->rememberToken();
                $table->boolean('is_active')->default(true);
                $table->timestamps();
            });
        }

        // Create role_user pivot table
        Schema::create('role_user', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('role_id')->constrained()->onDelete('cascade');
            $table->timestamps();
        });

        // Create groups table
        Schema::create('groups', function (Blueprint $table) {
            $table->id();
            $table->string('name'); // e.g., Certification Body, Organization, Consulting Firm
            $table->string('type'); // e.g., certification_body, organization, consulting_firm
            $table->timestamps();
        });

        // Create group_user pivot table
        Schema::create('group_user', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('group_id')->constrained()->onDelete('cascade');
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('group_user');
        Schema::dropIfExists('groups');
        Schema::dropIfExists('role_user');
        Schema::dropIfExists('users');
        Schema::dropIfExists('roles');
    }
}
