// Billing counter. Keeps a cart in the page; the server recalculates and
// validates everything on submit, so nothing here is trusted.
(function () {
  'use strict';
  var form = document.getElementById('counter');
  if (!form) return;

  var cart = [];
  try { cart = JSON.parse(form.getAttribute('data-cart') || '[]'); } catch (e) { cart = []; }

  var body = document.getElementById('cart-body');
  var empty = document.getElementById('cart-empty');
  var rxPanel = document.getElementById('rx-panel');
  var saveBtn = document.getElementById('save-bill');
  var discount = document.getElementById('discount_pct');

  function money(n) { return (Math.round(n * 100) / 100).toFixed(2); }
  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function render() {
    body.textContent = '';
    var gross = 0, gst = 0, needsRx = false, count = 0;
    var pct = Math.min(Math.max(parseFloat(discount.value) || 0, 0), 100);
    cart.forEach(function (item, index) {
      var mrp = parseFloat(item.mrp) || 0;
      var line = mrp * item.qty;
      var net = line * (1 - pct / 100);
      var rate = parseFloat(item.gst) || 0;
      gross += line;
      gst += net - net / (1 + rate / 100);
      count += item.qty;
      if (item.needs_rx) needsRx = true;

      var tr = el('tr');
      var name = el('td');
      name.appendChild(el('div', { 'class': 'fw-semibold' }, item.label));
      var meta = el('div', { 'class': 'small text-body-secondary' }, item.generic + ' · ' + item.packing +
        (item.expiry ? ' · exp ' + item.expiry : '') + ' · ' + item.stock + ' in stock');
      name.appendChild(meta);
      if (item.schedule !== 'OTC') {
        name.appendChild(el('span', { 'class': 'badge sched sched-' + item.schedule.toLowerCase() }, item.schedule));
      }
      if (item.qty > item.stock) {
        name.appendChild(el('div', { 'class': 'small text-bad' }, 'Only ' + item.stock + ' in stock'));
      }
      name.appendChild(el('input', { type: 'hidden', name: 'item_id[]', value: item.id }));
      tr.appendChild(name);
      tr.appendChild(el('td', { 'class': 'num' }, money(mrp)));
      var qtyCell = el('td');
      var qty = el('input', { type: 'number', min: '1', 'class': 'form-control form-control-sm cart-qty',
        name: 'item_qty[]', value: item.qty, 'aria-label': 'Quantity of ' + item.label });
      qty.addEventListener('change', function () {
        item.qty = Math.max(parseInt(qty.value, 10) || 1, 1);
        render();
      });
      qtyCell.appendChild(qty);
      tr.appendChild(qtyCell);
      tr.appendChild(el('td', { 'class': 'num' }, money(net)));
      var rm = el('td', { 'class': 'text-end' });
      var btn = el('button', { type: 'button', 'class': 'btn btn-sm btn-outline-secondary', 'aria-label': 'Remove ' + item.label });
      btn.appendChild(el('i', { 'class': 'bi bi-x-lg', 'aria-hidden': 'true' }));
      btn.addEventListener('click', function () { cart.splice(index, 1); render(); });
      rm.appendChild(btn);
      tr.appendChild(rm);
      body.appendChild(tr);
    });
    var net = gross * (1 - pct / 100);
    document.getElementById('t-items').textContent = count;
    document.getElementById('t-gross').textContent = money(gross);
    document.getElementById('t-disc').textContent = money(gross - net);
    document.getElementById('t-gst').textContent = money(gst);
    document.getElementById('t-total').textContent = Math.round(net);
    empty.classList.toggle('d-none', cart.length > 0);
    rxPanel.classList.toggle('d-none', !needsRx);
    saveBtn.disabled = cart.length === 0;
  }

  function add(product) {
    var existing = cart.filter(function (c) { return c.id === product.id; })[0];
    if (existing) existing.qty += 1;
    else cart.push(Object.assign({ qty: 1 }, product));
    render();
  }

  // Generic type-ahead used for products and customers.
  function typeahead(input, list, url, describe, choose, exactHit) {
    var timer, results = [], active = -1;
    function close() { list.classList.add('d-none'); input.setAttribute('aria-expanded', 'false'); active = -1; }
    function show() {
      list.textContent = '';
      results.forEach(function (r, i) {
        var b = el('button', { type: 'button', role: 'option', id: list.id + '-' + i });
        var d = describe(r);
        b.appendChild(el('span', {}, d[0]));
        b.appendChild(el('span', { 'class': 'text-body-secondary small' }, d[1]));
        if (i === active) b.classList.add('active');
        b.addEventListener('mousedown', function (e) { e.preventDefault(); pick(i); });
        list.appendChild(b);
      });
      if (!results.length) list.appendChild(el('div', { 'class': 'p-2 small text-body-secondary' }, 'Nothing found'));
      list.classList.remove('d-none');
      input.setAttribute('aria-expanded', 'true');
    }
    function pick(i) { if (results[i]) { choose(results[i]); input.value = ''; close(); } }
    function search(then) {
      var q = input.value.trim();
      if (q.length < 2) { results = []; close(); return; }
      fetch(url + '?q=' + encodeURIComponent(q), { credentials: 'same-origin' })
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (data) { results = data; active = data.length ? 0 : -1; show(); if (then) then(); });
    }
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(search, 180); });
    input.addEventListener('blur', function () { setTimeout(close, 150); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' && results.length) { active = (active + 1) % results.length; show(); e.preventDefault(); }
      else if (e.key === 'ArrowUp' && results.length) { active = (active - 1 + results.length) % results.length; show(); e.preventDefault(); }
      else if (e.key === 'Escape') { close(); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        clearTimeout(timer);
        // A barcode scanner types the code and presses Enter at once.
        search(function () { if (exactHit(results) || results.length) pick(Math.max(active, 0)); });
      }
    });
  }

  typeahead(document.getElementById('product-search'), document.getElementById('product-results'),
    form.getAttribute('data-product-url'),
    function (p) { return [p.label + (p.schedule !== 'OTC' ? ' [' + p.schedule + ']' : ''), '₹' + p.mrp + ' · ' + p.stock + ' left']; },
    function (p) {
      if (p.stock <= 0) { window.alert(p.label + ' has no unexpired stock.'); return; }
      add(p);
    },
    function (r) { return r.length === 1; });

  var cid = document.getElementById('c_id');
  var chosen = document.getElementById('customer-chosen');
  var csearch = document.getElementById('customer-search');
  function setCustomer(c) {
    cid.value = c ? c.id : '';
    document.getElementById('customer-label').textContent = c ? c.name + ' · ' + c.phone : '';
    document.getElementById('customer_label_input').value = c ? c.name : '';
    chosen.classList.toggle('d-none', !c);
    csearch.classList.toggle('d-none', !!c);
    var pn = document.getElementById('patient_name'), pa = document.getElementById('patient_address');
    if (c && !pn.value) pn.value = c.name;
    if (c && !pa.value) pa.value = c.address || '';
  }
  typeahead(csearch, document.getElementById('customer-results'), form.getAttribute('data-customer-url'),
    function (c) { return [c.name, '#' + c.id + ' · ' + c.phone]; }, setCustomer, function () { return false; });
  document.getElementById('customer-clear').addEventListener('click', function () { setCustomer(null); csearch.focus(); });

  discount.addEventListener('input', render);
  form.addEventListener('keydown', function (e) {
    // Enter in a field (or from a barcode scanner) must never save the bill
    // by accident; only the Save button does.
    if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
      e.preventDefault();
      if (e.target.classList.contains('cart-qty')) e.target.blur();
    }
  });
  render();
})();
