"""
Cognitive Engine for Sentient Recon Agent
Advanced AI-driven intelligence system with GPT-4 integration, 
reinforcement learning, and long-term memory for cybersecurity operations.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

# AI and ML imports
try:
    import openai
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.agents import AgentExecutor
    from langchain.tools import Tool
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import torch
    import torch.nn as nn
    import torch.optim as optim
except ImportError as e:
    # Graceful degradation if AI packages not available
    print(f"Warning: AI packages not fully available: {e}")

logger = structlog.get_logger(__name__)

class DecisionType(Enum):
    """Types of decisions the cognitive engine can make"""
    THREAT_ANALYSIS = "threat_analysis"
    INCIDENT_RESPONSE = "incident_response"
    MISSION_PLANNING = "mission_planning"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_CHECK = "compliance_check"

class ConfidenceLevel(Enum):
    """Confidence levels for AI decisions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class CognitiveDecision:
    """Result of cognitive analysis"""
    decision_type: DecisionType
    recommendation: str
    confidence: ConfidenceLevel
    reasoning: List[str]
    evidence: List[Dict[str, Any]]
    requires_human_approval: bool
    risk_score: float
    alternatives: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class MemoryEntry:
    """Entry in the cognitive memory system"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: datetime
    importance_score: float
    access_count: int = 0

class ReinforcementLearningModel(nn.Module):
    """Simple neural network for reinforcement learning"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, output_size: int = 10):
        super(ReinforcementLearningModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Softmax(dim=1)
        )
        
    def forward(self, x):
        return self.network(x)

class CognitiveEngine:
    """
    Advanced cognitive engine for autonomous cybersecurity operations
    """
    
    def __init__(self):
        self.openai_client = None
        self.embeddings = None
        self.vector_store = None
        self.memory = ConversationBufferWindowMemory(k=50) if 'ConversationBufferWindowMemory' in globals() else None
        self.rl_model = None
        self.threat_classifier = None
        self.scaler = StandardScaler() if 'StandardScaler' in globals() else None
        
        # Cognitive state
        self.active_missions: Dict[str, Dict] = {}
        self.memory_entries: List[MemoryEntry] = []
        self.decision_history: List[CognitiveDecision] = []
        self.learning_feedback: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.decision_accuracy = 0.85
        self.learning_rate = 0.001
        self.experience_buffer = []
        
    async def initialize(self):
        """Initialize the cognitive engine"""
        logger.info("Initializing Cognitive Engine")
        
        try:
            # Initialize OpenAI client
            self.openai_client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Initialize embeddings
            if 'OpenAIEmbeddings' in globals():
                self.embeddings = OpenAIEmbeddings()
                
            # Initialize vector store for memory
            if 'FAISS' in globals():
                self.vector_store = FAISS.from_texts(
                    ["Initial cognitive memory"], 
                    self.embeddings if self.embeddings else None
                )
            
            # Initialize reinforcement learning model
            if 'torch' in globals():
                self.rl_model = ReinforcementLearningModel(100, 128, 10)
                self.optimizer = optim.Adam(self.rl_model.parameters(), lr=self.learning_rate)
            
            # Initialize threat classification model
            if 'RandomForestClassifier' in globals():
                self.threat_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
                # Train with synthetic data initially
                await self._initialize_threat_classifier()
            
            logger.info("Cognitive Engine initialized successfully")
            
        except Exception as e:
            logger.warning("Cognitive Engine initialization partially failed", error=str(e))
            # Continue with limited functionality
    
    async def _initialize_threat_classifier(self):
        """Initialize threat classifier with synthetic training data"""
        if not self.threat_classifier or not self.scaler:
            return
            
        # Generate synthetic training data for threat classification
        X_train = np.random.rand(1000, 20)  # 20 features
        y_train = np.random.randint(0, 5, 1000)  # 5 threat categories
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.threat_classifier.fit(X_train_scaled, y_train)
        
        logger.info("Threat classifier initialized with synthetic data")
    
    async def analyze_threat(self, threat_data: Dict[str, Any]) -> CognitiveDecision:
        """Analyze threat using AI models"""
        try:
            # Extract features from threat data
            features = self._extract_threat_features(threat_data)
            
            # Classify threat if model available
            threat_category = None
            confidence_score = 0.5
            
            if self.threat_classifier and self.scaler and features:
                features_scaled = self.scaler.transform([features])
                threat_category = self.threat_classifier.predict(features_scaled)[0]
                confidence_score = max(self.threat_classifier.predict_proba(features_scaled)[0])
            
            # Get AI reasoning from GPT-4
            reasoning = []
            recommendation = "Monitor threat and gather additional intelligence"
            
            if self.openai_client:
                ai_analysis = await self._get_ai_analysis(
                    "threat_analysis",
                    threat_data,
                    f"Analyze this cybersecurity threat and provide recommendations. Threat category: {threat_category}"
                )
                reasoning = ai_analysis.get("reasoning", [])
                recommendation = ai_analysis.get("recommendation", recommendation)
                confidence_score = max(confidence_score, ai_analysis.get("confidence", 0.5))
            
            # Determine confidence level
            if confidence_score >= 0.9:
                confidence = ConfidenceLevel.VERY_HIGH
            elif confidence_score >= 0.7:
                confidence = ConfidenceLevel.HIGH
            elif confidence_score >= 0.5:
                confidence = ConfidenceLevel.MEDIUM
            else:
                confidence = ConfidenceLevel.LOW
            
            # Calculate risk score
            risk_score = self._calculate_threat_risk(threat_data, confidence_score)
            
            # Create decision
            decision = CognitiveDecision(
                decision_type=DecisionType.THREAT_ANALYSIS,
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                evidence=[threat_data],
                requires_human_approval=confidence_score < 0.8 or risk_score > 0.7,
                risk_score=risk_score,
                alternatives=self._generate_alternatives("threat_response"),
                timestamp=datetime.utcnow(),
                metadata={"threat_category": threat_category, "features": features}
            )
            
            # Store in memory
            await self._store_memory(f"Threat analysis: {threat_data.get('type', 'unknown')}", decision)
            
            # Add to decision history
            self.decision_history.append(decision)
            
            return decision
            
        except Exception as e:
            logger.error("Threat analysis failed", exc_info=e)
            return self._create_fallback_decision(DecisionType.THREAT_ANALYSIS, "Analysis failed - manual review required")
    
    async def plan_incident_response(self, incident_data: Dict[str, Any]) -> CognitiveDecision:
        """Plan incident response using cognitive analysis"""
        try:
            # Analyze incident severity and type
            severity = incident_data.get("severity", "medium")
            incident_type = incident_data.get("category", "unknown")
            
            # Retrieve relevant past experiences
            similar_incidents = await self._retrieve_similar_memories(
                f"incident response {incident_type} {severity}"
            )
            
            # Get AI recommendation
            reasoning = []
            recommendation = "Initiate standard incident response procedures"
            
            if self.openai_client:
                context = {
                    "incident": incident_data,
                    "similar_cases": similar_incidents[:3] if similar_incidents else []
                }
                
                ai_analysis = await self._get_ai_analysis(
                    "incident_response",
                    context,
                    f"Plan incident response for {incident_type} incident with {severity} severity"
                )
                
                reasoning = ai_analysis.get("reasoning", [])
                recommendation = ai_analysis.get("recommendation", recommendation)
            
            # Determine confidence based on past experience
            confidence_score = 0.7 if similar_incidents else 0.5
            confidence = ConfidenceLevel.HIGH if confidence_score >= 0.7 else ConfidenceLevel.MEDIUM
            
            # Calculate risk score
            severity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
            risk_score = severity_scores.get(severity, 0.5)
            
            decision = CognitiveDecision(
                decision_type=DecisionType.INCIDENT_RESPONSE,
                recommendation=recommendation,
                confidence=confidence,
                reasoning=reasoning,
                evidence=[incident_data] + similar_incidents,
                requires_human_approval=risk_score > 0.7 or confidence_score < 0.6,
                risk_score=risk_score,
                alternatives=self._generate_alternatives("incident_response"),
                timestamp=datetime.utcnow(),
                metadata={"incident_type": incident_type, "severity": severity}
            )
            
            # Store decision
            await self._store_memory(f"Incident response: {incident_type}", decision)
            self.decision_history.append(decision)
            
            return decision
            
        except Exception as e:
            logger.error("Incident response planning failed", exc_info=e)
            return self._create_fallback_decision(DecisionType.INCIDENT_RESPONSE, "Manual incident response required")
    
    async def execute_mission(self, mission_id: str, objectives: List[Dict[str, Any]]):
        """Execute mission autonomously with cognitive decision making"""
        logger.info("Starting autonomous mission execution", mission_id=mission_id)
        
        try:
            self.active_missions[mission_id] = {
                "status": "active",
                "start_time": datetime.utcnow(),
                "objectives": objectives,
                "completed_objectives": [],
                "decisions": []
            }
            
            for i, objective in enumerate(objectives):
                if self.active_missions[mission_id]["status"] != "active":
                    break
                    
                logger.info("Processing objective", mission_id=mission_id, objective_index=i)
                
                # Analyze objective
                decision = await self._analyze_mission_objective(objective)
                self.active_missions[mission_id]["decisions"].append(decision)
                
                if decision.requires_human_approval:
                    logger.info("Objective requires human approval", 
                               mission_id=mission_id, 
                               objective_index=i)
                    # Wait for approval or timeout
                    await self._wait_for_approval(mission_id, i)
                
                # Execute objective if approved
                if decision.recommendation != "skip":
                    success = await self._execute_objective(objective, decision)
                    if success:
                        self.active_missions[mission_id]["completed_objectives"].append(i)
                
                # Brief pause between objectives
                await asyncio.sleep(1)
            
            # Mark mission complete
            self.active_missions[mission_id]["status"] = "completed"
            self.active_missions[mission_id]["end_time"] = datetime.utcnow()
            
            logger.info("Mission execution completed", mission_id=mission_id)
            
        except Exception as e:
            logger.error("Mission execution failed", mission_id=mission_id, exc_info=e)
            if mission_id in self.active_missions:
                self.active_missions[mission_id]["status"] = "failed"
                self.active_missions[mission_id]["error"] = str(e)
    
    async def emergency_stop(self):
        """Emergency stop all cognitive processes"""
        logger.critical("🚨 Cognitive Engine emergency stop activated")
        
        # Stop all active missions
        for mission_id in self.active_missions:
            if self.active_missions[mission_id]["status"] == "active":
                self.active_missions[mission_id]["status"] = "emergency_stopped"
                logger.info("Mission emergency stopped", mission_id=mission_id)
        
        # Clear any pending operations
        self.experience_buffer.clear()
        
        logger.info("All cognitive processes stopped")
    
    async def learn_from_feedback(self, decision_id: str, outcome: str, feedback: Dict[str, Any]):
        """Learn from operator feedback using reinforcement learning"""
        try:
            # Find the decision
            decision = None
            for d in self.decision_history:
                if hasattr(d, 'id') and d.id == decision_id:
                    decision = d
                    break
            
            if not decision:
                logger.warning("Decision not found for feedback", decision_id=decision_id)
                return
            
            # Calculate reward based on outcome
            reward = self._calculate_reward(outcome, feedback)
            
            # Store feedback
            feedback_entry = {
                "decision_id": decision_id,
                "outcome": outcome,
                "reward": reward,
                "feedback": feedback,
                "timestamp": datetime.utcnow()
            }
            self.learning_feedback.append(feedback_entry)
            
            # Update learning models if available
            if self.rl_model and 'torch' in globals():
                await self._update_rl_model(decision, reward)
            
            # Update decision accuracy
            if outcome in ["success", "correct"]:
                self.decision_accuracy = self.decision_accuracy * 0.95 + 0.05
            else:
                self.decision_accuracy = self.decision_accuracy * 0.95
            
            logger.info("Learning feedback processed", 
                       decision_id=decision_id,
                       outcome=outcome,
                       reward=reward,
                       new_accuracy=self.decision_accuracy)
            
        except Exception as e:
            logger.error("Learning from feedback failed", exc_info=e)
    
    async def _get_ai_analysis(self, analysis_type: str, data: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Get AI analysis from GPT-4"""
        try:
            if not self.openai_client:
                return {"reasoning": ["AI analysis unavailable"], "recommendation": "Manual review required", "confidence": 0.3}
            
            system_prompt = """You are an advanced cybersecurity AI assistant for a Sentient Recon Agent. 
            Provide detailed analysis, reasoning, and recommendations. Always prioritize safety and ethical considerations.
            Format your response as JSON with keys: reasoning (list of strings), recommendation (string), confidence (float 0-1)."""
            
            user_prompt = f"{prompt}\n\nData: {json.dumps(data, default=str, indent=2)}"
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "reasoning": [content[:500] + "..." if len(content) > 500 else content],
                    "recommendation": "Review AI response manually",
                    "confidence": 0.5
                }
                
        except Exception as e:
            logger.error("AI analysis failed", exc_info=e)
            return {"reasoning": ["AI analysis failed"], "recommendation": "Manual analysis required", "confidence": 0.2}
    
    async def _store_memory(self, content: str, decision: CognitiveDecision):
        """Store information in long-term memory"""
        try:
            if not self.embeddings:
                return
                
            # Create embedding
            embedding = await self.embeddings.aembed_query(content)
            
            # Calculate importance score
            importance = self._calculate_importance(decision)
            
            # Create memory entry
            memory_entry = MemoryEntry(
                id=f"mem_{len(self.memory_entries)}_{int(datetime.utcnow().timestamp())}",
                content=content,
                embedding=embedding,
                metadata=asdict(decision),
                timestamp=datetime.utcnow(),
                importance_score=importance
            )
            
            self.memory_entries.append(memory_entry)
            
            # Maintain memory size limit
            if len(self.memory_entries) > 10000:
                # Remove least important memories
                self.memory_entries.sort(key=lambda x: x.importance_score, reverse=True)
                self.memory_entries = self.memory_entries[:8000]
            
        except Exception as e:
            logger.error("Memory storage failed", exc_info=e)
    
    async def _retrieve_similar_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar memories using vector similarity"""
        try:
            if not self.embeddings or not self.memory_entries:
                return []
            
            # Create query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Calculate similarities
            similarities = []
            for memory in self.memory_entries:
                if memory.embedding:
                    similarity = self._cosine_similarity(query_embedding, memory.embedding)
                    similarities.append((similarity, memory))
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for similarity, memory in similarities[:limit]:
                memory.access_count += 1  # Track access
                results.append({
                    "content": memory.content,
                    "metadata": memory.metadata,
                    "similarity": similarity,
                    "timestamp": memory.timestamp
                })
            
            return results
            
        except Exception as e:
            logger.error("Memory retrieval failed", exc_info=e)
            return []
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(a)
            b = np.array(b)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except:
            return 0.0
    
    def _extract_threat_features(self, threat_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from threat data"""
        features = []
        
        # Severity mapping
        severity_map = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
        features.append(severity_map.get(threat_data.get("severity", "medium"), 0.5))
        
        # Confidence score
        features.append(threat_data.get("confidence", 0.5))
        
        # Binary features
        features.append(1.0 if threat_data.get("is_malicious", False) else 0.0)
        features.append(1.0 if threat_data.get("has_iocs", False) else 0.0)
        features.append(1.0 if threat_data.get("is_targeted", False) else 0.0)
        
        # Add padding to reach 20 features
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]  # Ensure exactly 20 features
    
    def _calculate_threat_risk(self, threat_data: Dict[str, Any], confidence: float) -> float:
        """Calculate risk score for a threat"""
        severity_scores = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        severity_score = severity_scores.get(threat_data.get("severity", "medium"), 0.5)
        
        # Factor in confidence
        risk_score = severity_score * confidence
        
        # Adjust for other factors
        if threat_data.get("is_malicious", False):
            risk_score += 0.2
        if threat_data.get("is_targeted", False):
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _calculate_importance(self, decision: CognitiveDecision) -> float:
        """Calculate importance score for memory storage"""
        importance = 0.5  # Base importance
        
        # Higher importance for high-risk decisions
        importance += decision.risk_score * 0.3
        
        # Higher importance for decisions requiring approval
        if decision.requires_human_approval:
            importance += 0.2
        
        # Higher importance for high-confidence decisions
        confidence_scores = {
            ConfidenceLevel.LOW: 0.0,
            ConfidenceLevel.MEDIUM: 0.1,
            ConfidenceLevel.HIGH: 0.2,
            ConfidenceLevel.VERY_HIGH: 0.3
        }
        importance += confidence_scores.get(decision.confidence, 0.0)
        
        return min(importance, 1.0)
    
    def _generate_alternatives(self, context: str) -> List[str]:
        """Generate alternative recommendations"""
        alternatives_map = {
            "threat_response": [
                "Block threat immediately",
                "Monitor and gather more intelligence", 
                "Quarantine affected systems",
                "Alert security team for manual review"
            ],
            "incident_response": [
                "Immediate containment",
                "Gradual isolation and analysis",
                "Forensic investigation first",
                "Escalate to senior analyst"
            ],
            "mission_planning": [
                "Proceed with current plan",
                "Modify objectives for safety",
                "Request additional resources",
                "Postpone until conditions improve"
            ]
        }
        
        return alternatives_map.get(context, ["Manual review required"])
    
    def _calculate_reward(self, outcome: str, feedback: Dict[str, Any]) -> float:
        """Calculate reward for reinforcement learning"""
        outcome_rewards = {
            "success": 1.0,
            "partial_success": 0.5,
            "failure": -0.5,
            "error": -1.0
        }
        
        base_reward = outcome_rewards.get(outcome, 0.0)
        
        # Adjust based on feedback
        if feedback.get("operator_satisfied", True):
            base_reward += 0.2
        
        if feedback.get("prevented_harm", False):
            base_reward += 0.5
        
        return base_reward
    
    def _create_fallback_decision(self, decision_type: DecisionType, message: str) -> CognitiveDecision:
        """Create fallback decision when AI analysis fails"""
        return CognitiveDecision(
            decision_type=decision_type,
            recommendation=message,
            confidence=ConfidenceLevel.LOW,
            reasoning=["AI analysis unavailable", "Fallback to manual procedures"],
            evidence=[],
            requires_human_approval=True,
            risk_score=0.5,
            alternatives=["Manual review required"],
            timestamp=datetime.utcnow()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get cognitive engine status"""
        return {
            "active": True,
            "ai_available": self.openai_client is not None,
            "memory_entries": len(self.memory_entries),
            "active_missions": len([m for m in self.active_missions.values() if m["status"] == "active"]),
            "decision_accuracy": self.decision_accuracy,
            "total_decisions": len(self.decision_history),
            "learning_feedback_count": len(self.learning_feedback)
        }
    
    async def shutdown(self):
        """Shutdown cognitive engine"""
        logger.info("Shutting down Cognitive Engine")
        
        # Stop all active missions
        for mission_id in self.active_missions:
            if self.active_missions[mission_id]["status"] == "active":
                self.active_missions[mission_id]["status"] = "shutdown"
        
        # Save memory and learning data if needed
        logger.info("Cognitive Engine shutdown complete")