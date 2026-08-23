#!/usr/bin/env python3
"""Generate custom GitHub stats SVG cards for Bhuvan's profile."""

import json
import os
import sys
import urllib.request
import urllib.error


def fetch_json(url, token):
    """Fetch JSON from GitHub API with authentication."""
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "bhuvan-profile-stats")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error for {url}: {e.reason}", file=sys.stderr)
        sys.exit(1)


def fetch_all_repos(username, token):
    """Fetch all public repos with pagination."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner&page={page}"
        data = fetch_json(url, token)
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def generate_svg(stats, theme):
    """Generate SVG card with given theme (dark or light)."""
    if theme == "dark":
        border_color = "#30363D"
        text_color = "#F5F5F5"
        muted_color = "#8B949E"
    else:
        border_color = "#D0D7DE"
        text_color = "#1F2328"
        muted_color = "#656D76"

    crimson = "#C1121F"
    font_family = "'Segoe UI', Ubuntu, sans-serif"

    repos_str = f"{stats['public_repos']:,}"
    stars_str = f"{stats['total_stars']:,}"
    followers_str = f"{stats['followers']:,}"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 495 195" width="495" height="195">
  <rect width="495" height="195" rx="6" fill="none" stroke="{border_color}" stroke-width="1"/>

  <!-- Title -->
  <text x="24" y="34" fill="{crimson}" font-family="{font_family}" font-size="14" font-weight="700" letter-spacing="1.5">BHUVAN // GITHUB</text>
  <text x="24" y="50" fill="{muted_color}" font-family="{font_family}" font-size="9" letter-spacing="0.8">PUBLIC PROFILE SNAPSHOT</text>

  <!-- Vertical separators -->
  <line x1="182" y1="68" x2="182" y2="155" stroke="{border_color}" stroke-width="1"/>
  <line x1="337" y1="68" x2="337" y2="155" stroke="{border_color}" stroke-width="1"/>

  <!-- Column 1: Public Repos -->
  <text x="103" y="95" fill="{crimson}" font-family="{font_family}" font-size="36" font-weight="700" text-anchor="middle">{repos_str}</text>
  <text x="103" y="118" fill="{muted_color}" font-family="{font_family}" font-size="10" text-anchor="middle" letter-spacing="1">PUBLIC REPOS</text>

  <!-- Column 2: Total Stars -->
  <text x="260" y="95" fill="{crimson}" font-family="{font_family}" font-size="36" font-weight="700" text-anchor="middle">{stars_str}</text>
  <text x="260" y="118" fill="{muted_color}" font-family="{font_family}" font-size="10" text-anchor="middle" letter-spacing="1">TOTAL STARS</text>

  <!-- Column 3: Followers -->
  <text x="416" y="95" fill="{crimson}" font-family="{font_family}" font-size="36" font-weight="700" text-anchor="middle">{followers_str}</text>
  <text x="416" y="118" fill="{muted_color}" font-family="{font_family}" font-size="10" text-anchor="middle" letter-spacing="1">FOLLOWERS</text>

  <!-- Footer -->
  <text x="248" y="180" fill="{muted_color}" font-family="{font_family}" font-size="8" text-anchor="middle" letter-spacing="0.5">github.com/bhuvan5821n</text>
</svg>'''
    return svg


def main():
    username = os.environ.get("GITHUB_USERNAME")
    token = os.environ.get("GITHUB_TOKEN")

    if not username:
        print("Error: GITHUB_USERNAME environment variable not set.", file=sys.stderr)
        sys.exit(1)
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching profile for {username}...")
    user_data = fetch_json(f"https://api.github.com/users/{username}", token)

    print("Fetching all public repos...")
    repos = fetch_all_repos(username, token)

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

    stats = {
        "public_repos": user_data["public_repos"],
        "total_stars": total_stars,
        "followers": user_data["followers"],
    }

    print(f"Stats: {stats}")

    os.makedirs("assets/stats", exist_ok=True)

    for theme in ["dark", "light"]:
        svg = generate_svg(stats, theme)
        path = f"assets/stats/github-stats-{theme}.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {path}")

    print("Done.")


if __name__ == "__main__":
    main()
