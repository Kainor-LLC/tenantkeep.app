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
    open(path, 'w').write(HEAD.format(title=title, desc=desc) + nav(current) + f'<main><article class="doc"><span class="eyebrow">Tenantkeep Posture</span><h1>{h1}</h1><p class="lede">{lede}</p>{frag}</article></main>\n' + FOOT)
page(os.path.join(root, 'docs', 'guide', 'index.html'), 'Tenantkeep Posture · Using it, step by step', 'Step by step: install, one-time setup, sign in, collect, profile, evaluate, report, work the findings, trend, automation.', 'Using Tenantkeep Posture', 'Everything below reads your tenant; nothing in the module writes to it. Each run leaves an evidence folder you keep, a report you deliver, and a risk register you work from until the next run.', open(os.path.join(w, 'guide.fragment.html')).read(), '/guide/')
page(os.path.join(root, 'docs', 'licensing', 'index.html'), 'Tenantkeep Posture · Licensing', 'How the signed licence file works, what the module checks, what it does not do.', 'Licensing', 'Source-available, and the entitlement is a signed file verified offline. Nothing is sent anywhere to check it.', open(os.path.join(w, 'licensing.fragment.html')).read(), '/licensing/')
page(os.path.join(root, 'docs', 'how-it-works', 'index.html'), 'Tenantkeep Posture · How it works', 'What runs where, as whom, reading what, writing where.', 'How it works', 'One page for the person who has to reason about the whole thing: what runs where, as whom, reading what, writing where.', open(os.path.join(w, 'architecture.fragment.html')).read(), '/how-it-works/')
page(os.path.join(root, 'docs', 'architecture', 'index.html'), 'Tenantkeep Posture · Architecture: what gets installed, and where', 'The complete inventory of what Tenantkeep Posture puts in your environment, per way of running it, and how to remove every piece.', 'What gets installed, and where', 'The complete inventory, per way of running it: app registrations, identities and their roles, Azure resources, files on disk, and how to remove every piece.', open(os.path.join(w, 'footprint.fragment.html')).read(), '/architecture/')
cat = open(os.path.join(root, '..', 'tenantkeep-posture', 'out', 'catalog.html')).read()
body = re.search(r'<body>(.*?)</body>', cat, re.S).group(1)
body = re.sub(r'^\s*<h1>.*?</h1>', '', body, count=1, flags=re.S)
body = re.sub(r'^\s*<p>Every check the product evaluates.*?</p>', '', body, count=1, flags=re.S)
open(os.path.join(root, 'docs', 'catalog', 'index.html'), 'w').write(HEAD.format(title='Tenantkeep Posture · Check catalog', desc='Every check Tenantkeep Posture evaluates, by domain, with the licence each needs.') + nav('/catalog/') + '<main><article class="doc"><span class="eyebrow">Tenantkeep Posture</span><h1>Check catalog</h1><p class="lede">Every check the product evaluates, by domain. The pass logic, remediation and framework mappings are part of the product; this page lists what is checked and the licence each check needs.</p>' + body + '</article></main>\n' + FOOT)
print('rendered guide, licensing, how-it-works, catalog')
