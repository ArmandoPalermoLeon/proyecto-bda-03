document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-cerrar mensajes flash después de 4 segundos ────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = 'opacity 0.4s ease';
      flash.style.opacity = '0';
      setTimeout(function () { flash.remove(); }, 400);
    }, 4000);
  });

  // ── Confirmación antes de eliminar ──────────────────────
  const deleteForms = document.querySelectorAll('.form-delete');
  deleteForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const nombre = form.dataset.nombre || 'este registro';
      if (!confirm('¿Confirmas que deseas eliminar a ' + nombre + '? Esta acción no se puede deshacer.')) {
        e.preventDefault();
      }
    });
  });

});
