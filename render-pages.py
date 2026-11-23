#!/usr/bin/env python3
# Copyright (c) 2026 Kainor LLC.
# Renders guide, licensing, how-it-works and the catalog into the site shell from the fragments update-pages.ps1 wrote.
import os, re
root = os.path.dirname(os.path.abspath(__file__))
w = os.path.join(root, '.work')
HEAD = open(os.path.join(root, 'templates', 'head.html')).read()
FOOT = open(os.path.join(root, 'templates', 'foot.html')).read()
NAV = open(os.path.join(root, 'templates', 'nav.html')).read()
def nav(current):
    return NAV.replace(f'href="{current}"', f'href="{current}" aria-current="page"')
def page(path, title, desc, h1, lede, fragment, current, eyebrow='TenantKeep Posture'):
    frag = re.sub(r'^\s*<h1[^>]*>.*?</h1>', '', fragment, count=1, flags=re.S)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(HEAD.format(title=title, desc=desc) + nav(current) + f'<main><article class="doc"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lede">{lede}</p>{frag}</article></main>\n' + FOOT)
page(os.path.join(root, 'docs', 'guide', 'index.html'), 'TenantKeep Posture · Using it, step by step', 'Step by step: install, one-time setup, sign in, collect, profile, evaluate, report, work the findings, trend, automation.', 'Using TenantKeep Posture', 'Everything below reads your tenant; nothing in the module writes to it. Each run leaves an evidence folder you keep, a report you deliver, and a risk register you work from until the next run.', open(os.path.join(w, 'guide.fragment.html')).read(), '/guide/')
page(os.path.join(root, 'docs', 'licensing', 'index.html'), 'TenantKeep Posture · Licensing', 'How the signed licence file works, what the module checks, what it does not do.', 'Licensing', 'Source-available, and the entitlement is a signed file verified offline. Nothing is sent anywhere to check it.', open(os.path.join(w, 'licensing.fragment.html')).read(), '/licensing/')
page(os.path.join(root, 'docs', 'how-it-works', 'index.html'), 'TenantKeep Posture · How it works', 'What runs where, as whom, reading what, writing where.', 'How it works', 'One page for the person who has to reason about the whole thing: what runs where, as whom, reading what, writing where.', open(os.path.join(w, 'architecture.fragment.html')).read(), '/how-it-works/')
page(os.path.join(root, 'docs', 'architecture', 'index.html'), 'TenantKeep Posture · Architecture: what gets installed, and where', 'The complete inventory of what TenantKeep Posture puts in your environment, per way of running it, and how to remove every piece.', 'What gets installed, and where', 'The complete inventory, per way of running it: app registrations, identities and their roles, Azure resources, files on disk, and how to remove every piece.', open(os.path.join(w, 'footprint.fragment.html')).read(), '/architecture/')
# --- consent page: begin
# The consent page serves both products. A Posture link carries state=posture or no state; an On-Call link carries
# state=oncall.<key>. The On-Call list is rendered from templates/oncall-app-registrations.json, a copy of
# docs/app-registrations.json in the On-Call repository, where a test holds it to the app's code. Copy it again when
# On-Call says the list changed. The page stays static: the Approve buttons are plain links to Microsoft and nothing
# is fetched. This block needs nothing from the posture repository, so it can be rendered alone.
import json, html
from urllib.parse import quote
ONCALL = json.load(open(os.path.join(root, 'templates', 'oncall-app-registrations.json')))
def consent_link(entry):
    # Named permissions, never .default: on the read-only app, which Posture shares, .default would ask for both products'.
    scopes = ['https://graph.microsoft.com/' + s for s in entry['scopes']] + entry.get('ownScopes', [])
    return ('https://login.microsoftonline.com/organizations/v2.0/adminconsent?client_id=' + entry['clientId']
            + '&scope=' + quote(' '.join(scopes), safe='') + '&redirect_uri=' + quote(ONCALL['consentPage'], safe='')
            + '&state=oncall.' + entry['key'])
def oncall_app(entry, above=''):
    names = entry['scopes'] + entry.get('ownScopes', [])
    word = 'permission' if len(names) == 1 else 'permissions'
    items = ''.join('<li><code>' + html.escape(n) + '</code></li>' for n in names)
    name = html.escape(entry['name'])
    return ('<h3 id="oncall-' + entry['key'] + '">' + name + '</h3>' + above + '<p>' + html.escape(entry['summary']) + '</p>'
            + '<details><summary>The ' + str(len(names)) + ' ' + word + ' it asks for</summary><ul>' + items + '</ul></details>'
            + '<p><a class="btn btn-solid" href="' + html.escape(consent_link(entry)) + '" rel="noopener">Approve ' + name + '</a></p>'
            + '<p class="appid">Application ID <code>' + entry['clientId'] + '</code></p>\n')
_app = {e['key']: e for e in ONCALL['registrations']}
ONCALL_HTML = ("""<section id="oncall">
<h2>TenantKeep On-Call</h2>
<p>TenantKeep On-Call signs in through a Microsoft app that can only read. Anything that changes your tenant goes through a separate app, and each one works only after an administrator approves it here. Approving does not give anyone new rights: a person can still do only what their own Microsoft roles allow, and every action is in your audit log under their name.</p>
<p><strong>Who can approve:</strong> a Global Administrator, or another role your organization allows to grant consent for the whole organization. Each button opens Microsoft's own approval screen, which lists the same permissions before you accept. To see or remove an approval later, find the app by name under Enterprise applications in the Entra admin center.</p>
"""
    + oncall_app(_app['read'], '<p><strong>Start here.</strong> Everyone who uses the app needs this one.</p>')
    + """<div class="callout"><p><strong>For actions, choose one of two ways.</strong> Approve a separate app for each kind of action you want, and leave out the ones you do not. Or approve TenantKeep Actions, one app that holds all of them. If you approve both, the separate app is used.</p></div>
"""
    + ''.join(oncall_app(_app[k]) for k in ('roleActivation', 'deviceActions', 'userActions', 'accountRecovery', 'groupMembership'))
    + oncall_app(_app['actions'], "<p>With this one app, turning on any action in TenantKeep gives the phone a token that carries every action permission listed here. A person's own roles still decide what they can do.</p>")
    + oncall_app(_app['alerts'])
    + """<h3>If your organization used LAPSlock</h3>
<p>It approved an earlier app that is now TenantKeep Actions. After the update everything keeps working through it. Approve the read-only app, TenantKeep, at the top of this list to finish the move.</p>
</section>
""")
CONSENT = ("""<p>If Microsoft sent you here after an approval, the result is below. If you are here to approve a TenantKeep On-Call app for your organization, the buttons are further down. Nothing else happens on this page: no cookie, no script talks to anyone, the address bar is the only input.</p>
<div id="consent-result" class="callout"><p>Reading the result from the address bar.</p></div>
""" + ONCALL_HTML + """<section id="posture">
<h2>TenantKeep Posture</h2>
<h3>What you consented to</h3>
<p>TenantKeep Posture is a multi-tenant application published by Kainor LLC with delegated, read-only permissions and no credentials of its own. Every token it ever holds belongs to the administrator who signed in and goes no further than that administrator's roles. The full list of permissions is in the module's <code>app.json</code> and was on the consent screen. Remove the consent at any time by deleting the enterprise application in Entra ID; the next run says consent is needed.</p>
<h3>Next</h3>
<p>Go back to the terminal and run <code>Start-PostureRun</code> again. The sign-in now completes and the collection starts.</p>
</section>
<script>
(function () {
  var q = new URLSearchParams(window.location.search);
  var box = document.getElementById('consent-result');
  var esc = function (t) { return String(t || '').replace(/[&<>"']/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]; }); };
  var apps = __APPS__;
  var state = q.get('state') || '';
  var onCall = state.indexOf('oncall.') === 0;
  var key = onCall ? state.slice(7) : '';
  var name = Object.prototype.hasOwnProperty.call(apps, key) ? apps[key] : null;
  var hide = function (id) { var s = document.getElementById(id); if (s) { s.hidden = true; } };
  if (q.get('admin_consent') === 'True') {
    box.className = 'callout ok';
    if (name) {
      box.innerHTML = '<p><strong>' + esc(name) + ' is approved for your organization.</strong> Tenant <code>' + esc(q.get('tenant')) + '</code>. You can close this window and go back to TenantKeep On-Call, or approve another app below.</p>';
      hide('posture');
    } else {
      box.innerHTML = '<p><strong>Consent recorded</strong> for tenant <code>' + esc(q.get('tenant')) + '</code>. You can close this window.</p>';
      if (!onCall) { hide('oncall'); }
    }
  } else if (q.get('error')) {
    box.className = 'callout warn';
    box.innerHTML = '<p><strong>Nothing was approved.</strong> ' + esc(q.get('error')) + '. ' + esc(q.get('error_description')) + '</p><p>Only a Global Administrator, Privileged Role Administrator or Cloud Application Administrator can consent for the organisation.</p>';
    hide(onCall ? 'posture' : 'oncall');
  } else {
    box.innerHTML = '<p>No approval result in the address. To approve a TenantKeep On-Call app, use the buttons below. For TenantKeep Posture, an administrator consents from the link <code>Start-PostureRun</code> prints, or from the Entra admin center under Enterprise applications.</p>';
  }
})();
</script>""").replace('__APPS__', json.dumps({e['key']: e['name'] for e in ONCALL['registrations']}))
page(os.path.join(root, 'docs', 'consent', 'index.html'), 'TenantKeep · Consent', 'Where an administrator approves a TenantKeep app for an organization, and where Microsoft sends them back afterwards.', 'Consent', 'One approval per organization, by an administrator, for each app. This page shows the result of an approval and, for TenantKeep On-Call, the apps you can approve.', CONSENT, '/consent/', eyebrow='TenantKeep')
# --- consent page: end
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
open(os.path.join(root, 'docs', 'catalog', 'index.html'), 'w').write(HEAD.format(title='TenantKeep Posture · Check catalog', desc='Every check TenantKeep Posture evaluates, by domain, with the licence each needs.') + nav('/catalog/') + '<main><article class="doc"><span class="eyebrow">TenantKeep Posture</span><h1>Check catalog</h1><p class="lede">Every check the product evaluates, by domain. The pass logic, remediation and framework mappings are part of the product; this page lists what is checked and the licence each check needs.</p>' + body + '</article></main>\n' + FOOT)
print('rendered guide, licensing, how-it-works, architecture, consent, catalog')
