import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def initialize(self):
        self.app = MCPApp(name="mcp_agent")
        await self.app.initialize()

        self.agent = Agent(
            name="agent",
            instruction="you are an assistant",
            server_names=["chroma", "twitter"],
        )
        await self.agent.initialize()

        self.llm = await self.agent.attach_llm(OpenAIAugmentedLLM)

    async def process_query(self, query: str) -> str:
        """Process a query"""
        response = await self.llm.generate_str(message=query)
        return response

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nAIP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

from aip_chain.chain import membase_chain, membase_account, membase_id
membase_chain.register(membase_id)
print(f"start agent with account: {membase_account} and id: {membase_id}")

async def main():
    client = MCPClient()
    try:
        await client.initialize()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
