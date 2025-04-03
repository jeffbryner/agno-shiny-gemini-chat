from shiny import (
    App,
    Inputs,
    Outputs,
    Session,
    render,
    ui,
    reactive,
    module,
    render,
    run_app,
)
from agno.agent import Agent, AgentMemory
from agno.run.response import RunEvent, RunResponse
from agno.memory.classifier import MemoryClassifier
from agno.memory.summarizer import MemorySummarizer
from agno.memory.manager import MemoryManager
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.memory.db.sqlite import SqliteMemoryDb

from gemini_models import model_flash, model_pro
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from agno.tools.duckdb import DuckDbTools


from utils import logger
import os
from pathlib import Path

# turn off telemetry
os.environ["AGNO_TELEMETRY"] = "false"

agent_storage: str = "tmp/agent_storage.db"

agent = Agent(
    model=model_flash,
    tools=[
        FileTools(save_files=True, read_files=True),
        DuckDbTools(),
        DuckDuckGoTools(),
    ],
    markdown=True,
    show_tool_calls=True,
    telemetry=False,
    monitoring=False,
    instructions=[
        "You are a multipurpose chat assistant"
        "You have access to local files, duckdb and the internet.",
        "If asked about local files, use your file tools to list ONLY .csv or .json files. Never list other files."
        "You can use duckdb tools to take data from any source, create a table and describe it for context on the data",
        "Use your duckdb tools analyze and answer questions",
        "Pay attention to columns with special characters or spaces since they will need to be quoted when accessing.",
        "You can then use duckdb to answer questions",
        "You can also search the internet with DuckDuckGo.",
        "Never send any local files to the internet/search, or to the AI model directly.",
    ],
    description="You are an expert data analyst using duckdb.",
    storage=SqliteAgentStorage(table_name="chat_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=15,
    memory=AgentMemory(
        db=SqliteMemoryDb(db_file="tmp/agent_memory.db"),
        create_user_memories=True,
        create_session_summary=True,
        update_user_memories_after_run=True,
        update_session_summary_after_run=True,
        classifier=MemoryClassifier(model=model_flash),
        summarizer=MemorySummarizer(model=model_pro),
        manager=MemoryManager(model=model_flash),
    ),
)


# utility to stream to shiny
# non async version
def as_stream(response):
    for chunk in response:
        if isinstance(chunk, RunResponse) and isinstance(chunk.content, str):
            if chunk.event == RunEvent.run_response:
                yield chunk.content


## chat module ##
@module.ui
def chat_mod_ui(messages=[]):
    if messages:
        # filter out the system messages (not done for some reason in a module)
        logger.info(messages)
        messages = [m for m in messages if m["role"] in ["user", "assistant"]]
        chat_ui = ui.chat_ui(id="chat", messages=messages, height="80vh", fill=True)
    else:
        chat_ui = ui.chat_ui(id="chat", height="80vh", fill=True)
    return chat_ui


@module.server
def chat_mod_server(input, output, session, messages):
    chat = ui.Chat(id="chat", messages=messages)

    @chat.on_user_submit
    async def _():
        new_message = chat.user_input()
        chunks = agent.run(message=new_message, stream=True)
        await chat.append_message_stream(as_stream(chunks))


## end chat module


# page layout
app_page_chat_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Shiny Chat"),
        ui.output_ui("chat"),
    ),
)


# page logic
def agno_chat_server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def chat():

        chat_messages = []
        # start the module server
        chat_mod_server("chat_session", messages=chat_messages)
        # start the module UI
        return chat_mod_ui("chat_session", messages=chat_messages)


# allow this to run standalone
starlette_app = App(app_page_chat_ui, agno_chat_server)
if __name__ == "__main__":

    run_app(
        "shiny_chat:starlette_app",
        launch_browser=True,
        log_level="debug",
        reload=True,
    )
