

//Alerta
function mensaje(type, texto) {
    let icon = 'info';  // Valor por defecto

    if (type === 'success') {
        icon = 'success';
    } else if (type === 'error') {
        icon = 'error';
    }


    Swal.fire({
        position: "center",
        icon: type,
        title: texto,
        showConfirmButton: false,
        timer: 1500
    });
}





//Menu header
document.addEventListener('DOMContentLoaded', function() {
    const inicio = [...document.querySelectorAll('a')].find(a => a.href.includes('/principal'));
    const menu = document.querySelector('.menu');
    const iniciarSesionBtn = document.querySelector('.login_btn');

    if (inicio) {
        inicio.addEventListener('click', function(e) {
            e.preventDefault();
            menu.classList.add('fade-out');

            setTimeout(() => {
                window.location.href = inicio.href;
            }, 500);
        });
    }

    if (iniciarSesionBtn) {
        iniciarSesionBtn.addEventListener('click', function() {
            window.location.href = inicio.href;
        });
    }
});




