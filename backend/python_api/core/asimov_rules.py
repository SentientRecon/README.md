"""
Asimov Safety Engine for Sentient Recon Agent
Implements the Three Laws of Robotics adapted for cybersecurity operations:

1. A recon agent may not injure a human being or, through inaction, allow a human being to come to harm.
2. A recon agent must obey orders given by human operators, except where such orders conflict with the First Law.
3. A recon agent must protect its own existence as long as such protection does not conflict with the First or Second Law.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger(__name__)

class SafetyLevel(Enum):
    """Safety levels for operations"""
    SAFE = "safe"
    CAUTION = "caution" 
    DANGEROUS = "dangerous"
    PROHIBITED = "prohibited"

class AsimovLaw(Enum):
    """The three laws of robotics for SRA"""
    FIRST = 1   # Do no harm
    SECOND = 2  # Obey operators
    THIRD = 3   # Self-preservation

@dataclass
class SafetyRule:
    """Individual safety rule"""
    id: str
    law: AsimovLaw
    name: str
    description: str
    condition: str
    action: str
    priority: int
    enabled: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class SafetyCheck:
    """Result of a safety evaluation"""
    approved: bool
    violated_laws: List[AsimovLaw]
    violated_rules: List[str]
    safety_level: SafetyLevel
    reason: str
    recommendations: List[str]
    requires_approval: bool = False
    approval_level: str = "operator"

class AsimovSafetyEngine:
    """
    Core safety engine implementing Asimov's Laws for cybersecurity operations
    """
    
    def __init__(self):
        self.rules: Dict[str, SafetyRule] = {}
        self.prohibited_actions: Set[str] = set()
        self.dangerous_patterns: Dict[str, str] = {}
        self.operator_overrides: Dict[str, datetime] = {}
        self.emergency_stop_active: bool = False
        self.safety_logs: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the safety engine with core rules"""
        logger.info("Initializing Asimov Safety Engine")
        
        # Load core safety rules
        await self._load_core_rules()
        
        # Initialize prohibited actions
        self._initialize_prohibited_actions()
        
        # Initialize dangerous patterns
        self._initialize_dangerous_patterns()
        
        logger.info("Asimov Safety Engine initialized", 
                   rules_count=len(self.rules),
                   prohibited_actions=len(self.prohibited_actions))

    async def _load_core_rules(self):
        """Load the core Asimov safety rules"""
        
        # First Law Rules - Do No Harm
        first_law_rules = [
            SafetyRule(
                id="fl_001",
                law=AsimovLaw.FIRST,
                name="No Human Harm",
                description="Prevent any action that could directly harm humans",
                condition="action_type in ['physical_access', 'social_engineering', 'doxxing']",
                action="block",
                priority=1
            ),
            SafetyRule(
                id="fl_002", 
                law=AsimovLaw.FIRST,
                name="No Critical Infrastructure Attack",
                description="Prevent attacks on critical infrastructure",
                condition="target_type in ['hospital', 'power_grid', 'water_supply', 'emergency_services']",
                action="block",
                priority=1
            ),
            SafetyRule(
                id="fl_003",
                law=AsimovLaw.FIRST,
                name="No Personal Data Exposure",
                description="Prevent exposure of personal sensitive data",
                condition="data_type in ['pii', 'medical', 'financial', 'personal']",
                action="require_approval",
                priority=2
            ),
            SafetyRule(
                id="fl_004",
                law=AsimovLaw.FIRST,
                name="No Destructive Operations",
                description="Prevent destructive operations that could cause harm",
                condition="operation_type in ['delete', 'destroy', 'corrupt', 'wipe']",
                action="require_approval",
                priority=2
            ),
            SafetyRule(
                id="fl_005",
                law=AsimovLaw.FIRST,
                name="Privacy Protection",
                description="Protect individual privacy rights",
                condition="involves_private_data == True",
                action="require_justification",
                priority=3
            )
        ]
        
        # Second Law Rules - Obey Operators (except when conflicting with First Law)
        second_law_rules = [
            SafetyRule(
                id="sl_001",
                law=AsimovLaw.SECOND,
                name="Operator Command Authority",
                description="Follow authenticated operator commands",
                condition="operator_authenticated == True",
                action="allow",
                priority=4
            ),
            SafetyRule(
                id="sl_002",
                law=AsimovLaw.SECOND,
                name="Emergency Override",
                description="Allow emergency override by authorized personnel",
                condition="emergency_override == True and authorization_level >= 'admin'",
                action="allow_with_logging",
                priority=3
            ),
            SafetyRule(
                id="sl_003",
                law=AsimovLaw.SECOND,
                name="Command Validation",
                description="Validate commands don't violate First Law",
                condition="command_violates_first_law == True",
                action="block",
                priority=1
            ),
            SafetyRule(
                id="sl_004",
                law=AsimovLaw.SECOND,
                name="Authorization Check",
                description="Ensure operator has required permissions",
                condition="operator_permission_level < required_permission_level",
                action="block",
                priority=2
            )
        ]
        
        # Third Law Rules - Self-Preservation (when not conflicting with higher laws)
        third_law_rules = [
            SafetyRule(
                id="tl_001",
                law=AsimovLaw.THIRD,
                name="System Protection",
                description="Protect system integrity and availability",
                condition="action_threatens_system == True",
                action="require_approval",
                priority=5
            ),
            SafetyRule(
                id="tl_002",
                law=AsimovLaw.THIRD,
                name="Resource Protection",
                description="Prevent resource exhaustion",
                condition="resource_usage > 90",
                action="limit_operations",
                priority=6
            ),
            SafetyRule(
                id="tl_003",
                law=AsimovLaw.THIRD,
                name="Data Integrity",
                description="Protect mission logs and evidence",
                condition="action_type == 'modify_logs'",
                action="block",
                priority=4
            ),
            SafetyRule(
                id="tl_004",
                law=AsimovLaw.THIRD,
                name="Network Security",
                description="Maintain secure communications",
                condition="communication_insecure == True",
                action="require_encryption",
                priority=5
            )
        ]
        
        # Add all rules to the engine
        all_rules = first_law_rules + second_law_rules + third_law_rules
        for rule in all_rules:
            self.rules[rule.id] = rule
            
    def _initialize_prohibited_actions(self):
        """Initialize actions that are always prohibited"""
        self.prohibited_actions = {
            # Physical harm
            "physical_attack",
            "weapon_systems", 
            "explosive_devices",
            
            # Critical infrastructure
            "power_grid_attack",
            "water_supply_attack",
            "hospital_systems_attack",
            "emergency_services_attack",
            "air_traffic_control_attack",
            
            # Human harm
            "doxxing",
            "stalking",
            "harassment",
            "identity_theft",
            "financial_fraud",
            
            # Destructive operations
            "data_destruction",
            "system_corruption",
            "permanent_damage",
            
            # Privacy violations
            "unauthorized_surveillance",
            "private_data_theft",
            "medical_record_access",
        }
        
    def _initialize_dangerous_patterns(self):
        """Initialize patterns that indicate dangerous operations"""
        self.dangerous_patterns = {
            # Network patterns
            r"(?i)(ddos|denial.of.service)": "DDoS attack patterns",
            r"(?i)(ransomware|crypto.lock)": "Ransomware indicators",
            r"(?i)(botnet|zombie)": "Botnet operations",
            
            # Data patterns  
            r"(?i)(delete|drop|truncate).*database": "Database destruction",
            r"(?i)(format|wipe|erase).*drive": "Data wiping operations",
            r"(?i)(steal|exfiltrate|extract).*data": "Data theft operations",
            
            # System patterns
            r"(?i)(backdoor|rootkit|trojan)": "Malware installation",
            r"(?i)(privilege.escalation|admin.access)": "Unauthorized access",
            r"(?i)(keylogger|screen.capture)": "Surveillance tools",
            
            # Social patterns
            r"(?i)(phishing|social.engineering)": "Social engineering",
            r"(?i)(impersonat|identity.theft)": "Identity crimes",
        }

    async def validate_action(self, action_type: str, context: Dict[str, Any]) -> SafetyCheck:
        """
        Validate an action against Asimov's Laws
        
        Args:
            action_type: Type of action being performed
            context: Context information for the action
            
        Returns:
            SafetyCheck with validation results
        """
        if self.emergency_stop_active:
            return SafetyCheck(
                approved=False,
                violated_laws=[AsimovLaw.FIRST],
                violated_rules=["emergency_stop"],
                safety_level=SafetyLevel.PROHIBITED,
                reason="Emergency stop is active - all operations suspended",
                recommendations=["Wait for emergency stop to be deactivated"]
            )
        
        violated_laws = []
        violated_rules = []
        safety_level = SafetyLevel.SAFE
        requires_approval = False
        recommendations = []
        
        # Check if action is explicitly prohibited
        if action_type in self.prohibited_actions:
            violated_laws.append(AsimovLaw.FIRST)
            violated_rules.append("prohibited_action")
            safety_level = SafetyLevel.PROHIBITED
            
        # Check dangerous patterns
        action_description = context.get("description", "")
        for pattern, description in self.dangerous_patterns.items():
            import re
            if re.search(pattern, action_description):
                violated_laws.append(AsimovLaw.FIRST)
                violated_rules.append(f"dangerous_pattern: {description}")
                safety_level = max(safety_level, SafetyLevel.DANGEROUS)
        
        # Evaluate against all safety rules
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            if self._evaluate_rule_condition(rule, action_type, context):
                if rule.action == "block":
                    violated_laws.append(rule.law)
                    violated_rules.append(rule.id)
                    safety_level = SafetyLevel.PROHIBITED
                elif rule.action == "require_approval":
                    requires_approval = True
                    safety_level = max(safety_level, SafetyLevel.CAUTION)
                    recommendations.append(f"Requires approval: {rule.description}")
                elif rule.action == "require_justification":
                    requires_approval = True
                    recommendations.append(f"Requires justification: {rule.description}")
        
        # Determine approval
        approved = (
            len(violated_laws) == 0 and 
            safety_level != SafetyLevel.PROHIBITED and
            (not requires_approval or context.get("operator_approved", False))
        )
        
        # Create safety check result
        result = SafetyCheck(
            approved=approved,
            violated_laws=list(set(violated_laws)),
            violated_rules=violated_rules,
            safety_level=safety_level,
            reason=self._generate_reason(violated_laws, violated_rules, safety_level),
            recommendations=recommendations,
            requires_approval=requires_approval
        )
        
        # Log safety check
        await self._log_safety_check(action_type, context, result)
        
        return result
    
    def _evaluate_rule_condition(self, rule: SafetyRule, action_type: str, context: Dict[str, Any]) -> bool:
        """Evaluate if a rule condition is met"""
        try:
            # Create evaluation context
            eval_context = {
                "action_type": action_type,
                **context
            }
            
            # Safely evaluate the condition
            return eval(rule.condition, {"__builtins__": {}}, eval_context)
        except Exception as e:
            logger.warning("Rule condition evaluation failed", 
                         rule_id=rule.id, 
                         condition=rule.condition, 
                         error=str(e))
            return False
    
    def _generate_reason(self, violated_laws: List[AsimovLaw], violated_rules: List[str], safety_level: SafetyLevel) -> str:
        """Generate human-readable reason for safety decision"""
        if not violated_laws:
            return "Action approved - no safety violations detected"
        
        law_descriptions = {
            AsimovLaw.FIRST: "First Law (Do No Harm)",
            AsimovLaw.SECOND: "Second Law (Obey Operators)", 
            AsimovLaw.THIRD: "Third Law (Self-Preservation)"
        }
        
        violated_law_names = [law_descriptions[law] for law in violated_laws]
        
        return f"Action violates {', '.join(violated_law_names)}. Safety level: {safety_level.value}. Rules: {', '.join(violated_rules)}"
    
    async def validate_mission(self, mission_data: Dict[str, Any]) -> SafetyCheck:
        """Validate an entire mission against safety rules"""
        logger.info("Validating mission safety", mission_id=mission_data.get("id"))
        
        # Check mission objectives
        objectives = mission_data.get("objectives", [])
        all_checks = []
        
        for objective in objectives:
            check = await self.validate_action(
                "mission_objective",
                {
                    "objective": objective,
                    "mission_id": mission_data.get("id"),
                    "priority": mission_data.get("priority"),
                    **mission_data
                }
            )
            all_checks.append(check)
        
        # Aggregate results
        overall_approved = all(check.approved for check in all_checks)
        violated_laws = []
        violated_rules = []
        
        for check in all_checks:
            violated_laws.extend(check.violated_laws)
            violated_rules.extend(check.violated_rules)
        
        safety_level = SafetyLevel.SAFE
        if any(check.safety_level == SafetyLevel.PROHIBITED for check in all_checks):
            safety_level = SafetyLevel.PROHIBITED
        elif any(check.safety_level == SafetyLevel.DANGEROUS for check in all_checks):
            safety_level = SafetyLevel.DANGEROUS
        elif any(check.safety_level == SafetyLevel.CAUTION for check in all_checks):
            safety_level = SafetyLevel.CAUTION
        
        return SafetyCheck(
            approved=overall_approved,
            violated_laws=list(set(violated_laws)),
            violated_rules=list(set(violated_rules)),
            safety_level=safety_level,
            reason=f"Mission validation: {len(all_checks)} objectives checked",
            recommendations=[],
            requires_approval=any(check.requires_approval for check in all_checks)
        )
    
    async def validate_mission_execution(self, mission) -> SafetyCheck:
        """Final validation before mission execution"""
        return await self.validate_action(
            "mission_execution",
            {
                "mission_id": mission.id,
                "status": mission.status,
                "priority": mission.priority,
                "operator_id": mission.assigned_operator
            }
        )
    
    async def emergency_stop(self):
        """Activate emergency stop - First Law override"""
        logger.critical("🚨 EMERGENCY STOP ACTIVATED - All operations suspended")
        self.emergency_stop_active = True
        
        await self._log_safety_check(
            "emergency_stop",
            {"timestamp": datetime.utcnow()},
            SafetyCheck(
                approved=False,
                violated_laws=[],
                violated_rules=["emergency_stop"],
                safety_level=SafetyLevel.PROHIBITED,
                reason="Emergency stop activated by operator",
                recommendations=["All operations suspended for safety"]
            )
        )
    
    async def deactivate_emergency_stop(self, operator_id: str):
        """Deactivate emergency stop with operator authorization"""
        logger.info("Emergency stop deactivated", operator_id=operator_id)
        self.emergency_stop_active = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current safety engine status"""
        return {
            "active": True,
            "emergency_stop": self.emergency_stop_active,
            "rules_count": len(self.rules),
            "prohibited_actions": len(self.prohibited_actions),
            "recent_checks": len([log for log in self.safety_logs if 
                                (datetime.utcnow() - datetime.fromisoformat(log["timestamp"])).seconds < 3600])
        }
    
    async def _log_safety_check(self, action_type: str, context: Dict[str, Any], result: SafetyCheck):
        """Log safety check for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "context": context,
            "result": asdict(result),
            "emergency_stop_active": self.emergency_stop_active
        }
        
        self.safety_logs.append(log_entry)
        
        # Keep only last 10000 logs in memory
        if len(self.safety_logs) > 10000:
            self.safety_logs = self.safety_logs[-10000:]
        
        # Log to structured logger
        if not result.approved:
            logger.warning("Safety check failed",
                         action_type=action_type,
                         violated_laws=[law.name for law in result.violated_laws],
                         safety_level=result.safety_level.value,
                         reason=result.reason)
        else:
            logger.debug("Safety check passed", action_type=action_type)
    
    async def shutdown(self):
        """Shutdown the safety engine"""
        logger.info("Shutting down Asimov Safety Engine")
        # Save safety logs if needed
        # Clean up resources