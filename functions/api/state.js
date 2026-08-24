// Cloudflare Pages Function: /api/state
// 按同步码在 KV 中隔离读写用户数据。KV 绑定变量名需为 XUSHENG_KV。
export async function onRequestGet({ env, request }) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  if (!code) return json({ error: 'missing code' }, 400);
  const raw = await env.XUSHENG_KV.get('state:' + code);
  if (!raw) return json({ state: null, savedAt: 0 }, 200);
  try {
    return json(JSON.parse(raw), 200);
  } catch {
    return json({ state: null, savedAt: 0 }, 200);
  }
}

export async function onRequestPut({ env, request }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'bad body' }, 400);
  }
  const code = body && body.code;
  if (!code || !body.state) return json({ error: 'missing code or state' }, 400);
  const savedAt = body.savedAt || Date.now();
  await env.XUSHENG_KV.put('state:' + code, JSON.stringify({ state: body.state, savedAt }));
  return json({ ok: true, savedAt }, 200);
}

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
  });
}
