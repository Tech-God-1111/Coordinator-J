'use strict';

/*
 * Coordinator-J interface preview.
 * This file intentionally does NOT execute real Coordinator-J tools.
 * The Python web backend will be connected in a later milestone.
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

  /* ---------- Simulated routing ---------- */
  const SIM = ' This reply is simulated; the Python coordinator has not been called.';
  function route(raw) {
    const n = raw.trim().toLowerCase();
    if (['status', 'check status', 'project status'].includes(n))
      return { status: 'Simulated', tool: 'project_status', message: 'The core is shown as running in this preview. AI planner: not connected. SmartDoor: not connected.' + SIM };
    if (n === 'help')
      return { status: 'Simulated', tool: 'help', message: 'Try: status, help, tools, history, planner or safety. Natural-language planning is not connected yet.' + SIM };
    if (n === 'tools')
      return { status: 'Simulated', tool: 'tool_registry', message: 'Two tools are registered: project_status and help. Both are read only.' + SIM };
    if (n === 'history')
      return { status: 'Simulated', tool: 'task_history', message: `This tab has recorded ${history.length} request${history.length === 1 ? '' : 's'}. This is not the Python coordinator’s task history.` };
    if (n === 'planner')
      return { status: 'Simulated', tool: 'planner', message: 'The AI planner is offline. Requests are matched by simple rules until it is connected.' + SIM };
    if (n === 'safety')
      return { status: 'Simulated', tool: 'approval_gate', message: 'Tools that change state stay behind an approval step. Nothing on this page can trigger one.' + SIM };
    return { status: 'Not connected', tool: 'none', message: 'No action was taken. The Python backend must be connected before this request can reach Coordinator-J.' };
  }

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
    addMessage('bot', 'Welcome. This is the interface preview, so replies are simulated. Try Status or Help to see how the console will feel.');
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

  function run(raw) {
    const request = raw.trim();
    if (!request) return;
    setView('consoleView');
    const result = route(request);
    const time = nowTime();
    history.unshift({ request, status: result.status, tool: result.tool, time });
    addMessage('user', request);
    const pending = addMessage('bot', '…');
    if (pending) pending.classList.add('typing');
    setTimeout(() => {
      if (pending && pending.isConnected) {
        pending.remove();
        addMessage('bot', result.message, `${result.status} · ${result.tool} · ${time}`);
      }
    }, 450);
    renderHistory();
    const input = $('#commandInput');
    if (input) input.value = '';
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
