import './bootstrap';
import React from 'react';
import ReactDOM from 'react-dom';
import { Dashboard } from './components/Dashboard';

if (document.getElementById('dashboard-root')) {
    ReactDOM.render(<Dashboard />, document.getElementById('dashboard-root'));
}
