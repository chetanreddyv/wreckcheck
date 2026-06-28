import os
import json
import uuid
import concurrent.futures
import importlib
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

import tools as tools_module

# Global ThreadPoolExecutor for async tasks
_task_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
_async_tasks = {}

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
            elif type(sa).__name__ == "AsyncSubAgent":
                class StartAsyncInput(BaseModel):
                    input_text: str = Field(description="The instruction for the async agent.")
                
                def make_start_func(agent_name):
                    def start_func(input_text: str) -> str:
                        task_id = str(uuid.uuid4())
                        
                        agent_mapping = {
                            "CodeSentinel": "code_sentinel",
                            "ArchitectReview": "arch_reviewer",
                            "HarnessGuard": "harness_guard"
                        }
                        
                        module_name = f"agents.{agent_mapping.get(agent_name)}"
                        module = importlib.import_module(module_name)
                        actual_agent = getattr(module, agent_mapping.get(agent_name))
                        
                        future = _task_executor.submit(actual_agent.run, input_text)
                        _async_tasks[task_id] = (future, agent_name)
                        return f"Task started for {agent_name}. Task ID: {task_id}"
                    return start_func
                
                sa_tool = StructuredTool.from_function(
                    name=f"start_async_task_{sa.name.replace('-', '_')}",
                    func=make_start_func(sa.name),
                    description=f"Start an async task for {sa.name}. Returns a Task ID.",
                    args_schema=StartAsyncInput
                )
                self.resolved_tools.append(sa_tool)
            else:
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
                
        # If there are any async sub-agents, add the wait tool
        if any(type(sa).__name__ == "AsyncSubAgent" for sa in self.sub_agents):
            class WaitAsyncInput(BaseModel):
                task_ids: list[str] = Field(description="List of Task IDs to wait for.")
                
            def wait_for_tasks(task_ids: list[str]) -> str:
                results = []
                import os
                os.makedirs(self.workspace_dir or "./workspace", exist_ok=True)
                for tid in task_ids:
                    if tid not in _async_tasks:
                        results.append(f"Task ID {tid} not found.")
                    else:
                        future, agent_name = _async_tasks[tid]
                        # Block until done, with timeout to prevent permanent hangs
                        try:
                            res = future.result(timeout=600)  # 10 min max per agent
                        except concurrent.futures.TimeoutError:
                            res = json.dumps({"agent": agent_name, "error": f"Timed out after 600s", "summary": {"total_findings": 0}, "dimensions": {}})
                            print(f"WARNING: {agent_name} timed out after 600s")
                        except Exception as e:
                            res = json.dumps({"agent": agent_name, "error": str(e), "summary": {"total_findings": 0}, "dimensions": {}})
                            print(f"ERROR: {agent_name} failed with: {e}")
                        # Auto-save to workspace
                        filename = ""
                        if agent_name == "CodeSentinel": filename = "code_sentinel.json"
                        elif agent_name == "ArchitectReview": filename = "architect_review.json"
                        elif agent_name == "HarnessGuard": filename = "harness_guard.json"
                        else: filename = f"{agent_name.lower()}.json"
                        
                        file_path = os.path.join(self.workspace_dir or "./workspace", filename)
                        with open(file_path, "w") as f:
                            f.write(str(res))
                        results.append(f"Task ID {tid} for {agent_name} completed and saved to {file_path}")
                return "\n".join(results)
                
            wait_tool = StructuredTool.from_function(
                name="wait_for_async_tasks",
                func=wait_for_tasks,
                description="Wait for one or more async tasks to complete and return their results. ALWAYS wait for all running tasks before proceeding.",
                args_schema=WaitAsyncInput
            )
            self.resolved_tools.append(wait_tool)
                
        # Create the agent using langgraph's create_react_agent
        self.agent_graph = create_react_agent(
            model=self.llm,
            tools=self.resolved_tools,
            prompt=SystemMessage(content=self.system_prompt),
            name=self.name,
        )

    def run(self, input_text):
        print(f"\n[{self.name}] Running with input: {input_text}")
        result = self.agent_graph.invoke(
            {"messages": [HumanMessage(content=input_text)]},
            config={"recursion_limit": 50}
        )
        # Extract the final AI message content from the response
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1]
            content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
            # Handle list-type content (e.g., content blocks from Anthropic)
            if isinstance(content, list):
                try:
                    content = "".join([b.get("text", "") for b in content if isinstance(b, dict)])
                except Exception:
                    content = str(content)
            elif not isinstance(content, str):
                content = str(content)
            return content
        return "No output generated."

def create_deep_agent(name, model, system_prompt, tools, sub_agents=None, workspace_dir=None, skills=None):
    return DeepAgent(name, model, system_prompt, tools, sub_agents, workspace_dir, skills)

class AsyncSubAgent:
    def __init__(self, name):
        self.name = name
