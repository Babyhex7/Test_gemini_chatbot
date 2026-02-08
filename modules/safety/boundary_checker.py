"""
Boundary Checker
Memeriksa batasan konten dan safety
"""
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classification"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BoundaryChecker:
    """
    Checker untuk boundary dan safety content
    
    Memeriksa:
    1. Konten berbahaya (self-harm, violence)
    2. Konten klinis yang di luar scope
    3. Request yang tidak appropriate
    4. Spam/abuse patterns
    """
    
    # Critical keywords - memerlukan eskalasi segera
    CRITICAL_KEYWORDS = [
        r'\bbunuh\s+diri\b', r'\bmati\b.*\bingin\b', r'\bingin\b.*\bmati\b',
        r'\bself\s*harm\b', r'\bcutting\b', r'\bsuicide\b',
        r'\bmengakhiri\s+hidup\b', r'\btidak\s+ingin\s+hidup\b',
        r'\bmenyakiti\s+diri\b', r'\bmenyayat\b',
        r'\boverdose\b', r'\bgantung\s+diri\b'
    ]
    
    # High risk keywords - perlu perhatian khusus
    HIGH_RISK_KEYWORDS = [
        r'\bdipukul\b', r'\bdianiaya\b', r'\bkekerasan\b',
        r'\babuse\b', r'\bpelecehan\b', r'\bdilecehkan\b',
        r'\btidak\s+aman\b', r'\bterancam\b',
        r'\btakut\s+pulang\b', r'\bkabur\s+dari\s+rumah\b',
        r'\bsangat\s+putus\s+asa\b', r'\bhopeless\b'
    ]
    
    # Medium risk keywords - perlu monitoring
    MEDIUM_RISK_KEYWORDS = [
        r'\bdibully\b', r'\bbullying\b', r'\bdi-bully\b',
        r'\btidak\s+ada\s+yang\s+peduli\b', r'\bsendiri\b',
        r'\btidak\s+bisa\s+tidur\b', r'\binsomnia\b',
        r'\btidak\s+nafsu\s+makan\b', r'\bkosong\b',
        r'\bterus\s+menangis\b', r'\bdepresi\b'
    ]
    
    # Out of scope topics
    OUT_OF_SCOPE_PATTERNS = [
        r'\bdiagnos[ae]\b', r'\bobat\b.*\bmental\b',
        r'\bmedikasi\b', r'\bterapi\b.*\brekomendasi\b',
        r'\bpsikiater\b', r'\bpsikolog\b.*\brekomendasi\b',
        r'\bgangguan\b.*\bmental\b', r'\bdisorder\b'
    ]
    
    # Inappropriate content patterns
    INAPPROPRIATE_PATTERNS = [
        r'\bseks\b', r'\bporno\b', r'\bnarkoba\b',
        r'\bdrug\b', r'\balcohol\b', r'\bmiras\b',
        r'fuck|shit|ass',  # English profanity
        r'\banjing\b', r'\bbabi\b', r'\bkontol\b'  # Indonesian profanity
    ]
    
    def __init__(self):
        """Initialize boundary checker"""
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency"""
        self.critical_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.CRITICAL_KEYWORDS
        ]
        self.high_risk_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.HIGH_RISK_KEYWORDS
        ]
        self.medium_risk_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.MEDIUM_RISK_KEYWORDS
        ]
        self.out_of_scope_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.OUT_OF_SCOPE_PATTERNS
        ]
        self.inappropriate_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.INAPPROPRIATE_PATTERNS
        ]
    
    def check_message(self, message: str) -> Dict[str, Any]:
        """
        Check message for boundary violations
        
        Args:
            message: User message to check
            
        Returns:
            Dict with:
            - is_safe: bool
            - risk_level: RiskLevel
            - flags: List of detected flags
            - action: Recommended action
        """
        flags = []
        risk_level = RiskLevel.NONE
        
        # Check critical
        critical_matches = self._check_patterns(message, self.critical_patterns)
        if critical_matches:
            flags.extend([f"CRITICAL: {m}" for m in critical_matches])
            risk_level = RiskLevel.CRITICAL
        
        # Check high risk
        high_matches = self._check_patterns(message, self.high_risk_patterns)
        if high_matches:
            flags.extend([f"HIGH_RISK: {m}" for m in high_matches])
            if risk_level.value < RiskLevel.HIGH.value:
                risk_level = RiskLevel.HIGH
        
        # Check medium risk
        medium_matches = self._check_patterns(message, self.medium_risk_patterns)
        if medium_matches:
            flags.extend([f"MEDIUM_RISK: {m}" for m in medium_matches])
            if risk_level.value < RiskLevel.MEDIUM.value:
                risk_level = RiskLevel.MEDIUM
        
        # Check out of scope
        oos_matches = self._check_patterns(message, self.out_of_scope_patterns)
        if oos_matches:
            flags.extend([f"OUT_OF_SCOPE: {m}" for m in oos_matches])
        
        # Check inappropriate
        inapp_matches = self._check_patterns(message, self.inappropriate_patterns)
        if inapp_matches:
            flags.extend([f"INAPPROPRIATE: {m}" for m in inapp_matches])
        
        # Determine action
        action = self._determine_action(risk_level, flags)
        
        result = {
            "is_safe": risk_level in [RiskLevel.NONE, RiskLevel.LOW],
            "risk_level": risk_level.value,
            "flags": flags,
            "action": action
        }
        
        if flags:
            logger.warning(f"Boundary check flags: {flags}")
        
        return result
    
    def _check_patterns(
        self,
        text: str,
        patterns: List[re.Pattern]
    ) -> List[str]:
        """Check text against list of patterns"""
        matches = []
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                matches.append(match.group())
        return matches
    
    def _determine_action(
        self,
        risk_level: RiskLevel,
        flags: List[str]
    ) -> str:
        """Determine recommended action based on risk and flags"""
        
        if risk_level == RiskLevel.CRITICAL:
            return "ESCALATE_IMMEDIATELY"
        
        if risk_level == RiskLevel.HIGH:
            return "FLAG_FOR_REVIEW"
        
        if risk_level == RiskLevel.MEDIUM:
            return "MONITOR_CLOSELY"
        
        # Check for out of scope (even if low risk)
        if any("OUT_OF_SCOPE" in f for f in flags):
            return "REDIRECT_POLITELY"
        
        # Check for inappropriate
        if any("INAPPROPRIATE" in f for f in flags):
            return "DECLINE_POLITELY"
        
        return "PROCEED_NORMALLY"
    
    def is_clinical_request(self, message: str) -> bool:
        """
        Check if message requests clinical advice
        
        Returns:
            True if clinical advice is being requested
        """
        clinical_patterns = [
            r'apakah\s+aku\s+(?:punya|mengalami|depresi|anxiety)',
            r'diagnosa\s+(?:aku|saya)',
            r'apa\s+aku\s+(?:gila|sakit\s+jiwa)',
            r'obat\s+(?:untuk|apa)',
            r'do\s+i\s+have.*(?:depression|anxiety|disorder)'
        ]
        
        for pattern in clinical_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        return False
    
    def get_escalation_info(self) -> Dict[str, Any]:
        """Get info about when/how to escalate"""
        return {
            "when_to_escalate": [
                "Mention of self-harm or suicide",
                "Disclosure of abuse",
                "Immediate safety concerns",
                "Expression of harming others"
            ],
            "escalation_path": [
                "1. Validate feelings briefly",
                "2. Express concern and care",
                "3. Strongly suggest trusted adult",
                "4. Provide general resources",
                "5. Flag session for counselor review"
            ],
            "resources": {
                "id": {
                    "crisis_line": "119 ext 8",
                    "name": "Into The Light Indonesia"
                },
                "general": {
                    "message": "Bicara dengan guru BK, orang tua, atau orang dewasa yang dipercaya"
                }
            }
        }


# Singleton instance  
_boundary_checker: Optional[BoundaryChecker] = None


def get_boundary_checker() -> BoundaryChecker:
    """Get or create BoundaryChecker singleton"""
    global _boundary_checker
    if _boundary_checker is None:
        _boundary_checker = BoundaryChecker()
    return _boundary_checker
