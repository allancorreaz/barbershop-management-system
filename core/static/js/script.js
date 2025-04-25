document.addEventListener('DOMContentLoaded', function() {
    // Ativar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Fechar mensagens automaticamente
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Manter submenu aberto quando uma página filha está ativa
    var activeLinks = document.querySelectorAll('.nav-link.active');
    activeLinks.forEach(function(link) {
        var parentCollapse = link.closest('.collapse');
        if (parentCollapse) {
            var collapseId = parentCollapse.id;
            var trigger = document.querySelector('[href="#' + collapseId + '"]');
            if (trigger) {
                new bootstrap.Collapse(parentCollapse, { toggle: false }).show();
                trigger.classList.add('active');
            }
        }
    });
    
    // Máscaras para campos
    var phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            var x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    });
    
    // Máscara para moeda
    var currencyInputs = document.querySelectorAll('input.currency');
    currencyInputs.forEach(function(input) {
        input.addEventListener('keyup', function(e) {
            var value = e.target.value.replace(/\D/g, '');
            value = (value / 100).toFixed(2) + '';
            value = value.replace('.', ',');
            value = value.replace(/(\d)(\d{3})(\d{3}),/g, '$1.$2.$3,');
            value = value.replace(/(\d)(\d{3}),/g, '$1.$2,');
            e.target.value = 'R$ ' + value;
        });
    });
    
    // Confirmar antes de excluir
    var deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Tem certeza que deseja excluir este item?')) {
                e.preventDefault();
            }
        });
    });
});