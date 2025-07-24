import os
import random
import asyncio
from dotenv import load_dotenv
import streamlit as st
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig


# 🔐 Load Environment
load_dotenv()
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# 🧠 Agents
narrrator_agent = Agent(
    name="NarratorAgent",
    instructions="You narrate the adventure. Ask the player for choices.",
    model=model
)

monster_agent = Agent(
    name="MonsterAgent",
    instructions="You handle monster encounters using roll_dice and generate_event.",
    model=model,
    tools=[roll_dice, generate_event]
)

item_agent = Agent(
    name="ItemAgent",
    instructions="You provide rewards or items to the player.",
    model=model
)

# 🚀 Async Flow
async def play_game(choice):
    result1 = await Runner.run(narrrator_agent, choice, run_config=config)
    result2 = await Runner.run(monster_agent, "Start encounter", run_config=config)
    result3 = await Runner.run(item_agent, "Give reward", run_config=config)
    return result1.final_output, result2.final_output, result3.final_output

# 🌑 Streamlit UI
st.set_page_config(page_title="Fantasy Adventure Game", page_icon="🧙", layout="centered")

st.title("🧙‍♂️ Fantasy Adventure Game")
st.markdown("Enter the mystical world and face your fate!")

player_choice = st.radio(
    "🌲 Do you want to enter the forest or turn back?",
    options=["Enter the forest", "Turn back"]
)

if st.button("Start Adventure") and player_choice:
    with st.spinner("Weaving your story..."):
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        story, encounter, reward = loop.run_until_complete(play_game(player_choice))

        st.markdown("### 📖 Story")
        st.info(story)

        st.markdown("### 💥 Encounter")
        st.warning(encounter)

        st.markdown("### ✨ Reward")
        st.success(reward)
