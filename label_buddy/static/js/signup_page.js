const password = document.querySelector('#id_password1');
document.addEventListener('DOMContentLoaded', function() {
    $('#eyeDiv').click(function() {
        // toggle the type attribute
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        if(password.getAttribute('type') === 'password') {
            document.getElementById("togglePassword").classList.toggle('fa-eye-slash');
        } else {
            document.getElementById("togglePassword").classList.toggle('fa-eye');
        }
        password.setAttribute('type', type);
        // toggle the eye slash icon
        
    });
});