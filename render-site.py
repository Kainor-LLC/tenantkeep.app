#!/usr/bin/env python3
# Copyright (c) 2026 Kainor LLC.
# Renders everything that needs no posture repository: the consent page, TenantKeep On-Call's pages (from the On-Call
# repository's docs, checked out beside this one), the home page and each product's overview, and it gives Posture's
# generated pages the current shell. Run it after changing a template, a page in pages/, or On-Call's docs:
#   python3 render-site.py
import os, re
from site_shell import root, FOOT, head, nav, topbar, subnav, page, write

# --- consent page: begin
# The consent page serves both products. A Posture link carries state=posture or no state; an On-Call link carries
# state=oncall.<key>. The On-Call list is rendered from templates/oncall-app-registrations.json, a copy of
# docs/app-registrations.json in the On-Call repository, where a test holds it to the app's code. Copy it again when
# On-Call says the list changed. The page stays static: the Approve buttons are plain links to Microsoft and nothing
# is fetched.
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
page(os.path.join(root, 'docs', 'consent', 'index.html'), 'TenantKeep · Consent', 'Where an administrator approves a TenantKeep app for an organization, and where Microsoft sends them back afterwards.', 'Consent', 'One approval per organization, by an administrator, for each app. This page shows the result of an approval and, for TenantKeep On-Call, the apps you can approve.', CONSENT, '/consent/', eyebrow='TenantKeep', section=None)
# --- consent page: end

# --- TenantKeep On-Call's pages
# Written and tested in the On-Call repository (docs/), where a test holds the published app list to the code and a
# script builds the glossary from the one inside the app. Here each is given this site's shell: its own title block and
# main content, this site's navigation, footer and stylesheet (the pages' own styles are left behind). Links between them are pointed at their addresses on this site; the
# legal pages, the blog and the files a program reads stay on kainor.com.
ONCALL_DOCS = os.path.join(root, '..', 'LAPSlock-repo', 'docs')
RELINK = [
    ('href="/how-it-works/', 'href="/on-call/how-it-works/'),
    ('href="/pricing/', 'href="/on-call/pricing/'),
    ('href="/glossary/', 'href="/on-call/glossary/'),
    ('href="/privacy/', 'href="https://kainor.com/privacy/'),
    ('href="/terms/', 'href="https://kainor.com/terms/'),
    ('href="/blog/', 'href="https://kainor.com/blog/'),
    ('href="/app-registrations.json"', 'href="https://kainor.com/app-registrations.json"'),
    ('href="/instant-alerts/', 'href="https://kainor.com/instant-alerts/'),
    ('href="/"', 'href="/on-call/"'),
]
def oncall_page(source, dest, current, narrow=True):
    text = open(os.path.join(ONCALL_DOCS, source), encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', text, re.S).group(1).replace(' · Kainor LLC', ' · TenantKeep On-Call').replace('TenantKeep On-Call · TenantKeep On-Call', 'TenantKeep On-Call')
    desc = re.search(r'<meta name="description" content="(.*?)"', text, re.S).group(1)
    title_block = re.search(r'<div class="head-main">.*?</div>\s*(?=</div>\s*</header>)', text, re.S).group(0)
    main = re.search(r'<main.*?</main>', text, re.S).group(0)
    if narrow:
        # A page of prose reads at the document width; the pricing page keeps the full width for its plans.
        assert main.count('<div class="wrap">') == 1, source
        main = main.replace('<div class="wrap">', '<div class="wrap narrow">')
    for old, new in RELINK:
        main = main.replace(old, new); title_block = title_block.replace(old, new)
    left = re.findall(r'href="(/[^"]*)"', main + title_block)
    left = [h for h in left if not h.startswith(('/on-call/', '/consent/', '/posture/'))]
    assert not left, (source, 'links this site does not serve', left)
    write(os.path.join(root, 'docs', dest, 'index.html'),
          head(title, desc) + '<header class="top"><div class="wrap">' + topbar('oncall') + title_block + '</div></header>\n'
          + subnav('oncall', current) + main + '\n' + FOOT)
if os.path.isdir(ONCALL_DOCS):
    oncall_page('how-it-works/index.html', 'on-call/how-it-works', '/on-call/how-it-works/')
    oncall_page('pricing/index.html', 'on-call/pricing', '/on-call/pricing/', narrow=False)
    oncall_page('glossary/index.html', 'on-call/glossary', '/on-call/glossary/')
    print('rendered on-call: how-it-works, pricing, glossary')
else:
    print('On-Call repository not found beside this one; its pages were left as they are')

# --- TenantKeep On-Call's guide and architecture pages
# Written here, in pages/, as the body of a document page: the guide's pictures are in docs/assets/on-call/, taken from
# the app's demo data by the On-Call repository's scripts/store-screenshots.sh and never from a real tenant. Both
# restate what the On-Call repository's docs publish (how it works, the three contracts), so a change there is a
# change here.
def label_cells(body):
    # On a phone a table of three columns does not fit, so each row becomes a card (site.css, table.cards) and each
    # cell says which column it was: the column's heading, written onto the cell here.
    def one(m):
        table = m.group(0)
        labels = [re.sub(r'<[^>]+>', '', t) for t in re.findall(r'<th>(.*?)</th>', table, re.S)]
        def row(r):
            cells = iter(labels)
            return re.sub(r'<td>', lambda _: '<td data-label="%s">' % html.escape(next(cells, ''), quote=True), r.group(0))
        return re.sub(r'<tr><td>.*?</tr>', row, table, flags=re.S).replace('<table>', '<table class="cards">', 1)
    return re.sub(r'<table>.*?</table>', one, body, flags=re.S)
def oncall_doc(source, dest, title, desc, h1, lede):
    body = label_cells(open(os.path.join(root, 'pages', source), encoding='utf-8').read())
    for src in re.findall(r'<img src="/([^"]+)"', body):
        assert os.path.isfile(os.path.join(root, 'docs', src)), (source, 'picture not found', src)
    page(os.path.join(root, 'docs', 'on-call', dest, 'index.html'), title, desc, h1, lede, body, '/on-call/' + dest + '/', section='oncall')
oncall_doc('on-call-guide.html', 'guide', 'TenantKeep On-Call · Using it, step by step',
           'From the first sign-in to the first action in TenantKeep On-Call, with pictures of each screen from the app\'s demo data.',
           'Using TenantKeep On-Call', 'From the first launch to the first action, with what you will see on the way.')
oncall_doc('on-call-architecture.html', 'architecture', 'TenantKeep On-Call · Architecture: what runs where, and as whom',
           'How TenantKeep On-Call is built: the app and Microsoft with nothing between them, eight app registrations with one read-only, what is kept on the device, and the one hosted service.',
           'What Runs Where, and as Whom', 'The structure of TenantKeep On-Call, for the person deciding whether to let it into a tenant.')
print('rendered on-call: guide, architecture')

# --- the pages with a hero: the home page and each product's overview
# Hand-written in pages/, with <!--TOPBAR--> where the top row goes, so a change to the navigation reaches them too.
def hero_page(source, dest, title, desc, section=None, current=None):
    body = open(os.path.join(root, 'pages', source), encoding='utf-8').read()
    assert body.count('<!--TOPBAR-->') == 1 and body.count('<!--SUBNAV-->') == 1, source
    body = body.replace('<!--TOPBAR-->', topbar(section, current)).replace('<!--SUBNAV-->', subnav(section, current))
    write(os.path.join(root, 'docs', dest, 'index.html') if dest else os.path.join(root, 'docs', 'index.html'), head(title, desc) + body + FOOT)
hero_page('home.html', '', 'TenantKeep · Tools for the people who run Microsoft 365', 'TenantKeep On-Call puts the Microsoft administrator\'s on-call work on a phone. TenantKeep Posture turns a tenant\'s configuration into a security posture report. Both by Kainor LLC, both with the source published.', None, '/')
hero_page('on-call.html', 'on-call', 'TenantKeep On-Call · The Microsoft admin\'s on-call app', 'LAPS passwords, BitLocker keys, role activation, sign-in triage, tenant health, Conditional Access, Defender incidents and gated device and user actions, on your iPhone and iPad, as you.', 'oncall', '/on-call/')
hero_page('posture.html', 'posture', 'TenantKeep Posture · The report your Microsoft 365 security posture deserves', 'A read-only collection from your Microsoft 365 tenant becomes a branded security posture report with a risk register, Copilot readiness and Conditional Access documented and diffed. Nothing leaves your tenant.', 'posture', '/posture/')
print('rendered home, on-call, posture')

# --- Posture's generated pages, given the current shell without the posture repository
# render-pages.py writes the same shell when Posture next renders them from its own docs.
def reshell(name, section='posture'):
    path = os.path.join(root, 'docs', name, 'index.html')
    text = open(path, encoding='utf-8').read()
    title = re.search(r'<title>(.*?)</title>', text, re.S).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)"', text, re.S).group(1)
    main = re.search(r'<main>.*</main>', text, re.S).group(0)
    write(path, head(title, desc) + nav('/' + name + '/', section) + main + '\n' + FOOT)
for name in ('guide', 'licensing', 'how-it-works', 'architecture', 'catalog', 'trial'):
    reshell(name)
print('reshelled posture: guide, licensing, how-it-works, architecture, catalog, trial')
# Added for Posture: its security review page, rendered by render-pages.py from the posture repository like the six above.
if os.path.isfile(os.path.join(root, 'docs', 'security', 'index.html')):
    reshell('security')
    print('reshelled posture: security')
