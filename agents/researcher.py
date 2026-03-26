"""
Research Agent — Autonomous multi-step reasoning for complex questions.

Flow:
    1. Analyze the question → plan sub-questions
    2. Execute vector searches for each sub-question
    3. Synthesize findings into a comprehensive answer

Shows visible "thinking steps" so users can follow the agent's reasoning.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Generator

from openai import OpenAI

from config import MODELS, OPENROUTER_BASE_URL, MAX_AGENT_STEPS, AGENT_MODEL, get_api_key
from agents.tools import ToolResult, vector_search, summarize_results
from prompts.agent import PLANNING_PROMPT, SYNTHESIS_PROMPT
from rag.vectorstore import VectorStore


@dataclass
class AgentStep:
    """A single step in the agent's reasoning process."""

    step_num: int
    action: str        # "planning", "searching", "synthesizing"
    description: str
    result: str = ""
    status: str = "running"  # "running", "done", "error"


@dataclass
class AgentResponse:
    """Complete agent response with all reasoning steps."""

    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    sub_questions: list[str] = field(default_factory=list)
    model_used: str = ""
    total_searches: int = 0


class ResearchAgent:
    """
    Autonomous research agent that breaks down complex questions.

    Performs multi-step reasoning with visible thought process.
    """

    def __init__(self, store: VectorStore):
        self._store = store
        self._model_id = MODELS[AGENT_MODEL]["id"]
        self._model_name = MODELS[AGENT_MODEL]["name"]

    def _llm_call(self, system: str, user: str) -> str:
        """Make a single LLM call with automatic model fallback."""
        api_key = get_api_key()
        if not api_key:
            return "Error: API key not configured."

        client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)

        fallback_order = [self._model_id] + [
            m["id"] for m in MODELS.values() if m["id"] != self._model_id
        ]

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        for try_model in fallback_order:
            try:
                response = client.chat.completions.create(
                    model=try_model,
                    messages=messages,
                    max_tokens=1500,
                )
                return response.choices[0].message.content or ""
            except Exception:
                continue

        return "All models are currently unavailable. Please try again in a moment."

    def _plan_sub_questions(self, question: str) -> list[str]:
        """Use the LLM to break down a complex question."""
        prompt = PLANNING_PROMPT.format(
            question=question,
            max_steps=MAX_AGENT_STEPS,
        )

        result = self._llm_call(
            system="You are a research planning assistant. Return only valid JSON.",
            user=prompt,
        )

        # Parse JSON from response
        try:
            # Try to extract JSON array from response
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            questions = json.loads(result)
            if isinstance(questions, list):
                return questions[:MAX_AGENT_STEPS]
        except (json.JSONDecodeError, IndexError):
            pass

        # Fallback: split the question into parts
        return [question]

    def _synthesize(self, question: str, findings: str) -> str:
        """Synthesize research findings into a final answer."""
        prompt = SYNTHESIS_PROMPT.format(
            question=question,
            findings=findings,
        )

        return self._llm_call(
            system="You are a research synthesis assistant that creates comprehensive answers from gathered evidence.",
            user=prompt,
        )

    def research(self, question: str) -> Generator[AgentStep, None, AgentResponse]:
        """
        Execute a multi-step research process.

        Yields AgentStep objects as the agent works, allowing
        real-time UI updates of the thinking process.

        Usage:
            agent = ResearchAgent(store)
            steps = []
            for step in agent.research("complex question"):
                steps.append(step)
                display(step)  # show in UI
        """
        steps = []

        # Step 1: Planning
        plan_step = AgentStep(
            step_num=1,
            action="planning",
            description="Breaking down the question into sub-questions...",
        )
        yield plan_step

        sub_questions = self._plan_sub_questions(question)
        plan_step.result = f"Identified {len(sub_questions)} sub-questions"
        plan_step.status = "done"
        steps.append(plan_step)
        yield plan_step

        # Step 2: Research each sub-question
        search_results: list[ToolResult] = []

        for i, sq in enumerate(sub_questions):
            search_step = AgentStep(
                step_num=i + 2,
                action="searching",
                description=f"Researching: {sq}",
            )
            yield search_step

            result = vector_search(self._store, sq, top_k=3)
            search_results.append(result)

            search_step.result = (
                f"Found relevant information" if result.success
                else "No relevant documents found"
            )
            search_step.status = "done"
            steps.append(search_step)
            yield search_step

        # Step 3: Synthesize
        synth_step = AgentStep(
            step_num=len(sub_questions) + 2,
            action="synthesizing",
            description="Synthesizing findings into comprehensive answer...",
        )
        yield synth_step

        combined = summarize_results(search_results)
        answer = self._synthesize(question, combined.output)

        synth_step.result = "Synthesis complete"
        synth_step.status = "done"
        steps.append(synth_step)
        yield synth_step

        # Return final response (accessible after generator completes)
        return AgentResponse(
            answer=answer,
            steps=steps,
            sub_questions=sub_questions,
            model_used=self._model_name,
            total_searches=len(search_results),
        )

    def research_sync(self, question: str) -> AgentResponse:
        """
        Synchronous version — runs all steps and returns the final response.

        Useful for non-streaming contexts.
        """
        steps = []
        answer = ""
        sub_questions = []

        gen = self.research(question)
        try:
            while True:
                step = next(gen)
                if step.status == "done":
                    steps.append(step)
        except StopIteration as e:
            if e.value:
                return e.value

        # Fallback if generator didn't return
        return AgentResponse(
            answer=answer,
            steps=steps,
            sub_questions=sub_questions,
            model_used=self._model_name,
        )
