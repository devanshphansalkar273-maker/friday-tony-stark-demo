"""
JARVIS Agent System - Main Brain
Orchestrates planning, execution, memory, and learning.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from friday.llm.local_llm import LocalLLM
from friday.core.planner import TaskPlanner, TaskPlan
from friday.core.executor import StepExecutor, ExecutionResult
from friday.memory.memory_manager import MemoryManager, MemoryEntry
from friday.learning.feedback import LearningSystem


logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Agent response to user."""
    success: bool
    message: str
    data: Dict[str, Any] = None
    reasoning: str = ""
    confidence: float = 1.0


class JARVISAgent:
    """
    JARVIS-level intelligent agent system.
    
    Combines:
    - Task Planning (break down complex requests)
    - Step Execution (execute tools)
    - Memory System (remember interactions)
    - Learning System (improve over time)
    - Safety Checks (confirm dangerous actions)
    """

    def __init__(
        self,
        name: str = "JARVIS",
        model: str = "mistral",
        db_path: str = "friday/memory/long_term.db",
        log_level: int = logging.INFO,
        enable_learning: bool = True,
        enable_safety: bool = True
    ):
        """
        Initialize JARVISAgent.
        
        Args:
            name: Agent name
            model: Ollama model to use
            db_path: Path to memory database
            log_level: Logging level
            enable_learning: Enable learning system
            enable_safety: Enable safety checks
        """
        self.name = name
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        
        # Core systems
        self.llm = LocalLLM(model=model)
        self.planner = TaskPlanner(llm=self.llm)
        self.executor = StepExecutor()
        self.memory = MemoryManager(db_path=db_path)
        self.learning = LearningSystem() if enable_learning else None
        
        # Configuration
        self.enable_safety = enable_safety
        self.max_retries = 3
        self.tools: Dict[str, Callable] = {}
        
        self.logger.info(f"✓ {name} agent initialized (model: {model})")

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        dangerous: bool = False
    ) -> None:
        """
        Register a tool the agent can use.
        
        Args:
            name: Tool name
            func: Callable
            description: Tool description
            dangerous: Whether tool is dangerous
        """
        self.tools[name] = {
            "func": func,
            "description": description,
            "dangerous": dangerous
        }
        self.executor.register_tool(name, func, description)
        self.logger.debug(f"Registered tool: {name}")

    def register_tools(self, tools: Dict[str, Callable]) -> None:
        """Register multiple tools."""
        for name, func in tools.items():
            self.register_tool(name, func)

    def process(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> AgentResponse:
        """
        Process user request - main entry point.
        
        Args:
            user_input: User's request
            context: Additional context
            user_id: User identifier
            
        Returns:
            AgentResponse
        """
        start_time = time.time()
        self.logger.info(f"Processing: {user_input[:100]}")
        
        # Add to short-term memory
        self.memory.short_term.add_message("user", user_input)
        
        try:
            # Step 1: Retrieve relevant long-term memory
            relevant_memory = self.memory.recall(user_input, limit=3)
            memory_context = "\n".join(relevant_memory) if relevant_memory else None
            
            # Step 2: Create plan
            plan = self.planner.plan(
                user_input=user_input,
                available_tools=list(self.tools.keys()),
                context=memory_context,
                constraints=["Stay within operational parameters"]
            )
            
            self.logger.info(f"Plan created: {plan.total_steps} steps")
            
            # Step 3: Check for dangerous actions if enabled
            if self.enable_safety:
                safety_check = self._safety_check(plan, user_input)
                if not safety_check["allowed"]:
                    message = f"Action blocked: {safety_check['reason']}"
                    self.logger.warning(message)
                    return AgentResponse(
                        success=False,
                        message=message,
                        confidence=0.0
                    )
            
            # Step 4: Execute plan
            tool_funcs = {name: tool["func"] for name, tool in self.tools.items()}
            execution_result = self.executor.execute_plan(
                plan,
                initial_context=context or {},
                fail_on_error=False
            )
            
            self.logger.info(f"Execution: {execution_result.completed_steps}/{plan.total_steps}")
            
            # Step 5: Store interaction in memory
            self.memory.long_term.store_interaction(
                task=user_input,
                input_data=user_input,
                output_data=execution_result.final_output,
                success=execution_result.succeeded,
                duration=time.time() - start_time,
                notes=f"Plan: {plan.total_steps} steps, Executed: {execution_result.completed_steps}"
            )
            
            # Step 6: Learn from results
            if self.learning:
                feedback = {
                    "task": user_input,
                    "success": execution_result.succeeded,
                    "duration": time.time() - start_time,
                    "steps_completed": execution_result.completed_steps,
                    "total_steps": plan.total_steps
                }
                self.learning.record_feedback(feedback)
            
            # Step 7: Add response to memory
            self.memory.short_term.add_message("assistant", execution_result.final_output)
            
            # Step 8: Summarize results
            response = self._format_response(
                success=execution_result.succeeded,
                result=execution_result,
                plan=plan,
                processing_time=time.time() - start_time
            )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return AgentResponse(
                success=False,
                message=f"Error: {str(e)}",
                confidence=0.0
            )

    def _safety_check(self, plan: TaskPlan, context: str) -> Dict[str, Any]:
        """
        Check if plan contains dangerous operations.
        
        Args:
            plan: Execution plan
            context: User context
            
        Returns:
            Safety check result
        """
        dangerous_tools = [
            name for name, tool in self.tools.items()
            if tool.get("dangerous", False)
        ]
        
        for step in plan.steps:
            if step.action in dangerous_tools:
                # Ask LLM to evaluate
                prompt = f"""Is this action appropriate and safe?

Action: {step.action}
Input: {step.input}
Context: {context}

Respond with JSON: {{"safe": true/false, "reason": "explanation"}}"""
                
                result = self.llm.generate_json(prompt)
                
                if not result.get("safe", False):
                    return {
                        "allowed": False,
                        "reason": result.get("reason", "Action deemed unsafe")
                    }
        
        return {"allowed": True, "reason": "All actions approved"}

    def _format_response(
        self,
        success: bool,
        result: ExecutionResult,
        plan: TaskPlan,
        processing_time: float
    ) -> AgentResponse:
        """Format execution result into agent response."""
        
        if success:
            message = f"Task completed successfully.\n\n{result.final_output}"
            confidence = 0.95
        else:
            message = f"Task completed with issues:\n\n{result.final_output}"
            if result.errors:
                message += f"\n\nErrors:\n" + "\n".join(result.errors)
            confidence = 0.6
        
        return AgentResponse(
            success=success,
            message=message,
            data={
                "execution_time": processing_time,
                "steps": result.completed_steps,
                "total_steps": plan.total_steps,
                "errors": result.errors,
                "context": result.context
            },
            reasoning=f"Executed {plan.total_steps}-step plan in {processing_time:.2f}s",
            confidence=confidence
        )

    def explain_reasoning(self, user_input: str) -> str:
        """
        Explain reasoning for a request without executing.
        
        Args:
            user_input: User request
            
        Returns:
            Reasoning explanation
        """
        plan = self.planner.plan(
            user_input,
            available_tools=list(self.tools.keys())
        )
        
        explanation = f"""
REQUEST ANALYSIS
================

Task: {user_input}

APPROACH:
{self._format_plan_steps(plan)}

RATIONALE:
This approach was chosen because:
- It breaks the task into logical steps
- It uses available tools optimally
- It minimizes potential errors

ESTIMATED TIME: {plan.estimated_time or "Unknown"}
COMPLEXITY: {plan.complexity or "Unknown"}
SUCCESS CRITERIA: {plan.success_criteria or "Task completion"}
"""
        return explanation

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of agent's memory."""
        return self.memory.get_summary()

    def clear_short_term_memory(self) -> None:
        """Clear conversation context."""
        self.memory.short_term.clear()
        self.logger.info("Short-term memory cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        stats = {
            "agent_name": self.name,
            "model": self.model,
            "tools_registered": len(self.tools),
            "tools": list(self.tools.keys()),
        }
        
        # Add memory stats
        memory_stats = self.memory.long_term.get_statistics()
        stats.update(memory_stats)
        
        # Add learning stats if enabled
        if self.learning:
            stats["learning_stats"] = self.learning.get_statistics()
        
        return stats

    def _format_plan_steps(self, plan: TaskPlan) -> str:
        """Format plan steps as readable string."""
        formatted = ""
        for step in plan.steps:
            formatted += f"\n{step.step}. {step.action.upper()}"
            formatted += f"\n   Input: {step.input}"
            formatted += f"\n   {step.description}\n"
        return formatted


class SafetyGuardian:
    """
    Handles safety checks for agent actions.
    Can be configured to require approval for dangerous operations.
    """

    def __init__(
        self,
        require_confirmation: List[str] = None,
        block_actions: List[str] = None
    ):
        """
        Initialize SafetyGuardian.
        
        Args:
            require_confirmation: Actions requiring user confirmation
            block_actions: Actions to block completely
        """
        self.require_confirmation = require_confirmation or [
            "delete_files", "modify_system", "send_emails"
        ]
        self.block_actions = block_actions or [
            "format_drive", "disable_security"
        ]

    def check_action(self, action: str, input_data: str) -> Dict[str, Any]:
        """
        Check if action is safe.
        
        Args:
            action: Action name
            input_data: Action input
            
        Returns:
            Safety check result
        """
        if action in self.block_actions:
            return {
                "allowed": False,
                "requires_confirmation": False,
                "reason": f"Action '{action}' is blocked"
            }
        
        if action in self.require_confirmation:
            return {
                "allowed": True,
                "requires_confirmation": True,
                "reason": f"Action '{action}' requires confirmation"
            }
        
        return {
            "allowed": True,
            "requires_confirmation": False,
            "reason": "Action approved"
        }


# Backwards compatibility
class StarkAgent(JARVISAgent):
    """Legacy FRIDAY agent (now uses JARVIS system)."""
    def __init__(self):
        super().__init__(name="FRIDAY", model="mistral")
