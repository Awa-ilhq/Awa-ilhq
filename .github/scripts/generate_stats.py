import html
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USERNAME = os.environ.get("GITHUB_USERNAME", "Awa-ilhq")
API_URL = f"https://api.github.com/users/{USERNAME}/repos"
OUTPUT_DIR = Path("profile")
ACCENT = "#ff3b5c"
TEXT = "#e6e6e6"
MUTED = "#9a9a9a"
BACKGROUND = "#0d0d12"
LANGUAGE_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "PHP": "#4F5D95",
    "Dart": "#00B4AB",
    "Java": "#b07219",
    "Kotlin": "#A97BFF",
    "C": "#555555",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Go": "#00ADD8",
    "Ruby": "#701516",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Vue": "#41b883",
}


def fetch_repositories():
    repositories = []
    page = 1
    while True:
        request = Request(
            f"{API_URL}?type=owner&per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "github-profile-stats",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                page_repositories = json.load(response)
        except (HTTPError, URLError) as error:
            raise RuntimeError(f"GitHub API request failed: {error}") from error

        if not isinstance(page_repositories, list):
            raise RuntimeError("GitHub API returned an unexpected response.")

        repositories.extend(page_repositories)
        if len(page_repositories) < 100:
            break
        page += 1

    return [
        repository
        for repository in repositories
        if not repository.get("private") and not repository.get("fork")
    ]


def card_start(width, height, title, subtitle):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{html.escape(title)}</title>
<style>
  text {{ font-family: 'Segoe UI', Ubuntu, sans-serif; }}
  .title {{ fill: {TEXT}; font-size: 17px; font-weight: 600; }}
  .subtitle {{ fill: {MUTED}; font-size: 11px; }}
  .value {{ fill: {TEXT}; font-size: 25px; font-weight: 700; }}
  .label {{ fill: {MUTED}; font-size: 12px; }}
</style>
<rect width="100%" height="100%" rx="8" fill="{BACKGROUND}" stroke="#30363d"/>
<text x="24" y="29" class="title">{html.escape(title)}</text>
<text x="24" y="47" class="subtitle">{html.escape(subtitle)}</text>
<line x1="24" y1="60" x2="{width - 24}" y2="60" stroke="#30363d"/>
"""


def stats_svg(repositories):
    metrics = [
        ("Public repos", len(repositories)),
        ("Stars", sum(repo.get("stargazers_count", 0) for repo in repositories)),
        ("Forks", sum(repo.get("forks_count", 0) for repo in repositories)),
    ]
    svg = [card_start(495, 190, "GitHub Stats", "Public, non-fork repositories")]
    column_width = 495 / len(metrics)
    for index, (label, value) in enumerate(metrics):
        x = column_width * index + column_width / 2
        svg.append(
            f'<text x="{x:g}" y="112" text-anchor="middle" class="value">'
            f"{value:,}</text>"
        )
        svg.append(
            f'<text x="{x:g}" y="137" text-anchor="middle" class="label">'
            f"{html.escape(label)}</text>"
        )
        if index < len(metrics) - 1:
            separator_x = column_width * (index + 1)
            svg.append(
                f'<line x1="{separator_x:g}" y1="83" x2="{separator_x:g}" '
                'y2="151" stroke="#30363d"/>'
            )
    svg.append(
        f'<circle cx="24" cy="169" r="3" fill="{ACCENT}"/>'
        f'<text x="34" y="173" class="subtitle">'
        f"Stats from {len(repositories)} public repositories</text>"
    )
    svg.append("</svg>")
    return "\n".join(svg)


def languages_svg(repositories):
    language_counts = {}
    for repository in repositories:
        language = repository.get("language")
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1

    languages = sorted(
        language_counts.items(), key=lambda item: (-item[1], item[0])
    )[:5]
    svg = [card_start(495, 190, "Top Languages", "Primary language by repository")]
    if not languages:
        svg.append(
            f'<text x="24" y="90" fill="{MUTED}" '
            'font-family="Segoe UI, Ubuntu, sans-serif" font-size="13">'
            "No public repositories with a primary language found.</text>"
        )
    else:
        total_count = sum(language_counts.values())
        for index, (language, count) in enumerate(languages):
            y = 79 + index * 22
            color = LANGUAGE_COLORS.get(language, ACCENT)
            label = html.escape(language)
            repository_label = "repo" if count == 1 else "repos"
            percentage = count * 100 / total_count
            svg.append(
                f'<text x="24" y="{y}" fill="{TEXT}" font-size="11">'
                f"{label} <tspan fill=\"{MUTED}\">· {count} "
                f"{repository_label}</tspan></text>"
            )
            svg.append(
                f'<text x="471" y="{y}" text-anchor="end" fill="{MUTED}" '
                f'font-size="11">{percentage:.0f}%</text>'
            )
            svg.append(
                f'<rect x="24" y="{y + 5}" width="447" height="5" rx="2.5" '
                'fill="#21262d"/>'
            )
            svg.append(
                f'<rect x="24" y="{y + 5}" '
                f'width="{447 * percentage / 100:.1f}" height="5" rx="2.5" '
                f'fill="{color}"/>'
            )
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    repositories = fetch_repositories()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "stats.svg").write_text(stats_svg(repositories), encoding="utf-8")
    (OUTPUT_DIR / "top-langs.svg").write_text(
        languages_svg(repositories), encoding="utf-8"
    )
    print(f"Generated cards using {len(repositories)} public non-fork repositories.")


if __name__ == "__main__":
    main()
