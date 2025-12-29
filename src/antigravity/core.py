from dataclasses import dataclass
from typing import List, Callable, Any, Dict
import asyncio

@dataclass
class Agent:
    name: str
    instructions: str
    tools: List[Callable]
    analysis_logic: Callable[[Dict], str] = None


class Session:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.history = []

    @classmethod
    async def start(cls, agent: Agent):
        """Initializes a new session with the given agent."""
        return cls(agent)

    async def ask(self, prompt: str) -> 'Response':
        """
        Simulates the agent 'thinking' and using tools.
        In a real LLM system, this would:
        1. Send prompt + tool definitions to LLM.
        2. LLM decides to call a tool.
        3. Runtime executes tool.
        4. Runtime sends tool output back to LLM.
        5. LLM generates final response.
        
        For this prototype, we'll do a simplified 'Orchestration' 
        that tries to map the prompt to tool calls if explicit, 
        or just passes the prompt to a simulated LLM.
        """
        print(f"[{self.agent.name}]: Processing request...")
        
        # 1. Identify relevant tools based on simplified keywords in prompt (Prototype logic)
        # In a real system, the LLM does this.
        results = {}
        for tool_func in self.agent.tools:
            # Heuristic: Check if tool name or key concepts are in prompt
            # This is a placeholder for actual Intent Recognition
            if "fetch" in prompt.lower() or "audit" in prompt.lower():
                # For the demo, we'll blindly execute the tool if it looks like a 'fetcher'
                # and we can guess arguments (hardcoded for the prototype flow)
                
                # Check for specific known series IDs in prompt to demonstrate parameter extraction
                series_to_check = []
                if "Debt-to-GDP" in prompt or "GFDEGDQ188S" in prompt:
                    series_to_check.append("GFDEGDQ188S")
                if "Fed Funds" in prompt or "FEDFUNDS" in prompt:
                    series_to_check.append("FEDFUNDS")
                if "Industrial Production" in prompt or "INDPRO" in prompt:
                    series_to_check.append("INDPRO")
                if "M2" in prompt or "M2SL" in prompt:
                    series_to_check.append("M2SL")
                if "Repo" in prompt or "RRPONTSYD" in prompt:
                    series_to_check.append("RRPONTSYD")
                if "HOUST" in prompt or "Housing" in prompt:
                    series_to_check.append("HOUST")
                if "MORTGAGE" in prompt or "MORTGAGE30US" in prompt:
                    series_to_check.append("MORTGAGE30US")
                if "Yield" in prompt or "T10Y2Y" in prompt:
                    series_to_check.append("T10Y2Y")
                if "Sentiment" in prompt or "UMCSENT" in prompt:
                    series_to_check.append("UMCSENT")
                if "Unemployment" in prompt or "UNRATE" in prompt:
                    series_to_check.append("UNRATE")
                    
                if series_to_check and tool_func._name == "get_macro_indicator":
                    print(f"  -> Calling tool: {tool_func._name} for {series_to_check}")
                    for series in series_to_check:
                         # Execute the async tool
                        res = await tool_func(series_id=series)
                        results[series] = res

            # Check for Margin Debt
            if "Margin" in prompt and tool_func._name == "get_margin_debt":
                print(f"  -> Calling tool: {tool_func._name}")
                res = await tool_func()
                results["Margin Debt"] = res

            # Check for Market Risk / VIX
            if ("Risk" in prompt or "VIX" in prompt) and tool_func._name == "get_market_risk_sentiment":
                 print(f"  -> Calling tool: {tool_func._name}")
                 res = await tool_func()
                 results["Market Sentiment"] = res
            
            # Check for Metals
            if ("Gold" in prompt or "Copper" in prompt or "Platinum" in prompt) and tool_func._name == "get_metal_prices":
                 print(f"  -> Calling tool: {tool_func._name}")
                 res = await tool_func()
                 results["Metals"] = res

            # Check for Sector Performance
            if "Sector" in prompt and tool_func._name == "get_sector_performance":
                 print(f"  -> Calling tool: {tool_func._name}")
                 res = await tool_func()
                 results["Sector Performance"] = res

            # Check for Crypto
            if "Crypto" in prompt and tool_func._name == "get_crypto_prices":
                 print(f"  -> Calling tool: {tool_func._name}")
                 res = await tool_func()
                 results["Crypto"] = res

            # Check for Global Markets
            if "Global" in prompt and tool_func._name == "get_global_indices":
                 print(f"  -> Calling tool: {tool_func._name}")
                 res = await tool_func()
                 results["Global Markets"] = res

        # 2. Synthesize a response
        response_text = "Analysis based on fetched data:\n"
        if results:
            for series, data in results.items():
                if isinstance(data, dict):
                    if "vix" in data:
                        response_text += f"- {series}: VIX={data.get('vix')}, Volume={data.get('sp500_volume')}\n"
                    elif "error" in data:
                        response_text += f"- {series}: ERROR - {data.get('error')}\n"
                    elif "metals" in data:
                        # Format nested metals dict
                        response_text += f"- {series}: "
                        for m, vals in data['metals'].items():
                            response_text += f"{m}=${vals['price']} ({vals['5d_change_pct']}%), "
                        response_text += "\n"
                    elif "crypto" in data:
                        response_text += f"- {series}: "
                        for c, vals in data['crypto'].items():
                            response_text += f"{c}=${vals.get('price')} ({vals.get('5d_change_pct')}%), "
                        response_text += "\n"
                    elif "global_markets" in data:
                         response_text += f"- {series}: "
                         for c, vals in data['global_markets'].items():
                            response_text += f"{c}=${vals.get('price')} ({vals.get('5d_change_pct')}%), "
                         response_text += "\n"
                    else:
                        val = data.get('value')
                        date = data.get('date')
                        label = data.get('indicator', series)
                        if val is not None:
                            response_text += f"- {label}: {val} (as of {date})\n"
                        else:
                             response_text += f"- {label}: {data}\n"
                else:
                    response_text += f"- {series}: {data}\n"
            # In a real app, this would be a second LLM call with the tool outputs.
            response_text += "\n[MacroWatchdog Assessment]:\n"
            if self.agent.analysis_logic:
                response_text += self.agent.analysis_logic(results)
            else:
                response_text += "Data successfully retrieved. (Real contrarian analysis would go here based on LLM inference)."
        else:
            response_text = "I couldn't identify specific data points to fetch. Please specify series IDs."

        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "agent", "content": response_text})
        
        return Response(text=response_text)

@dataclass
class Response:
    text: str
