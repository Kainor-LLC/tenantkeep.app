#!/usr/bin/env python3
# Copyright (c) 2026 Kainor LLC.
# The page shell every renderer shares: the head, the top navigation, each product's second navigation row and the
# footer. render-pages.py (Posture's generated pages, needs the posture repository) and render-site.py (everything
# else, needs only this repository and the On-Call repository's docs) both import it, so a page looks the same
# whichever script wrote it.
import os, re
root = os.path.dirname(os.path.abspath(__file__))
def _template(name):
    return open(os.path.join(root, 'templates', name), encoding='utf-8').read()
HEAD = _template('head.html')
FOOT = _template('foot.html')
NAV = _template('nav.html')
SUBNAV = {'posture': _template('subnav-posture.html'), 'oncall': _template('subnav-oncall.html')}
SECTION_HOME = {'posture': '/posture/', 'oncall': '/on-call/'}
EYEBROW = {'posture': 'TenantKeep Posture', 'oncall': 'TenantKeep On-Call', None: 'TenantKeep'}
TOPBAR = re.search(r'<div class="topbar">.*</nav></div>', NAV, re.S).group(0)
def _mark(markup, href):
    return markup.replace(f'href="{href}"', f'href="{href}" aria-current="page"')
def topbar(section=None, current=None):
    # The top row marks the product; the second row marks the page.
    return _mark(TOPBAR, SECTION_HOME.get(section, current))
def subnav(section, current):
    return _mark(SUBNAV[section], current) if section else ''
def nav(current, section=None):
    return _mark(NAV, SECTION_HOME.get(section, current)) + subnav(section, current)
def head(title, desc, extra=''):
    return HEAD.format(title=title, desc=desc).replace('</head>', extra + '</head>', 1)
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
def page(path, title, desc, h1, lede, fragment, current, eyebrow=None, section='posture'):
    # A document page: the dark top rows, then one article. Posture's pages are the default, as before.
    frag = re.sub(r'^\s*<h1[^>]*>.*?</h1>', '', fragment, count=1, flags=re.S)
    label = eyebrow or EYEBROW[section]
    write(path, head(title, desc) + nav(current, section)
          + f'<main><article class="doc"><span class="eyebrow">{label}</span><h1>{h1}</h1><p class="lede">{lede}</p>{frag}</article></main>\n' + FOOT)
