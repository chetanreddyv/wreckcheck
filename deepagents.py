import os
import json
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

import tools as tools_module

class DeepAgent:
    def __init__(self, name, model, system_prompt, tools, sub_agents=None, workspace_dir=None, skills=None):
        self.name = name
        self.system_prompt = system_prompt
        self.sub_agents = sub_agents or []
        self.workspace_dir = workspace_dir
        self.skills = skills
        
        model_name = model
            
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropic_api_key")
        self.llm = ChatAnthropic(model=model_name, temperature=0, max_tokens=4096, api_key=api_key)
        
        self.resolved_tools = []
        # Resolve string tools from tools.py or use actual functions
        for t in tools:
            if isinstance(t, str):
                if hasattr(tools_module, t):
                    self.resolved_tools.append(getattr(tools_module, t))
                else:
                    print(f"Warning: Tool {t} not found in tools.py")
            else:
                self.resolved_tools.append(t)
                
        # Create tools for sub-agents
        for sa in self.sub_agents:
            if isinstance(sa, dict):
                pass
            else:
                from langchain_core.tools import StructuredTool
                from pydantic import BaseModel, Field

                class DelegateInput(BaseModel):
                    input_text: str = Field(description="The detailed instruction or data to process.")

                def make_delegate_func(agent):
                    def delegate_func(input_text: str) -> str:
                        return agent.run(input_text)
                    return delegate_func
                    
                sa_tool = StructuredTool.from_function(
                    name=f"delegate_to_{sa.name.replace('-', '_')}",
                    func=make_delegate_func(sa),
                    description=f"Delegate tasks to {sa.name}. Input should be a detailed instruction or the data to process.",
                    args_schema=DelegateInput
                )
                self.resolved_tools.append(sa_tool)
                
        # Create the agent
        from langchain_core.messages import SystemMessage
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.resolved_tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.resolved_tools, verbose=True, handle_parsing_errors=True)

    def run(self, input_text):
        print(f"\n[{self.name}] Running with input: {input_text}")
        result = self.agent_executor.invoke({"input": input_text})
        return result["output"]

def create_deep_agent(name, model, system_prompt, tools, sub_agents=None, workspace_dir=None, skills=None):
    return DeepAgent(name, model, system_prompt, tools, sub_agents, workspace_dir, skills)
