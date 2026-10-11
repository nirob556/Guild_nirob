# -*- coding: utf-8 -*-
# ==================== STANDARD IMPORTS ====================
import sys
import asyncio
import httpx
import random
import json
import socket
import struct
import time
import os
import uuid
import itertools
import traceback
import aiohttp
import ssl
import base64
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from google_play_scraper import app as play_scraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from protobuf_decoder.protobuf_decoder import Parser
from message_ids import MESSAGE_ID_TO_NAME
import thunderFF_pb2
import StartMatch_pb2

try:
    import reqClan_pb2
    import encode_id_clan_pb2
    import data_pb2
    _CLAN_PB_AVAILABLE = True
except Exception:
    _CLAN_PB_AVAILABLE = False

from dashboard_server import bot_state, start_web_dashboard

# ==================== CONFIGURATION ====================
WEB_HOST = "0.0.0.0"
WEB_PORT = int(os.environ.get("PORT", 6667))
ACCOUNTS_FILE = "accounts.json"
TOKEN_CACHE_FILE = "token_cache.json"
DEVICES_FILE = "devices.json"
TOKEN_CACHE_TTL = 1200

START_MATCH_INTERVAL = 4.0
NEW_MATCH_DELAY = 3.0
MAX_MATCH_DURATION = 1800
MATCH_IDLE_TIMEOUT = 60.0
MATCH_SILENCE_EXIT = 120.0
MAX_CONCURRENT_MATCHES = 1

FALLBACK_UID = ""
FALLBACK_PASSWORD = ""

_accept_friend_request = True
DEBUG_ALL_PACKETS = False

# ==================== TEAM / SQUAD MODE ====================
TEAM_MODE = True
TEAM_SIZE = 4
MIN_SQUAD_SIZE = 2                  # ← ২ জন হলেই start হবে (২-৪)
TEAM_READY_DELAY = 2.5
TEAM_INVITE_WAIT = 1.5
TEAM_MEMBER_TRIGGER_DELAY = 10.0
TEAM_MATCH_LOOP_COUNT = 60
TEAM_MATCH_LOOP_INTERVAL = 1.0
TEAM_GROUP_TIMEOUT = 45.0
TEAM_FILL_WAIT = 8.0                # ২ জন হয়ে গেলে আর কতক্ষণ ৪ জনের জন্য অপেক্ষা

SQUAD_MATCH_FIELD1 = 9

# ==================== CLAN ====================
CLAN_ID = "3105631591"
AUTO_JOIN_CLAN = True               # ← clan join login-এর সাথেই হবে
CLAN_JOIN_RETRIES = 3
CLAN_JOIN_DELAY = 0.8

# ==================== HARDCODED ACCOUNTS ====================
HARDCODED_ACCOUNTS = [
    {"uid": "4278586807", "password": "SPEED_X_F63NA_BY_SPIDEERIO_GAMING_U8X4M"},
    {"uid": "4278586797", "password": "SPEED_X_PBN8R_BY_SPIDEERIO_GAMING_NSTMP"},
    {"uid": "4278586802", "password": "SPEED_X_BCOIS_BY_SPIDEERIO_GAMING_HLNM0"},
    {"uid": "4278586795", "password": "SPEED_X_Y6LO6_BY_SPIDEERIO_GAMING_1IYYP"},
    {"uid": "4278586801", "password": "SPEED_X_6SQLH_BY_SPIDEERIO_GAMING_ZPJR0"},
    {"uid": "4278587254", "password": "SPEED_X_JTY7D_BY_SPIDEERIO_GAMING_X0MBF"},
    {"uid": "4278587281", "password": "SPEED_X_CPIDU_BY_SPIDEERIO_GAMING_O95ZY"},
    {"uid": "4278587305", "password": "SPEED_X_O3348_BY_SPIDEERIO_GAMING_2VSB4"},
    {"uid": "4278587279", "password": "SPEED_X_IAOG2_BY_SPIDEERIO_GAMING_O87X9"},
    {"uid": "4278587409", "password": "SPEED_X_M6I7B_BY_SPIDEERIO_GAMING_7R2QP"},
    {"uid": "4278587542", "password": "SPEED_X_VRDGZ_BY_SPIDEERIO_GAMING_7TS70"},
    {"uid": "4278587596", "password": "SPEED_X_ZK11T_BY_SPIDEERIO_GAMING_EBY8C"},
    {"uid": "4278587603", "password": "SPEED_X_7QCX9_BY_SPIDEERIO_GAMING_48M3Z"},
    {"uid": "4278587642", "password": "SPEED_X_11TBW_BY_SPIDEERIO_GAMING_H0FO0"},
    {"uid": "4278587660", "password": "SPEED_X_RPILV_BY_SPIDEERIO_GAMING_J1MQK"},
    {"uid": "4278587720", "password": "SPEED_X_LPRRP_BY_SPIDEERIO_GAMING_Q2NK2"},
    {"uid": "4278587809", "password": "SPEED_X_FP4T9_BY_SPIDEERIO_GAMING_HV6M6"},
    {"uid": "4278587836", "password": "SPEED_X_2X15C_BY_SPIDEERIO_GAMING_EQLPF"},
    {"uid": "4278587901", "password": "SPEED_X_2LXPI_BY_SPIDEERIO_GAMING_BRJZM"},
    {"uid": "4278587920", "password": "SPEED_X_FECQ9_BY_SPIDEERIO_GAMING_1SV47"},
    {"uid": "4278588058", "password": "SPEED_X_V1HXE_BY_SPIDEERIO_GAMING_IA6MB"},
    {"uid": "4278588073", "password": "SPEED_X_TV7F9_BY_SPIDEERIO_GAMING_8QRYQ"},
    {"uid": "4278588142", "password": "SPEED_X_BAFRQ_BY_SPIDEERIO_GAMING_Z1D2S"},
    {"uid": "4278588156", "password": "SPEED_X_M2DP6_BY_SPIDEERIO_GAMING_CP5MY"},
    {"uid": "4278588192", "password": "SPEED_X_ITBQG_BY_SPIDEERIO_GAMING_TB8WF"},
    {"uid": "4278588951", "password": "SPEED_X_H54DL_BY_SPIDEERIO_GAMING_STGJI"},
    {"uid": "4278589105", "password": "SPEED_X_KFU7O_BY_SPIDEERIO_GAMING_MMPVS"},
    {"uid": "4278589048", "password": "SPEED_X_GT183_BY_SPIDEERIO_GAMING_9Y20G"},
    {"uid": "4278589098", "password": "SPEED_X_9YZRJ_BY_SPIDEERIO_GAMING_KXMZM"},
    {"uid": "4278588984", "password": "SPEED_X_YSE0K_BY_SPIDEERIO_GAMING_4B2PG"},
    {"uid": "4278589536", "password": "SPEED_X_VR7MX_BY_SPIDEERIO_GAMING_ZKEP8"},
    {"uid": "4278589580", "password": "SPEED_X_97EFV_BY_SPIDEERIO_GAMING_KLPF5"},
    {"uid": "4278589558", "password": "SPEED_X_PB1FW_BY_SPIDEERIO_GAMING_9CLDX"},
    {"uid": "4278589582", "password": "SPEED_X_L3K8X_BY_SPIDEERIO_GAMING_VKBEV"},
    {"uid": "4278589730", "password": "SPEED_X_ZFTHA_BY_SPIDEERIO_GAMING_IH2H9"},
    {"uid": "4278589825", "password": "SPEED_X_U3QOI_BY_SPIDEERIO_GAMING_FKMZY"},
    {"uid": "4278589855", "password": "SPEED_X_9RT1A_BY_SPIDEERIO_GAMING_Z9I4G"},
    {"uid": "4278589881", "password": "SPEED_X_MELWM_BY_SPIDEERIO_GAMING_YOMYQ"},
    {"uid": "4278589932", "password": "SPEED_X_HXXJC_BY_SPIDEERIO_GAMING_ZJOFS"},
    {"uid": "4278589948", "password": "SPEED_X_QLQ24_BY_SPIDEERIO_GAMING_25V7B"},
    {"uid": "4278590035", "password": "SPEED_X_FAQHH_BY_SPIDEERIO_GAMING_2IVL8"},
    {"uid": "4278590092", "password": "SPEED_X_QEXIF_BY_SPIDEERIO_GAMING_3JTZQ"},
    {"uid": "4278590098", "password": "SPEED_X_J136Q_BY_SPIDEERIO_GAMING_NZ0EP"},
    {"uid": "4278590158", "password": "SPEED_X_PJ8UQ_BY_SPIDEERIO_GAMING_TCLQY"},
    {"uid": "4278590183", "password": "SPEED_X_41UN2_BY_SPIDEERIO_GAMING_62BX7"},
    {"uid": "4278590261", "password": "SPEED_X_VNPL0_BY_SPIDEERIO_GAMING_CV8YG"},
    {"uid": "4278590323", "password": "SPEED_X_DXFGM_BY_SPIDEERIO_GAMING_SPAQC"},
    {"uid": "4278590466", "password": "SPEED_X_SH6LK_BY_SPIDEERIO_GAMING_0IXJ1"},
    {"uid": "4278590494", "password": "SPEED_X_OXD7Q_BY_SPIDEERIO_GAMING_N7UML"},
    {"uid": "4278590475", "password": "SPEED_X_E66Z2_BY_SPIDEERIO_GAMING_XEG6S"},
    {"uid": "4278590477", "password": "SPEED_X_3AHBE_BY_SPIDEERIO_GAMING_30MQ8"},
    {"uid": "4278590564", "password": "SPEED_X_ICI8M_BY_SPIDEERIO_GAMING_2ALRL"},
]

# ==================== PER-ACCOUNT TEAM STATE ====================
_TEAM_STATES: Dict[str, Dict[str, Any]] = {}
_TEAM_STATE_LOCK = asyncio.Lock()

async def _get_team_state(uid: str) -> Dict[str, Any]:
    uid = str(uid)
    async with _TEAM_STATE_LOCK:
        if uid not in _TEAM_STATES:
            _TEAM_STATES[uid] = {
                "peers": {},
                "leader_uid": None,
                "team_code": None,
                "group_id": None,
                "match_started": False,
            }
        return _TEAM_STATES[uid]

async def _remove_team_state(uid: str):
    uid = str(uid)
    async with _TEAM_STATE_LOCK:
        _TEAM_STATES.pop(uid, None)
        for other_uid, other_st in _TEAM_STATES.items():
            other_st["peers"].pop(uid, None)

# ==================== SQUAD GROUPING ====================
_TEAM_GROUPS: Dict[str, int] = {}
_TEAM_GROUPS_LOCK = asyncio.Lock()
_GROUP_LEADERS: Dict[int, str] = {}
_GROUP_LOCK = asyncio.Lock()

async def _assign_group(uid: str) -> int:
    uid = str(uid)
    async with _TEAM_GROUPS_LOCK:
        if uid in _TEAM_GROUPS:
            return _TEAM_GROUPS[uid]
        counts: Dict[int, int] = {}
        for u, g in _TEAM_GROUPS.items():
            counts[g] = counts.get(g, 0) + 1
        for g in sorted(counts.keys()):
            if counts[g] < TEAM_SIZE:
                _TEAM_GROUPS[uid] = g
                return g
        new_g = (max(_TEAM_GROUPS.values()) + 1) if _TEAM_GROUPS else 0
        _TEAM_GROUPS[uid] = new_g
    async with _GROUP_LOCK:
        if new_g not in _GROUP_LEADERS:
            _GROUP_LEADERS[new_g] = uid
    return new_g

async def _group_members(group_idx: int) -> List[str]:
    async with _TEAM_GROUPS_LOCK:
        return [u for u, g in _TEAM_GROUPS.items() if g == group_idx]

async def _my_group_index(uid: str) -> Optional[int]:
    async with _TEAM_GROUPS_LOCK:
        return _TEAM_GROUPS.get(str(uid))

async def _unregister_group(uid: str):
    uid = str(uid)
    async with _TEAM_GROUPS_LOCK:
        g = _TEAM_GROUPS.pop(uid, None)
    if g is not None:
        async with _GROUP_LOCK:
            if _GROUP_LEADERS.get(g) == uid:
                remaining = [u for u, gg in _TEAM_GROUPS.items() if gg == g]
                _GROUP_LEADERS[g] = remaining[0] if remaining else None

# ==================== GLOBAL SQUAD REGISTRY ====================
# Active squads + their online members. Used for re-forming & matching.
_ACTIVE_SQUADS: Dict[int, Dict[str, Any]] = {}
_SQUAD_LOCK = asyncio.Lock()

async def _squad_register_member(group_idx: int, uid: str, acc_id: str):
    """mark uid as online member of squad group_idx"""
    uid = str(uid); acc_id = str(acc_id)
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.setdefault(group_idx, {
            "members": {},         # uid -> acc_id
            "leader": None,
            "state": "forming",    # forming | ready | in_match
            "last_start": 0.0,
        })
        sq["members"][uid] = acc_id
        if sq["leader"] is None:
            sq["leader"] = uid

async def _squad_unregister_member(group_idx: int, uid: str):
    uid = str(uid)
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if not sq:
            return
        sq["members"].pop(uid, None)
        if sq["leader"] == uid:
            remaining = list(sq["members"].keys())
            sq["leader"] = remaining[0] if remaining else None
        if not sq["members"]:
            _ACTIVE_SQUADS.pop(group_idx, None)

async def _squad_online_members(group_idx: int) -> Dict[str, str]:
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if not sq:
            return {}
        return dict(sq["members"])

async def _squad_set_state(group_idx: int, state: str):
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if sq:
            sq["state"] = state

async def _squad_mark_start(group_idx: int):
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if sq:
            sq["last_start"] = time.time()
            sq["state"] = "in_match"

# ==================== DEVICE RANDOMIZER ====================
def _generate_new_device() -> dict:
    device_list = [
        ("Samsung", "SM-G998B", "Adreno (TM) 660", "Android OS 12 / API-31"),
        ("Xiaomi", "2201122G", "Adreno (TM) 730", "Android OS 13 / API-33"),
        ("Realme", "RMX3700", "Mali-G710", "Android OS 14 / API-34"),
        ("OnePlus", "CPH2451", "Adreno (TM) 740", "Android OS 13 / API-33"),
        ("OPPO", "CPH2611", "Adreno (TM) 720", "Android OS 14 / API-34"),
        ("Vivo", "V2203", "Mali-G710", "Android OS 12 / API-31"),
        ("Poco", "M2102J20SG", "Adreno (TM) 660", "Android OS 13 / API-33"),
    ]
    brand, model, gpu, os_ver = random.choice(device_list)
    return {
        "unique_device_id": f"Google|{str(uuid.uuid4())}",
        "brand": brand, "model": model, "gpu_renderer": gpu,
        "system_software": os_ver,
        "screen_width": random.choice([1080, 1440, 720, 1280]),
        "screen_height": random.choice([2400, 3200, 1600, 2400]),
        "screen_dpi": str(random.randint(300, 420)),
        "memory": random.randint(2800, 6500),
        "processor_details": f"ARM64 FP ASIMD AES VMH | {random.randint(2200, 3200)} | {random.randint(6, 12)}",
        "client_ip": f"{random.randint(103, 223)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(10, 250)}"
    }

def sync_devices_with_accounts() -> dict:
    accounts = load_accounts()
    devices = {}
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f:
                devices = json.load(f)
                if not isinstance(devices, dict):
                    devices = {}
        except Exception:
            devices = {}
    cached_data = _load_token_cache()
    synced_devices = {}
    for acc in accounts:
        acc_key = None
        aliases = []
        if "uid" in acc and acc["uid"]:
            acc_key = str(acc["uid"]).strip()
            aliases.append(acc_key)
            if acc_key in bot_state.auth_to_game_id:
                aliases.append(str(bot_state.auth_to_game_id[acc_key]))
        elif "token" in acc and acc["token"]:
            tok = str(acc["token"]).strip()
            tok_pfx = tok[:16]
            aliases.append(tok_pfx)
            aliases.append(tok)
            cached_entry = cached_data.get(f"tok_{tok[:20]}") or cached_data.get(tok)
            if cached_entry:
                if cached_entry.get("open_id"):
                    aliases.insert(0, str(cached_entry["open_id"]))
                if cached_entry.get("account_id"):
                    aliases.append(str(cached_entry["account_id"]))
            acc_key = aliases[0] if aliases else tok_pfx
        if not acc_key:
            continue
        dev_profile = None
        for a in aliases:
            if a in devices:
                dev_profile = devices[a]
                break
        if not dev_profile and acc_key in devices:
            dev_profile = devices[acc_key]
        if not dev_profile:
            dev_profile = _generate_new_device()
        synced_devices[acc_key] = dev_profile
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(synced_devices, f, indent=4)
    except Exception as e:
        print_error(f"Failed to save synced devices: {e}")
    return synced_devices

def get_device_for_account(account_identifier: str) -> dict:
    devices = {}
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f:
                devices = json.load(f)
                if not isinstance(devices, dict):
                    devices = {}
        except Exception:
            devices = {}
    acc_key = str(account_identifier).strip()
    if acc_key in devices:
        return devices[acc_key]
    for alias in [bot_state.auth_to_game_id.get(acc_key),
                  bot_state.game_to_auth_id.get(acc_key),
                  bot_state.account_token_map.get(acc_key)]:
        if alias and str(alias) in devices:
            dev = devices.pop(str(alias))
            devices[acc_key] = dev
            try:
                with open(DEVICES_FILE, "w", encoding="utf-8") as f:
                    json.dump(devices, f, indent=4)
            except Exception:
                pass
            return dev
    new_device = _generate_new_device()
    devices[acc_key] = new_device
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=4)
    except Exception:
        pass
    return new_device

# ==================== DNS RESOLVER ====================
CLOUDFLARE_PRIMARY_DNS = "1.1.1.1"
CLOUDFLARE_SECONDARY_DNS = "1.0.0.1"
_DNS_CACHE: Dict[str, Tuple[str, float]] = {}
_DNS_CACHE_TTL = 300.0

async def resolve_host_cloudflare(hostname: str) -> str:
    if not hostname:
        return hostname
    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return hostname
    now = time.time()
    if hostname in _DNS_CACHE:
        ip, exp = _DNS_CACHE[hostname]
        if now < exp:
            return ip

    def _query(server_ip: str) -> Optional[str]:
        s = None
        try:
            tx_id = random.randint(1000, 65535)
            header = struct.pack(">HHHHHH", tx_id, 0x0100, 1, 0, 0, 0)
            qname = b"".join(bytes([len(part)]) + part.encode('ascii') for part in hostname.split('.')) + b"\x00"
            query_pkt = header + qname + struct.pack(">HH", 1, 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.2)
            s.sendto(query_pkt, (server_ip, 53))
            resp, _ = s.recvfrom(1024)
            if len(resp) >= 12:
                ancount = struct.unpack(">H", resp[6:8])[0]
                if ancount > 0:
                    offset = 12 + len(qname) + 4
                    for _ in range(ancount):
                        if offset >= len(resp):
                            break
                        if (resp[offset] & 0xC0) == 0xC0:
                            offset += 2
                        else:
                            while offset < len(resp) and resp[offset] != 0:
                                offset += 1 + resp[offset]
                            offset += 1
                        if offset + 10 > len(resp):
                            break
                        rtype, rclass, ttl, rdlen = struct.unpack(">HHIH", resp[offset:offset+10])
                        offset += 10
                        if rtype == 1 and rdlen == 4 and offset + 4 <= len(resp):
                            return socket.inet_ntoa(resp[offset:offset+4])
                        offset += rdlen
        except Exception:
            pass
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        return None

    loop = asyncio.get_running_loop()
    ip = await loop.run_in_executor(None, _query, CLOUDFLARE_PRIMARY_DNS)
    if not ip:
        ip = await loop.run_in_executor(None, _query, CLOUDFLARE_SECONDARY_DNS)
    if not ip:
        try:
            ip_info = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
            if ip_info:
                ip = ip_info[0][4][0]
        except Exception:
            ip = hostname
    if ip:
        _DNS_CACHE[hostname] = (ip, now + _DNS_CACHE_TTL)
    return ip or hostname

def optimize_tcp_socket(sock: socket.socket):
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "SIO_KEEPALIVE_VALS") and os.name == 'nt':
            try:
                sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 2000))
            except Exception:
                pass
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    except Exception:
        pass

async def safe_close_writer(writer):
    if not writer:
        return
    try:
        if not writer.is_closing():
            writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=1.5)
    except Exception:
        pass

def optimize_udp_socket(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
        if hasattr(socket, 'SIO_UDP_CONNRESET') and os.name == 'nt':
            try:
                sock.ioctl(socket.SIO_UDP_CONNRESET, False)
            except Exception:
                pass
    except Exception:
        pass

# ==================== NETWORK & CRYPTO ====================
client = httpx.AsyncClient(
    verify=False,
    timeout=15.0,
    limits=httpx.Limits(max_connections=300, max_keepalive_connections=150)
)
_LOGIN_SEMAPHORE = asyncio.Semaphore(6)

headers = {
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Expect': '100-continue',
    'X-Unity-Version': '2018.4.12f1',
    'X-GA-SV': '1789535859',
    'X-GA': 'v1 1',
    'ReleaseVersion': 'OB55'
}

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

CRC7_TABLE = bytes([
    0, 9, 18, 27, 36, 45, 54, 63, 72, 65, 90, 83, 108, 101, 126, 119,
    25, 16, 11, 2, 61, 52, 47, 38, 81, 88, 67, 74, 117, 124, 103, 110,
    50, 59, 32, 41, 22, 31, 4, 13, 122, 115, 104, 97, 94, 87, 76, 69,
    43, 34, 57, 48, 15, 6, 29, 20, 99, 106, 113, 120, 71, 78, 85, 92,
    100, 109, 118, 127, 64, 73, 82, 91, 44, 37, 62, 55, 8, 1, 26, 19,
    125, 116, 111, 102, 89, 80, 75, 66, 53, 60, 39, 46, 17, 24, 3, 10,
    86, 95, 68, 77, 114, 123, 96, 105, 30, 23, 12, 5, 58, 51, 40, 33,
    79, 70, 93, 84, 107, 98, 121, 112, 7, 14, 21, 28, 35, 42, 49, 56,
    65, 72, 83, 90, 101, 108, 119, 126, 9, 0, 27, 18, 45, 36, 63, 54,
    88, 81, 74, 67, 124, 117, 110, 103, 16, 25, 2, 11, 52, 61, 38, 47,
    115, 122, 97, 104, 87, 94, 69, 76, 59, 50, 41, 32, 31, 22, 13, 4,
    106, 99, 120, 113, 78, 71, 92, 85, 34, 43, 48, 57, 6, 15, 20, 29,
    37, 44, 55, 62, 1, 8, 19, 26, 109, 100, 127, 118, 73, 64, 91, 82,
    60, 53, 46, 39, 24, 17, 10, 3, 116, 125, 102, 111, 80, 89, 66, 75,
    23, 30, 5, 12, 51, 58, 33, 40, 95, 86, 77, 68, 123, 114, 105, 96,
    14, 7, 28, 21, 42, 35, 56, 49, 70, 79, 84, 93, 98, 107, 112, 121,
])

_DELTA = 0x9E3779B9
_ROUNDS = 16
_FIELD_SIZES = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}
_FIELD_NAMES = {0: "sendOption", 1: "cmd", 2: "orderId", 3: "flags", 4: "length"}

class Colors:
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    WARNING = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    try:
        print(f"{color}{text}{Colors.ENDC}")
    except Exception:
        try:
            print(f"{color}{text.encode('ascii', errors='replace').decode('ascii')}{Colors.ENDC}")
        except Exception:
            pass

def print_success(text):
    print_colored(f"[+] {text}", Colors.GREEN)
    try: bot_state.log(text, "success")
    except Exception: pass

def print_error(text):
    print_colored(f"[-] {text}", Colors.FAIL)
    try: bot_state.log(text, "error")
    except Exception: pass

def print_warning(text):
    print_colored(f"[!] {text}", Colors.WARNING)
    try: bot_state.log(text, "warning")
    except Exception: pass

def print_info(text):
    print_colored(f"[i] {text}", Colors.CYAN)
    try: bot_state.log(text, "info")
    except Exception: pass

def get_proto_field(d, key, default=None):
    if not d or not isinstance(d, dict):
        return default
    if key in d:
        val = d[key].get('data')
        return val if val is not None else default
    if str(key) in d:
        val = d[str(key)].get('data')
        return val if val is not None else default
    return default

# ==================== MATCH COUNTER ====================
_match_counters: Dict[str, int] = {}
_match_counter_lock = asyncio.Lock()

async def _inc_match(uid: str) -> int:
    async with _match_counter_lock:
        _match_counters[uid] = _match_counters.get(uid, 0) + 1
        return _match_counters[uid]

async def _dec_match(uid: str) -> int:
    async with _match_counter_lock:
        if uid in _match_counters and _match_counters[uid] > 0:
            _match_counters[uid] -= 1
        return _match_counters.get(uid, 0)

# ==================== TOKEN CACHE ====================
_token_cache_memo: Dict[str, Any] = {}
_token_cache_memo_time: float = 0.0
_TOKEN_CACHE_MEMO_TTL = 5.0

def _json_serializer(obj):
    if isinstance(obj, (bytes, bytearray)):
        return {"__bytes_hex__": bytes(obj).hex()}
    raise TypeError(f"Type {type(obj)} not serializable")

def _json_deserializer(obj):
    if isinstance(obj, dict):
        if "__bytes_hex__" in obj and len(obj) == 1:
            try: return bytes.fromhex(obj["__bytes_hex__"])
            except Exception: return b""
        return {k: _json_deserializer(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_deserializer(x) for x in obj]
    return obj

def _load_token_cache() -> Dict[str, Any]:
    global _token_cache_memo, _token_cache_memo_time
    now = time.time()
    if _token_cache_memo and (now - _token_cache_memo_time) < _TOKEN_CACHE_MEMO_TTL:
        return _token_cache_memo
    if not os.path.exists(TOKEN_CACHE_FILE):
        return {}
    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return {}
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Cache root must be dict")
        parsed = _json_deserializer(data)
        _token_cache_memo = parsed
        _token_cache_memo_time = now
        return parsed
    except Exception as e:
        print_error(f"Token cache corrupt -> deleting: {e}")
        try: os.remove(TOKEN_CACHE_FILE)
        except Exception: pass
        return {}

def _save_token_cache(cache: Dict[str, Any]):
    global _token_cache_memo, _token_cache_memo_time
    try:
        tmp_file = TOKEN_CACHE_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, default=_json_serializer)
        os.replace(tmp_file, TOKEN_CACHE_FILE)
        _token_cache_memo = cache
        _token_cache_memo_time = time.time()
    except Exception as e:
        print_error(f"Token cache save error: {e}")

def cache_get(uid: str) -> Optional[Dict]:
    cache = _load_token_cache()
    entry = cache.get(str(uid))
    if not entry:
        return None
    if time.time() - entry.get("cached_at", 0) > TOKEN_CACHE_TTL:
        cache_invalidate(uid)
        return None
    if str(entry.get("account_id", "")).isdigit():
        entry["account_id"] = int(entry["account_id"])
    if not isinstance(entry.get("login_payload_data"), (bytes, bytearray)):
        cache_invalidate(uid)
        return None
    return entry

def cache_set(uid: str, account_data: Dict):
    cache = _load_token_cache()
    entry = dict(account_data)
    entry["cached_at"] = time.time()
    cache[str(uid)] = entry
    _save_token_cache(cache)

def cache_invalidate(uid: str):
    cache = _load_token_cache()
    if str(uid) in cache:
        del cache[str(uid)]
        _save_token_cache(cache)

# ==================== PROTOBUF HELPERS ====================
def encode_varint(n: int) -> bytes:
    out = bytearray()
    if n < 0: n &= 0xFFFFFFFFFFFFFFFF
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def _pb_varint(field_number, value) -> bytes:
    return encode_varint((field_number << 3) | 0) + encode_varint(value)

def _pb_length(field_number, value) -> bytes:
    encoded = value.encode('utf-8') if isinstance(value, str) else value
    return encode_varint((field_number << 3) | 2) + encode_varint(len(encoded)) + encoded

def create_proto(fields) -> bytes:
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(field, str): field = int(field)
        if isinstance(value, dict):
            packet.extend(_pb_length(field, bytes(create_proto(value))))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    packet.extend(_pb_length(field, bytes(create_proto(item))))
                elif isinstance(item, str):
                    packet.extend(_pb_length(field, item))
                elif isinstance(item, (bytes, bytearray)):
                    packet.extend(_pb_length(field, bytes(item)))
                elif isinstance(item, bool):
                    packet.extend(_pb_varint(field, 1 if item else 0))
                elif isinstance(item, int):
                    packet.extend(_pb_varint(field, item))
        elif isinstance(value, bool):
            packet.extend(_pb_varint(field, 1 if value else 0))
        elif isinstance(value, int):
            packet.extend(_pb_varint(field, value))
        elif isinstance(value, str):
            packet.extend(_pb_length(field, value))
        elif isinstance(value, (bytes, bytearray)):
            packet.extend(_pb_length(field, bytes(value)))
    return bytes(packet)

def encrypt_aes(hex_data: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    raw = bytes.fromhex(hex_data)
    return cipher.encrypt(pad(raw, AES.block_size)).hex()

def decode_varint(data, offset):
    result = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80): return result, offset
        shift += 7
    return None, offset

def extract_raw_fields(data: bytes) -> dict:
    result = {}
    offset = 0
    data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        fn = header >> 3
        wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            if offset + length > data_len: break
            result[fn] = bytes(data[offset:offset + length])
            offset += length
        elif wt == 1: offset += 8
        elif wt == 3: offset += 4
        else: break
    return result

def _parse_results_sync(results):
    out = {}
    for r in results:
        field_data = {"wire_type": r.wire_type}
        if r.wire_type == "varint":
            field_data["data"] = r.data
        elif r.wire_type in ("string", "bytes"):
            field_data["data"] = r.data
        elif r.wire_type == "length_delimited":
            if hasattr(r.data, "results"):
                field_data["data"] = _parse_results_sync(r.data.results)
            elif isinstance(r.data, list):
                field_data["data"] = _parse_results_sync(r.data)
            else:
                field_data["data"] = str(r.data)
        out[str(r.field)] = field_data
    return out

def decode_protobuf_dict(data: bytes) -> dict:
    try:
        parsed = Parser().parse(data)
        return _parse_results_sync(parsed)
    except Exception:
        return {}

def decode_protobuf_2(data):
    result = {}
    offset = 0
    data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        fn = header >> 3
        wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset + length]
            offset += length
            try:
                decoded_str = value.decode('utf-8')
                if decoded_str and len(decoded_str) > 0:
                    if len(decoded_str) > 10 and all(c in '0123456789abcdef' for c in decoded_str.lower()):
                        try:
                            hex_decoded = bytes.fromhex(decoded_str).decode('utf-8', errors='ignore')
                            result[fn] = hex_decoded if hex_decoded else decoded_str
                        except Exception:
                            result[fn] = decoded_str
                    else:
                        result[fn] = decoded_str
                else:
                    nested = decode_protobuf_2(value)
                    result[fn] = nested if nested else value.hex()
            except UnicodeDecodeError:
                nested = decode_protobuf_2(value)
                result[fn] = nested if nested else value.hex()
        elif wt == 1: offset += 8
        elif wt == 3: offset += 4
        else: break
    return result

# ==================== TCP PACKET BUILDERS ====================
def create_packet(Pk, N, K, V):
    if isinstance(K, str):
        K = bytes.fromhex(K) if len(K) == 32 else K.encode()
    if isinstance(V, str):
        V = bytes.fromhex(V) if len(V) == 32 else V.encode()
    PkEnc = AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(Pk), 16)).hex()
    L = len(PkEnc) // 2
    hexlen = hex(L)[2:]
    if len(hexlen) % 2 != 0: hexlen = '0' + hexlen
    total_pad = 12 - len(N) - len(hexlen)
    if total_pad < 0: total_pad = 0
    padding = '0' * total_pad
    return bytes.fromhex(N + padding + hexlen + PkEnc)

# ==================== TEAM PACKET FUNCTIONS ====================
def create_team(key, iv, game_version="1.132.9"):
    fields = {
        1: 1,
        2: {
            2: bytes.fromhex("01"), 3: 1, 4: 3, 5: "en",
            8: {1: "IDC3", 2: 123, 3: "BD"},
            9: 1,
            10: bytes.fromhex("01090a0b1219202729"),
            11: 2, 13: 1,
            14: {
                1: "08FBA33B4BABE2790205390333330000009700050092005F72697EB2134DCBB2467625142201040e38e848dc0e748c3f6aa04d81000000ff1113090dcacfa16d",
                2: 478,
                3: "7e585d55110201440555560d0103035104575b0e0d0d0d040708050206010201050c0452045600541b0605487d5c41444b1b0114061d1709034d00547d730b586c45627e7b624b45736e597d700e770965790178750a1705447b5c62537552754d7b607f7657517675485379555b5a5b505161440c1b515b5a4c1e62781f7441480648636a664100414754425b4163134b7948450a68777f5f416a1e47080f10000b4b425e56447b6159637462455746524b047c7a477a7a5b67577b575e0d110b4d4c00641b5362631f680a754b6d5e475343785b4b187f13584c47790c12024e187740537245174050587d5d6b4a4047595a030109664b014a5e7d091b084d616b727d1742606517505c6979494876727e1f526904784141040c0a1705004d7f5b5a72057644641f56025405687f62756507070155027360565605140748701a00546160007c411f065e0559660752441358077313771a67020e120c4b524d7f50467a6b7200696e01466968770561475217444e037f74740d11010144467302135058427c547d4a5c61604a434401054b7f0b425d7b4f700c13074f5e4e445d7c5e5f5a71405144551c60735041527a63441e01636e4305",
                4: "y[Z]", 6: 12,
                7: "15686677735a7506101c",
                8: f"{game_version}",
                9: 3, 10: 1,
                11: "036262535136377541744a7369416456324b796f566c6635484c354651547049535a717050414561414156744d436a7555533853514a492f42594f6b5075326e34595836376f4862364d3161594c352b6e745a67446a7a6339786876524674344f686d794271696e7a70417a665135486555476e5a5344374b77746f6d786a70363377347279547a2b595442792f6c4c676d356738745a784f6d51474433484d303974456a6142332b3071445a68432f752b34616671504c4531355077794e6f71677a7a66786d57787030574d4377584d347a685066354d52566676747a763056592b6a416a4768383045664e392f55366b377530314a54527374747564333977493078765a48727247437870547455584b4a38354a656844797a2f53474a4a49455a6b754141535a2f6f706c42764b2b314a70367578776a70377176414a652f4e664d75347450786343646f5573444f535351476f6d634f2f6f3569795063796b68437544777a477a536f774a6b6d494a7833345a456637624f72494f6130747937736e692f536630353638655367585a544664414143307a6c747141386167695772624955392f4c41474278727a496e62415235524b346d4b426d6d2b74784c462b6f544d6b627032776a626d63497a66524c363646715339515a30646c2b6c7a6861446a4d6477342f6747776f7241777a346e7939725744466e3577515670617a4a4778615964654b564843594b4b6c5a542b74736e632b597062596437696361316b6a442f462f4c45354a485233776f56317933754a385a733873483178384446647a32692b586461383030663761507954685554344958566e4257634d5676724f4152634c2b416566594e6a5633485339385846493967506e647a6f4c30727847614e6c716f42694770617771502f665667786d46496f4f4b773d3d"
            },
            19: 329,
            21: bytes.fromhex("374f521955"),
            24: {1: 21},
            27: "a_6534489873065906362"
        }
    }
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def team_fresh(account_id, key, iv):
    fields = {1: 72, 2: {1: int(account_id)}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def invite_player_in_team(target_uid, key, iv):
    fields = {1: 2, 2: {1: int(target_uid), 2: "BD", 4: 1}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def accept_team_invite(target_uid, group_id, key, iv):
    fields = {
        1: 4,
        2: {
            1: int(target_uid),
            3: int(target_uid),
            4: bytes.fromhex("0107090a0b120f19202729"),
            8: 1,
            9: {
                1: "08FBA33B0522052002041B0222220007000C00010004000547E265AE1080779546762514110104076fa2e8770e748c3f6a68ed75000000ff08080500cacfa16d",
                2: 235,
                3: {14: 80, 11: 86},
                4: "{Y\\R", 6: 13,
                7: {2: 4}, 8: "1.132.9",
                9: 2, 10: 1,
                11: "0362625351363749545a306f50416456324b796f566c664b314a522b4c336737676d2f597a6f7064736278516b676d6f3275696a4e5a512f6445356778643942356c6f69644867315574306e34573146634c382b624a69436c61532b305a625070547a32574f302b436d497067325958347a4d38722f526a4a735371764a334a357a69756950676b5a35642b386a7576664367547a7135776e78756b4d5a734d63745544582b666a65325373565833542b6950676c4f31474736526e66383661754e7945786c4a6942316a656d59636452595459496c65612f68757353657a6c6753424c49714e64482f584b7876507a6c74417461756b53746d50414b4c5679544b42337536685146456b7635584962534f626f6f436b4b357a614e523736746e6e6b576176776748446e73426770656c75506e6652644e75714c43547a5553707569355a77425448653937667465354c3432365a71554441724933565a3636687030546234384c756730562b366c514d66636e467143486d33436a356f5549395369776934424758454e33317436786c794932416f6b2f4a322f2b355255574d3645774c497338306a632f55317765745a6b457639524e496f70563275726d38324e4a4858757166346e4d45785a516e6879766268334e5a68554a3431427934574a4b6f44656d367864733873474e444e5874472b4a68466976714d683235536139744b354462336f416871463769416675472f336535304e44744e4e3643796a794a5370633334784765696f6165533544597663782b77634c656e4c373945517475547477716d7a4b4d7575536268514635785272717978796538452f7a5563706a7739534d58654b5268394b685252666b6f4f51785741673d3d"
            },
            10: str(group_id),
            11: {"1": "IDC3", "2": 107, "3": "BD"},
            13: "en", 16: "374f5219",
            20: {1: 21},
            23: "a_6534489873065906362",
            24: "https://dl-sg-production.freefiremobile.com/D5A73B5E05EC88BB7181_7104104913_107_1767710870_0",
            27: {1: 2, 2: 4}
        }
    }
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def start_match_team(account_id, key, iv, region="BD"):
    """Squad matchmaking — regular queue."""
    fields = {
        1: SQUAD_MATCH_FIELD1,
        2: {
            1: int(account_id),
            2: 1,               # squad type
            3: TEAM_SIZE,       # team size 4
            7: {1: "IDC3", 2: 410, 3: region},
        }
    }
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def exit_team(account_id, key, iv):
    fields = {1: 7, 2: {1: int(account_id)}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

# ==================== AES KEY/IV EXTRACTOR ====================
def _extract_key_iv(res_json):
    if "__RAW_HEX__" in res_json and "__OFFSET__" in res_json:
        try:
            raw = bytes.fromhex(res_json["__RAW_HEX__"])
            off = int(res_json["__OFFSET__"])
            raw_fields = extract_raw_fields(raw[off:])
            for kf, vf in [(22, 23), (24, 25), (6, 7)]:
                k = raw_fields.get(kf)
                v = raw_fields.get(vf)
                if isinstance(k, (bytes, bytearray)) and len(k) == 16 and \
                   isinstance(v, (bytes, bytearray)) and len(v) == 16:
                    return bytes(k), bytes(v)
            candidates = {fn: v for fn, v in raw_fields.items()
                          if isinstance(v, (bytes, bytearray)) and len(v) == 16 and fn >= 20}
            if len(candidates) >= 2:
                sk = sorted(candidates.keys())
                return bytes(candidates[sk[0]]), bytes(candidates[sk[1]])
        except Exception:
            pass

    found = {}
    for k, v in res_json.items():
        if str(k).startswith("__"): continue
        if not isinstance(v, dict): continue
        data = v.get("data")
        if data is None: continue
        raw = None
        if isinstance(data, (bytes, bytearray)):
            if len(data) == 16: raw = bytes(data)
        elif isinstance(data, str):
            if len(data) == 32:
                try:
                    cand = bytes.fromhex(data)
                    if len(cand) == 16: raw = cand
                except Exception: pass
            if raw is None and len(data) == 16:
                raw = data.encode('latin-1')
        if raw and len(raw) == 16:
            try: found[int(k)] = raw
            except Exception: pass
    if len(found) < 2:
        return None, None
    for kf, vf in [(22, 23), (24, 25), (6, 7)]:
        if kf in found and vf in found:
            return found[kf], found[vf]
    sk = sorted(found.keys())
    return found[sk[0]], found[sk[1]]

async def aes_encrypt(payload, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(payload, AES.block_size))

async def get_playstore_version():
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth', lang='hi', country='id'))
        return result.get("version")
    except Exception:
        return "1.132.9"

async def version_config():
    app_version = await get_playstore_version()
    api_url = (
        "https://version.ggwhitehawk.com/live/ver.php"
        f"?version={app_version}&lang=hi&device=android&channel=android"
        "&appstore=googleplay&region=BD&whitelist_version=1.3.0&whitelist_sp_version=1.0.0"
    )
    try:
        response = await client.get(api_url)
        response.raise_for_status()
        data = response.json()
        server_url = data.get("server_url")
        remote_version = data.get("remote_version")
        latest_release_version = data.get("latest_release_version")
        if not server_url or not remote_version or not latest_release_version:
            return None
        return latest_release_version, remote_version, server_url
    except Exception as e:
        print_error(f"[VERCONFIG] {e}")
        return None

async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B Build/SP1A.210812.016)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid, "password": password,
        "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    for attempt in range(5):
        try:
            response = await client.post(url, headers=hdrs, data=data)
            if response.status_code == 200:
                response_data = response.json()
                open_id = response_data.get("open_id")
                access_token = response_data.get("access_token")
                platform = response_data.get("platform", 4)
                if open_id and access_token:
                    return open_id, access_token, platform
            if response.status_code == 429:
                await asyncio.sleep(1)
                continue
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return None

async def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {"wire_type": result.wire_type}
        if result.wire_type in ("varint", "string", "bytes"):
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            if hasattr(result.data, "results"):
                field_data["data"] = await parse_results(result.data.results)
            elif isinstance(result.data, list):
                field_data["data"] = await parse_results(result.data)
            else:
                field_data["data"] = str(result.data)
        result_dict[str(result.field)] = field_data
    return result_dict

async def decode_protobuf_async(data):
    parsed_results = Parser().parse(data)
    parsed_results_dict = await parse_results(parsed_results)
    return json.dumps(parsed_results_dict)

# ==================== PAYLOAD BUILDER ====================
async def get_payload(access_token, open_id, platform, version):
    device_id = f"Google|{uuid.uuid4()}"
    major_login = {
        "3": str(datetime.now())[:-7], "4": "free fire", "5": 1,
        "7": f"{version}",
        "8": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)",
        "9": "Handheld", "11": "CarrierDataNetwork",
        "12": 1672, "13": 750, "14": "338",
        "15": "ARMv7 VFPv3 NEON | 2002 | 8",
        "16": 3702, "17": "Mali-G52",
        "18": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "19": device_id, "20": "104.28.197.151", "21": "en",
        "22": f"{open_id}", "23": f"{platform}", "24": "Handheld",
        "25": "samsung SM-E135F", "26": "BD",
        "29": f"{access_token}", "30": 1, "42": "Cellular",
        "57": "7428b253defc164018c604a1ebbfebdf",
        "60": 52037, "61": 5355, "62": 3723, "63": 3,
        "64": 5483, "65": 52037, "66": 5483, "67": 52037,
        "73": 2,
        "74": "/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/lib/arm",
        "76": 1,
        "77": "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/base.apk",
        "78": 3, "79": 1, "81": "32", "83": "2019121229",
        "86": "OpenGLES2", "87": 8191, "88": int(platform),
        "92": 16091, "93": "android",
        "94": "KqsHT3Yeqo3RLRl8efNiL3aL/1SHwlSrtK0DwNAqdkNBQz70TeVy+icaIwuR3UK4b65Uf3IG5xBFEv0uu+jQZI+rOYCmNCsXjJT4QcZaYgoaaUGG",
        "95": 111107,
        "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1, "98": 1,
        "99": f"{platform}", "100": f"{platform}",
        "102": "4503454457550c0766",
        "104": 53792, "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1",
    }
    get_login_data = dict(major_login)
    get_login_data["90"] = "Khulna"
    get_login_data["91"] = "D"
    get_login_data["99"] = "0"
    get_login_data["103"] = 1
    proto1 = create_proto(major_login).hex()
    proto2 = create_proto(get_login_data).hex()
    return bytes.fromhex(encrypt_aes(proto1)), bytes.fromhex(encrypt_aes(proto2))

async def build_majorlogin_payload(open_id, access_token, platform, client_version, device_info=None):
    try:
        return await get_payload(access_token, open_id, platform, client_version)
    except Exception as e:
        print_error(f"[BUILD_PAYLOAD] {e}")
        return None, None

# ==================== MAJOR LOGIN ====================
async def major_login(payload, login_url, release_version):
    try:
        url = f"{login_url}MajorLogin" if login_url.endswith("/") else f"{login_url}/MajorLogin"
        req_headers = {
            "Accept": "*/*", "Authorization": "Bearer ",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
            "X-Unity-Version": "2018.4.12f1",
        }
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=req_headers, data=payload, ssl=ssl_context) as response:
                response_content = await response.read()
                if response.status != 200:
                    print_error(f"[MAJOR LOGIN] {response.status}")
                    return None
                if len(response_content) < 200:
                    return {"__SHORT_RESPONSE__": True}
                decoded_json = None
                best_fields = 0
                best_offset = 64
                offsets_to_try = [64, 0, 48, 32, 80, 16, 128, 8, 96]
                for offset in offsets_to_try:
                    if offset >= len(response_content): continue
                    cb = response_content[offset:]
                    try:
                        cand = decode_protobuf_dict(cb)
                        cnt = len(cand) if cand else 0
                    except Exception:
                        cand = {}; cnt = 0
                    if cnt > best_fields:
                        decoded_json = cand; best_fields = cnt; best_offset = offset
                    if best_fields >= 5: break
                if not decoded_json or best_fields < 3:
                    for offset in offsets_to_try:
                        if offset >= len(response_content): continue
                        cb = response_content[offset:]
                        try:
                            cand2 = decode_protobuf_2(cb)
                            cnt2 = len(cand2) if cand2 else 0
                        except Exception:
                            cand2 = {}; cnt2 = 0
                        if cnt2 > best_fields:
                            decoded_json = {str(k): {"data": v} for k, v in cand2.items()}
                            best_fields = cnt2; best_offset = offset
                        if best_fields >= 5: break
                if not decoded_json or len(decoded_json) < 3:
                    return None
                decoded_json["__RAW_HEX__"] = response_content.hex()
                decoded_json["__OFFSET__"] = best_offset
                return decoded_json
    except asyncio.TimeoutError:
        return None
    except Exception as e:
        print_error(f"[MAJOR LOGIN] {e}")
        return None

# ==================== GET LOGIN DATA ====================
async def get_login_data(payload, jwt_token, server_url, release_version):
    try:
        url = f"{server_url.rstrip('/')}/GetLoginData"
        req_headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
            "X-Unity-Version": "2018.4.12f1",
            "Host": "clientbp.ppmainecoonghj.com",
        }
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=req_headers, data=payload, ssl=ssl_context) as response:
                response_content = await response.read()
                if response.status != 200:
                    return None
                decoded_json = None
                best_fields = 0
                offsets_to_try = [0, 64, 48, 32, 80, 16, 128, 8, 96]
                for offset in offsets_to_try:
                    if offset >= len(response_content): continue
                    cb = response_content[offset:]
                    try:
                        cand = decode_protobuf_dict(cb)
                        cnt = len(cand) if cand else 0
                    except Exception:
                        cand = {}; cnt = 0
                    if cnt > best_fields:
                        decoded_json = cand; best_fields = cnt
                    if best_fields >= 5: break
                if not decoded_json or best_fields < 3:
                    for offset in offsets_to_try:
                        if offset >= len(response_content): continue
                        cb = response_content[offset:]
                        try:
                            cand2 = decode_protobuf_2(cb)
                            cnt2 = len(cand2) if cand2 else 0
                        except Exception:
                            cand2 = {}; cnt2 = 0
                        if cnt2 > best_fields:
                            decoded_json = {str(k): {"data": v} for k, v in cand2.items()}
                            best_fields = cnt2
                        if best_fields >= 5: break
                if not decoded_json or len(decoded_json) < 3:
                    return None
                return decoded_json
    except Exception as e:
        print_error(f"[LOGIN DATA] {e}")
        return None

# ==================== GET PLAYER PERSONAL SHOW ====================
async def get_player_personal_show(target_uid, jwt_token, server_url, release_version):
    try:
        url = f"{server_url}/GetPlayerPersonalShow"
        proto_bytes = create_proto({"1": int(target_uid)}).hex()
        payload = bytes.fromhex(encrypt_aes(proto_bytes))
        hdrs = {
            "authorization": f"Bearer {jwt_token}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{release_version}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*", "x-unity-version": "2022.3.47f1",
        }
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=hdrs, data=payload, ssl=ssl_context) as response:
                if response.status != 200:
                    return None
                return decode_protobuf_2(await response.read())
    except Exception:
        return None

# ==================== FRIEND ACCEPT ====================
async def accept_friend_request(target_uid, own_account_id, jwt_token, server_url, release_version):
    try:
        url = f"{server_url}/ConfirmFriendRequest"
        fields = {"1": int(target_uid), "2": int(own_account_id)}
        payload = bytes.fromhex(encrypt_aes(create_proto(fields).hex()))
        hdrs = {
            "authorization": f"Bearer {jwt_token}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{release_version}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*", "x-unity-version": "2022.3.47f1",
        }
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=hdrs, data=payload, ssl=ssl_context) as response:
                if response.status == 200:
                    resp_content = await response.read()
                    return decode_protobuf_dict(resp_content) or decode_protobuf_2(resp_content)
                return None
    except Exception:
        return None

# ==================== CLAN JOIN ====================
def _get_region_from_jwt(jwt_token):
    try:
        payload = jwt_token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        region = data.get('lock_region') or data.get('noti_region') or 'BD'
        return region.upper()
    except Exception:
        return "BD"

def _get_region_url(region):
    region = region.upper()
    if region == "IND": return "https://client.ind.freefiremobile.com"
    elif region in ["BR", "US", "NA"]: return "https://client.us.freefiremobile.com"
    else: return "https://clientbp.ggpolarbear.com"

def _create_clan_payload(clan_id):
    if not _CLAN_PB_AVAILABLE:
        return None
    try:
        msg = reqClan_pb2.MyMessage()
        msg.field_1 = int(clan_id)
        raw = msg.SerializeToString()
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        return cipher.encrypt(pad(raw, AES.block_size))
    except Exception:
        # fallback: raw protobuf
        try:
            return bytes.fromhex(encrypt_aes(create_proto({"1": int(clan_id)}).hex()))
        except Exception:
            return None

async def join_clan(jwt_token, clan_id):
    """Returns True on success, False otherwise. Retries internally."""
    if not _CLAN_PB_AVAILABLE:
        print_warning("[CLAN] reqClan_pb2 not available")
        return False
    for attempt in range(CLAN_JOIN_RETRIES):
        try:
            region = _get_region_from_jwt(jwt_token)
            base_url = _get_region_url(region)
            url = base_url.rstrip("/") + "/RequestJoinClan"
            host = base_url.replace("https://", "")
            payload = _create_clan_payload(clan_id)
            if not payload:
                return False
            hdrs = {
                "Expect": "100-continue",
                "Authorization": f"Bearer {jwt_token}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1",
                "ReleaseVersion": "OB55",
                "Content-Type": "application/octet-stream",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
                "Host": host,
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=hdrs, data=payload, ssl=ssl_context) as resp:
                    if resp.status == 200:
                        return True
                    else:
                        body = await resp.read()
                        if attempt < CLAN_JOIN_RETRIES - 1:
                            await asyncio.sleep(CLAN_JOIN_DELAY)
                        continue
        except Exception:
            if attempt < CLAN_JOIN_RETRIES - 1:
                await asyncio.sleep(CLAN_JOIN_DELAY)
            continue
    return False

# ==================== TCP STARTUP ====================
async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="BD", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"
    timestamp_hex = f"{int(server_time):08x}"
    encrypted_packet = (await aes_encrypt(token.encode(), key, iv)).hex()
    encrypted_packet_length = f"{len(encrypted_packet) // 2:08x}"
    reg = str(region).upper() if region else "BD"
    if typ == 'OnLine':
        prefix = '7219' if reg == 'BD' else ('7214' if reg == 'IND' else '7215')
        return f"{prefix}{uid_hex}{timestamp_hex}00000000{encrypted_packet_length}{encrypted_packet}"
    else:
        prefix = '8119' if reg == 'BD' else ('8114' if reg == 'IND' else '8115')
        return f"{prefix}{uid_hex}{timestamp_hex}{encrypted_packet_length}{encrypted_packet}"

async def send_keep_alive(region="BD"):
    try:
        reg = str(region).upper() if region else "BD"
        return bytes.fromhex("0219" if reg == "BD" else ("0214" if reg == "IND" else "0215"))
    except Exception:
        return bytes.fromhex("0219")

async def start_game_battle_royale(region, client_version, writer, key, iv):
    packet = bytes.fromhex("080112800a0a010110013a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f504540014a0801090a0b1219202758016291090a8001303838463832424630324139363736373032303130313030303030303030303030303136303030313030313530303032323246393745454530463030303030303436373632353134303030303030303030303030303030303030303030303030303030303030303030303030303066663030303030303030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e75196001477c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b625f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d615f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e5078487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b441b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f477776484f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b3247525268377a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a565072564b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c4434744478706771385533595973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e4249725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d74757077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a201050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815")
    proto = thunderFF_pb2.StartMatch()
    proto.ParseFromString(packet)
    if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
        proto.main.region_list[0].region = region
        if len(proto.main.region_list) > 1:
            proto.main.region_list[1].region = region
    if hasattr(proto.main, 'client_version'):
        proto.main.client_version.remote_version = client_version
    packet = proto.SerializeToString()
    encrypted_packet = (await aes_encrypt(packet, key, iv)).hex()
    packet_length = len(encrypted_packet) // 2
    hex_length = hex(packet_length)[2:]
    hex_length = hex_length if len(hex_length) > 1 else "0" + hex_length
    reg = str(region).upper() if region else "BD"
    reg_prefix = "031900" if reg == "BD" else ("031400" if reg == "IND" else "031500")
    final_packet = reg_prefix + "0" * (6 - len(hex_length)) + hex_length + encrypted_packet
    writer.write(bytes.fromhex(final_packet))
    await writer.drain()

# ==================== UDP HELPERS ====================
async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80:
        out.append((z & 0x7F) | 0x80)
        z >>= 7
    out.append(z)
    return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (_DELTA * _ROUNDS) & 0xFFFFFFFF
    for _ in range(_ROUNDS):
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - _DELTA) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(padded))
    prev_cipher = bytearray(8)
    prev_intermediate = bytearray(8)
    for i in range(0, len(padded), 8):
        xored = bytearray(8)
        for j in range(8): xored[j] = padded[i + j] ^ prev_cipher[j]
        e0, e1 = await tea_enc(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0); struct.pack_into("<I", enc, 4, e1)
        for j in range(8): out[i + j] = enc[j] ^ prev_intermediate[j]
        prev_cipher[:] = out[i:i + 8]; prev_intermediate[:] = xored
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def encode_header(layout, send_option, cmd, order_id, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: length}[code]
        if _FIELD_SIZES[code] == 1:
            out.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF); out.append((v >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf:
        c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def sv_frame(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, send_option, cmd, order_id, flags, len(body), k, v80)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val,
                                      server_ip="", region="BD", client_version="1.132.9",
                                      client_version_code="2019121229", access_token="",
                                      mode_id=1, map_id=1):
    token = token.strip()
    udp_key = bytes.fromhex(udp_key)
    match_code = [int(ch) for ch in str(match_code).strip()]
    thunder_jwt = token[:660] if len(token) > 660 else token
    sharma_jwt = token[660:] if len(token) > 660 else ""
    encoded_thunder_jwt = thunder_jwt.encode() if isinstance(thunder_jwt, str) else thunder_jwt
    encoded_sharma_jwt = sharma_jwt.encode() if isinstance(sharma_jwt, str) else sharma_jwt
    garena420 = await has_ssan_zig(len(encoded_thunder_jwt)) + encoded_thunder_jwt
    reg = str(region).upper() if region else "BD"
    csoversea_block = bytes.fromhex("ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e3137302e3233303b33352e3138352e3138332e3537000000000000010000000000000000000000000100000800000100000000000100a8a2d7bebd8d8bdf110200")
    mid = bytes.fromhex('0000000001000102030101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030003000004')
    mid += await has_ssan_zig(len(client_version)) + client_version.encode()
    mid += await has_ssan_zig(len(client_version_code)) + client_version_code.encode()
    mid += csoversea_block
    clean_ip = server_ip.split(':')[0] if server_ip else "0.0.0.0"
    mid += await has_ssan_zig(len(clean_ip)) + clean_ip.encode()
    clean_acc_tok = access_token.strip() if access_token else ""
    if clean_acc_tok:
        mid += await has_ssan_zig(len(clean_acc_tok)) + clean_acc_tok.encode()
    mid += await has_ssan_zig(len(encoded_sharma_jwt)) + encoded_sharma_jwt
    tg_garena420 = (await uleb_encode(int(account_id)) + await uleb_encode(int(block_val)) +
                    await uleb_encode(1) + await uleb_encode(int(mode_id)) +
                    await uleb_encode(int(block_val)) + await uleb_encode(int(map_id)) + mid)
    process = await sv_frame(0x5E, match_code, 2, 447, 0, 1, garena420, udp_key)
    loading = await sv_frame(0x5A, match_code, 2, 448, 1, 1, tg_garena420, udp_key)
    return process.hex(), loading.hex()

async def produce_xor_key(secret_key):
    k = secret_key[0] if secret_key and len(secret_key) > 0 else 10
    return k, ((k << 8) | k) & 0xFFFF

async def tea_cbc_decrypt(body, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(body))
    prev_intermediate = bytearray(8); prev_cipher = bytearray(8)
    xored = bytearray(8); dec = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8): xored[j] = body[i + j] ^ prev_intermediate[j]
        d0, d1 = await tea_dec(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        struct.pack_into("<I", dec, 0, d0); struct.pack_into("<I", dec, 4, d1)
        for j in range(8): out[i + j] = dec[j] ^ prev_cipher[j]
        prev_cipher[:] = body[i:i + 8]; prev_intermediate[:] = dec
    return bytes(out)

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")
    if len(data) > 25: raise ValueError(f"Text too long ({len(data)})")
    content = b"\x10\x00\x00\x00" + data + b"\x00" * (29 - 4 - len(data))
    k, v80 = await produce_xor_key(key)
    layout = [int(c) for c in str(layout).strip()] if isinstance(layout, str) else list(layout)
    padded = await build_padded(content)
    enc_body = await tea_cbc_encrypt(padded, key)
    header_bytes = await encode_header(layout, 1, 1, 0, 1, len(enc_body), k, v80)
    packet = bytearray([0x63, 0x00]) + header_bytes + enc_body
    packet[1] = await crc7_buff(0, packet[2:]) & 0x7F
    return bytes(packet).hex()

async def classify(frame):
    cmd = frame["cmd"]
    msg_name = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
    if msg_name == "UDP_HELLO": return "HELLO"
    if msg_name == "UDP_ACK": return "ACK"
    if msg_name == "UDP_PING": return "PING"
    if msg_name == "RUDP_JOIN_MATCH": return "JOIN_MATCH"
    if msg_name.startswith("RUDP_"): return msg_name
    if msg_name.startswith("UDP_"): return msg_name
    return "DATA"

async def build_packet(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1:
            hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF); hdr.append((v >> 8) & 0xFF)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def layouts_from_mask(mask):
    ru = [int(c) for c in str(mask).strip()]
    nr = [c for c in ru if c != 2]
    return ru, nr

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    ru, nr = await layouts_from_mask(mask)
    typ = await classify(frame)
    if typ == "HELLO":
        if ack_style == "echo":
            content = frame["content"] if frame["content"] else b"\x10\x00\x00\x00"
            return typ, await build_packet(hello_key, nr, 1, 1, None, 1, content, key)
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x01\x00", key)
    if typ == "ACK":
        content = frame["content"] if frame["content"] else b"\x01\x00"
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, content, key)
    if typ == "PING":
        c = frame["content"]
        counter = c[:4] if len(c) >= 4 else c
        return typ, await build_packet(ping_key, nr, 0, 3, None, 0, counter + b"\x00\x00\x00", key, encrypted=False)
    if typ == "JOIN_MATCH":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return typ, None

async def keepalive_ping(sock, ip, port, key_bytes, mask, stop_event):
    nr = (await layouts_from_mask(mask))[1]
    ping_keys = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop()
    i = 0
    while not stop_event.is_set():
        pk = ping_keys[i % len(ping_keys)]
        counter = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = await build_packet(pk, nr, 0, 3, None, 0, struct.pack("<I", counter) + b"\x00\x00\x00", key_bytes, encrypted=False)
        try: await loop.sock_sendto(sock, pkt, (ip, port))
        except Exception: pass
        i += 1
        try: await asyncio.wait_for(stop_event.wait(), timeout=3.0)
        except asyncio.TimeoutError: pass

async def try_header(buf, layout, k, v80):
    off = 2; out = {}
    for code in layout:
        size = _FIELD_SIZES[code]
        if off + size > len(buf): return None
        out[_FIELD_NAMES[code]] = (buf[off] ^ k) if size == 1 else ((buf[off] | (buf[off + 1] << 8)) ^ v80) & 0xFFFF
        off += size
    out["headerLen"] = off
    return out

async def oicq_unpad(padded):
    if not padded or len(padded) < 8: return None
    if not all(padded[-1 - i] == 0 for i in range(7)): return None
    pad_len = padded[0] & 0x07
    s = 3 + pad_len; e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def decode_packet(packet, key, mask=None):
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8: return None
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    candidates = []
    if mask:
        ru, nr = await layouts_from_mask(mask)
        layouts = [("RUDP", ru), ("nonRUDP", nr)]
    else:
        layouts = [("RUDP", list(p)) for p in itertools.permutations([0, 1, 2, 3, 4])]
        layouts += [("nonRUDP", list(p)) for p in itertools.permutations([0, 1, 3, 4])]
    for kind, layout in layouts:
        f = await try_header(data, layout, k, v80)
        if not f: continue
        if f["flags"] > 7 or f["sendOption"] > 7: continue
        if f["length"] != len(data) - f["headerLen"]: continue
        body = data[f["headerLen"]:f["headerLen"] + f["length"]]
        content = None; padded = None
        if f["flags"] & 1:
            if len(body) < 8 or len(body) % 8 != 0: continue
            padded = await tea_cbc_decrypt(body, key)
            content = await oicq_unpad(padded)
            if content is None: continue
        else:
            content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        candidates.append({
            "kind": kind, "layout": layout, "headerLen": f["headerLen"],
            "msgKey": data[0], "cmd": f["cmd"], "flags": f["flags"],
            "sendOption": f["sendOption"], "orderId": f.get("orderId"),
            "length": f["length"], "content": content, "crcOk": crc_ok,
            "padded": padded, "score": score, "total": len(data),
        })
    if not candidates: return None
    candidates.sort(key=lambda c: (c["kind"] == "RUDP" or c["kind"] == "nonRUDP", c["score"]), reverse=True)
    return candidates[0]

# ==================== PLAY GAME ====================
async def play_game(server_ip_port, thunder, sharma, udp_key, match_code,
                    account_id, player_region, client_version, key, iv, match_index: int):
    match_start_time = time.time()
    ping_task = None
    sock = None
    ping_stop = asyncio.Event()
    uid_str = str(account_id)
    completed_cleanly = False
    try:
        ip, port = server_ip_port.split(":")
        port = int(port)
        resolved_ip = await resolve_host_cloudflare(ip)
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: sock.bind(('0.0.0.0', 0))
        except Exception: pass
        optimize_udp_socket(sock); sock.setblocking(False)
        udp_key_bytes = bytes.fromhex(udp_key)
        hello_packet = await build_hello_packet(f"{account_id}_2585", udp_key_bytes, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello_packet), (resolved_ip, port))

        ack_state = "waiting_for_hello_reply"
        thunder_sent = False
        join_match_received = False
        local_closed = False
        send_lock = asyncio.Lock()
        ping_task = asyncio.create_task(keepalive_ping(sock, resolved_ip, port, udp_key_bytes, match_code, ping_stop))
        last_activity = time.time()

        async def send_thunder_sharma_inline():
            nonlocal ack_state, thunder_sent
            if thunder_sent: return
            async with send_lock:
                if thunder_sent: return
                try:
                    await loop.sock_sendto(sock, bytes.fromhex(thunder), (resolved_ip, port))
                    thunder_sent = True
                    await asyncio.sleep(0.3)
                    prepare_ack = await build_packet(0x68, (await layouts_from_mask(match_code))[1], 0, 2, None, 1, b"\x01\x00", udp_key_bytes)
                    await loop.sock_sendto(sock, prepare_ack, (resolved_ip, port))
                    await asyncio.sleep(0.4)
                    await loop.sock_sendto(sock, bytes.fromhex(sharma), (resolved_ip, port))
                    ack_state = "thunder_sharma_sent"
                    print_success(f"[MATCH #{match_index}] In-game now!")
                except Exception as e:
                    print_error(f"[MATCH #{match_index}] Startup: {e}")

        while not local_closed:
            if time.time() - match_start_time > MAX_MATCH_DURATION:
                completed_cleanly = True; break
            try:
                response, server_addr = await asyncio.wait_for(loop.sock_recvfrom(sock, 65535), timeout=2.0)
                if response:
                    last_activity = time.time()
                    frame = await decode_packet(response, udp_key_bytes, match_code)
                    if frame:
                        ptype = await classify(frame)
                        if frame['cmd'] in [103, 107]:
                            completed_cleanly = True; local_closed = True; continue
                        if frame['cmd'] == 101:
                            try:
                                ack_pkt = await build_packet(0x68, (await layouts_from_mask(match_code))[1], 0, 2, None, 1, b"\x01\x00", udp_key_bytes)
                                await loop.sock_sendto(sock, ack_pkt, server_addr)
                            except Exception: pass
                            continue
                        if ptype in ["ACK", "PING", "HELLO", "JOIN_MATCH"]:
                            if ptype == "HELLO" and ack_state == "waiting_for_hello_reply":
                                typ, reply = await reply_for(frame, udp_key_bytes, match_code, ack_style="short")
                                if reply: await loop.sock_sendto(sock, reply, server_addr)
                                ack_state = "ack_sent_waiting"
                            elif ptype == "ACK":
                                if ack_state == "waiting_for_hello_reply":
                                    typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                    if reply: await loop.sock_sendto(sock, reply, server_addr)
                                    ack_state = "ready_to_send_thunder"
                                elif ack_state == "ack_sent_waiting":
                                    ack_state = "ready_to_send_thunder"
                                else:
                                    typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                    if reply: await loop.sock_sendto(sock, reply, server_addr)
                            elif ptype == "PING":
                                typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                if reply: await loop.sock_sendto(sock, reply, server_addr)
                            elif ptype == "JOIN_MATCH" and not join_match_received:
                                typ, reply = await reply_for(frame, udp_key_bytes, match_code)
                                if reply:
                                    await loop.sock_sendto(sock, reply, server_addr)
                                    join_match_received = True
            except asyncio.TimeoutError:
                if ack_state == "ready_to_send_thunder" and not thunder_sent:
                    await send_thunder_sharma_inline()
                elif ack_state == "waiting_for_hello_reply":
                    if (time.time() - last_activity) > 7.0:
                        try:
                            pkt = await build_hello_packet(f"{account_id}_2585", udp_key_bytes, match_code)
                            await loop.sock_sendto(sock, bytes.fromhex(pkt), (resolved_ip, port))
                        except Exception: pass
                        last_activity = time.time()
                    if (time.time() - match_start_time) > 25.0:
                        break
                elif ack_state == "thunder_sharma_sent":
                    if (time.time() - last_activity) > MATCH_SILENCE_EXIT:
                        completed_cleanly = True; break
            except (BlockingIOError, OSError):
                await asyncio.sleep(0.5); continue
            except Exception:
                await asyncio.sleep(0.5); continue
            if ack_state == "ready_to_send_thunder" and not thunder_sent:
                await send_thunder_sharma_inline()
        return f"match #{match_index} finished"
    except Exception as e:
        print_error(f"[MATCH #{match_index}] {e}")
        return f"match #{match_index} error"
    finally:
        if completed_cleanly:
            try:
                bot_state.increment_match(uid_str)
                print_success(f"[★] Match #{match_index} Complete | UID: {uid_str}")
            except Exception: pass
        ping_stop.set()
        if ping_task:
            ping_task.cancel()
            try: await ping_task
            except asyncio.CancelledError: pass
        if sock:
            try: sock.close()
            except Exception: pass
        await _dec_match(uid_str)
        try:
            remaining = _match_counters.get(uid_str, 0)
            bot_state.update_status(uid_str, "ONLINE" if remaining == 0 else "IN_MATCH", remaining)
        except Exception: pass

# ==================== FUNCTIONAL (SQUAD LOOP, AUTO RESTART) ====================
async def functional_lone_wolf(addrs, starter_packet, account_region, client_version,
                                key, iv, account_id="", account_data=None, max_reconnects=10):
    reconnects = 0
    ip, port = addrs.split(":")
    play_matches: List[asyncio.Task] = []
    no_response_count = 0
    search_attempts = 0
    last_start_time = 0.0
    uid_str = str(account_id)

    current_token = starter_packet
    current_key = key
    current_iv = iv
    current_account_data = account_data
    _writer_ref = {"w": None}

    local_team_state = await _get_team_state(uid_str)

    async def _process_social_packet(raw_bytes, tag="MAIN"):
        try:
            hex_data = raw_bytes.hex()
            inner_bytes = bytes.fromhex(hex_data[10:])
            decoded = decode_protobuf_dict(inner_bytes)
            if not decoded or ("5" not in decoded and 5 not in decoded):
                alt = decode_protobuf_2(inner_bytes)
                if alt: decoded = {str(k): {"data": v} for k, v in alt.items()}
            if not decoded: return
            f5wrap = decoded.get("5") or decoded.get(5)
            field5 = f5wrap["data"] if isinstance(f5wrap, dict) and "data" in f5wrap else f5wrap
            if not isinstance(field5, dict): return
            def _f5get(key):
                v = field5.get(key) if key in field5 else field5.get(str(key))
                if isinstance(v, dict) and "data" in v: return v["data"]
                return v
            target_uid = _f5get(1)
            has_field7 = _f5get(7) is not None
            if not target_uid or not str(target_uid).isdigit() or len(str(target_uid)) < 6: return
            if not has_field7: return
            if not _accept_friend_request or not current_account_data: return
            jwt_l = current_account_data.get('token')
            srv_l = current_account_data.get('server_url')
            rel_l = current_account_data.get('release_version')
            own_id = current_account_data.get('account_id')
            if not (jwt_l and srv_l and rel_l and own_id): return
            resp = await accept_friend_request(int(target_uid), int(own_id), jwt_l, srv_l, rel_l)
            if resp:
                print_success(f"[FRIEND-{tag}] ✅ Accepted ({target_uid})")
        except Exception:
            pass

    # ════════════ TEAM COORDINATOR (LEADER) ════════════
    async def _team_coordinator():
        try:
            my_group = await _assign_group(uid_str)
            # register self as online member
            my_acc_id = str(current_account_data.get("account_id", uid_str)) if current_account_data else uid_str
            await _squad_register_member(my_group, uid_str, my_acc_id)

            # wait for at least MIN_SQUAD_SIZE (2) online, keep collecting up to TEAM_SIZE
            waited = 0.0
            got_min = False
            while waited < TEAM_GROUP_TIMEOUT:
                if bot_state.is_paused(uid_str): return
                online = await _squad_online_members(my_group)
                # filter by actually-connected peers
                online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
                if len(online_peers) >= MIN_SQUAD_SIZE and not got_min:
                    got_min = True
                    print_success(f"[TEAM] group {my_group} has min squad ({len(online_peers)}) — extending wait {TEAM_FILL_WAIT}s")
                    # small extra window to allow more to join
                    await asyncio.sleep(TEAM_FILL_WAIT)
                    break
                await asyncio.sleep(1.0)
                waited += 1.0

            online = await _squad_online_members(my_group)
            online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
            if len(online_peers) < MIN_SQUAD_SIZE:
                print_warning(f"[TEAM] group {my_group} only {len(online_peers)} online — not starting")
                return

            # deterministic leader = smallest uid
            async with _GROUP_LOCK:
                grp_leader = _GROUP_LEADERS.get(my_group)
                if not grp_leader or grp_leader not in online_peers:
                    grp_leader = sorted(online_peers)[0]
                    _GROUP_LEADERS[my_group] = grp_leader

            if grp_leader != uid_str:
                print_info(f"[TEAM] {uid_str} member — waiting for invites from {grp_leader}")
                return

            await asyncio.sleep(TEAM_READY_DELAY)

            own_id_num = None
            if current_account_data:
                own_id_num = current_account_data.get('account_id')
            if not own_id_num:
                try: own_id_num = int(uid_str)
                except Exception: own_id_num = 0

            def _w_ok():
                return _writer_ref["w"] and not _writer_ref["w"].is_closing()

            async def _send(pkt, tag):
                try:
                    if _w_ok():
                        _writer_ref["w"].write(pkt)
                        await _writer_ref["w"].drain()
                        return True
                except Exception:
                    pass
                return False

            print_success(f"[TEAM] 👑 {uid_str} creating team for group {my_group} ({len(online_peers)} online)")

            await _send(create_team(current_key, current_iv, client_version), "create_team")
            await asyncio.sleep(1.2)
            await _send(team_fresh(int(own_id_num), current_key, current_iv), "team_fresh#1")
            await asyncio.sleep(1.0)

            invite_targets = []
            for peer_uid in online_peers:
                if peer_uid == uid_str: continue
                p_info = local_team_state["peers"].get(peer_uid)
                p_acc = None
                if p_info:
                    try: p_acc = p_info["data"].get("account_id")
                    except Exception: pass
                if not p_acc: p_acc = peer_uid
                invite_targets.append(int(p_acc))

            for round_i in range(3):
                for tgt in invite_targets:
                    await _send(invite_player_in_team(tgt, current_key, current_iv),
                                f"invite→{tgt} r{round_i+1}")
                    await asyncio.sleep(0.4)
                await asyncio.sleep(1.0)

            await asyncio.sleep(TEAM_INVITE_WAIT + 1.5)
            await _send(team_fresh(int(own_id_num), current_key, current_iv), "team_fresh#2")
            await asyncio.sleep(0.8)

            # wait for team_code confirmation (max 10s)
            waited_tc = 0.0
            while waited_tc < 10.0:
                if local_team_state.get("team_code"): break
                await asyncio.sleep(0.5); waited_tc += 0.5

            own_id = current_account_data.get('account_id', own_id_num) if current_account_data else own_id_num

            # fire start_match now
            try:
                sm = start_match_team(int(own_id), current_key, current_iv, region=account_region)
                if _w_ok():
                    _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                    print_success(f"[TEAM] 🚀 leader start_match FIRED ({len(sm)}B)")
                    await _squad_mark_start(my_group)
            except Exception: pass

            # loop start_match while waiting for match allocation
            for attempt in range(TEAM_MATCH_LOOP_COUNT):
                if bot_state.is_paused(uid_str): return
                try:
                    sm = start_match_team(int(own_id), current_key, current_iv, region=account_region)
                    if _w_ok():
                        _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                        if attempt % 5 == 0:
                            print_info(f"[TEAM]   leader start_match #{attempt+1}")
                except Exception: pass
                await asyncio.sleep(TEAM_MATCH_LOOP_INTERVAL)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print_error(f"[TEAM] coordinator error: {e}")

    # ════════════ MEMBER MATCH TRIGGER ════════════
    async def _member_match_trigger():
        try:
            my_group = await _my_group_index(uid_str)
            if my_group is None: return

            my_acc_id = str(current_account_data.get("account_id", uid_str)) if current_account_data else uid_str
            await _squad_register_member(my_group, uid_str, my_acc_id)

            # wait for group leader + MIN_SQUAD_SIZE members
            waited = 0.0
            while waited < TEAM_GROUP_TIMEOUT:
                online = await _squad_online_members(my_group)
                online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
                async with _GROUP_LOCK:
                    grp_leader = _GROUP_LEADERS.get(my_group)
                if grp_leader and grp_leader != uid_str and len(online_peers) >= MIN_SQUAD_SIZE:
                    break
                await asyncio.sleep(0.5); waited += 0.5

            async with _GROUP_LOCK:
                grp_leader = _GROUP_LEADERS.get(my_group)
            if not grp_leader or grp_leader == uid_str: return

            await asyncio.sleep(TEAM_MEMBER_TRIGGER_DELAY)

            print_success(f"[TEAM] 🚀 member {uid_str} start_match loop")
            my_id = current_account_data.get('account_id', uid_str) if current_account_data else uid_str

            for attempt in range(TEAM_MATCH_LOOP_COUNT):
                if bot_state.is_paused(uid_str): return
                try:
                    if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                        sm = start_match_team(int(my_id), current_key, current_iv, region=account_region)
                        _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                        if attempt % 5 == 0:
                            print_info(f"[TEAM]   member start_match #{attempt+1}")
                except Exception: pass
                await asyncio.sleep(TEAM_MATCH_LOOP_INTERVAL)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print_warning(f"[TEAM] member trigger outer: {e}")

    # ════════════ MAIN LOOP ════════════
    try:
        while True:
            while bot_state.is_paused(uid_str):
                try: bot_state.update_status(uid_str, "PAUSED", 0)
                except Exception: pass
                await asyncio.sleep(1.0)

            writer = None
            gateway_ping_task = None
            team_coord_task = None
            member_trigger_task = None
            try:
                if current_account_data:
                    fresh = None
                    if current_account_data.get('auth_type') == 'guest' and current_account_data.get('auth_uid'):
                        fresh = cache_get(str(current_account_data['auth_uid']))
                    elif current_account_data.get('auth_type') == 'token' and current_account_data.get('auth_token'):
                        fresh = cache_get(f"tok_{current_account_data['auth_token'][:20]}")
                    if fresh:
                        current_account_data = fresh
                        current_key = fresh['aes_ak']
                        current_iv = fresh['iv_i']
                        current_token = await build_tcp_startup_packet(
                            fresh['account_id'], fresh['token'], fresh['server_time'],
                            current_key, current_iv,
                            region=fresh.get('region', account_region), typ='OnLine'
                        )
                    else:
                        raise ConnectionError("Cache expired")

                resolved_ip = await resolve_host_cloudflare(ip)
                reader, writer = await asyncio.open_connection(resolved_ip, int(port))
                bot_state.register_writer(uid_str, writer)
                _writer_ref["w"] = writer
                raw_sock = writer.get_extra_info('socket')
                if raw_sock: optimize_tcp_socket(raw_sock)

                writer.write(bytes.fromhex(current_token)); await writer.drain()
                try:
                    init_ka = await send_keep_alive(account_region)
                    if init_ka and not writer.is_closing():
                        writer.write(init_ka)
                        await asyncio.wait_for(writer.drain(), timeout=3)
                except Exception: pass

                async def func_gateway_keepalive():
                    ka_bytes = await send_keep_alive(account_region)
                    while True:
                        await asyncio.sleep(5)
                        try:
                            if writer and not writer.is_closing():
                                writer.write(ka_bytes); await writer.drain()
                        except Exception: break

                gateway_ping_task = asyncio.create_task(func_gateway_keepalive())
                print_success(f"[✓] TCP Gateway Connected | UID: {uid_str}")
                reconnects = 0
                no_response_count = 0

                # register as peer in local + all other team states
                local_team_state["peers"][uid_str] = {
                    "writer": writer, "data": current_account_data,
                    "key": current_key, "iv": current_iv,
                }
                async with _TEAM_STATE_LOCK:
                    for other_uid, other_st in _TEAM_STATES.items():
                        if other_uid == uid_str: continue
                        other_st["peers"][uid_str] = {
                            "writer": writer, "data": current_account_data,
                            "key": current_key, "iv": current_iv,
                        }

                # squad logic
                if TEAM_MODE:
                    team_coord_task = asyncio.create_task(_team_coordinator())
                    member_trigger_task = asyncio.create_task(_member_match_trigger())

                while True:
                    play_matches[:] = [m for m in play_matches if not m.done()]
                    if bot_state.is_paused(uid_str): break

                    try:
                        data = await asyncio.wait_for(reader.read(8192), timeout=0.5)
                    except asyncio.TimeoutError:
                        no_response_count += 1; continue

                    if not data: raise ConnectionError("Connection closed")

                    hex_data = data.hex()
                    packet_length = len(data)
                    no_response_count = 0

                    if hex_data.startswith("0600") and packet_length > 20:
                        await _process_social_packet(data, tag="MAIN")
                        continue

                    if hex_data.startswith("0500") and packet_length > 10:
                        try:
                            inner = bytes.fromhex(hex_data[10:])
                            dec = decode_protobuf_dict(inner)
                            if not dec:
                                alt = decode_protobuf_2(inner)
                                if alt: dec = {str(k): {"data": v} for k, v in alt.items()}
                            f5w = dec.get("5") or dec.get(5)
                            f5 = f5w.get("data") if isinstance(f5w, dict) and "data" in f5w else f5w
                            if not isinstance(f5, dict): f5 = dec
                            def _f5g(key):
                                if not isinstance(f5, dict): return None
                                v = f5.get(key) if key in f5 else f5.get(str(key))
                                if isinstance(v, dict) and "data" in v: return v["data"]
                                return v
                            tc = None
                            for fk in [11, 5, 1, 3, 2]:
                                cand = _f5g(fk)
                                if cand and str(cand).isdigit() and len(str(cand)) == 7:
                                    tc = str(cand); break
                            if tc: local_team_state["team_code"] = tc
                            group_id = None
                            for fk in [8, 10, 12, 6]:
                                cand = _f5g(fk)
                                if cand and isinstance(cand, str) and 20 <= len(cand) <= 40:
                                    group_id = cand; break
                            if group_id: local_team_state["group_id"] = group_id

                            own_acc = str(current_account_data.get('account_id')) if current_account_data else None
                            my_group = await _my_group_index(uid_str)
                            async with _GROUP_LOCK:
                                grp_leader = _GROUP_LEADERS.get(my_group) if my_group is not None else None
                            is_leader = (grp_leader == uid_str)

                            inviter = None
                            for fk in [1, 2, 3, 4, 6, 7, 13, 15, 20]:
                                cand = _f5g(fk)
                                if cand and str(cand).isdigit() and 6 <= len(str(cand)) <= 15:
                                    if str(cand) != uid_str and str(cand) != own_acc:
                                        inviter = cand; break

                            if inviter and group_id and not is_leader:
                                for _ in range(2):
                                    try:
                                        acc = accept_team_invite(int(inviter), group_id, current_key, current_iv)
                                        if writer and not writer.is_closing():
                                            writer.write(acc); await writer.drain()
                                    except Exception: pass
                                    await asyncio.sleep(0.5)
                        except Exception: pass
                        continue

                    if hex_data.startswith("0300") and 10 < packet_length < 30:
                        continue

                    if hex_data.startswith("0300") and packet_length >= 300:
                        print_success(f"[⚔] Match Found | UID: {uid_str}")
                        try:
                            res = json.loads(await decode_protobuf_async(hex_data[10:]))
                            token = udp_key = match_code = server_ip_port = None
                            match_account_id = block_val = None
                            if '42' in res and 'data' in res['42']: match_code = res['42']['data']
                            if '5' in res and 'data' in res['5']:
                                rf5 = res['5']['data']
                                server_ip_port = rf5.get('2', {}).get('data')
                                udp_key = rf5.get('3', {}).get('data')
                                token = rf5.get('4', {}).get('data')
                                if '42' in rf5: match_code = rf5['42']['data']
                            if '1' in res and 'data' in res['1']: match_account_id = res['1']['data']
                            if '5' in res and 'data' in res['5']:
                                block_val = res['5']['data'].get('1', {}).get('data')
                            effective_acc_id = match_account_id or account_id or "BD_BOT"
                            if token and udp_key and match_code and server_ip_port:
                                acc_tok = current_account_data.get('access_token', '') if current_account_data else ""
                                thunder, sharma = await build_match_startup_packets(
                                    token, udp_key, match_code, effective_acc_id, block_val or 0,
                                    server_ip=server_ip_port, region=account_region,
                                    client_version=client_version, access_token=acc_tok,
                                    mode_id=1, map_id=1)
                                match_index = await _inc_match(uid_str)
                                print_info(f"[⚔] Match #{match_index} Injected → {server_ip_port}")
                                try:
                                    bot_state.increment_match_started()
                                    bot_state.update_status(uid_str, "IN_MATCH (SQUAD)", 1)
                                except Exception: pass
                                new_match = asyncio.create_task(
                                    play_game(server_ip_port, thunder, sharma, udp_key,
                                              match_code, effective_acc_id, "BD",
                                              client_version, current_key, current_iv,
                                              match_index=match_index))
                                play_matches.append(new_match)

                                async def drain_gw():
                                    while not new_match.done():
                                        try:
                                            dg = await asyncio.wait_for(reader.read(4096), timeout=1.0)
                                            if not dg: break
                                            gh = dg.hex()
                                            if gh.startswith("0600") and len(dg) > 20:
                                                await _process_social_packet(dg, tag="DRAIN")
                                        except asyncio.TimeoutError: continue
                                        except Exception: break

                                drain_task = asyncio.create_task(drain_gw())
                                try: await new_match
                                except Exception as e: print_error(f"[MATCH #{match_index}] {e}")
                                finally:
                                    drain_task.cancel()
                                    try: await drain_task
                                    except asyncio.CancelledError: pass

                                play_matches[:] = [m for m in play_matches if not m.done()]
                                print_info(f"[OFFLINE] Match #{match_index} ended — next in {NEW_MATCH_DELAY}s...")
                                await asyncio.sleep(NEW_MATCH_DELAY)

                                # reset local team state
                                local_team_state["team_code"] = None
                                local_team_state["group_id"] = None
                                local_team_state["match_started"] = False

                                # cancel old squad tasks
                                for tk in (team_coord_task, member_trigger_task):
                                    if tk and not tk.done():
                                        tk.cancel()
                                        try: await tk
                                        except asyncio.CancelledError: pass

                                # re-form squad with same group — leader re-elected
                                await _squad_set_state(my_group if my_group is not None else 0, "forming")
                                team_coord_task = asyncio.create_task(_team_coordinator())
                                member_trigger_task = asyncio.create_task(_member_match_trigger())
                                print_success(f"[TEAM] 🔁 re-squad started after match #{match_index}")
                                continue
                        except Exception as e:
                            print_warning(f"[MATCH] {e}")
                            continue

                    if 30 <= packet_length <= 40: continue

            except asyncio.CancelledError:
                raise
            except Exception as e:
                if "Cache expired" in str(e):
                    print_warning(f"[!] Token expired {uid_str}")
                    break
                reconnects += 1
                if reconnects > max_reconnects:
                    if current_account_data:
                        try:
                            if current_account_data.get('auth_uid'):
                                cache_invalidate(str(current_account_data['auth_uid']))
                            if current_account_data.get('auth_token'):
                                cache_invalidate(f"tok_{current_account_data['auth_token'][:20]}")
                        except Exception: pass
                    reconnects = 0; break
                print_warning(f"[{uid_str}] Reconnect #{reconnects}: {e}")
                await asyncio.sleep(min(reconnects * 0.5, 2.0))
            finally:
                local_team_state["peers"].pop(uid_str, None)
                async with _TEAM_STATE_LOCK:
                    for other_uid, other_st in _TEAM_STATES.items():
                        if other_uid == uid_str: continue
                        other_st["peers"].pop(uid_str, None)
                try:
                    my_group = await _my_group_index(uid_str)
                    if my_group is not None:
                        await _squad_unregister_member(my_group, uid_str)
                except Exception: pass
                for tk in (team_coord_task, member_trigger_task):
                    if tk and not tk.done():
                        tk.cancel()
                        try: await tk
                        except asyncio.CancelledError: pass
                if gateway_ping_task: gateway_ping_task.cancel()
                if writer:
                    bot_state.unregister_writer(uid_str, writer)
                    await safe_close_writer(writer)
    except asyncio.CancelledError:
        raise
    finally:
        for m in play_matches:
            if not m.done(): m.cancel()
        await _remove_team_state(uid_str)
        try:
            g = await _my_group_index(uid_str)
            if g is not None: await _squad_unregister_member(g, uid_str)
        except Exception: pass

# ==================== INFORMATIONAL ====================
async def informational(addrs, starter_packet, key, iv, region="BD", account_id="",
                         max_reconnects=3, account_data=None):
    uid_str = str(account_id)
    reconnects = 0
    ip, port = addrs.split(":")
    while True:
        while uid_str and bot_state.is_paused(uid_str):
            await asyncio.sleep(1.0)
        writer = None
        ping_task = None
        try:
            resolved_ip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.open_connection(resolved_ip, int(port))
            if uid_str: bot_state.register_writer(uid_str, writer)
            raw_sock = writer.get_extra_info('socket')
            if raw_sock: optimize_tcp_socket(raw_sock)
            writer.write(bytes.fromhex(starter_packet)); await writer.drain()
            reconnects = 0
            try:
                init_ka = await send_keep_alive(region)
                if init_ka and not writer.is_closing():
                    writer.write(init_ka)
                    await asyncio.wait_for(writer.drain(), timeout=3)
            except Exception: pass

            async def info_keepalive():
                ka_bytes = await send_keep_alive(region)
                while True:
                    await asyncio.sleep(5)
                    try:
                        if writer and not writer.is_closing():
                            writer.write(ka_bytes); await writer.drain()
                    except Exception: break

            ping_task = asyncio.create_task(info_keepalive())
            while True:
                if uid_str and bot_state.is_paused(uid_str):
                    if ping_task: ping_task.cancel()
                    if uid_str: bot_state.unregister_writer(uid_str, writer)
                    await safe_close_writer(writer); writer = None
                    while bot_state.is_paused(uid_str):
                        await asyncio.sleep(1.0)
                    break
                try:
                    data = await asyncio.wait_for(reader.read(8192), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                if not data: raise ConnectionError("Connection closed")
        except asyncio.CancelledError:
            if ping_task: ping_task.cancel()
            if uid_str: bot_state.unregister_writer(uid_str, writer)
            await safe_close_writer(writer); raise
        except Exception:
            if ping_task: ping_task.cancel()
            if uid_str: bot_state.unregister_writer(uid_str, writer)
            await safe_close_writer(writer)
            reconnects += 1
            if reconnects > max_reconnects:
                await asyncio.sleep(3); reconnects = 0
            else:
                await asyncio.sleep(1)

# ==================== ACCOUNT PROCESSORS ====================
def _register_credentials(account_data: Dict):
    try:
        acc_id = str(account_data['account_id'])
        bot_state.account_credentials[acc_id] = account_data
        if account_data.get('auth_uid'):
            bot_state.account_credentials[str(account_data['auth_uid'])] = account_data
        if account_data.get('auth_token'):
            bot_state.account_credentials[f"tok_{account_data['auth_token'][:20]}"] = account_data
    except Exception: pass

async def process_account_uid_pass(uid: str, password: str) -> Optional[Dict]:
    cached = cache_get(uid)
    if cached:
        acc_id = str(cached['account_id'])
        nick = cached.get('nickname', f"Player_{acc_id}")
        bot_state.register_account(uid=acc_id, nickname=nick,
            region=cached.get('region', 'BD'), level=cached.get('level', 1),
            exp=cached.get('exp', 0), likes=cached.get('likes', 0), auth_uid=str(uid))
        _register_credentials(cached)
        return cached

    print_info(f"[LOGIN] Authenticating UID: {uid}...")
    try:
        async with _LOGIN_SEMAPHORE:
            verconfig_res = await version_config()
            if verconfig_res is None: return None
            release_version, client_version, server_url = verconfig_res
            tokengrant_response = await get_access_token(uid, password)
            if tokengrant_response is None: return None
            open_id, access_token, platform = tokengrant_response
            major_payload, login_payload = await build_majorlogin_payload(open_id, access_token, platform, client_version)
            if not major_payload or not login_payload: return None
            res_json = await major_login(major_payload, server_url, release_version)
            if not res_json or res_json.get("__SHORT_RESPONSE__"): return None

            def _get_data(key):
                v = res_json.get(str(key))
                if isinstance(v, dict) and "data" in v: return v["data"]
                if key in res_json and not isinstance(res_json[key], dict): return res_json[key]
                if isinstance(v, dict): return v.get("data")
                return None

            acc_id_raw = _get_data(1)
            region_raw = _get_data(2) or "BD"
            jwt_token = _get_data(8)
            server_url_raw = _get_data(10)
            server_time = _get_data(21)
            aes_ak_raw, iv_i_raw = _extract_key_iv(res_json)
            if not jwt_token or not server_url_raw: return None
            if not aes_ak_raw or not iv_i_raw: return None
            url_raw = server_url_raw
            getlogin_json = await get_login_data(login_payload, jwt_token, url_raw, release_version)
            if not getlogin_json: return None

        def _gf(field, default=None):
            v = getlogin_json.get(str(field), {}).get("data")
            return v if v is not None else default

        level = int(_gf(6, 1) or 1)
        exp = int(_gf(7, 0) or 0)
        likes = int(_gf(8, 0) or 0)
        nickname = _gf(4, f"Player_{acc_id_raw}") or f"Player_{acc_id_raw}"
        region = region_raw or _gf(3, "BD") or "BD"
        acc_id = str(acc_id_raw)

        bot_state.register_account(uid=acc_id, nickname=nickname, region=region,
            level=level, exp=exp, likes=likes, auth_uid=str(uid))
        print_success(f"[✓] Login OK: {acc_id} | {nickname}")

        account_data = {
            'account_id': acc_id_raw, 'nickname': nickname, 'region': region,
            'level': level, 'exp': exp, 'likes': likes, 'open_id': open_id,
            'access_token': access_token, 'platform': str(platform),
            'token': jwt_token, 'server_time': server_time,
            'aes_ak': aes_ak_raw, 'iv_i': iv_i_raw,
            'functional_addrs': _gf(14), 'informational_addrs': _gf(32),
            'release_version': release_version, 'client_version': client_version,
            'server_url': url_raw, 'login_payload_data': login_payload,
            'auth_type': 'guest', 'auth_uid': uid, 'auth_password': password,
        }
        _register_credentials(account_data)
        cache_set(uid, account_data)
        return account_data
    except Exception as e:
        print_error(f"process_account_uid_pass error: {e}")
        return None

async def process_account_token(access_token: str) -> Optional[Dict]:
    cache_key = f"tok_{access_token[:20]}"
    cached = cache_get(cache_key)
    if cached:
        acc_id = str(cached['account_id'])
        nick = cached.get('nickname', f"Player_{acc_id}")
        bot_state.register_account(uid=acc_id, nickname=nick,
            region=cached.get('region', 'BD'), level=cached.get('level', 1),
            exp=cached.get('exp', 0), likes=cached.get('likes', 0), token=access_token)
        _register_credentials(cached)
        return cached
    # (token flow omitted for brevity; guest path is main)
    return None

async def run_account_worker(account_data: Dict, label: str):
    acc_id = str(account_data['account_id'])
    informational_task = None
    exp_task = None
    try:
        reg = account_data.get('region', 'BD')
        tcp_packet_online = await build_tcp_startup_packet(
            account_data['account_id'], account_data['token'], account_data['server_time'],
            account_data['aes_ak'], account_data['iv_i'], region=reg, typ='OnLine')
        tcp_packet_chat = await build_tcp_startup_packet(
            account_data['account_id'], account_data['token'], account_data['server_time'],
            account_data['aes_ak'], account_data['iv_i'], region=reg, typ='ChaT')

        # ── CLAN JOIN FIRST ──
        if AUTO_JOIN_CLAN and CLAN_ID:
            try:
                ok = await join_clan(account_data['token'], CLAN_ID)
                if ok:
                    print_success(f"[CLAN] ✅ {acc_id} joined {CLAN_ID}")
                else:
                    print_warning(f"[CLAN] ⚠️ {acc_id} join failed — continuing")
            except Exception as e:
                print_warning(f"[CLAN] {acc_id} err: {e}")

        informational_task = asyncio.create_task(informational(
            account_data['informational_addrs'], tcp_packet_chat,
            account_data['aes_ak'], account_data['iv_i'],
            region=reg, account_id=acc_id, account_data=account_data))

        async def exp_refresher():
            while True:
                await asyncio.sleep(90 + random.uniform(-10.0, 10.0))
                fresh = bot_state.account_credentials.get(acc_id)
                if fresh: await refresh_account_profile(fresh)

        exp_task = asyncio.create_task(exp_refresher())

        functional_task = asyncio.create_task(functional_lone_wolf(
            account_data['functional_addrs'], tcp_packet_online,
            account_data['region'], account_data['client_version'],
            account_data['aes_ak'], account_data['iv_i'],
            account_id=acc_id, account_data=account_data))
        await functional_task
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print_error(f"run_account_worker {label}: {e}")
    finally:
        for t in (informational_task, exp_task):
            if t and not t.done(): t.cancel()
        for t in (informational_task, exp_task):
            if t:
                try: await t
                except (asyncio.CancelledError, Exception): pass

async def refresh_account_profile(account_data_or_uid: Any):
    try:
        if isinstance(account_data_or_uid, str):
            account_data = bot_state.account_credentials.get(str(account_data_or_uid))
        else:
            account_data = account_data_or_uid
        if not account_data: return
        token = account_data.get('token'); acc_id = account_data.get('account_id')
        server_url = account_data.get('server_url'); release_version = account_data.get('release_version')
        if not (token and acc_id and server_url and release_version): return
        data = await get_player_personal_show(int(acc_id), token, server_url, release_version)
        if not data: return
        player_data = data.get(1, {}) if isinstance(data.get(1), dict) else {}
        nickname = player_data.get(3); current_level = player_data.get(6); current_exp = player_data.get(7)
        if current_exp is None: return
        try:
            current_exp = int(current_exp); current_level = int(current_level) if current_level else 1
        except Exception: return
        acc_id_str = str(acc_id)
        if acc_id_str in bot_state.accounts:
            bot_state.update_exp(acc_id_str, current_exp, current_level)
    except Exception: pass

async def account_loop_guest(uid: str, password: str):
    uid_str = str(uid)
    bot_state.account_workers[uid_str] = asyncio.current_task()
    acc_id = None
    while True:
        try:
            try: bot_state.update_status(uid_str, "CONNECTING")
            except Exception: pass
            account_data = await process_account_uid_pass(uid_str, password)
            if not account_data:
                await asyncio.sleep(15); continue
            acc_id = str(account_data['account_id'])
            bot_state.account_workers[acc_id] = asyncio.current_task()
            bot_state.account_workers[uid_str] = asyncio.current_task()
            bot_state.auth_to_game_id[uid_str] = acc_id
            bot_state.game_to_auth_id[acc_id] = uid_str
            await run_account_worker(account_data, uid_str)
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            try:
                bot_state.update_status(uid_str, "OFFLINE")
                if acc_id: bot_state.update_status(acc_id, "OFFLINE")
            except Exception: pass
            break
        except Exception:
            await asyncio.sleep(10)

# ==================== ACCOUNTS LOADER ====================
def load_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): accounts = data
        except Exception as e:
            print_error(f"load accounts: {e}")
    return accounts

# ==================== MAIN ====================
async def main():
    print_colored("╔════════════════════════════════════════════════════════════╗", Colors.CYAN)
    print_colored("║   ⚡ SQUAD MODE — 2-4 AUTO MATCH + AUTO CLAN + LOOP ⚡     ║", Colors.CYAN)
    print_colored(f"║   Dashboard: http://localhost:{WEB_PORT}                        ║", Colors.GREEN)
    print_colored("╚════════════════════════════════════════════════════════════╝", Colors.CYAN)

    try:
        await start_web_dashboard(host=WEB_HOST, port=WEB_PORT)
        print_success(f"[✓] Dashboard UI Active")
    except Exception as e:
        print_error(f"dashboard: {e}")

    # write accounts.json from hardcoded list
    if HARDCODED_ACCOUNTS:
        try:
            clean = []
            for a in HARDCODED_ACCOUNTS:
                if not isinstance(a, dict): continue
                u = str(a.get("uid","")).strip(); p = str(a.get("password","")).strip()
                if u and p: clean.append({"uid": u, "password": p})
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                json.dump(clean, f, indent=2, ensure_ascii=False)
            print_success(f"[TEAM] Loaded {len(clean)} hardcoded accounts")
        except Exception as e:
            print_error(f"write accounts.json: {e}")

    sync_devices_with_accounts()
    accounts = load_accounts()
    if not accounts:
        print_warning("[!] no accounts"); return
    print_success(f"[✓] Total accounts: {len(accounts)}")

    # pre-assign groups (deterministic)
    sorted_accounts = sorted(accounts, key=lambda a: str(a.get("uid","")))
    for acc in sorted_accounts:
        uid = str(acc.get("uid","")).strip()
        if uid:
            g = await _assign_group(uid)
            print_info(f"[TEAM] pre-assign {uid} → group {g}")

    # start bots
    for i, acc in enumerate(accounts):
        u = str(acc.get("uid","")).strip()
        p = str(acc.get("password","")).strip()
        if u and p:
            t = asyncio.create_task(account_loop_guest(u, p))
            bot_state.account_workers[u] = t
        await asyncio.sleep(0.5)   # stagger for Garena rate-limit

    try:
        while True: await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print_warning("\n[STOP] shutting down...")
        for t in list(bot_state.account_workers.values()):
            t.cancel()
        await asyncio.gather(*bot_state.account_workers.values(), return_exceptions=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nstopped by user")
