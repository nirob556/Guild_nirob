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
NEW_MATCH_DELAY = 1.0                   # ← match শেষ → 1s → আবার start
MAX_MATCH_DURATION = 2400               # 40 min hard cap
MATCH_IDLE_TIMEOUT = 90.0
MATCH_SILENCE_EXIT = 180.0
MAX_CONCURRENT_MATCHES = 1

FALLBACK_UID = ""
FALLBACK_PASSWORD = ""

_accept_friend_request = True
DEBUG_ALL_PACKETS = False

# ==================== TEAM / SQUAD MODE ====================
TEAM_MODE = True
TEAM_SIZE = 4                           # প্রতি squad-এ MAX ৪
MIN_SQUAD_SIZE = 2                      # MIN ২ হলেই start
TEAM_READY_DELAY = 1.5
TEAM_INVITE_WAIT = 1.0
TEAM_MEMBER_TRIGGER_DELAY = 6.0
TEAM_MATCH_LOOP_COUNT = 60
TEAM_MATCH_LOOP_INTERVAL = 1.0
TEAM_GROUP_TIMEOUT = 30.0
TEAM_FILL_WAIT = 6.0                    # ২ জন হলেও আর ৬s অপেক্ষা (বাকিরা আসার জন্য)

SQUAD_MATCH_FIELD1 = 9

# ==================== CLAN ====================
CLAN_ID = "3105631591"
AUTO_JOIN_CLAN = True
CLAN_JOIN_RETRIES = 5
CLAN_JOIN_DELAY = 1.2

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
    """Deterministic group assignment: fill group 0 with 4, then group 1, etc."""
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

async def _group_leader(group_idx: int) -> Optional[str]:
    async with _GROUP_LOCK:
        return _GROUP_LEADERS.get(group_idx)

async def _choose_group_leader(group_idx: int, online_uids: List[str]) -> Optional[str]:
    """Deterministic: smallest uid among online members"""
    if not online_uids:
        return None
    candidates = sorted(online_uids)
    leader = candidates[0]
    async with _GROUP_LOCK:
        _GROUP_LEADERS[group_idx] = leader
    return leader

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
_ACTIVE_SQUADS: Dict[int, Dict[str, Any]] = {}
_SQUAD_LOCK = asyncio.Lock()

async def _squad_register_member(group_idx: int, uid: str, acc_id: str):
    uid = str(uid); acc_id = str(acc_id)
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.setdefault(group_idx, {
            "members": {},
            "state": "forming",
            "last_start": 0.0,
        })
        sq["members"][uid] = acc_id
        sq["state"] = "forming"

async def _squad_unregister_member(group_idx: int, uid: str):
    uid = str(uid)
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if not sq: return
        sq["members"].pop(uid, None)
        if not sq["members"]:
            _ACTIVE_SQUADS.pop(group_idx, None)

async def _squad_online_members(group_idx: int) -> Dict[str, str]:
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if not sq: return {}
        return dict(sq["members"])

async def _squad_set_state(group_idx: int, state: str):
    async with _SQUAD_LOCK:
        sq = _ACTIVE_SQUADS.get(group_idx)
        if sq: sq["state"] = state

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
                if not isinstance(devices, dict): devices = {}
        except Exception: devices = {}
    synced_devices = {}
    for acc in accounts:
        uid = str(acc.get("uid", "")).strip()
        if not uid: continue
        dev_profile = devices.get(uid) or _generate_new_device()
        synced_devices[uid] = dev_profile
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(synced_devices, f, indent=4)
    except Exception: pass
    return synced_devices

# ==================== DNS RESOLVER ====================
CLOUDFLARE_PRIMARY_DNS = "1.1.1.1"
CLOUDFLARE_SECONDARY_DNS = "1.0.0.1"
_DNS_CACHE: Dict[str, Tuple[str, float]] = {}
_DNS_CACHE_TTL = 300.0

async def resolve_host_cloudflare(hostname: str) -> str:
    if not hostname: return hostname
    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return hostname
    now = time.time()
    if hostname in _DNS_CACHE:
        ip, exp = _DNS_CACHE[hostname]
        if now < exp: return ip

    def _query(server_ip):
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
                        if offset >= len(resp): break
                        if (resp[offset] & 0xC0) == 0xC0:
                            offset += 2
                        else:
                            while offset < len(resp) and resp[offset] != 0:
                                offset += 1 + resp[offset]
                            offset += 1
                        if offset + 10 > len(resp): break
                        rtype, rclass, ttl, rdlen = struct.unpack(">HHIH", resp[offset:offset+10])
                        offset += 10
                        if rtype == 1 and rdlen == 4 and offset + 4 <= len(resp):
                            return socket.inet_ntoa(resp[offset:offset+4])
                        offset += rdlen
        except Exception: pass
        finally:
            if s:
                try: s.close()
                except Exception: pass
        return None

    loop = asyncio.get_running_loop()
    ip = await loop.run_in_executor(None, _query, CLOUDFLARE_PRIMARY_DNS)
    if not ip:
        ip = await loop.run_in_executor(None, _query, CLOUDFLARE_SECONDARY_DNS)
    if not ip:
        try:
            ip_info = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
            if ip_info: ip = ip_info[0][4][0]
        except Exception: ip = hostname
    if ip: _DNS_CACHE[hostname] = (ip, now + _DNS_CACHE_TTL)
    return ip or hostname

def optimize_tcp_socket(sock):
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "SIO_KEEPALIVE_VALS") and os.name == 'nt':
            try: sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 2000))
            except Exception: pass
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    except Exception: pass

async def safe_close_writer(writer):
    if not writer: return
    try:
        if not writer.is_closing(): writer.close()
        await asyncio.wait_for(writer.wait_closed(), timeout=1.5)
    except Exception: pass

def optimize_udp_socket(sock):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
        if hasattr(socket, 'SIO_UDP_CONNRESET') and os.name == 'nt':
            try: sock.ioctl(socket.SIO_UDP_CONNRESET, False)
            except Exception: pass
    except Exception: pass

# ==================== NETWORK & CRYPTO ====================
client = httpx.AsyncClient(verify=False, timeout=15.0,
    limits=httpx.Limits(max_connections=300, max_keepalive_connections=150))
_LOGIN_SEMAPHORE = asyncio.Semaphore(6)

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
    HEADER = '\033[95m'; GREEN = '\033[92m'; FAIL = '\033[91m'
    WARNING = '\033[93m'; CYAN = '\033[96m'; MAGENTA = '\033[95m'
    WHITE = '\033[97m'; ENDC = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    try: print(f"{color}{text}{Colors.ENDC}")
    except Exception:
        try: print(f"{color}{text.encode('ascii', errors='replace').decode('ascii')}{Colors.ENDC}")
        except Exception: pass

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

# ==================== MATCH COUNTER ====================
_match_counters: Dict[str, int] = {}
_match_counter_lock = asyncio.Lock()

async def _inc_match(uid):
    async with _match_counter_lock:
        _match_counters[uid] = _match_counters.get(uid, 0) + 1
        return _match_counters[uid]

async def _dec_match(uid):
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

def _load_token_cache():
    global _token_cache_memo, _token_cache_memo_time
    now = time.time()
    if _token_cache_memo and (now - _token_cache_memo_time) < _TOKEN_CACHE_MEMO_TTL:
        return _token_cache_memo
    if not os.path.exists(TOKEN_CACHE_FILE): return {}
    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content: return {}
        data = json.loads(content)
        if not isinstance(data, dict): raise ValueError("bad cache")
        parsed = _json_deserializer(data)
        _token_cache_memo = parsed; _token_cache_memo_time = now
        return parsed
    except Exception:
        try: os.remove(TOKEN_CACHE_FILE)
        except Exception: pass
        return {}

def _save_token_cache(cache):
    global _token_cache_memo, _token_cache_memo_time
    try:
        tmp_file = TOKEN_CACHE_FILE + ".tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, default=_json_serializer)
        os.replace(tmp_file, TOKEN_CACHE_FILE)
        _token_cache_memo = cache; _token_cache_memo_time = time.time()
    except Exception: pass

def cache_get(uid):
    cache = _load_token_cache()
    entry = cache.get(str(uid))
    if not entry: return None
    if time.time() - entry.get("cached_at", 0) > TOKEN_CACHE_TTL:
        cache_invalidate(uid); return None
    if str(entry.get("account_id", "")).isdigit():
        entry["account_id"] = int(entry["account_id"])
    if not isinstance(entry.get("login_payload_data"), (bytes, bytearray)):
        cache_invalidate(uid); return None
    return entry

def cache_set(uid, account_data):
    cache = _load_token_cache()
    entry = dict(account_data); entry["cached_at"] = time.time()
    cache[str(uid)] = entry
    _save_token_cache(cache)

def cache_invalidate(uid):
    cache = _load_token_cache()
    if str(uid) in cache:
        del cache[str(uid)]; _save_token_cache(cache)

# ==================== PROTOBUF HELPERS ====================
def encode_varint(n):
    if n < 0: n &= 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def _pb_varint(field, value):
    return encode_varint((field << 3) | 0) + encode_varint(value)

def _pb_length(field, value):
    enc = value.encode('utf-8') if isinstance(value, str) else value
    return encode_varint((field << 3) | 2) + encode_varint(len(enc)) + enc

def create_proto(fields):
    pkt = bytearray()
    for field, value in fields.items():
        if isinstance(field, str): field = int(field)
        if isinstance(value, dict):
            pkt.extend(_pb_length(field, bytes(create_proto(value))))
        elif isinstance(value, list):
            for it in value:
                if isinstance(it, dict):
                    pkt.extend(_pb_length(field, bytes(create_proto(it))))
                elif isinstance(it, str): pkt.extend(_pb_length(field, it))
                elif isinstance(it, (bytes, bytearray)): pkt.extend(_pb_length(field, bytes(it)))
                elif isinstance(it, bool): pkt.extend(_pb_varint(field, 1 if it else 0))
                elif isinstance(it, int): pkt.extend(_pb_varint(field, it))
        elif isinstance(value, bool): pkt.extend(_pb_varint(field, 1 if value else 0))
        elif isinstance(value, int): pkt.extend(_pb_varint(field, value))
        elif isinstance(value, str): pkt.extend(_pb_length(field, value))
        elif isinstance(value, (bytes, bytearray)): pkt.extend(_pb_length(field, bytes(value)))
    return bytes(pkt)

def encrypt_aes(hex_data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    raw = bytes.fromhex(hex_data)
    return cipher.encrypt(pad(raw, AES.block_size)).hex()

def decode_varint(data, offset):
    result = 0; shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80): return result, offset
        shift += 7
    return None, offset

def extract_raw_fields(data):
    result = {}; offset = 0; data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        fn = header >> 3; wt = header & 0x7
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
        fd = {"wire_type": r.wire_type}
        if r.wire_type == "varint": fd["data"] = r.data
        elif r.wire_type in ("string", "bytes"): fd["data"] = r.data
        elif r.wire_type == "length_delimited":
            if hasattr(r.data, "results"): fd["data"] = _parse_results_sync(r.data.results)
            elif isinstance(r.data, list): fd["data"] = _parse_results_sync(r.data)
            else: fd["data"] = str(r.data)
        out[str(r.field)] = fd
    return out

def decode_protobuf_dict(data):
    try: return _parse_results_sync(Parser().parse(data))
    except Exception: return {}

def decode_protobuf_2(data):
    result = {}; offset = 0; data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        fn = header >> 3; wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset + length]; offset += length
            try:
                ds = value.decode('utf-8')
                if ds:
                    if len(ds) > 10 and all(c in '0123456789abcdef' for c in ds.lower()):
                        try:
                            hx = bytes.fromhex(ds).decode('utf-8', errors='ignore')
                            result[fn] = hx if hx else ds
                        except Exception: result[fn] = ds
                    else: result[fn] = ds
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
    if isinstance(K, str): K = bytes.fromhex(K) if len(K) == 32 else K.encode()
    if isinstance(V, str): V = bytes.fromhex(V) if len(V) == 32 else V.encode()
    PkEnc = AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(Pk), 16)).hex()
    L = len(PkEnc) // 2
    hexlen = hex(L)[2:]
    if len(hexlen) % 2 != 0: hexlen = '0' + hexlen
    total_pad = 12 - len(N) - len(hexlen)
    if total_pad < 0: total_pad = 0
    return bytes.fromhex(N + ('0' * total_pad) + hexlen + PkEnc)

# ==================== TEAM PACKET FUNCTIONS ====================
def create_team(key, iv, game_version="1.132.9"):
    fields = {
        1: 1,
        2: {
            2: bytes.fromhex("01"), 3: 1, 4: 3, 5: "en",
            8: {1: "IDC3", 2: 123, 3: "BD"},
            9: 1, 10: bytes.fromhex("01090a0b1219202729"),
            11: 2, 13: 1,
            14: {
                1: "08FBA33B4BABE2790205390333330000009700050092005F72697EB2134DCBB2467625142201040e38e848dc0e748c3f6aa04d81000000ff1113090dcacfa16d",
                2: 478,
                3: "7e585d55110201440555560d0103035104575b0e0d0d0d040708050206010201050c0452045600541b0605487d5c41444b1b0114061d1709034d00547d730b586c45627e7b624b45736e597d700e770965790178750a1705447b5c62537552754d7b607f7657517675485379555b5a5b505161440c1b515b5a4c1e62781f7441480648636a664100414754425b4163134b7948450a68777f5f416a1e47080f10000b4b425e56447b6159637462455746524b047c7a477a7a5b67577b575e0d110b4d4c00641b5362631f680a754b6d5e475343785b4b187f13584c47790c12024e187740537245174050587d5d6b4a4047595a030109664b014a5e7d091b084d616b727d1742606517505c6979494876727e1f526904784141040c0a1705004d7f5b5a72057644641f56025405687f62756507070155027360565605140748701a00546160007c411f065e0559660752441358077313771a67020e120c4b524d7f50467a6b7200696e01466968770561475217444e037f74740d11010144467302135058427c547d4a5c61604a434401054b7f0b425d7b4f700c13074f5e4e445d7c5e5f5a71405144551c60735041527a63441e01636e4305",
                4: "y[Z]", 6: 12, 7: "15686677735a7506101c",
                8: f"{game_version}", 9: 3, 10: 1,
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
            1: int(target_uid), 3: int(target_uid),
            4: bytes.fromhex("0107090a0b120f19202729"),
            8: 1,
            9: {
                1: "08FBA33B0522052002041B0222220007000C00010004000547E265AE1080779546762514110104076fa2e8770e748c3f6a68ed75000000ff08080500cacfa16d",
                2: 235,
                3: {14: 80, 11: 86},
                4: "{Y\\R", 6: 13, 7: {2: 4}, 8: "1.132.9",
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
    fields = {
        1: SQUAD_MATCH_FIELD1,
        2: {
            1: int(account_id),
            2: 1, 3: TEAM_SIZE,
            7: {1: "IDC3", 2: 410, 3: region},
        }
    }
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

# ==================== AES KEY/IV EXTRACTOR ====================
def _extract_key_iv(res_json):
    if "__RAW_HEX__" in res_json and "__OFFSET__" in res_json:
        try:
            raw = bytes.fromhex(res_json["__RAW_HEX__"])
            off = int(res_json["__OFFSET__"])
            rf = extract_raw_fields(raw[off:])
            for kf, vf in [(22, 23), (24, 25), (6, 7)]:
                k = rf.get(kf); v = rf.get(vf)
                if isinstance(k, (bytes, bytearray)) and len(k) == 16 and \
                   isinstance(v, (bytes, bytearray)) and len(v) == 16:
                    return bytes(k), bytes(v)
            candidates = {fn: v for fn, v in rf.items()
                          if isinstance(v, (bytes, bytearray)) and len(v) == 16 and fn >= 20}
            if len(candidates) >= 2:
                sk = sorted(candidates.keys())
                return bytes(candidates[sk[0]]), bytes(candidates[sk[1]])
        except Exception: pass

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
                    c = bytes.fromhex(data)
                    if len(c) == 16: raw = c
                except Exception: pass
            if raw is None and len(data) == 16: raw = data.encode('latin-1')
        if raw and len(raw) == 16:
            try: found[int(k)] = raw
            except Exception: pass
    if len(found) < 2: return None, None
    for kf, vf in [(22, 23), (24, 25), (6, 7)]:
        if kf in found and vf in found:
            return found[kf], found[vf]
    sk = sorted(found.keys())
    return found[sk[0]], found[sk[1]]

async def aes_encrypt(payload, key, iv):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(payload, AES.block_size))

async def get_playstore_version():
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth', lang='hi', country='id'))
        return result.get("version")
    except Exception: return "1.132.9"

async def version_config():
    app_version = await get_playstore_version()
    api_url = ("https://version.ggwhitehawk.com/live/ver.php"
        f"?version={app_version}&lang=hi&device=android&channel=android"
        "&appstore=googleplay&region=BD&whitelist_version=1.3.0&whitelist_sp_version=1.0.0")
    try:
        r = await client.get(api_url)
        r.raise_for_status()
        j = r.json()
        srv = j.get("server_url"); rem = j.get("remote_version"); rel = j.get("latest_release_version")
        if not srv or not rem or not rel: return None
        return rel, rem, srv
    except Exception: return None

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
            r = await client.post(url, headers=hdrs, data=data)
            if r.status_code == 200:
                j = r.json()
                oid = j.get("open_id"); tok = j.get("access_token"); plat = j.get("platform", 4)
                if oid and tok: return oid, tok, plat
            if r.status_code == 429:
                await asyncio.sleep(1.0); continue
        except Exception: pass
        await asyncio.sleep(0.5)
    return None

async def parse_results(pr):
    out = {}
    for r in pr:
        fd = {"wire_type": r.wire_type}
        if r.wire_type in ("varint", "string", "bytes"): fd["data"] = r.data
        elif r.wire_type == "length_delimited":
            if hasattr(r.data, "results"): fd["data"] = await parse_results(r.data.results)
            elif isinstance(r.data, list): fd["data"] = await parse_results(r.data)
            else: fd["data"] = str(r.data)
        out[str(r.field)] = fd
    return out

async def decode_protobuf_async(data):
    return json.dumps(await parse_results(Parser().parse(data)))

# ==================== PAYLOAD BUILDER ====================
async def get_payload(access_token, open_id, platform, version):
    device_id = f"Google|{uuid.uuid4()}"
    ml = {
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
        "95": 111107, "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1, "98": 1, "99": f"{platform}", "100": f"{platform}",
        "102": "4503454457550c0766", "104": 53792, "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1",
    }
    gld = dict(ml); gld["90"] = "Khulna"; gld["91"] = "D"; gld["99"] = "0"; gld["103"] = 1
    return bytes.fromhex(encrypt_aes(create_proto(ml).hex())), bytes.fromhex(encrypt_aes(create_proto(gld).hex()))

async def build_majorlogin_payload(open_id, access_token, platform, client_version, device_info=None):
    try: return await get_payload(access_token, open_id, platform, client_version)
    except Exception: return None, None

# ==================== MAJOR LOGIN ====================
async def major_login(payload, login_url, release_version):
    try:
        url = f"{login_url}MajorLogin" if login_url.endswith("/") else f"{login_url}/MajorLogin"
        rh = {
            "Accept": "*/*", "Authorization": "Bearer ",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
            "X-Unity-Version": "2018.4.12f1",
        }
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.post(url, headers=rh, data=payload, ssl=ctx) as r:
                rc = await r.read()
                if r.status != 200: return None
                if len(rc) < 200: return {"__SHORT_RESPONSE__": True}
                best = None; bf = 0; bo = 64
                for offset in [64, 0, 48, 32, 80, 16, 128, 8, 96]:
                    if offset >= len(rc): continue
                    cb = rc[offset:]
                    try:
                        c = decode_protobuf_dict(cb); n = len(c) if c else 0
                    except Exception: c = {}; n = 0
                    if n > bf: best = c; bf = n; bo = offset
                    if bf >= 5: break
                if not best or bf < 3:
                    for offset in [64, 0, 48, 32, 80, 16, 128, 8, 96]:
                        if offset >= len(rc): continue
                        cb = rc[offset:]
                        try:
                            c2 = decode_protobuf_2(cb); n2 = len(c2) if c2 else 0
                        except Exception: c2 = {}; n2 = 0
                        if n2 > bf:
                            best = {str(k): {"data": v} for k, v in c2.items()}
                            bf = n2; bo = offset
                        if bf >= 5: break
                if not best or len(best) < 3: return None
                best["__RAW_HEX__"] = rc.hex(); best["__OFFSET__"] = bo
                return best
    except Exception: return None

async def get_login_data(payload, jwt, server_url, rel):
    try:
        url = f"{server_url.rstrip('/')}/GetLoginData"
        rh = {
            "Accept": "*/*", "Authorization": f"Bearer {jwt}",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{rel}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
            "X-Unity-Version": "2018.4.12f1",
            "Host": "clientbp.ppmainecoonghj.com",
        }
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.post(url, headers=rh, data=payload, ssl=ctx) as r:
                rc = await r.read()
                if r.status != 200: return None
                best = None; bf = 0
                for offset in [0, 64, 48, 32, 80, 16, 128, 8, 96]:
                    if offset >= len(rc): continue
                    cb = rc[offset:]
                    try:
                        c = decode_protobuf_dict(cb); n = len(c) if c else 0
                    except Exception: c = {}; n = 0
                    if n > bf: best = c; bf = n
                    if bf >= 5: break
                if not best or bf < 3:
                    for offset in [0, 64, 48, 32, 80, 16, 128, 8, 96]:
                        if offset >= len(rc): continue
                        cb = rc[offset:]
                        try:
                            c2 = decode_protobuf_2(cb); n2 = len(c2) if c2 else 0
                        except Exception: c2 = {}; n2 = 0
                        if n2 > bf:
                            best = {str(k): {"data": v} for k, v in c2.items()}
                            bf = n2
                        if bf >= 5: break
                if not best or len(best) < 3: return None
                return best
    except Exception: return None

async def get_player_personal_show(target_uid, jwt, server_url, rel):
    try:
        url = f"{server_url}/GetPlayerPersonalShow"
        payload = bytes.fromhex(encrypt_aes(create_proto({"1": int(target_uid)}).hex()))
        hdrs = {
            "authorization": f"Bearer {jwt}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{rel}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*", "x-unity-version": "2022.3.47f1",
        }
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as s:
            async with s.post(url, headers=hdrs, data=payload, ssl=ctx) as r:
                if r.status != 200: return None
                return decode_protobuf_2(await r.read())
    except Exception: return None

async def accept_friend_request(target_uid, own_id, jwt, server_url, rel):
    try:
        url = f"{server_url}/ConfirmFriendRequest"
        payload = bytes.fromhex(encrypt_aes(create_proto({"1": int(target_uid), "2": int(own_id)}).hex()))
        hdrs = {
            "authorization": f"Bearer {jwt}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{rel}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*", "x-unity-version": "2022.3.47f1",
        }
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as s:
            async with s.post(url, headers=hdrs, data=payload, ssl=ctx) as r:
                if r.status == 200:
                    return decode_protobuf_dict(await r.read())
                return None
    except Exception: return None

# ==================== CLAN JOIN (AGGRESSIVE) ====================
def _get_region_from_jwt(jwt):
    try:
        p = jwt.split('.')[1]; p += '=' * (-len(p) % 4)
        d = json.loads(base64.urlsafe_b64decode(p))
        return (d.get('lock_region') or d.get('noti_region') or 'BD').upper()
    except Exception: return "BD"

def _get_region_url(region):
    r = region.upper()
    if r == "IND": return "https://client.ind.freefiremobile.com"
    if r in ("BR","US","NA"): return "https://client.us.freefiremobile.com"
    return "https://clientbp.ggpolarbear.com"

def _create_clan_payload(clan_id):
    if not _CLAN_PB_AVAILABLE: return None
    try:
        msg = reqClan_pb2.MyMessage()
        msg.field_1 = int(clan_id)
        raw = msg.SerializeToString()
        return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(raw, AES.block_size))
    except Exception:
        try: return bytes.fromhex(encrypt_aes(create_proto({"1": int(clan_id)}).hex()))
        except Exception: return None

async def join_clan(jwt, clan_id):
    if not _CLAN_PB_AVAILABLE:
        print_warning("[CLAN] reqClan_pb2 missing — cannot join")
        return False
    for attempt in range(CLAN_JOIN_RETRIES):
        try:
            region = _get_region_from_jwt(jwt)
            base = _get_region_url(region)
            url = base.rstrip("/") + "/RequestJoinClan"
            host = base.replace("https://", "")
            payload = _create_clan_payload(clan_id)
            if not payload: return False
            hdrs = {
                "Expect": "100-continue",
                "Authorization": f"Bearer {jwt}",
                "X-Unity-Version": "2018.4.11f1",
                "X-GA": "v1 1", "ReleaseVersion": "OB55",
                "Content-Type": "application/octet-stream",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
                "Host": host, "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }
            ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
                async with s.post(url, headers=hdrs, data=payload, ssl=ctx) as resp:
                    if resp.status == 200:
                        return True
                    await resp.read()
                    await asyncio.sleep(CLAN_JOIN_DELAY)
        except Exception:
            await asyncio.sleep(CLAN_JOIN_DELAY)
    return False

# ==================== TCP STARTUP ====================
async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="BD", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"
    th = f"{int(server_time):08x}"
    ep = (await aes_encrypt(token.encode(), key, iv)).hex()
    epl = f"{len(ep) // 2:08x}"
    reg = str(region).upper() if region else "BD"
    if typ == 'OnLine':
        prefix = '7219' if reg == 'BD' else ('7214' if reg == 'IND' else '7215')
        return f"{prefix}{uid_hex}{th}00000000{epl}{ep}"
    else:
        prefix = '8119' if reg == 'BD' else ('8114' if reg == 'IND' else '8115')
        return f"{prefix}{uid_hex}{th}{epl}{ep}"

async def send_keep_alive(region="BD"):
    try:
        reg = str(region).upper() if region else "BD"
        return bytes.fromhex("0219" if reg == "BD" else ("0214" if reg == "IND" else "0215"))
    except Exception: return bytes.fromhex("0219")

# ==================== UDP HELPERS ====================
async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80:
        out.append((z & 0x7F) | 0x80); z >>= 7
    out.append(z)
    return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
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
    prev_c = bytearray(8); prev_i = bytearray(8)
    for i in range(0, len(padded), 8):
        x = bytearray(8)
        for j in range(8): x[j] = padded[i + j] ^ prev_c[j]
        e0, e1 = await tea_enc(struct.unpack_from("<I", x, 0)[0], struct.unpack_from("<I", x, 4)[0], k0, k1, k2, k3)
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0); struct.pack_into("<I", enc, 4, e1)
        for j in range(8): out[i + j] = enc[j] ^ prev_i[j]
        prev_c[:] = out[i:i + 8]; prev_i[:] = x
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def encode_header(layout, so, cmd, oid, fl, ln, k, v80):
    out = bytearray()
    for code in layout:
        value = {0: so, 1: cmd, 2: oid, 3: fl, 4: ln}[code]
        if _FIELD_SIZES[code] == 1: out.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF); out.append((v >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf: c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def sv_frame(msg_key, layout, so, cmd, oid, fl, content, key, enc=True):
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if enc else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, so, cmd, oid, fl, len(body), k, v80)
    pkt = bytearray(hdr + body)
    pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
    return bytes(pkt)

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val,
                                      server_ip="", region="BD", client_version="1.132.9",
                                      client_version_code="2019121229", access_token="",
                                      mode_id=1, map_id=1):
    token = token.strip()
    udp_key = bytes.fromhex(udp_key)
    mc = [int(ch) for ch in str(match_code).strip()]
    tj = token[:660] if len(token) > 660 else token
    sj = token[660:] if len(token) > 660 else ""
    etj = tj.encode() if isinstance(tj, str) else tj
    esj = sj.encode() if isinstance(sj, str) else sj
    g420 = await has_ssan_zig(len(etj)) + etj
    reg = str(region).upper() if region else "BD"
    csb = bytes.fromhex("ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e3137302e3233303b33352e3138352e3138332e3537000000000000010000000000000000000000000100000800000100000000000100a8a2d7bebd8d8bdf110200")
    mid = bytes.fromhex('0000000001000102030101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030003000004')
    mid += await has_ssan_zig(len(client_version)) + client_version.encode()
    mid += await has_ssan_zig(len(client_version_code)) + client_version_code.encode()
    mid += csb
    cip = server_ip.split(':')[0] if server_ip else "0.0.0.0"
    mid += await has_ssan_zig(len(cip)) + cip.encode()
    cat = access_token.strip() if access_token else ""
    if cat: mid += await has_ssan_zig(len(cat)) + cat.encode()
    mid += await has_ssan_zig(len(esj)) + esj
    tg = (await uleb_encode(int(account_id)) + await uleb_encode(int(block_val)) +
          await uleb_encode(1) + await uleb_encode(int(mode_id)) +
          await uleb_encode(int(block_val)) + await uleb_encode(int(map_id)) + mid)
    process = await sv_frame(0x5E, mc, 2, 447, 0, 1, g420, udp_key)
    loading = await sv_frame(0x5A, mc, 2, 448, 1, 1, tg, udp_key)
    return process.hex(), loading.hex()

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")
    if len(data) > 25: raise ValueError(f"Text too long ({len(data)})")
    content = b"\x10\x00\x00\x00" + data + b"\x00" * (29 - 4 - len(data))
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    layout = [int(c) for c in str(layout).strip()] if isinstance(layout, str) else list(layout)
    padded = await build_padded(content)
    eb = await tea_cbc_encrypt(padded, key)
    hb = await encode_header(layout, 1, 1, 0, 1, len(eb), k, v80)
    pkt = bytearray([0x63, 0x00]) + hb + eb
    pkt[1] = await crc7_buff(0, pkt[2:]) & 0x7F
    return bytes(pkt).hex()

async def classify(frame):
    cmd = frame["cmd"]
    mn = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
    if mn == "UDP_HELLO": return "HELLO"
    if mn == "UDP_ACK": return "ACK"
    if mn == "UDP_PING": return "PING"
    if mn == "RUDP_JOIN_MATCH": return "JOIN_MATCH"
    if mn.startswith("RUDP_"): return mn
    if mn.startswith("UDP_"): return mn
    return "DATA"

async def build_packet(msg_key, layout, so, cmd, oid, fl, content, key, enc=True):
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if enc else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        value = {0: so, 1: cmd, 2: oid, 3: fl, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1: hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF); hdr.append((v >> 8) & 0xFF)
    pkt = bytearray(hdr + body)
    pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
    return bytes(pkt)

async def layouts_from_mask(mask):
    ru = [int(c) for c in str(mask).strip()]
    nr = [c for c in ru if c != 2]
    return ru, nr

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    ru, nr = await layouts_from_mask(mask)
    typ = await classify(frame)
    if typ == "HELLO":
        content = frame["content"] if frame["content"] else b"\x10\x00\x00\x00" if ack_style == "echo" else b"\x01\x00"
        return typ, await build_packet(hello_key if ack_style == "echo" else ack_key, nr, 1 if ack_style == "echo" else 0, 1 if ack_style == "echo" else 2, None, 1, content, key)
    if typ == "ACK":
        content = frame["content"] if frame["content"] else b"\x01\x00"
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, content, key)
    if typ == "PING":
        c = frame["content"]
        counter = c[:4] if len(c) >= 4 else c
        return typ, await build_packet(ping_key, nr, 0, 3, None, 0, counter + b"\x00\x00\x00", key, enc=False)
    if typ == "JOIN_MATCH":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return typ, None

async def keepalive_ping(sock, ip, port, key_bytes, mask, stop_event):
    nr = (await layouts_from_mask(mask))[1]
    pk = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop(); i = 0
    while not stop_event.is_set():
        k = pk[i % len(pk)]
        c = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = await build_packet(k, nr, 0, 3, None, 0, struct.pack("<I", c) + b"\x00\x00\x00", key_bytes, enc=False)
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
    pl = padded[0] & 0x07
    s = 3 + pl; e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def tea_cbc_decrypt(body, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(body))
    pi = bytearray(8); pc = bytearray(8)
    x = bytearray(8); d = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8): x[j] = body[i + j] ^ pi[j]
        d0, d1 = await tea_dec(struct.unpack_from("<I", x, 0)[0], struct.unpack_from("<I", x, 4)[0], k0, k1, k2, k3)
        struct.pack_into("<I", d, 0, d0); struct.pack_into("<I", d, 4, d1)
        for j in range(8): out[i + j] = d[j] ^ pc[j]
        pc[:] = body[i:i + 8]; pi[:] = d
    return bytes(out)

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
        else: content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        candidates.append({"kind": kind, "layout": layout, "headerLen": f["headerLen"],
            "msgKey": data[0], "cmd": f["cmd"], "flags": f["flags"],
            "sendOption": f["sendOption"], "orderId": f.get("orderId"),
            "length": f["length"], "content": content, "crcOk": crc_ok,
            "padded": padded, "score": score, "total": len(data)})
    if not candidates: return None
    candidates.sort(key=lambda c: (c["kind"] == "RUDP" or c["kind"] == "nonRUDP", c["score"]), reverse=True)
    return candidates[0]

# ==================== PLAY GAME ====================
async def play_game(server_ip_port, thunder, sharma, udp_key, match_code,
                    account_id, player_region, client_version, key, iv, match_index):
    match_start_time = time.time()
    ping_task = None; sock = None
    ping_stop = asyncio.Event()
    uid_str = str(account_id)
    completed_cleanly = False
    try:
        ip, port = server_ip_port.split(":"); port = int(port)
        resolved_ip = await resolve_host_cloudflare(ip)
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: sock.bind(('0.0.0.0', 0))
        except Exception: pass
        optimize_udp_socket(sock); sock.setblocking(False)
        udkb = bytes.fromhex(udp_key)
        hello = await build_hello_packet(f"{account_id}_2585", udkb, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello), (resolved_ip, port))

        ack_state = "waiting_for_hello_reply"
        thunder_sent = False
        join_match_received = False
        local_closed = False
        send_lock = asyncio.Lock()
        ping_task = asyncio.create_task(keepalive_ping(sock, resolved_ip, port, udkb, match_code, ping_stop))
        last_activity = time.time()

        async def _send_thunder():
            nonlocal ack_state, thunder_sent
            if thunder_sent: return
            async with send_lock:
                if thunder_sent: return
                try:
                    await loop.sock_sendto(sock, bytes.fromhex(thunder), (resolved_ip, port))
                    thunder_sent = True
                    await asyncio.sleep(0.3)
                    pa = await build_packet(0x68, (await layouts_from_mask(match_code))[1], 0, 2, None, 1, b"\x01\x00", udkb)
                    await loop.sock_sendto(sock, pa, (resolved_ip, port))
                    await asyncio.sleep(0.4)
                    await loop.sock_sendto(sock, bytes.fromhex(sharma), (resolved_ip, port))
                    ack_state = "thunder_sharma_sent"
                    print_success(f"[MATCH #{match_index}] In-game ({uid_str})")
                except Exception as e:
                    print_error(f"[MATCH #{match_index}] startup: {e}")

        while not local_closed:
            if time.time() - match_start_time > MAX_MATCH_DURATION:
                completed_cleanly = True; break
            try:
                resp, saddr = await asyncio.wait_for(loop.sock_recvfrom(sock, 65535), timeout=2.0)
                if resp:
                    last_activity = time.time()
                    fr = await decode_packet(resp, udkb, match_code)
                    if fr:
                        pt = await classify(fr)
                        if fr['cmd'] in [103, 107]:
                            print_success(f"[★] Match #{match_index} FINISHED (cmd {fr['cmd']}) — exiting")
                            completed_cleanly = True; local_closed = True; continue
                        if fr['cmd'] == 101:
                            try:
                                ak = await build_packet(0x68, (await layouts_from_mask(match_code))[1], 0, 2, None, 1, b"\x01\x00", udkb)
                                await loop.sock_sendto(sock, ak, saddr)
                            except Exception: pass
                            continue
                        if pt in ["ACK", "PING", "HELLO", "JOIN_MATCH"]:
                            if pt == "HELLO" and ack_state == "waiting_for_hello_reply":
                                _, reply = await reply_for(fr, udkb, match_code, ack_style="short")
                                if reply: await loop.sock_sendto(sock, reply, saddr)
                                ack_state = "ack_sent_waiting"
                            elif pt == "ACK":
                                if ack_state == "waiting_for_hello_reply":
                                    _, reply = await reply_for(fr, udkb, match_code)
                                    if reply: await loop.sock_sendto(sock, reply, saddr)
                                    ack_state = "ready_to_send_thunder"
                                elif ack_state == "ack_sent_waiting":
                                    ack_state = "ready_to_send_thunder"
                                else:
                                    _, reply = await reply_for(fr, udkb, match_code)
                                    if reply: await loop.sock_sendto(sock, reply, saddr)
                            elif pt == "PING":
                                _, reply = await reply_for(fr, udkb, match_code)
                                if reply: await loop.sock_sendto(sock, reply, saddr)
                            elif pt == "JOIN_MATCH" and not join_match_received:
                                _, reply = await reply_for(fr, udkb, match_code)
                                if reply:
                                    await loop.sock_sendto(sock, reply, saddr)
                                    join_match_received = True
            except asyncio.TimeoutError:
                if ack_state == "ready_to_send_thunder" and not thunder_sent:
                    await _send_thunder()
                elif ack_state == "waiting_for_hello_reply":
                    if (time.time() - last_activity) > 7.0:
                        try:
                            pkt = await build_hello_packet(f"{account_id}_2585", udkb, match_code)
                            await loop.sock_sendto(sock, bytes.fromhex(pkt), (resolved_ip, port))
                        except Exception: pass
                        last_activity = time.time()
                    if (time.time() - match_start_time) > 30.0:
                        print_warning(f"[MATCH #{match_index}] handshake timeout"); break
                elif ack_state == "thunder_sharma_sent":
                    if (time.time() - last_activity) > MATCH_SILENCE_EXIT:
                        print_warning(f"[MATCH #{match_index}] silence {MATCH_SILENCE_EXIT}s — exiting")
                        completed_cleanly = True; break
            except (BlockingIOError, OSError):
                await asyncio.sleep(0.5); continue
            except Exception:
                await asyncio.sleep(0.5); continue
            if ack_state == "ready_to_send_thunder" and not thunder_sent:
                await _send_thunder()
        return f"match #{match_index} finished"
    except Exception as e:
        print_error(f"[MATCH #{match_index}] {e}")
        return f"match #{match_index} error"
    finally:
        if completed_cleanly:
            try:
                bot_state.increment_match(uid_str)
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
            rem = _match_counters.get(uid_str, 0)
            bot_state.update_status(uid_str, "ONLINE" if rem == 0 else "IN_MATCH", rem)
        except Exception: pass

# ==================== FUNCTIONAL LOOP ====================
async def functional_lone_wolf(addrs, starter_packet, account_region, client_version,
                                key, iv, account_id="", account_data=None, max_reconnects=10):
    reconnects = 0
    ip, port = addrs.split(":")
    play_matches: List[asyncio.Task] = []
    uid_str = str(account_id)
    current_token = starter_packet
    current_key = key; current_iv = iv
    current_account_data = account_data
    _writer_ref = {"w": None}
    local_team_state = await _get_team_state(uid_str)

    async def _process_social_packet(raw_bytes, tag="MAIN"):
        try:
            inner = bytes.fromhex(raw_bytes.hex()[10:])
            dec = decode_protobuf_dict(inner)
            if not dec or ("5" not in dec and 5 not in dec):
                alt = decode_protobuf_2(inner)
                if alt: dec = {str(k): {"data": v} for k, v in alt.items()}
            if not dec: return
            f5w = dec.get("5") or dec.get(5)
            f5 = f5w["data"] if isinstance(f5w, dict) and "data" in f5w else f5w
            if not isinstance(f5, dict): return
            def _f5g(key):
                v = f5.get(key) if key in f5 else f5.get(str(key))
                if isinstance(v, dict) and "data" in v: return v["data"]
                return v
            target_uid = _f5g(1)
            if not target_uid or not str(target_uid).isdigit(): return
            if _f5g(7) is None: return
            if not _accept_friend_request or not current_account_data: return
            j = current_account_data.get('token'); s = current_account_data.get('server_url')
            r = current_account_data.get('release_version'); o = current_account_data.get('account_id')
            if not (j and s and r and o): return
            await accept_friend_request(int(target_uid), int(o), j, s, r)
        except Exception: pass

    # ════ LEADER COORDINATOR ════
    async def _team_coordinator():
        try:
            my_group = await _assign_group(uid_str)
            my_acc_id = str(current_account_data.get("account_id", uid_str)) if current_account_data else uid_str
            await _squad_register_member(my_group, uid_str, my_acc_id)

            # wait until MIN_SQUAD_SIZE online (checking actual peers)
            waited = 0.0; extended = False
            while waited < TEAM_GROUP_TIMEOUT:
                if bot_state.is_paused(uid_str): return
                online = await _squad_online_members(my_group)
                online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
                if len(online_peers) >= MIN_SQUAD_SIZE and not extended:
                    extended = True
                    print_success(f"[TEAM] group {my_group} has {len(online_peers)} — extending {TEAM_FILL_WAIT}s")
                    await asyncio.sleep(TEAM_FILL_WAIT)
                    break
                await asyncio.sleep(1.0); waited += 1.0

            online = await _squad_online_members(my_group)
            online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
            if len(online_peers) < MIN_SQUAD_SIZE:
                print_warning(f"[TEAM] group {my_group} <{MIN_SQUAD_SIZE} online — skip")
                return

            # pick deterministic leader
            leader = await _choose_group_leader(my_group, online_peers)
            if leader != uid_str:
                print_info(f"[TEAM] {uid_str} → member, leader={leader}")
                return

            await asyncio.sleep(TEAM_READY_DELAY)
            own_id = current_account_data.get('account_id') if current_account_data else None
            if not own_id:
                try: own_id = int(uid_str)
                except Exception: own_id = 0

            def _ok():
                return _writer_ref["w"] and not _writer_ref["w"].is_closing()

            async def _send(pkt, tag):
                try:
                    if _ok():
                        _writer_ref["w"].write(pkt); await _writer_ref["w"].drain()
                        return True
                except Exception: pass
                return False

            print_success(f"[TEAM] 👑 group {my_group} leader {uid_str} creating team ({len(online_peers)})")
            await _send(create_team(current_key, current_iv, client_version), "create_team")
            await asyncio.sleep(1.2)
            await _send(team_fresh(int(own_id), current_key, current_iv), "team_fresh#1")
            await asyncio.sleep(1.0)

            targets = []
            for peer_uid in online_peers:
                if peer_uid == uid_str: continue
                p_info = local_team_state["peers"].get(peer_uid)
                p_acc = None
                if p_info:
                    try: p_acc = p_info["data"].get("account_id")
                    except Exception: pass
                if not p_acc: p_acc = peer_uid
                targets.append(int(p_acc))

            for r in range(3):
                for tgt in targets:
                    await _send(invite_player_in_team(tgt, current_key, current_iv), f"inv→{tgt} r{r+1}")
                    await asyncio.sleep(0.4)
                await asyncio.sleep(1.0)

            await asyncio.sleep(TEAM_INVITE_WAIT + 1.5)
            await _send(team_fresh(int(own_id), current_key, current_iv), "team_fresh#2")
            await asyncio.sleep(0.8)

            wt = 0.0
            while wt < 10.0:
                if local_team_state.get("team_code"): break
                await asyncio.sleep(0.5); wt += 0.5

            # FIRE start_match immediately + loop
            for attempt in range(TEAM_MATCH_LOOP_COUNT):
                if bot_state.is_paused(uid_str): return
                try:
                    sm = start_match_team(int(own_id), current_key, current_iv, region=account_region)
                    if _ok():
                        _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                        if attempt % 5 == 0:
                            print_info(f"[TEAM]   leader start_match #{attempt+1}")
                except Exception: pass
                await asyncio.sleep(TEAM_MATCH_LOOP_INTERVAL)

        except asyncio.CancelledError: raise
        except Exception as e: print_error(f"[TEAM] coordinator: {e}")

    # ════ MEMBER TRIGGER ════
    async def _member_trigger():
        try:
            my_group = await _my_group_index(uid_str)
            if my_group is None: return
            my_acc_id = str(current_account_data.get("account_id", uid_str)) if current_account_data else uid_str
            await _squad_register_member(my_group, uid_str, my_acc_id)

            waited = 0.0
            while waited < TEAM_GROUP_TIMEOUT:
                online = await _squad_online_members(my_group)
                online_peers = [u for u in online.keys() if u in local_team_state["peers"]]
                leader = await _group_leader(my_group)
                if leader and leader != uid_str and len(online_peers) >= MIN_SQUAD_SIZE:
                    break
                await asyncio.sleep(0.5); waited += 0.5

            leader = await _group_leader(my_group)
            if not leader or leader == uid_str: return

            await asyncio.sleep(TEAM_MEMBER_TRIGGER_DELAY)

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
        except asyncio.CancelledError: raise
        except Exception as e: print_warning(f"[TEAM] member: {e}")

    # ════════ MAIN LOOP ════════
    try:
        while True:
            while bot_state.is_paused(uid_str):
                try: bot_state.update_status(uid_str, "PAUSED", 0)
                except Exception: pass
                await asyncio.sleep(1.0)

            writer = None
            gateway_ping = None
            tc_task = None; mt_task = None
            try:
                if current_account_data:
                    fresh = None
                    if current_account_data.get('auth_type') == 'guest' and current_account_data.get('auth_uid'):
                        fresh = cache_get(str(current_account_data['auth_uid']))
                    if fresh:
                        current_account_data = fresh
                        current_key = fresh['aes_ak']; current_iv = fresh['iv_i']
                        current_token = await build_tcp_startup_packet(
                            fresh['account_id'], fresh['token'], fresh['server_time'],
                            current_key, current_iv,
                            region=fresh.get('region', account_region), typ='OnLine')
                    else:
                        raise ConnectionError("Cache expired")

                resolved_ip = await resolve_host_cloudflare(ip)
                reader, writer = await asyncio.open_connection(resolved_ip, int(port))
                bot_state.register_writer(uid_str, writer)
                _writer_ref["w"] = writer
                rs = writer.get_extra_info('socket')
                if rs: optimize_tcp_socket(rs)

                writer.write(bytes.fromhex(current_token)); await writer.drain()
                try:
                    ik = await send_keep_alive(account_region)
                    if ik and not writer.is_closing():
                        writer.write(ik)
                        await asyncio.wait_for(writer.drain(), timeout=3)
                except Exception: pass

                async def _gw_keepalive():
                    kb = await send_keep_alive(account_region)
                    while True:
                        await asyncio.sleep(5)
                        try:
                            if writer and not writer.is_closing():
                                writer.write(kb); await writer.drain()
                        except Exception: break

                gateway_ping = asyncio.create_task(_gw_keepalive())
                print_success(f"[✓] TCP Connected | {uid_str}")
                reconnects = 0

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

                if TEAM_MODE:
                    tc_task = asyncio.create_task(_team_coordinator())
                    mt_task = asyncio.create_task(_member_trigger())

                while True:
                    play_matches[:] = [m for m in play_matches if not m.done()]
                    if bot_state.is_paused(uid_str): break
                    try:
                        data = await asyncio.wait_for(reader.read(8192), timeout=0.5)
                    except asyncio.TimeoutError: continue
                    if not data: raise ConnectionError("Connection closed")
                    hd = data.hex(); pl = len(data)

                    if hd.startswith("0600") and pl > 20:
                        await _process_social_packet(data, tag="MAIN"); continue

                    if hd.startswith("0500") and pl > 10:
                        try:
                            inner = bytes.fromhex(hd[10:])
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
                                c = _f5g(fk)
                                if c and str(c).isdigit() and len(str(c)) == 7:
                                    tc = str(c); break
                            if tc: local_team_state["team_code"] = tc
                            gid = None
                            for fk in [8, 10, 12, 6]:
                                c = _f5g(fk)
                                if c and isinstance(c, str) and 20 <= len(c) <= 40:
                                    gid = c; break
                            if gid: local_team_state["group_id"] = gid

                            own_acc = str(current_account_data.get('account_id')) if current_account_data else None
                            my_group = await _my_group_index(uid_str)
                            leader = await _group_leader(my_group) if my_group is not None else None
                            is_leader = (leader == uid_str)

                            inviter = None
                            for fk in [1, 2, 3, 4, 6, 7, 13, 15, 20]:
                                c = _f5g(fk)
                                if c and str(c).isdigit() and 6 <= len(str(c)) <= 15:
                                    if str(c) != uid_str and str(c) != own_acc:
                                        inviter = c; break

                            if inviter and gid and not is_leader:
                                for _ in range(2):
                                    try:
                                        acc = accept_team_invite(int(inviter), gid, current_key, current_iv)
                                        if writer and not writer.is_closing():
                                            writer.write(acc); await writer.drain()
                                    except Exception: pass
                                    await asyncio.sleep(0.5)
                        except Exception: pass
                        continue

                    if hd.startswith("0300") and 10 < pl < 30: continue

                    if hd.startswith("0300") and pl >= 300:
                        print_success(f"[⚔] Match Found | {uid_str}")
                        try:
                            res = json.loads(await decode_protobuf_async(hd[10:]))
                            tok = udk = mc = sip = None
                            maid = bv = None
                            if '42' in res and 'data' in res['42']: mc = res['42']['data']
                            if '5' in res and 'data' in res['5']:
                                rf5 = res['5']['data']
                                sip = rf5.get('2', {}).get('data')
                                udk = rf5.get('3', {}).get('data')
                                tok = rf5.get('4', {}).get('data')
                                if '42' in rf5: mc = rf5['42']['data']
                            if '1' in res and 'data' in res['1']: maid = res['1']['data']
                            if '5' in res and 'data' in res['5']:
                                bv = res['5']['data'].get('1', {}).get('data')
                            eff = maid or account_id or "BD_BOT"
                            if tok and udk and mc and sip:
                                at = current_account_data.get('access_token', '') if current_account_data else ""
                                th, sh = await build_match_startup_packets(
                                    tok, udk, mc, eff, bv or 0, server_ip=sip,
                                    region=account_region, client_version=client_version,
                                    access_token=at, mode_id=1, map_id=1)
                                mi = await _inc_match(uid_str)
                                try:
                                    bot_state.increment_match_started()
                                    bot_state.update_status(uid_str, "IN_MATCH", 1)
                                except Exception: pass
                                nm = asyncio.create_task(play_game(sip, th, sh, udk, mc, eff, "BD",
                                    client_version, current_key, current_iv, match_index=mi))
                                play_matches.append(nm)

                                async def _drain():
                                    while not nm.done():
                                        try:
                                            d = await asyncio.wait_for(reader.read(4096), timeout=1.0)
                                            if not d: break
                                            gh = d.hex()
                                            if gh.startswith("0600") and len(d) > 20:
                                                await _process_social_packet(d, tag="DRAIN")
                                        except asyncio.TimeoutError: continue
                                        except Exception: break

                                dt = asyncio.create_task(_drain())
                                try: await nm
                                except Exception: pass
                                finally:
                                    dt.cancel()
                                    try: await dt
                                    except asyncio.CancelledError: pass

                                play_matches[:] = [m for m in play_matches if not m.done()]
                                print_info(f"[OFFLINE] Match #{mi} done — restarting in {NEW_MATCH_DELAY}s")
                                await asyncio.sleep(NEW_MATCH_DELAY)

                                local_team_state["team_code"] = None
                                local_team_state["group_id"] = None

                                for tk in (tc_task, mt_task):
                                    if tk and not tk.done():
                                        tk.cancel()
                                        try: await tk
                                        except asyncio.CancelledError: pass

                                await _squad_set_state(my_group if my_group is not None else 0, "forming")
                                tc_task = asyncio.create_task(_team_coordinator())
                                mt_task = asyncio.create_task(_member_trigger())
                                print_success(f"[TEAM] 🔁 re-squad after match #{mi}")
                                continue
                        except Exception as e:
                            print_warning(f"[MATCH] {e}"); continue

                    if 30 <= pl <= 40: continue

            except asyncio.CancelledError: raise
            except Exception as e:
                if "Cache expired" in str(e):
                    print_warning(f"Token expired {uid_str}"); break
                reconnects += 1
                if reconnects > max_reconnects:
                    if current_account_data:
                        try:
                            if current_account_data.get('auth_uid'):
                                cache_invalidate(str(current_account_data['auth_uid']))
                        except Exception: pass
                    reconnects = 0; break
                print_warning(f"[{uid_str}] reconnect #{reconnects}: {e}")
                await asyncio.sleep(min(reconnects * 0.5, 2.0))
            finally:
                local_team_state["peers"].pop(uid_str, None)
                async with _TEAM_STATE_LOCK:
                    for ou, os_ in _TEAM_STATES.items():
                        if ou == uid_str: continue
                        os_["peers"].pop(uid_str, None)
                try:
                    g = await _my_group_index(uid_str)
                    if g is not None: await _squad_unregister_member(g, uid_str)
                except Exception: pass
                for tk in (tc_task, mt_task):
                    if tk and not tk.done():
                        tk.cancel()
                        try: await tk
                        except asyncio.CancelledError: pass
                if gateway_ping: gateway_ping.cancel()
                if writer:
                    bot_state.unregister_writer(uid_str, writer)
                    await safe_close_writer(writer)
    except asyncio.CancelledError: raise
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
        writer = None; ping_task = None
        try:
            rip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.open_connection(rip, int(port))
            if uid_str: bot_state.register_writer(uid_str, writer)
            rs = writer.get_extra_info('socket')
            if rs: optimize_tcp_socket(rs)
            writer.write(bytes.fromhex(starter_packet)); await writer.drain()
            reconnects = 0
            try:
                ik = await send_keep_alive(region)
                if ik and not writer.is_closing():
                    writer.write(ik)
                    await asyncio.wait_for(writer.drain(), timeout=3)
            except Exception: pass

            async def _ik():
                kb = await send_keep_alive(region)
                while True:
                    await asyncio.sleep(5)
                    try:
                        if writer and not writer.is_closing():
                            writer.write(kb); await writer.drain()
                    except Exception: break

            ping_task = asyncio.create_task(_ik())
            while True:
                if uid_str and bot_state.is_paused(uid_str):
                    if ping_task: ping_task.cancel()
                    if uid_str: bot_state.unregister_writer(uid_str, writer)
                    await safe_close_writer(writer); writer = None
                    while bot_state.is_paused(uid_str):
                        await asyncio.sleep(1.0)
                    break
                try:
                    d = await asyncio.wait_for(reader.read(8192), timeout=1.0)
                except asyncio.TimeoutError: continue
                if not d: raise ConnectionError("closed")
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
            else: await asyncio.sleep(1)

# ==================== ACCOUNT PROCESSORS ====================
def _register_credentials(ad):
    try:
        ai = str(ad['account_id'])
        bot_state.account_credentials[ai] = ad
        if ad.get('auth_uid'): bot_state.account_credentials[str(ad['auth_uid'])] = ad
    except Exception: pass

async def refresh_account_profile(ad):
    try:
        if isinstance(ad, str): ad = bot_state.account_credentials.get(str(ad))
        if not ad: return
        t = ad.get('token'); ai = ad.get('account_id')
        s = ad.get('server_url'); r = ad.get('release_version')
        if not (t and ai and s and r): return
        d = await get_player_personal_show(int(ai), t, s, r)
        if not d: return
        pd = d.get(1, {}) if isinstance(d.get(1), dict) else {}
        ce = pd.get(7)
        if ce is None: return
        try: ce = int(ce); cl = int(pd.get(6) or 1)
        except Exception: return
        ai_str = str(ai)
        if ai_str in bot_state.accounts:
            bot_state.update_exp(ai_str, ce, cl)
    except Exception: pass

async def process_account_uid_pass(uid, password):
    cached = cache_get(uid)
    if cached:
        ai = str(cached['account_id']); nk = cached.get('nickname', f"P_{ai}")
        bot_state.register_account(uid=ai, nickname=nk, region=cached.get('region', 'BD'),
            level=cached.get('level', 1), exp=cached.get('exp', 0), likes=0, auth_uid=str(uid))
        _register_credentials(cached)
        return cached
    print_info(f"[LOGIN] {uid}…")
    try:
        async with _LOGIN_SEMAPHORE:
            vc = await version_config()
            if vc is None: return None
            rel, cv, srv = vc
            tg = await get_access_token(uid, password)
            if tg is None: return None
            oid, at, plat = tg
            mp, lp = await build_majorlogin_payload(oid, at, plat, cv)
            if not mp or not lp: return None
            rj = await major_login(mp, srv, rel)
            if not rj or rj.get("__SHORT_RESPONSE__"): return None
            def _g(key):
                v = rj.get(str(key))
                if isinstance(v, dict) and "data" in v: return v["data"]
                if key in rj and not isinstance(rj[key], dict): return rj[key]
                if isinstance(v, dict): return v.get("data")
                return None
            ai_raw = _g(1); reg_raw = _g(2) or "BD"
            jwt = _g(8); srv_raw = _g(10); st = _g(21)
            ak, ivv = _extract_key_iv(rj)
            if not jwt or not srv_raw or not ak or not ivv: return None
            url_raw = srv_raw
            gj = await get_login_data(lp, jwt, url_raw, rel)
            if not gj: return None
        def _gf(f, d=None):
            v = gj.get(str(f), {}).get("data")
            return v if v is not None else d
        lvl = int(_gf(6, 1) or 1); ex = int(_gf(7, 0) or 0); lk = int(_gf(8, 0) or 0)
        nk = _gf(4, f"P_{ai_raw}") or f"P_{ai_raw}"
        reg = reg_raw or _gf(3, "BD") or "BD"
        ai = str(ai_raw)
        bot_state.register_account(uid=ai, nickname=nk, region=reg, level=lvl,
            exp=ex, likes=lk, auth_uid=str(uid))
        print_success(f"[✓] {ai} | {nk}")
        ad = {
            'account_id': ai_raw, 'nickname': nk, 'region': reg,
            'level': lvl, 'exp': ex, 'likes': lk, 'open_id': oid,
            'access_token': at, 'platform': str(plat),
            'token': jwt, 'server_time': st,
            'aes_ak': ak, 'iv_i': ivv,
            'functional_addrs': _gf(14), 'informational_addrs': _gf(32),
            'release_version': rel, 'client_version': cv,
            'server_url': url_raw, 'login_payload_data': lp,
            'auth_type': 'guest', 'auth_uid': uid, 'auth_password': password,
        }
        _register_credentials(ad)
        cache_set(uid, ad)
        return ad
    except Exception as e:
        print_error(f"process login {uid}: {e}"); return None

async def run_account_worker(ad, label):
    ai = str(ad['account_id'])
    info_t = None; exp_t = None
    try:
        reg = ad.get('region', 'BD')
        tcp_online = await build_tcp_startup_packet(ad['account_id'], ad['token'],
            ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='OnLine')
        tcp_chat = await build_tcp_startup_packet(ad['account_id'], ad['token'],
            ad['server_time'], ad['aes_ak'], ad['iv_i'], region=reg, typ='ChaT')

        # ── CLAN JOIN FIRST ──
        if AUTO_JOIN_CLAN and CLAN_ID:
            ok = await join_clan(ad['token'], CLAN_ID)
            print_success(f"[CLAN] {ai} joined") if ok else print_warning(f"[CLAN] {ai} failed")

        info_t = asyncio.create_task(informational(ad['informational_addrs'], tcp_chat,
            ad['aes_ak'], ad['iv_i'], region=reg, account_id=ai, account_data=ad))

        async def _exp_loop():
            while True:
                await asyncio.sleep(120)
                f = bot_state.account_credentials.get(ai)
                if f: await refresh_account_profile(f)
        exp_t = asyncio.create_task(_exp_loop())

        ft = asyncio.create_task(functional_lone_wolf(ad['functional_addrs'], tcp_online,
            ad['region'], ad['client_version'], ad['aes_ak'], ad['iv_i'],
            account_id=ai, account_data=ad))
        await ft
    except asyncio.CancelledError: raise
    except Exception as e: print_error(f"run_account_worker {label}: {e}")
    finally:
        for t in (info_t, exp_t):
            if t and not t.done(): t.cancel()
        for t in (info_t, exp_t):
            if t:
                try: await t
                except (asyncio.CancelledError, Exception): pass

async def account_loop_guest(uid, password):
    us = str(uid)
    bot_state.account_workers[us] = asyncio.current_task()
    ai = None
    while True:
        try:
            try: bot_state.update_status(us, "CONNECTING")
            except Exception: pass
            ad = await process_account_uid_pass(us, password)
            if not ad:
                await asyncio.sleep(15); continue
            ai = str(ad['account_id'])
            bot_state.account_workers[ai] = asyncio.current_task()
            bot_state.account_workers[us] = asyncio.current_task()
            bot_state.auth_to_game_id[us] = ai
            bot_state.game_to_auth_id[ai] = us
            await run_account_worker(ad, us)
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            try:
                bot_state.update_status(us, "OFFLINE")
                if ai: bot_state.update_status(ai, "OFFLINE")
            except Exception: pass
            break
        except Exception as e:
            print_error(f"acct_loop {us}: {e}")
            await asyncio.sleep(10)

# ==================== LOAD ====================
def load_accounts():
    accs = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, list): accs = d
        except Exception as e: print_error(f"load: {e}")
    return accs

# ==================== MAIN ====================
async def main():
    print_colored("╔══════════════════════════════════════════════════╗", Colors.CYAN)
    print_colored("║  ⚡ SQUAD MODE — 2-4 MIN, 1s RESTART, AUTO CLAN ⚡║", Colors.CYAN)
    print_colored("╚══════════════════════════════════════════════════╝", Colors.CYAN)

    try:
        await start_web_dashboard(host=WEB_HOST, port=WEB_PORT)
        print_success(f"[✓] Dashboard on :{WEB_PORT}")
    except Exception as e: print_error(f"dashboard: {e}")

    if HARDCODED_ACCOUNTS:
        try:
            clean = [{"uid": str(a["uid"]).strip(), "password": str(a["password"]).strip()}
                     for a in HARDCODED_ACCOUNTS if a.get("uid") and a.get("password")]
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                json.dump(clean, f, indent=2, ensure_ascii=False)
            print_success(f"[TEAM] wrote {len(clean)} accounts")
        except Exception as e: print_error(f"write: {e}")

    sync_devices_with_accounts()
    accounts = load_accounts()
    if not accounts: print_warning("[!] no accounts"); return
    print_success(f"[✓] {len(accounts)} accounts")

    # pre-assign groups: 0..3 → 0, 4..7 → 1, etc
    for i, acc in enumerate(accounts):
        u = str(acc.get("uid", "")).strip()
        if u:
            g = await _assign_group(u)
            print_info(f"[GRP] {u} → group {g}")

    for i, acc in enumerate(accounts):
        u = str(acc.get("uid", "")).strip(); p = str(acc.get("password", "")).strip()
        if u and p:
            t = asyncio.create_task(account_loop_guest(u, p))
            bot_state.account_workers[u] = t
        await asyncio.sleep(0.5)

    try:
        while True: await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print_warning("\nshutting down…")
        for t in list(bot_state.account_workers.values()): t.cancel()
        await asyncio.gather(*bot_state.account_workers.values(), return_exceptions=True)

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print_warning("\nstopped")
