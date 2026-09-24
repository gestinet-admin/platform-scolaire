// PlatformScolaire - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('PlatformScolaire chargé');
    
    // Smooth animations
    const cards = document.querySelectorAll('.card-premium');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100);
    });
    
    // Form handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const token = localStorage.getItem('access_token');
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('Success:', result);
                    alert('✅ ' + result.message);
                } else {
                    alert('❌ Erreur');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('❌ Erreur réseau');
            }
        });
    });
});

// Login handling
function handleLogin(email, password) {
    fetch('/api/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    })
    .then(r => r.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            window.location.href = '/dashboard';
        }
    });
}
