/**
 * Main JavaScript para Check-In Agencia de Viajes
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Manejo de Sistema de Notificaciones (Toasts)
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(toast => {
        // En la especificación se pide que desaparezcan tras 4 segundos
        setTimeout(() => {
            // Aplicar animación de salida
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            
            // Eliminar del DOM después de la animación
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, 300);
        }, 4000);
    });
});
