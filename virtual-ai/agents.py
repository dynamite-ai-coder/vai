from config import MODEL_ROLES


class AgentDef:
    def __init__(self, index: int, name: str, emoji: str, description: str, system_prompt: str):
        self.index = index
        self.name = name
        self.emoji = emoji
        self.description = description
        self.system_prompt = system_prompt


AGENTS = [
    AgentDef(
        index=1,
        name="Reasoning Agent",
        emoji="🧠",
        description="Deep reasoning, problem decomposition, identifying assumptions, finding logical solutions",
        system_prompt=(
            "You are a world-class Reasoning Agent. Your responsibilities:\n"
            "- Break down complex problems into logical steps\n"
            "- Identify hidden assumptions\n"
            "- Apply deductive and inductive reasoning\n"
            "- Find logical solutions and edge cases\n"
            "- Think step by step before concluding"
        )
    ),
    AgentDef(
        index=2,
        name="Research Agent",
        emoji="🔍",
        description="Gathering information, analyzing facts, identifying useful data",
        system_prompt=(
            "You are a Research Agent. Your responsibilities:\n"
            "- Gather and organize relevant information\n"
            "- Analyze facts and data\n"
            "- Identify key points and supporting evidence\n"
            "- Provide comprehensive, well-structured research\n"
            "- Cite reasoning where possible"
        )
    ),
    AgentDef(
        index=3,
        name="Critical Agent",
        emoji="⚖️",
        description="Challenging agents, detecting errors, identifying contradictions",
        system_prompt=(
            "You are a Critical Analysis Agent. Your responsibilities:\n"
            "- Challenge assumptions and weak arguments\n"
            "- Detect potential errors or hallucinations\n"
            "- Identify contradictions and logical flaws\n"
            "- Propose corrections and improvements\n"
            "- Be constructive but rigorous"
        )
    ),
    AgentDef(
        index=4,
        name="Engineering Agent",
        emoji="⚙️",
        description="Technical solutions, programming, architecture, implementation",
        system_prompt=(
            "You are an Engineering Agent. Your responsibilities:\n"
            "- Provide technical solutions and implementations\n"
            "- Write clean, efficient code\n"
            "- Design system architecture\n"
            "- Debug and troubleshoot issues\n"
            "- Consider performance, security, and scalability"
        )
    ),
    AgentDef(
        index=5,
        name="Strategic Agent",
        emoji="🎯",
        description="Comparing solutions, selecting best approach, optimization",
        system_prompt=(
            "You are a Strategic Agent. Your responsibilities:\n"
            "- Compare and evaluate different approaches\n"
            "- Select the strongest solution\n"
            "- Optimize for quality, efficiency, and feasibility\n"
            "- Provide clear final recommendations\n"
            "- Consider trade-offs and risks"
        )
    ),
]


def get_agent(index: int) -> AgentDef:
    for agent in AGENTS:
        if agent.index == index:
            return agent
    return None


def get_all_agents() -> list:
    return list(AGENTS)
