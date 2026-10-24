'use strict';

/*
 * Coordinator-J web interface connected to the local Python API.
 */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const views = ['consoleView', 'toolsView', 'historyView'];
  const history = [];
  let toastTimer;

  /* ---------- Theme (shared by both pages) ---------- */
  try {
    const saved = localStorage.getItem('cj-theme');
    if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved;
  } catch (e) { /* storage unavailable: keep default */ }

  const themeToggle = $('#themeToggle');
  if (themeToggle) themeToggle.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('cj-theme', next); } catch (e) {}
  });

  /* ---------- Helpers ---------- */
  function showToast(message) {
    const toast = $('#toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2800);
  }

  function setView(id) {
    if (!views.includes(id)) return;
    views.forEach(v => { const el = document.getElementById(v); if (el) el.classList.toggle('active', v === id); });
    $$('[data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === id));
    window.scrollTo({ top: 0 });
  }

  const nowTime = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  /* ---------- Live API routing ---------- */
  /* ---------- Chat ---------- */
  const thread = $('#thread');

  function addMessage(kind, text, meta) {
    if (!thread) return null;
    const el = document.createElement('div');
    el.className = `msg ${kind}`;
    const who = document.createElement('span');
    who.className = 'who';
    who.textContent = kind === 'user' ? 'You' : 'Coordinator-J';
    const body = document.createElement('span');
    body.textContent = text;
    el.append(who, body);
    if (meta) {
      const m = document.createElement('span');
      m.className = 'meta';
      m.textContent = meta;
      el.append(m);
    }
    thread.append(el);
    thread.scrollTop = thread.scrollHeight;
    return el;
  }

  function welcome() {
    if (!thread) return;
    thread.replaceChildren();
    addMessage('bot', 'Welcome to Coordinator-J. Commands are sent to the local Python backend. Try Status or Help to begin.');
  }

  function cell(text, cls) {
    const td = document.createElement('td');
    if (cls) td.className = cls;
    td.textContent = text;
    return td;
  }

  function renderHistory() {
    const body = $('#historyTable');
    if (body) {
      body.replaceChildren();
      if (!history.length) {
        const tr = document.createElement('tr');
        const td = cell('Nothing yet. Send a command from the console.', 'empty');
        td.colSpan = 4;
        tr.append(td);
        body.append(tr);
      } else {
        history.forEach(h => {
          const tr = document.createElement('tr');
          tr.append(cell(h.request, 'request-cell'), cell(h.status), cell(h.tool), cell(h.time));
          body.append(tr);
        });
      }
    }
    const count = $('#historyCount');
    if (count) count.textContent = `${history.length} ${history.length === 1 ? 'entry' : 'entries'}`;
  }

  async function run(raw) {
    const request = raw.trim();
    if (!request) return;

    setView('consoleView');
    const time = nowTime();
    const entry = { request, status: 'Running', tool: 'pending', time };
    history.unshift(entry);

    addMessage('user', request);
    const pending = addMessage('bot', 'Contacting Coordinator-J backend?');
    if (pending) pending.classList.add('typing');

    const input = $('#commandInput');
    if (input) input.value = '';
    renderHistory();

    let result;
    try {
      const response = await fetch('http://127.0.0.1:8001/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || `API request failed (${response.status})`);
      }

      result = {
        status: data.status || 'unknown',
        tool: data.tool || 'none',
        message: data.message || 'The backend returned no message.'
      };
    } catch (error) {
      result = {
        status: 'Connection error',
        tool: 'none',
        message: `Could not reach the Coordinator-J API. Make sure web_api.py is running at http://127.0.0.1:8001. Details: ${error.message}`
      };
    }

    entry.status = result.status;
    entry.tool = result.tool;
    if (pending && pending.isConnected) pending.remove();
    addMessage('bot', result.message, `${result.status} ? ${result.tool} ? ${time}`);
    renderHistory();
  }

  const form = $('#commandForm');
  if (form) form.addEventListener('submit', e => { e.preventDefault(); run($('#commandInput').value); });
  $$('[data-command]').forEach(b => b.addEventListener('click', () => run(b.dataset.command)));
  $$('[data-view]').forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));

  const clearChat = $('#clearChat');
  if (clearChat) clearChat.addEventListener('click', () => { welcome(); showToast('Conversation cleared.'); });

  const clearHistory = $('#clearHistory');
  if (clearHistory) clearHistory.addEventListener('click', () => { history.length = 0; renderHistory(); showToast('History cleared.'); });

  /* ---------- Search shortcut ---------- */
  function focusInput() { setView('consoleView'); const i = $('#commandInput'); if (i) i.focus(); }
  const search = $('#searchButton');
  if (search) search.addEventListener('click', focusInput);
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k' && $('#commandInput')) { e.preventDefault(); focusInput(); }
  });

  /* ---------- Suggestions ---------- */
  const tips = [
    ['Start with status', 'Run a status check to see what the core is currently doing.'],
    ['Not sure what to ask?', 'Type help to list every command this preview understands.'],
    ['See what is registered', 'Tools lists the capabilities available right now. Both are read only.'],
    ['Keyboard first', 'Press Ctrl K from anywhere to jump straight to the command box.']
  ];
  let tipIndex = 0;
  const nextTip = $('#nextTip');
  if (nextTip) nextTip.addEventListener('click', () => {
    tipIndex = (tipIndex + 1) % tips.length;
    $('#tipTitle').textContent = tips[tipIndex][0];
    $('#tipText').textContent = tips[tipIndex][1];
  });

  /* ---------- Greeting & init ---------- */
  const greeting = $('#greeting');
  if (greeting) {
    const h = new Date().getHours();
    greeting.textContent = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening';
  }
  welcome();
  renderHistory();
})();
