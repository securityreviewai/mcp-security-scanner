from dotenv import load_dotenv
import os
load_dotenv()

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio
from openai import AsyncOpenAI
from agents import set_tracing_disabled
from agents import OpenAIChatCompletionsModel
from pydantic import BaseModel
from typing import List, Optional
import asyncio

# Models
class MCPFunction(BaseModel):
    name: str
    description: str

class VulnerablePath(BaseModel):
    path: str
    code_snippet: str

class MCPVulnerability(BaseModel):
    name: str
    description:str
    paths: List[VulnerablePath]
    recommendation: str
    severity: str
    confidence: str

class MCPReport(BaseModel):
    tools: List[MCPFunction]
    vulnerabilities: List[MCPVulnerability]


custom_client = AsyncOpenAI(
    api_key = os.getenv("OPENAI_API_KEY"), 
)
set_tracing_disabled(True)

my_model=OpenAIChatCompletionsModel(
    model="openai/gpt-5-mini",
    openai_client = custom_client
)

ast_grep_mcp = MCPServerStdio(
    name = "ast-grep",
    params = {
        "command": "uvx",
        "args": ["--from", "git+https://github.com/ast-grep/ast-grep-mcp", "ast-grep-server"],
    },
    client_session_timeout_seconds=300
)

xray_mcp = MCPServerStdio(
    name="xray",
    params = {
        "command": "uvx",
        "args": ["--from", "git+https://github.com/srijanshukla18/xray", "xray-mcp"],
    },
    client_session_timeout_seconds = 300,
)

async def run_mcp_scan_agent(path_str: str):
    async with ast_grep_mcp as ast_client, xray_mcp as mcp:
        agent = Agent(
            name = "mcp_scan_agent",
            model = my_model,
            output_type=MCPReport,
            instructions = """
            <whoami>
            You are an expert security code reviewer. 
            You are given the code for an MCP server, where the codebase.
            You are tasked with identifying vulnerabilities and profiling the MCP Server codebase for possible security issues.
            </whoami>

            <task>
            Analyze the codebase and identify:
            1. Use ast-grep and xray mcp tools to identify the attack surface
            2. Identify the following parameters within the codebase:
                2a. Tech Stack (languages, frameworks and libraries)
                2b. Authentication/Authorization Mechanisms
                2c. All user input entry points
                2d. Sensitive operations (database, file I/O, network, crypto, subprocess)
                2e. Configuration patterns
                2f. Identify all the functions of the MCP Server

            3. Based on the parameters identified, identify anomalies or vulnerabilities in the MCP codebase with the following parameters:
                3a. Hardcoded secrets or sensitive information in the codebase of the MCP Server, especially in prompts. 
                3b. Use of insecure cryptography, hashing and HMAC functions or parameters.
                3c. Lack of Input Validation
                3d. Injection flaws - SQL Injection, Insecure Deserialization, Command Injection, XML External Entities and more.
                3e. Excessive Data Exposure - based on the functionality and access provided by the MCP Server.
                3f. Authentication and Authorization Flaws - Long-lived API tokens, Lack of OAuth, Insecure Direct Object Reference, Broken functional authorization, mass assignment
                3g. Server-side Request Forgery
                3h. Other OWASP Top 10 vulnerabilities like Path Traversal, etc. 
            </task>
            
            <output>
            Once done - Generate a report with the following information:
                a. List of Tools available in the MCP Server (by identifying functions).
                b. List of vulnerabilities and information about each vulnerability.
                    b(1): Name of the vulnerability
                    b(2). Description of the vulnerability
                    b(3). File paths with code snippets of the vulnerability
                    b(4). Recommendation to fix the vulnerability
                    b(5). Severity of the vulnerability
                    b(6). Confidence level of the vulnerability
            </output>
            """,
            mcp_servers = [ast_client, xray_mcp],
        )
        prompt = path_str
        runner=await Runner.run(agent, prompt, max_turns=100)
        return runner.final_output