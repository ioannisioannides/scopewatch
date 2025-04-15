<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="bg-gray-100 flex items-center justify-center h-screen">
    <div id="register-root"></div>
    <script>
        import React from 'react';
        import ReactDOM from 'react-dom';
        import { Register } from './components/Register';

        ReactDOM.render(<Register />, document.getElementById('register-root'));
    </script>
</body>
</html>
