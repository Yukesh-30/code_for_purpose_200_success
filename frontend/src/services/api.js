const BASE = '';

const getToken = () => localStorage.getItem('token') || null;

const headers = (extra = {}) => ({
  'Content-Type': 'application/json',
  ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
  ...extra,
});

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: headers(),
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || data.error || `HTTP ${res.status}`);
  return data;
}

// ── Auth ──────────────────────────────────────────────────────
export const authAPI = {
  login:  (email, password)  => request('POST', '/auth/login',  { email, password }),
  signup: (payload)          => request('POST', '/auth/signup', payload),
};

// ── Business ──────────────────────────────────────────────────
export const businessAPI = {
  create: (payload) => request('POST', '/business/create', payload),
};

// ── Talk-to-Data Intelligence ─────────────────────────────────
export const intelligenceAPI = {
  chat: (business_id, question, history = [], include_sql = true) =>
    request('POST', '/chat', { business_id, question, history, include_sql }),

  forecast: (business_id, horizon_days = 30) =>
    request('POST', '/forecast', { business_id, horizon_days, include_sql: true }),

  anomaly: (business_id, lookback_days = 90) =>
    request('POST', '/anomaly', { business_id, lookback_days, include_sql: true }),
};

// ── Dashboard data ──────────────────────────────────────────────
export const dashboardAPI = {
  getStats: (business_id) => request('GET', `/dashboard/stats?business_id=${business_id}`),
};

// ── Upload ────────────────────────────────────────────────────
export const uploadAPI = {
  upload: async (type, file, business_id) => {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('business_id', business_id);
    const endpoint = type === 'transactions' ? 'bank-transactions' : type;
    const res = await fetch(`${BASE}/upload/${endpoint}`, {
      method: 'POST',
      headers: getToken() ? { Authorization: `Bearer ${getToken()}` } : {},
      body: fd,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  },
};
