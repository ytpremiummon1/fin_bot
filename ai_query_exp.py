from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain import hub
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

import os


# Load environment variables
load_dotenv(override=True)

# print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
# print(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')}")

STANDARD_MODEL = "gpt-4o"
QUICK_MODEL = "gpt-4o-mini"
REASONING_MODEL = "o3-mini"

class QueryAgent:
    def __init__(self):
        # Initialize database connection
        self.db = SQLDatabase.from_uri(
            f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
            f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
        )
        
        # Initialize LLM
        CLAUDE_3_5_SONNET = os.getenv('CLAUDE_3_5_SONNET')
        self.llm = ChatAnthropic(
            model=CLAUDE_3_5_SONNET,
            temperature=0
        )
        
        # Initialize SQL toolkit and get tools
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
        
        # Load system prompt for the agent
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
        
        # Add custom instructions to the prompt template
        today = datetime.now().strftime("%Y-%m-%d")
        additional_instructions = f"""
        
        Additional Instructions:
        1. When dealing with financial ratios like ROE, ROA, or Net Income Margin (NIM), they are stored as percentages but in decimal form (E.g: 15% is stored as 0.15) in the database.
        2. Format your responses with appropriate units (Bn. VND for money, % for ratios).
        3. Khi user hỏi về 1 ngành nào đó, tên ngành chưa chắc đúng, tìm và match với ngành gần nhất trong bảng vn100_listing_by_industry
        4. Các câu hỏi về "top" cần trả vể kết quả unique (ví dụ: "Top 3 công ty có lợi nhuận cao nhất" phải trả về 3 công ty, không được trả về 1 công ty)
        Today is (YYYY-MM-DD): {today}
        Your final answer should be in Vietnamese.
        """ 
        
        system_message = prompt_template.format(dialect="MySQL", top_k=5) + additional_instructions
        
        # Create ReAct agent
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=system_message
        )

    def query(self, question: str) -> str:
        """Process a question using ReAct agent and return an answer."""
        # Format the input for the agent
        agent_input = {
            "messages": [{"role": "user", "content": question}]
        }
        
        # Get the final response
        response = []
        for step in self.agent_executor.stream(agent_input, stream_mode="values"):
            # Print intermediate steps for debugging
            print("\nStep:", step["messages"][-1])
            response = step["messages"][-1]
            
        # Return the final answer
        return response.content if hasattr(response, 'content') else str(response)

def main():
    # Example usage
    agent = QueryAgent()
    
    # Example questions
    questions = [
        # "What are the top 5 companies by revenue in 2024?",
        "Which industry has the highest average ROE in 2024?",
        # "Top 3 cong ty cong nghe lam an tot nhat ?",
        # "Top 3 nha banks lam an tot nhat ?",
        # "Toi co nen dau tu vao cong ty FPT hay khong ?",
        # "FPT lai nhieu ko ?" 
        # "FPT lãi ròng 10 năm gần đây ntn ?",
        # "FPT tỉ suất lãi ròng 10 năm gần đây ntn ?",
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = agent.query(question)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
