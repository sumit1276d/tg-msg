from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import InviteHashInvalidError, ChannelPrivateError
from datetime import datetime
import socket
import requests
import re
import time

# --- CONFIG ---
api_id = 25494810
api_hash = '19c0e1aec617479077971013f88cc63f'
session_name = 'group_analyzer'

# 🔗 Add any Telegram group invite links here:
group_links = [
    'https://t.me/joinchat/zUKcJ4A_Jgc5YWU1',
    # Add more links if needed
]

# --- HELPERS ---
def extract_invite_hash(link):
    match = re.search(r'(joinchat/)?([\w\d_-]{16,})', link)
    return match.group(2) if match else None

def detect_country_from_lang(lang_code):
    lang_map = {
        'en': 'US/UK/Global', 'hi': 'India', 'fa': 'Iran', 'ru': 'Russia',
        'tr': 'Turkey', 'id': 'Indonesia', 'pt': 'Brazil/Portugal',
        'es': 'Spain/Latin America', 'bn': 'Bangladesh',
        'ar': 'Arabic Region', 'zh': 'China'
    }
    return lang_map.get(lang_code, 'Unknown')

def detect_hosting_provider(org_str):
    org_str = (org_str or "").lower()
    if 'cloudflare' in org_str:
        return "[Cloudflare CDN]"
    elif 'contabo' in org_str:
        return "[Contabo VPS]"
    elif 'digitalocean' in org_str:
        return "[DigitalOcean VPS]"
    elif 'amazon' in org_str or 'aws' in org_str:
        return "[Amazon AWS]"
    elif 'google' in org_str:
        return "[Google Cloud]"
    elif 'microsoft' in org_str or 'azure' in org_str:
        return "[Microsoft Azure]"
    elif 'ovh' in org_str:
        return "[OVH VPS]"
    elif 'hetzner' in org_str:
        return "[Hetzner VPS]"
    elif 'linode' in org_str:
        return "[Linode VPS]"
    elif 'unknown' in org_str or org_str == "":
        return "[Mobile Network / VPN?]"
    else:
        return "[Other]"

def get_ip_location(domain):
    try:
        ip = socket.gethostbyname(domain)
        res = requests.get(f'https://ipinfo.io/{ip}/json', timeout=5).json()
        country = res.get("country", "Unknown")
        org = res.get("org", "Unknown")
        tag = detect_hosting_provider(org)
        return ip, country, org, tag
    except:
        return "N/A", "N/A", "N/A", "N/A"

# --- MAIN ---
with TelegramClient(session_name, api_id, api_hash) as client:
    for link in group_links:
        print("\n" + "="*60)
        print(f"🔍 Analyzing group: {link}")
        try:
            invite_hash = extract_invite_hash(link)
            if not invite_hash:
                print("❌ Invalid link format.")
                continue

            result = client(ImportChatInviteRequest(invite_hash))
            entity = result.chats[0]
            print(f"✅ Joined group: {entity.title}")

            # Admins
            admins = client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsAdmins(),
                offset=0,
                limit=100,
                hash=0
            ))

            print("\n👑 Admins Detected:")
            only_anonymous = True
            for admin in admins.users:
                name = f"{admin.first_name or ''} {admin.last_name or ''}".strip()
                username = f"@{admin.username}" if admin.username else "No Username"
                lang = getattr(admin, 'lang_code', None)
                country_guess = detect_country_from_lang(lang) if lang else "Unknown"

                if admin.username and admin.username.lower() != "groupanonymousbot":
                    only_anonymous = False

                print(f"  - {username} | {name} | Lang: {lang} | Country: {country_guess}")

            if only_anonymous:
                print("⚠️ All admins use @GroupAnonymousBot (Full anonymity enabled)")

            # Group creation estimate
            for msg in client.iter_messages(entity, reverse=True, limit=1):
                first_time = msg.date
                now = datetime.now(first_time.tzinfo)
                age = (now - first_time).days
                print(f"\n📅 Estimated Group Creation: {first_time.strftime('%Y-%m-%d %H:%M:%S')} ({age} days ago)")
                break

            # External Links
            print("\n🔗 External Domains (from last 200 msgs):")
            domains = set()
            for msg in client.iter_messages(entity, limit=200):
                if msg.message:
                    found = re.findall(r'https?://([^/\s]+)', msg.message)
                    for d in found:
                        domains.add(d.lower())

            if not domains:
                print("  ❌ No external domains found.")
            else:
                for domain in sorted(domains):
                    ip, country, org, tag = get_ip_location(domain)
                    print(f"  - {domain} → IP: {ip}, Country: {country}, Host: {org} {tag}")
                    time.sleep(0.5)

        except InviteHashInvalidError:
            print("❌ Invalid or expired invite link.")
        except ChannelPrivateError:
            print("❌ Cannot access private channel.")
        except Exception as e:
            print(f"❌ Error: {e}")
