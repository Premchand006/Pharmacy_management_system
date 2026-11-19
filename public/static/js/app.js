// Behaviour shared by every page. No inline scripts are used anywhere, so the
// Content-Security-Policy can forbid them.
(function () {
  'use strict';

  // Flash messages close after a few seconds; errors stay until dismissed.
  setTimeout(function () {
    document.querySelectorAll('.alert-success').forEach(function (el) {
      bootstrap.Alert.getOrCreateInstance(el).close();
    });
  }, 6000);

  // <form data-confirm="Are you sure?"> asks before submitting.
  document.addEventListener('submit', function (event) {
    var form = event.target;
    var message = form.getAttribute('data-confirm');
    if (message && !window.confirm(message)) {
      event.preventDefault();
      return;
    }
    if (!form.checkValidity()) return;
    var button = form.querySelector('button[type="submit"]:not([data-keep])');
    if (button) {
      // Defer so the button's name/value is still submitted.
      setTimeout(function () { button.disabled = true; }, 0);
    }
  });

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      document.querySelectorAll('button[type="submit"][disabled]').forEach(function (b) { b.disabled = false; });
    }
  });

  // Repeating rows: a <template data-row-template="name"> plus a button with
  // data-add-row="name" appends a copy into [data-rows="name"].
  document.addEventListener('click', function (event) {
    var add = event.target.closest('[data-add-row]');
    if (add) {
      var name = add.getAttribute('data-add-row');
      var tpl = document.querySelector('template[data-row-template="' + name + '"]');
      var target = document.querySelector('[data-rows="' + name + '"]');
      if (tpl && target) {
        target.appendChild(tpl.content.cloneNode(true));
        var inputs = target.lastElementChild && target.lastElementChild.querySelectorAll('input, select');
        if (inputs && inputs.length) inputs[0].focus();
      }
    }
    var remove = event.target.closest('[data-remove-row]');
    if (remove) {
      var row = remove.closest('[data-row]');
      if (row && row.parentElement.querySelectorAll('[data-row]').length > 1) row.remove();
    }
    var printBtn = event.target.closest('[data-print]');
    if (printBtn) {
      document.body.classList.toggle('thermal', printBtn.getAttribute('data-print') === 'thermal');
      window.print();
    }
  });

  if (document.body.hasAttribute('data-autoprint')) {
    window.addEventListener('load', function () { window.print(); });
  }
})();
