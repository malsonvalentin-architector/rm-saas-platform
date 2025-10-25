/**
 * Force Dark Theme - Emergency Fix
 * Applies dark theme styles immediately on page load
 */

(function() {
    'use strict';
    
    console.log('🎨 ProMonitor: Forcing dark theme...');
    
    // Set data-theme attribute
    document.documentElement.setAttribute('data-theme', 'dark');
    document.body.setAttribute('data-theme', 'dark');
    
    // Apply inline styles as fallback
    document.body.style.backgroundColor = '#1a1d24';
    document.body.style.color = '#e4e6eb';
    
    // Force CSS variables
    const root = document.documentElement;
    root.style.setProperty('--bg-primary', '#1a1d29');
    root.style.setProperty('--bg-secondary', '#252833');
    root.style.setProperty('--bg-tertiary', '#2d3139');
    root.style.setProperty('--bg-card', '#2d3139');
    root.style.setProperty('--text-primary', '#ffffff');
    root.style.setProperty('--text-secondary', '#b8bcc8');
    
    console.log('✅ Dark theme applied successfully');
})();
