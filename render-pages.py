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
def page(path, title, desc, h1, lede, fragment, current):
    frag = re.sub(r'^\s*<h1[^>]*>.*?</h1>', '', fragment, count=1, flags=re.S)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(HEAD.format(title=title, desc=desc) + nav(current) + f'<main><article class="doc"><span class="eyebrow">TenantKeep Posture</span><h1>{h1}</h1><p class="lede">{lede}</p>{frag}</article></main>\n' + FOOT)
page(os.path.join(root, 'docs', 'guide', 'index.html'), 'TenantKeep Posture · Using it, step by step', 'Step by step: install, one-time setup, sign in, collect, profile, evaluate, report, work the findings, trend, automation.', 'Using TenantKeep Posture', 'Everything below reads your tenant; nothing in the module writes to it. Each run leaves an evidence folder you keep, a report you deliver, and a risk register you work from until the next run.', open(os.path.join(w, 'guide.fragment.html')).read(), '/guide/')
page(os.path.join(root, 'docs', 'licensing', 'index.html'), 'TenantKeep Posture · Licensing', 'How the signed licence file works, what the module checks, what it does not do.', 'Licensing', 'Source-available, and the entitlement is a signed file verified offline. Nothing is sent anywhere to check it.', open(os.path.join(w, 'licensing.fragment.html')).read(), '/licensing/')
page(os.path.join(root, 'docs', 'how-it-works', 'index.html'), 'TenantKeep Posture · How it works', 'What runs where, as whom, reading what, writing where.', 'How it works', 'One page for the person who has to reason about the whole thing: what runs where, as whom, reading what, writing where.', open(os.path.join(w, 'architecture.fragment.html')).read(), '/how-it-works/')
page(os.path.join(root, 'docs', 'architecture', 'index.html'), 'TenantKeep Posture · Architecture: what gets installed, and where', 'The complete inventory of what TenantKeep Posture puts in your environment, per way of running it, and how to remove every piece.', 'What gets installed, and where', 'The complete inventory, per way of running it: app registrations, identities and their roles, Azure resources, files on disk, and how to remove every piece.', open(os.path.join(w, 'footprint.fragment.html')).read(), '/architecture/')
CONSENT = """<p>If you came here from an admin consent prompt, the result is below. Nothing else happens on this page: no cookie, no script talks to anyone, the address bar is the only input.</p>
<div id="consent-result" class="callout"><p>Reading the result from the address bar.</p></div>
<h2>What you consented to</h2>
<p>TenantKeep Posture is a multi-tenant application published by Kainor LLC with delegated, read-only permissions and no credentials of its own. Every token it ever holds belongs to the administrator who signed in and goes no further than that administrator's roles. The full list of permissions is in the module's <code>app.json</code> and was on the consent screen. Remove the consent at any time by deleting the enterprise application in Entra ID; the next run says consent is needed.</p>
<h2>Next</h2>
<p>Go back to the terminal and run <code>Start-PostureRun</code> again. The sign-in now completes and the collection starts.</p>
<script>
(function () {
  var q = new URLSearchParams(window.location.search);
  var box = document.getElementById('consent-result');
  var esc = function (t) { return String(t || '').replace(/[&<>"']/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]; }); };
  if (q.get('admin_consent') === 'True') {
    box.className = 'callout ok';
    box.innerHTML = '<p><strong>Consent recorded</strong> for tenant <code>' + esc(q.get('tenant')) + '</code>. You can close this window.</p>';
  } else if (q.get('error')) {
    box.className = 'callout warn';
    box.innerHTML = '<p><strong>Consent did not complete:</strong> ' + esc(q.get('error')) + '. ' + esc(q.get('error_description')) + '</p><p>Only a Global Administrator, Privileged Role Administrator or Cloud Application Administrator can consent for the organisation.</p>';
  } else {
    box.innerHTML = '<p>No consent result in the address. An administrator consents from the link <code>Start-PostureRun</code> prints, or from the Entra admin center under Enterprise applications.</p>';
  }
})();
</script>"""
page(os.path.join(root, 'docs', 'consent', 'index.html'), 'TenantKeep Posture · Consent', 'The landing page for the admin consent to the TenantKeep Posture application.', 'Consent', 'One consent per tenant, by an administrator, to a read-only application with no credentials. This page shows the result and nothing more.', CONSENT, '/consent/')
cat = open(os.path.join(root, '..', 'tenantkeep-posture', 'out', 'catalog.html')).read()
body = re.search(r'<body>(.*?)</body>', cat, re.S).group(1)
body = re.sub(r'^\s*<h1>.*?</h1>', '', body, count=1, flags=re.S)
body = re.sub(r'^\s*<p>Every check the product evaluates.*?</p>', '', body, count=1, flags=re.S)
open(os.path.join(root, 'docs', 'catalog', 'index.html'), 'w').write(HEAD.format(title='TenantKeep Posture · Check catalog', desc='Every check TenantKeep Posture evaluates, by domain, with the licence each needs.') + nav('/catalog/') + '<main><article class="doc"><span class="eyebrow">TenantKeep Posture</span><h1>Check catalog</h1><p class="lede">Every check the product evaluates, by domain. The pass logic, remediation and framework mappings are part of the product; this page lists what is checked and the licence each check needs.</p>' + body + '</article></main>\n' + FOOT)
print('rendered guide, licensing, how-it-works, architecture, consent, catalog')
