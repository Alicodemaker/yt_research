import os, re, subprocess, sys, time
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

# Videos to fetch: (video ID, title). Add or remove lines as you like.
VIDEOS = [
    ('eiz7FwVSBNk', 'New way to prompt Fable 5 to design amazing websites'),
    ('inRonh4mTYQ', 'Fable 5 VS Web Designer: Who Designs a Better Website?'),
    ('sUMHUMNtGaY', 'AI Web Design Process: Claude to Webflow'),
    ('0xzUw4NnzFk', 'Build a Website with AI For Beginners in 2026 (Relume Crash Course)'),
    ('i8fj-nOvpek', 'I used Claude to design… too much'),
    ('_cP7l_hFcVw', 'Designer reveals real $29k proposal'),
    ('RCneB_MQ7qs', 'The one thing vibe coding CAN’T fix about your website'),
    ('eMMiLeo_UGI', 'The 4 Levels of Landing Page UI/UX Design'),
    ('PDcQJOPby1k', '5 SaaS UI/UX mistakes that SCREAM you Vibe Code'),
    ('EcbgbKtOELY', 'Every UI/UX Concept Explained in Under 10 Minutes'),
    ('YSYqFBq68Wk', 'Using Claude Design 2.0 to NOT Produce SLOP'),
    ('k472CaM72Jk', 'Making Vibe Designed Layouts Better'),
    ('tSg3FAdWvzI', 'Claude Fable 5 UI/UX One-Shots - 5 Tests'),
    ('nl6zw_L1j_U', "Copying other website's Design.MD File. Is it stealing?"),
    ('PgEhelyX5hU', 'Build Websites With AI AND Keep Full Design Control!'),
    ('RTrbg5z_UBk', 'EmDash + Astro: The CMS Combo That Could Power Your Next Site'),
    ('qokQQRtYYqg', 'Web Design Workflow: Are You Ready for the Future?'),
    ('2pJHWhmqlNU', 'The most undervalued front-end skill right now'),
    ('CU8Plk-53RU', 'Three CSS patterns I use in every project'),
    ('bLB90QwRki4', 'No more clamp() magic numbers'),
    ('R1kiLX-Z-Io', 'Handy CSS layout patterns, and fun ways to elevate them'),
    ('jijpWhXgj00', "I Built a $20k Real Estate Website With Claude. It's Yours (Use It, Sell It)"),
    ('wH_J_SdRxrQ', 'My New App Got 1,800 Signups (But We Have a Problem)'),
    ('9Hwanevuhd8', 'Top 6 AI Productivity Tips for Work!'),
    ('P2_8dTsno1s', 'These Mobile mistakes drop conversion'),
    ('yMKHtJpgZzc', '13 Mind-Blowing AI Hacks That Can Actually Change Your Life'),
    ('mImbbszCjCI', 'I Studied 10,000 AI Websites… Here’s what I learned'),
    ('XtvbzN67PhA', 'My Best Claude Code Advice After 20 Years of Coding'),
    ('VnJiHSS5Pjk', 'Claude Code Projects is INSANE for Building Apps (From Your Phone)'),
    ('hWe-j78vNpc', 'The Home Repo: The effortless multi-repo agent setup'),
    ('XNlfTH9XX5w', 'Context7 Search: The Best Free Way to Give AI Fresh Docs'),
    ('_3Slvs-LDGE', 'I REBUILT My Oldest App (Revenue Jumped 41%)'),
    ('nPSvUczm8M0', 'nobody wants your AI app...'),
    ('THtxqKwQdw4', '10 cybersecurity terms to prepare you for the age of AI'),
    ('zsCGS-Yzjnw', 'UI Libraries for Claude Code (Ban the AI Look)'),
    ('cxQLKsktiBA', 'How To Use AI Skills Like A Senior Developer'),
    ('Bhc3CL-cQm0', 'Give Claude a Senior Designer’s Taste (3 FREE Skills)'),
    ('-bv2xKQzZio', 'Creator Of The Best Design Skill Just Unveiled His AI Design Workflow'),
    ('pSritFeoYFo', "Frontend is HARDER for AI than backend (here's how to fix it)"),
    ('ia8xgSqqQ_0', 'Claude Skills for Designers (Ban AI Slop Forever)'),
]

LANGS = ['en', 'da']   # caption languages, in order of preference
WAIT = 15             # seconds between videos: your time to paste into Notion


def desktop():
    """The real Desktop folder, also when OneDrive has moved it."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
        return Path(os.path.expandvars(winreg.QueryValueEx(key, 'Desktop')[0]))
    except (ImportError, OSError):
        return Path.home() / 'Desktop'


def copy_to_clipboard(text):
    # UTF-16 keeps characters like ’ and é intact
    subprocess.run('clip', input=text.encode('utf-16'), check=True)


OUT = desktop() / 'yt_transcripts'
OUT.mkdir(parents=True, exist_ok=True)
api = YouTubeTranscriptApi()
done = skipped = failed = 0

for n, (vid, title) in enumerate(VIDEOS, 1):
    name = re.sub(r'[<>:"/\\|?*]', '', title).strip()[:80]
    path = OUT / f'{name}.txt'   # by title, so videos from an earlier batch are skipped
    if path.exists():
        skipped += 1
        continue
    print(f'[{n}/{len(VIDEOS)}] {title} ... ', end='', flush=True)
    try:
        text = ' '.join(p.text for p in api.fetch(vid, languages=LANGS))
        path.write_text(text, encoding='utf-8')
        copy_to_clipboard(text)
        print(f'saved + copied ({len(text.split())} words): paste it into Notion now')
        done += 1
    except Exception as e:
        kind = type(e).__name__
        print(f'FAILED: {kind}')
        if 'Block' in kind or '429' in str(e):
            print('\nYouTube is blocking you. Stop for today (or restart your router), then run again;'
                  ' finished videos are skipped.')
            break
        failed += 1   # e.g. no captions: move on to the next video
    time.sleep(WAIT)

print(f'\nDone: {done} saved, {skipped} already there, {failed} without captions. Files are in {OUT}')
