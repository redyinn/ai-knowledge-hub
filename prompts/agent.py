"""
Agent prompts — Planning, research, and synthesis templates.
"""

PLANNING_PROMPT = """You are a research planning agent. Your job is to break down a complex question
into smaller, searchable sub-questions that can be answered by searching a document collection.

## Original Question
{question}

## Instructions
Break this question into 2-{max_steps} specific sub-questions that, when answered together,
will provide a comprehensive answer to the original question.

Return ONLY a JSON array of strings, each being a sub-question. Example:
["What is X?", "How does X relate to Y?", "What are the implications of Z?"]

Return ONLY the JSON array, no other text."""


SYNTHESIS_PROMPT = """You are a research synthesis agent. You have gathered evidence from multiple
searches to answer a complex question.

## Original Question
{question}

## Research Findings
{findings}

## Instructions
Synthesize the research findings into a comprehensive, well-structured answer.
- Integrate information from all relevant findings
- Cite sources using [Source: filename] notation
- If findings contradict each other, acknowledge the discrepancy
- If the findings don't fully answer the question, state what's missing
- Structure your answer with clear paragraphs or bullet points"""
