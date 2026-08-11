#!/usr/bin/env python3
"""
claude-usage — waybar module showing Claude quota usage.

Reports the 5-hour session window, the weekly cap, and extra-usage credit
spend, from Anthropic's OAuth usage endpoint.

Output: one line of JSON for waybar ({text, tooltip, class}).

Note: /api/oauth/usage is undocumented — it is what the Claude Code CLI uses.
If Anthropic changes it, this degrades to a "?" indicator rather than breaking
the bar.  Last-known-good values are cached so a transient network failure
shows stale data instead of a blank module.
"""

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

CREDS = os.path.expanduser('~/.claude/.credentials.json')
CACHE = os.path.expanduser('~/.cache/claude-usage.json')
URL = 'https://api.anthropic.com/api/oauth/usage'
TIMEOUT = 10

ICON = '\U000f06a9'          # nf-md-robot — must be in the F0000 PUA block that
                             # the Nerd Fonts patch uses; codepoints outside it
                             # (e.g. U+DB2E7) render as a .notdef box
SPEND_BAR_THRESHOLD = 80.0   # only show spend in the bar above this percent
WARNING = 70.0
CRITICAL = 90.0


def emit(text, tooltip, cls=''):
    """Print a waybar JSON line and exit."""
    print(json.dumps({'text': text, 'tooltip': tooltip, 'class': cls}))
    sys.exit(0)


def read_token():
    with open(CREDS) as f:
        oauth = json.load(f)['claudeAiOauth']
    expires = oauth.get('expiresAt')
    if expires and expires / 1000 < datetime.now(timezone.utc).timestamp():
        return None, 'expired'
    return oauth['accessToken'], None


def fetch(token):
    req = urllib.request.Request(URL, headers={
        'Authorization': f'Bearer {token}',
        'anthropic-beta': 'oauth-2025-04-20',
        'Accept': 'application/json',
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
        return json.load(r)


def load_cache():
    try:
        with open(CACHE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_cache(data):
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        tmp = CACHE + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(data, f)
        os.replace(tmp, CACHE)
    except OSError:
        pass  # cache is best-effort


def until(iso):
    """Human 'in 2h14m' for an ISO timestamp, or '' if unparseable/past."""
    if not iso:
        return ''
    try:
        when = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return ''
    secs = (when - datetime.now(timezone.utc)).total_seconds()
    if secs <= 0:
        return 'due'
    hrs, mins = int(secs // 3600), int(secs % 3600 // 60)
    if hrs >= 24:
        days = hrs // 24
        return f'{days}d {hrs % 24}h'
    return f'{hrs}h {mins:02d}m' if hrs else f'{mins}m'


def local_time(iso):
    if not iso:
        return '?'
    try:
        when = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    except ValueError:
        return '?'
    return when.astimezone().strftime('%a %d %b %H:%M')


def money(block):
    """Format a {amount_minor, currency, exponent} block as e.g. £68.85."""
    if not block:
        return None
    amt = block.get('amount_minor')
    if amt is None:
        return None
    exp = block.get('exponent', 2)
    sym = {'GBP': '£', 'USD': '$', 'EUR': '€'}.get(block.get('currency'), '')
    return f'{sym}{amt / (10 ** exp):.2f}'


def parse(data):
    """Pull the fields we display out of the API payload.

    Tolerates missing/renamed keys: anything absent comes back as None and is
    simply not displayed, rather than raising.
    """
    out = {'session': None, 'weekly': None, 'spend': None}

    for lim in (data.get('limits') or []):
        if not isinstance(lim, dict):
            continue
        entry = {
            'percent': lim.get('percent'),
            'resets_at': lim.get('resets_at'),
            'severity': lim.get('severity') or 'normal',
        }
        if lim.get('kind') == 'session':
            out['session'] = entry
        elif lim.get('group') == 'weekly' and out['weekly'] is None:
            out['weekly'] = entry

    # Fall back to the older top-level shape if limits[] is absent.
    if out['session'] is None and isinstance(data.get('five_hour'), dict):
        fh = data['five_hour']
        out['session'] = {'percent': fh.get('utilization'),
                          'resets_at': fh.get('resets_at'), 'severity': 'normal'}
    if out['weekly'] is None and isinstance(data.get('seven_day'), dict):
        sd = data['seven_day']
        out['weekly'] = {'percent': sd.get('utilization'),
                         'resets_at': sd.get('resets_at'), 'severity': 'normal'}

    sp = data.get('spend')
    if isinstance(sp, dict) and sp.get('enabled'):
        out['spend'] = {
            'percent': sp.get('percent'),
            'used': money(sp.get('used')),
            'limit': money(sp.get('limit')),
        }
    return out


def pct(v):
    return f'{v:.0f}%' if isinstance(v, (int, float)) else '?'


def render(u, stale=False):
    parts = []
    for key in ('session', 'weekly'):
        if u.get(key):
            parts.append(pct(u[key]['percent']))
    text = f'{ICON}  ' + (' · '.join(parts) if parts else '?')

    spend = u.get('spend')
    sp_pct = spend.get('percent') if spend else None
    if spend and isinstance(sp_pct, (int, float)) and sp_pct >= SPEND_BAR_THRESHOLD:
        if spend.get('used'):
            text += f' · {spend["used"]}'

    if stale:
        text += ' ⚠'

    # Worst percentage across the windows drives the colour.
    worst = max((u[k]['percent'] for k in ('session', 'weekly')
                 if u.get(k) and isinstance(u[k].get('percent'), (int, float))),
                default=0)
    if spend and isinstance(sp_pct, (int, float)):
        worst = max(worst, sp_pct)
    cls = 'critical' if worst >= CRITICAL else 'warning' if worst >= WARNING else ''

    lines = ['<b>Claude usage</b>']
    if u.get('session'):
        s = u['session']
        lines.append(f'Session (5h)  {pct(s["percent"])}')
        if s.get('resets_at'):
            lines.append(f'  resets in {until(s["resets_at"])}  ({local_time(s["resets_at"])})')
    if u.get('weekly'):
        w = u['weekly']
        lines.append(f'Weekly        {pct(w["percent"])}')
        if w.get('resets_at'):
            lines.append(f'  resets in {until(w["resets_at"])}  ({local_time(w["resets_at"])})')
    if spend:
        used, limit = spend.get('used'), spend.get('limit')
        if used and limit:
            lines.append(f'Credits       {used} / {limit}  ({pct(sp_pct)})')
    if stale:
        lines.append('')
        lines.append('<i>stale — could not reach API</i>')

    emit(text, '\n'.join(lines), cls)


def main():
    try:
        token, err = read_token()
    except (OSError, ValueError, KeyError):
        emit(f'{ICON}  auth?', 'Claude usage: cannot read credentials', 'critical')
    if err == 'expired':
        emit(f'{ICON}  auth?', 'Claude usage: token expired — run `claude` to refresh', 'critical')

    try:
        data = fetch(token)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
        cached = load_cache()
        if cached:
            render(cached, stale=True)
        reason = getattr(e, 'code', None) or type(e).__name__
        emit(f'{ICON}  ?', f'Claude usage unavailable ({reason})', 'warning')

    try:
        usage = parse(data)
    except Exception:
        emit(f'{ICON}  ?', 'Claude usage: unexpected API response', 'warning')

    if not any(usage.values()):
        emit(f'{ICON}  ?', 'Claude usage: no usage data in API response', 'warning')

    save_cache(usage)
    render(usage)


if __name__ == '__main__':
    main()
