import React from 'react';

export const Dashboard = () => {
    return (
        <div className="max-w-4xl w-full bg-white p-8 rounded-lg shadow-md">
            <h2 className="text-3xl font-bold mb-6 text-center">Dashboard</h2>
            <p className="text-gray-700 text-center">Welcome to your dashboard!</p>
            <div className="mt-6 flex justify-center">
                <button
                    className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                >
                    Logout
                </button>
            </div>
        </div>
    );
};
