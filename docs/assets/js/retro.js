/* The Agent Autopsy: vanilla JS for the retro theme. No build step, no dependencies. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      window.localStorage.setItem(key, value);
    } catch (e) { /* storage can be blocked; the page still works */ }
    return null;
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  /* ---------- FX toggle ---------- */
  (function fx() {
    var btn = document.getElementById('fx-toggle');
    if (!btn) return;
    var root = document.documentElement;
    function sync() {
      var off = root.classList.contains('fx-off');
      btn.textContent = off ? 'FX OFF' : 'FX ON';
      btn.setAttribute('aria-pressed', off ? 'false' : 'true');
    }
    btn.addEventListener('click', function () {
      root.classList.toggle('fx-off');
      store('aa-fx', root.classList.contains('fx-off') ? 'off' : 'on');
      sync();
    });
    sync();
  })();

  /* ---------- Copy helper ---------- */
  function copyText(text, button) {
    function done() {
      var old = button.textContent;
      button.textContent = 'COPIED';
      button.classList.add('done');
      setTimeout(function () { button.textContent = old; button.classList.remove('done'); }, 1400);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {});
    }
  }

  /* ---------- Terminal demo (home) ---------- */
  (function terminal() {
    var root = document.getElementById('term');
    if (!root) return;
    var linesEl = document.getElementById('term-lines');
    var cmdEl = document.getElementById('term-cmd');
    var metersEl = document.getElementById('term-meters');
    var statusEl = document.getElementById('term-status');
    var runBtn = document.getElementById('term-run');
    var killBtn = document.getElementById('term-kill');
    var tabs = root.querySelectorAll('[role="tab"]');

    var mode = 'broken', running = false, step = 0, elapsed = 0, stopped = null, lines = [], timer = null;
    var MAX_STEPS = 10, TOKEN_BUDGET = 4000, TIMEOUT = 60;

    function stop() { if (timer) { clearInterval(timer); timer = null; } running = false; }
    function push(text, cls) { lines.push({ text: text, cls: cls || '' }); lines = lines.slice(-14); }

    function meter(label, value, pct, color, track) {
      var wrap = el('div');
      var top = el('div', 'meter-top');
      top.appendChild(el('span', '', label));
      var v = el('span', '', value); v.style.color = color; top.appendChild(v);
      var tr = el('div', 'meter-track'); tr.style.background = track;
      var fill = el('div', 'meter-fill'); fill.style.width = Math.max(0, Math.min(100, pct)) + '%';
      fill.style.background = color; fill.style.boxShadow = '0 0 8px ' + color;
      tr.appendChild(fill); wrap.appendChild(top); wrap.appendChild(tr);
      return wrap;
    }

    function render() {
      cmdEl.textContent = '$ python ' + mode + '.py';
      linesEl.textContent = '';
      lines.forEach(function (l) { linesEl.appendChild(el('div', 'term-line ' + l.cls, l.text)); });
      var tokens = step * 18;
      metersEl.textContent = '';
      if (mode === 'broken') {
        metersEl.appendChild(meter('STEPS', step + ' / ∞', (step % 40) / 40 * 100, '#FF006E', 'rgba(255,0,110,.12)'));
        metersEl.appendChild(meter('TOKENS', tokens + ' / ∞', (tokens % 720) / 720 * 100, '#FF006E', 'rgba(255,0,110,.12)'));
        metersEl.appendChild(meter('GUARDS', 'NONE', 0, '#FF006E', 'rgba(255,0,110,.12)'));
      } else {
        metersEl.appendChild(meter('MAX_STEPS', step + ' / ' + MAX_STEPS, step / MAX_STEPS * 100, stopped === 'max_steps' ? '#FFD700' : '#00FFFF', 'rgba(0,255,255,.12)'));
        metersEl.appendChild(meter('TOKEN_BUDGET', tokens + ' / ' + TOKEN_BUDGET, tokens / TOKEN_BUDGET * 100, '#00FFFF', 'rgba(0,255,255,.12)'));
        metersEl.appendChild(meter('TIMEOUT', elapsed.toFixed(1) + 's / ' + TIMEOUT + 's', elapsed / TIMEOUT * 100, '#00FFFF', 'rgba(0,255,255,.12)'));
      }
      var text = 'IDLE', color = '#A9A6C4';
      if (running) { text = mode === 'broken' ? '● RUNNING · NO EXIT' : '● RUNNING · GUARDED'; color = mode === 'broken' ? '#FF006E' : '#00FFFF'; }
      else if (stopped === 'max_steps') { text = '■ STOPPED_BY=MAX_STEPS'; color = '#FFD700'; }
      else if (stopped === 'ctrl_c') { text = '■ KILLED BY HUMAN'; color = '#FFD700'; }
      if (statusEl.textContent !== text) statusEl.textContent = text;
      statusEl.style.color = color;
      killBtn.disabled = !running;
      tabs.forEach(function (t) { t.setAttribute('aria-selected', t.getAttribute('data-mode') === mode ? 'true' : 'false'); });
    }

    function tick() {
      step += 1;
      var reply = 'Draft ' + step + ': still refining the summary, one more pass...';
      if (mode === 'broken') {
        push('step=' + step + '  tokens~' + step * 18 + '  ' + reply, step > 12 ? 'hot' : '');
        elapsed += 0.38;
      } else {
        push('  step=' + step + ' tokens~' + step * 18 + '  ' + reply);
        elapsed += 0.26;
        if (step >= MAX_STEPS) {
          push(' ');
          push('stopped_by=max_steps after ' + MAX_STEPS + ' steps', 'ok');
          stopped = 'max_steps'; stop();
        }
      }
      render();
    }

    function start(m) {
      stop();
      mode = m; step = 0; elapsed = 0; stopped = null; running = true;
      lines = [];
      if (mode === 'broken') { push('WARNING: no stop guard. Ctrl+C to escape.', 'warn'); push(' '); }
      render();
      timer = setInterval(tick, mode === 'broken' ? 380 : 260);
    }

    tabs.forEach(function (t) { t.addEventListener('click', function () { start(t.getAttribute('data-mode')); }); });
    runBtn.addEventListener('click', function () { start(mode); });
    killBtn.addEventListener('click', function () {
      if (!running) return;
      stop(); stopped = 'ctrl_c'; push('^C KeyboardInterrupt', 'kill'); render();
    });

    if (reduceMotion) { render(); } else { start('broken'); }
  })();

  /* ---------- Home filters ---------- */
  (function filters() {
    var pills = document.querySelectorAll('.pill[data-filter]');
    if (!pills.length) return;
    var rows = document.querySelectorAll('.cat-row[data-cat]');
    pills.forEach(function (p) {
      p.addEventListener('click', function () {
        var f = p.getAttribute('data-filter');
        pills.forEach(function (q) {
          var on = q === p;
          q.classList.toggle('on', on);
          q.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        rows.forEach(function (r) { r.hidden = !(f === 'ALL' || r.getAttribute('data-cat') === f); });
      });
    });
  })();

  /* ---------- Prose enhancements ---------- */
  var prose = document.getElementById('prose');

  function slugify(t) { return t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }

  function markLeads() {
    prose.querySelectorAll('p').forEach(function (p) {
      var first = p.firstChild;
      if (first && first.nodeType === 1 && first.tagName === 'STRONG') p.classList.add('lead');
    });
  }

  function highlightLines(box, code, kind) {
    var set = {};
    var attr = box.getAttribute('data-hl');
    if (attr) {
      attr.split(',').forEach(function (part) {
        var r = part.trim().split('-');
        var a = parseInt(r[0], 10), b = parseInt(r[1] || r[0], 10);
        for (var i = a; i <= b; i++) set[i] = kind === 'bug' ? 'bug' : 'fix';
      });
    } else if (kind === 'bug') {
      var rows = code.split('\n');
      for (var n = 0; n < rows.length; n++) {
        if (/THE BUG/.test(rows[n])) {
          set[n + 1] = 'bug';
          for (var m = n + 1; m < rows.length && rows[m].trim() !== ''; m++) {
            if (/^\s*#/.test(rows[m])) { set[m + 1] = 'bug'; continue; }
            set[m + 1] = 'bug';
          }
        }
      }
    }
    return set;
  }

  function sectionKind(node) {
    var cur = node.previousElementSibling;
    while (cur) {
      if (cur.tagName === 'H2') {
        if (cur.id === 'the-bug') return 'bug';
        if (cur.id === 'the-fix') return 'fix';
        return '';
      }
      cur = cur.previousElementSibling;
    }
    return '';
  }

  function enhanceCode() {
    prose.querySelectorAll('div.highlighter-rouge').forEach(function (box) {
      var pre = box.querySelector('pre');
      if (!pre) return;
      var langMatch = box.className.match(/language-([\w-]+)/);
      var lang = langMatch ? langMatch[1] : 'text';
      var source = pre.textContent.replace(/\n$/, '');
      var kind = (lang === 'text' || lang === 'console') ? '' : sectionKind(box);
      var label = lang.toUpperCase();
      var prev = box.previousElementSibling;
      if (prev && prev.tagName === 'P') {
        var a = prev.querySelector('a[href*="broken.py"], a[href*="fixed.py"], a[href*="test_fixed.py"]');
        if (a) {
          var m = (a.getAttribute('href') || '').match(/main\/(.+)$/);
          if (m) label = m[1];
          if (/broken\.py/.test(a.href)) kind = 'bug';
          else if (/fixed\.py/.test(a.href) && !/test_fixed/.test(a.href)) kind = 'fix';
        }
      }
      var count = source.split('\n').length;
      var hl = highlightLines(box, source, kind);

      var wrap = el('div', 'code' + (kind ? ' k-' + kind : ''));
      var head = el('div', 'code-h');
      head.appendChild(el('span', 'code-lbl', label));
      var right = el('div', 'code-r');
      right.appendChild(el('span', '', lang));
      var copy = el('button', 'copy', 'COPY'); copy.type = 'button';
      copy.addEventListener('click', function () { copyText(source, copy); });
      right.appendChild(copy);
      head.appendChild(right);

      var body = el('div', 'code-b');
      var nums = [];
      for (var i = 1; i <= count; i++) nums.push(i);
      var gut = el('pre', 'gut', nums.join('\n')); gut.setAttribute('aria-hidden', 'true');
      var scroller = el('div', 'code-s');
      var inner = el('div', 'code-i');
      Object.keys(hl).forEach(function (n) {
        var bar = el('div', 'hl ' + hl[n]);
        bar.style.top = ((parseInt(n, 10) - 1) * 22.1) + 'px';
        inner.appendChild(bar);
      });
      pre.classList.add('src');
      inner.appendChild(pre);
      scroller.appendChild(inner);
      body.appendChild(gut); body.appendChild(scroller);
      wrap.appendChild(head); wrap.appendChild(body);
      box.parentNode.replaceChild(wrap, box);
    });
  }

  function buildToc() {
    var toc = document.getElementById('toc');
    if (!toc) return;
    var heads = prose.querySelectorAll('h2');
    if (!heads.length) { toc.hidden = true; return; }
    toc.appendChild(el('div', 'toc-h', '// ON THIS PAGE'));
    var links = [];
    heads.forEach(function (h, i) {
      if (!h.id) h.id = slugify(h.textContent);
      var a = el('a');
      a.href = '#' + h.id;
      a.appendChild(el('span', '', (i < 9 ? '0' : '') + (i + 1)));
      a.appendChild(el('span', '', h.textContent));
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var top = h.getBoundingClientRect().top + window.pageYOffset - 88;
        window.scrollTo({ top: top, behavior: reduceMotion ? 'auto' : 'smooth' });
        if (history.replaceState) history.replaceState(null, '', '#' + h.id);
      });
      toc.appendChild(a); links.push({ a: a, h: h });
    });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            links.forEach(function (l) { l.a.classList.toggle('on', l.h === en.target); });
          }
        });
      }, { rootMargin: '-90px 0px -65% 0px' });
      links.forEach(function (l) { io.observe(l.h); });
    }
  }

  /* ---------- Start here: copy buttons and cards ---------- */
  function startPage() {
    prose.querySelectorAll('p.lead').forEach(function (p) {
      var h2 = p; while (h2 && h2.tagName !== 'H2') h2 = h2.previousElementSibling;
      if (h2 && /four things/i.test(h2.textContent)) p.classList.add('card');
    });
  }

  /* ---------- Field checklist ---------- */
  function checklist() {
    var tones = ['#FF10F0', '#00FFFF', '#0080FF', '#FFD700'];
    var progress = document.getElementById('progress');
    var checks = {};
    try { checks = JSON.parse(store('aa-checks') || '{}') || {}; } catch (e) { checks = {}; }
    var rows = [];
    var groupIndex = -1;
    var children = Array.prototype.slice.call(prose.children);
    var inCross = false;

    children.forEach(function (node) {
      if (node.tagName === 'H2') {
        inCross = /^three questions/i.test(node.textContent);
        if (inCross) { node.classList.add('cross'); node.style.removeProperty('--c'); return; }
        groupIndex += 1;
        node.style.setProperty('--c', tones[groupIndex % tones.length]);
        return;
      }
      if (inCross && node.tagName === 'OL') { node.classList.add('cross'); return; }
      if (node.tagName === 'UL' && groupIndex >= 0 && !inCross) {
        var color = tones[groupIndex % tones.length];
        var list = el('div', 'chk');
        Array.prototype.slice.call(node.children).forEach(function (li) {
          var idx = rows.length;
          var strong = li.querySelector('strong');
          var q = strong ? strong.textContent : li.textContent;
          var rest = li.cloneNode(true);
          var rs = rest.querySelector('strong'); if (rs) rs.remove();
          var link = li.querySelector('a[href*="/failures/"]');
          var num = link ? (link.getAttribute('href').match(/failures\/(\d+)-/) || [])[1] : null;

          var row = el('div', 'chk-row'); row.style.setProperty('--c', color);
          var box = el('button', 'chk-box'); box.type = 'button';
          box.setAttribute('role', 'checkbox'); box.setAttribute('aria-label', 'Mark reviewed: ' + q);
          var main = el('div', 'chk-main');
          main.appendChild(el('span', 'chk-q', q));
          var d = el('span', 'chk-d'); d.innerHTML = rest.innerHTML.trim(); main.appendChild(d);
          row.appendChild(box); row.appendChild(main);
          if (link && num) {
            var chip = el('a', 'chk-chip', 'FAILURE ' + num + ' →'); chip.href = link.getAttribute('href'); row.appendChild(chip);
          }
          function paint() {
            var on = !!checks[idx];
            row.classList.toggle('on', on);
            box.setAttribute('aria-checked', on ? 'true' : 'false');
            box.textContent = on ? '✓' : '';
          }
          box.addEventListener('click', function () {
            if (checks[idx]) delete checks[idx]; else checks[idx] = true;
            store('aa-checks', JSON.stringify(checks)); paint(); summary();
          });
          rows.push({ paint: paint });
          list.appendChild(row);
        });
        node.parentNode.replaceChild(list, node);
      }
    });

    function summary() {
      if (!progress) return;
      var n = Object.keys(checks).filter(function (k) { return +k < rows.length; }).length;
      document.getElementById('progress-n').textContent = n + ' / ' + rows.length;
      document.getElementById('progress-fill').style.width = (rows.length ? n / rows.length * 100 : 0) + '%';
    }
    rows.forEach(function (r) { r.paint(); });
    if (progress) {
      progress.hidden = rows.length === 0;
      document.getElementById('progress-reset').addEventListener('click', function () {
        checks = {}; store('aa-checks', '{}'); rows.forEach(function (r) { r.paint(); }); summary();
      });
      summary();
    }
  }

  if (prose) {
    markLeads();
    enhanceCode();
    var body = document.body.className;
    if (/page-article/.test(body)) buildToc();
    if (/page-start/.test(body)) startPage();
    if (/page-checklist/.test(body)) checklist();
  }
})();
