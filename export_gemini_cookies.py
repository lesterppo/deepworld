#!/usr/bin/env python3
"""
Export Gemini Web session cookies for GitHub Actions.
Run this ONCE locally, then add the output to GitHub Secrets.

Usage:
    python3 export_gemini_cookies.py
    # Copy GEMINI_SID and GEMINI_TS to:
    # https://github.com/lesterppo/deepworld/settings/secrets/actions
"""

import browser_cookie3, sys

def get_cookies():
    results = {}
    # Try Chrome, then Firefox
    for browser_name, getter in [
        ("Chrome", lambda: browser_cookie3.chrome(domain_name='google.com')),
        ("Firefox", lambda: browser_cookie3.firefox(domain_name='google.com')),
    ]:
        try:
            cj = getter()
            for c in cj:
                if c.name == '__Secure-1PSID':
                    results['GEMINI_SID'] = c.value
                elif c.name == '__Secure-1PSIDTS':
                    results['GEMINI_TS'] = c.value
            if results:
                print(f"Found cookies in {browser_name}")
                break
        except Exception as e:
            print(f"{browser_name}: {e}", file=sys.stderr)

    return results

cookies = get_cookies()
if not cookies:
    print("ERROR: No Gemini cookies found. Sign in to gemini.google.com first.")
    sys.exit(1)

print("\n=== ADD THESE TO GITHUB SECRETS ===")
print("Go to: https://github.com/lesterppo/deepworld/settings/secrets/actions\n")
for key, value in cookies.items():
    print(f"Secret name: {key}")
    print(f"Secret value: {value}")
    print()
print("=== END SECRETS ===")
print(f"\nSID expires check: these are session cookies from your browser.")
print("If simulation fails with auth errors, re-run this script.")
