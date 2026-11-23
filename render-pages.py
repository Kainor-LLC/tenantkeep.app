#!/usr/bin/env python3
# Copyright (c) 2026 Kainor LLC.
# Renders Posture's guide, licensing, how-it-works, architecture, trial page and catalog into the site shell from the
# fragments update-pages.ps1 wrote. Everything that needs no posture repository is in render-site.py.
import os, re
from site_shell import root, HEAD, FOOT, nav, page
w = os.path.join(root, '.work')
def frag(name):
    # A page's body as update-pages.ps1 converted it from the posture repository's Markdown. A picture is written there
    # with its full address on this site, so that it also shows where the Markdown is read on GitHub; here it becomes
    # a path on this site, which the local preview serves too, and a picture that is not in docs/ stops the render.
    # A link to another page of this site is written the same way and becomes a path the same way.
    text = open(os.path.join(w, name + '.fragment.html'), encoding='utf-8').read().replace('src="https://tenantkeep.app/assets/', 'src="/assets/').replace('href="https://tenantkeep.app/', 'href="/')
    for src in re.findall(r'<img[^>]* src="/([^"]+)"', text):
        assert os.path.isfile(os.path.join(root, 'docs', src)), (name, 'picture not found', src)
    return text
page(os.path.join(root, 'docs', 'guide', 'index.html'), 'TenantKeep Posture · Using it, step by step', 'Step by step: install, one-time setup, sign in, collect, profile, evaluate, report, work the findings, trend, automation.', 'Using TenantKeep Posture', 'From the first run to the scheduled one, step by step, with pictures of the report it produces.', frag('guide'), '/guide/')
page(os.path.join(root, 'docs', 'licensing', 'index.html'), 'TenantKeep Posture · Licensing', 'How the signed licence file works, what the module checks, what it does not do.', 'Licensing', 'Source-available, and the entitlement is a signed file verified offline. Nothing is sent anywhere to check it.', frag('licensing'), '/licensing/')
page(os.path.join(root, 'docs', 'how-it-works', 'index.html'), 'TenantKeep Posture · How it works', 'What runs where, as whom, reading what, writing where.', 'How it works', 'One page for the person who has to reason about the whole thing: what runs where, as whom, reading what, writing where.', frag('architecture'), '/how-it-works/')
page(os.path.join(root, 'docs', 'architecture', 'index.html'), 'TenantKeep Posture · Architecture: what runs where, and what gets installed', 'What runs where and as whom in TenantKeep Posture, what it reads, what leaves your tenant, and the complete inventory of what it installs, with how to remove every piece.', 'What Runs Where, and What Gets Installed', 'What runs where and as whom, what it reads, and what leaves your tenant, which is nothing.', frag('footprint'), '/architecture/')
# The trial page. The Turnstile site key is public; it lives in templates/turnstile-site-key.txt once the widget exists in
# Cloudflare. Without it the page says to email instead of showing a form that cannot pass the bot check.
TRIAL_API = 'https://func-tkp-lic-flex-c7w36xj7gjlug.azurewebsites.net/api/trial'
_k = os.path.join(root, 'templates', 'turnstile-site-key.txt')
SITE_KEY = open(_k).read().strip() if os.path.exists(_k) else ''
TRIAL_FORM = """<form id="trial" class="trial-form" novalidate>
<label>Tenant id<input name="tenantId" id="tenantId" required pattern="[0-9a-fA-F-]{36}" autocomplete="off" placeholder="00000000-0000-0000-0000-000000000000"></label>
<label>Work email<input name="email" type="email" required autocomplete="email" placeholder="you@yourcompany.com"></label>
<label>Organisation<input name="customer" required maxlength="120" autocomplete="organization" placeholder="Contoso Ltd"></label>
<div class="cf-turnstile" data-sitekey="%s"></div>
<button type="submit">Send my trial licence</button>
</form>
<div id="trial-result" class="callout" hidden></div>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<script>
(function () {
  var q = new URLSearchParams(location.search), f = document.getElementById('trial'), box = document.getElementById('trial-result');
  if (q.get('tenant')) { document.getElementById('tenantId').value = q.get('tenant'); }
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(f), btn = f.querySelector('button');
    btn.disabled = true; box.hidden = false; box.textContent = 'Checking and sending...';
    fetch('%s', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tenantId: d.get('tenantId'), email: d.get('email'), customer: d.get('customer'), turnstile: d.get('cf-turnstile-response') }) })
      .then(function (r) { return r.json(); })
      .then(function (j) { box.textContent = j.message; if (!j.ok) { btn.disabled = false; if (window.turnstile) { turnstile.reset(); } } })
      .catch(function () { box.textContent = 'The request did not reach us. Write to licensing@kainor.com and we will send the trial by hand.'; btn.disabled = false; });
  });
})();
</script>""" % (SITE_KEY, TRIAL_API)
TRIAL_CLOSED = """<div class="callout"><p>The trial form opens shortly. Until then, write to <a href="mailto:licensing@kainor.com?subject=TenantKeep%20Posture%20trial">licensing@kainor.com</a> with your tenant id and we will send a 30-day licence by hand.</p></div>"""
TRIAL = """<p>Thirty days of every domain in the report, for one tenant, free. The Conditional Access domain needs no licence at all.</p>
<h2>What you send, and why</h2>
<ul><li><strong>Tenant id:</strong> the licence is bound to it. <code>Start-PostureRun</code> prints this page's link with it filled in.</li>
<li><strong>Work email:</strong> the licence arrives there. Its domain must be one your tenant has verified, which is how we know the request comes from inside your organisation.</li>
<li><strong>Organisation:</strong> the name the report prints on its cover.</li></ul>
<p>That is all we keep: one row recording that this tenant had its trial. Nothing about your tenant is collected, now or when you run the module; verification of the licence is offline.</p>
""" + (TRIAL_FORM if SITE_KEY else TRIAL_CLOSED) + """
<h2>When it arrives</h2>
<p>Save the attachment, then run <code>Initialize-PostureClient -LicensePath &lt;file&gt;</code> once and <code>Start-PostureRun</code> as usual. One trial per tenant; reply to the email if you need longer.</p>"""
page(os.path.join(root, 'docs', 'trial', 'index.html'), 'TenantKeep Posture · Free trial', 'A 30-day TenantKeep Posture licence for one tenant, sent to a work email in a domain the tenant owns.', 'Free trial', 'Every domain, one tenant, thirty days.', TRIAL, '/trial/')
cat = open(os.path.join(root, '..', 'tenantkeep-posture', 'out', 'catalog.html')).read()
body = re.search(r'<body>(.*?)</body>', cat, re.S).group(1)
body = re.sub(r'^\s*<h1>.*?</h1>', '', body, count=1, flags=re.S)
body = re.sub(r'^\s*<p>Every check the product evaluates.*?</p>', '', body, count=1, flags=re.S)
open(os.path.join(root, 'docs', 'catalog', 'index.html'), 'w').write(HEAD.format(title='TenantKeep Posture · Check catalog', desc='Every check TenantKeep Posture evaluates, by domain, with the licence each needs.') + nav('/catalog/', 'posture') + '<main><article class="doc"><span class="eyebrow">TenantKeep Posture</span><h1>Check catalog</h1><p class="lede">Every check the product evaluates, by domain. The pass logic, remediation and framework mappings are part of the product; this page lists what is checked and the licence each check needs.</p>' + body + '</article></main>\n' + FOOT)
# The counts on Posture's overview page come from the catalog the build just wrote ("N checks in M domains."), so they
# never go stale: every element marked data-count="checks" or data-count="domains-word", in the page's source
# (pages/posture.html, which render-site.py renders) and in the page as last rendered.
_m = re.search(r'(\d+) checks in (\d+) domains\.', open(os.path.join(root, '..', 'tenantkeep-posture', 'out', 'catalog.md'), encoding='utf-8').read())
if _m:
    _words = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen', 'Twenty']
    _checks, _domains = int(_m.group(1)), int(_m.group(2))
    for _path in (os.path.join(root, 'pages', 'posture.html'), os.path.join(root, 'docs', 'posture', 'index.html')):
        _text = open(_path, encoding='utf-8').read()
        _new = re.sub(r'(data-count="checks">)[\d,]+(<)', lambda x: x.group(1) + str(_checks) + x.group(2), _text)
        _new = re.sub(r'(data-count="domains-word">)\w+(<)', lambda x: x.group(1) + (_words[_domains] if _domains < len(_words) else str(_domains)) + x.group(2), _new)
        if _new != _text:
            open(_path, 'w', encoding='utf-8').write(_new)
    print(f'posture overview counts: {_checks} checks, {_domains} domains')
print('rendered guide, licensing, how-it-works, architecture, trial, catalog')
