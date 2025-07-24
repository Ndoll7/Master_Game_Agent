import os
import random
import asyncio
from dotenv import load_dotenv
import streamlit as st

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
from game_tool import roll_dice, generate_event

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

st.markdown("""
    <style>
        /* Import Tailwind for utility classes */
        @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');

        /* App background (Mystical gradient) */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a202c 0%, #2d3748 50%, #111827 100%);
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
        }

        /* Gold glowing headers */
        h1, h2, h3 {
            font-weight: 800;
            color: #facc15 !important;
            text-shadow: 0 0 10px #f59e0b, 0 0 20px #d97706;
        }

        /* General text color */
        div, p, span, label {
            color: #f1f5f9 !important;
        }

        /* Styled buttons with glow effect */
        .stButton>button {
            background: linear-gradient(to right, #6d28d9, #4f46e5);
            color: #ffffff;
            font-size: 18px;
            padding: 12px 25px;
            border-radius: 0.75rem;
            border: none;
            box-shadow: 0 0 10px rgba(79, 70, 229, 0.7);
            transition: all 0.3s ease-in-out;
        }

        .stButton>button:hover {
            background: linear-gradient(to right, #7c3aed, #4338ca);
            transform: scale(1.07);
            box-shadow: 0 0 20px rgba(79, 70, 229, 0.9);
        }

        /* Radio button styles */
        .stRadio label {
            font-size: 18px;
            padding: 5px 10px;
            border-radius: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            margin: 3px 0;
            transition: all 0.2s ease;
        }
        .stRadio label:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        /* Alert boxes styled */
        .stAlert {
            border-radius: 0.5rem;
            background: rgba(255, 255, 255, 0.05) !important;
            color: #ffffff !important;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
        }

        /* Spinner style */
        .stSpinner > div {
            color: #facc15 !important;
            font-weight: bold;
        }

        /* Center text styling */
        .text-center {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)


# 🏰 Epic Header
st.markdown("<h1 class='text-5xl text-center gold-text'>🧙‍♂️ Fantasy Adventure Game</h1>", unsafe_allow_html=True)
st.markdown("<p class='text-center text-gray-300 text-xl italic'>Enter the mystical world and face your fate!</p>", unsafe_allow_html=True)

# 🎲 Player Choice
player_choice = st.radio(
    "🌲 Do you want to enter the forest or turn back?",
    options=["Enter the forest", "Turn back"],
    key="player_choice",
    label_visibility="visible"
)

# 🚀 Start Adventure
if st.button("⚔ Start Adventure"):
    with st.spinner("✨ Forging your destiny..."):
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        story, encounter, reward = loop.run_until_complete(play_game(player_choice))

        st.markdown("<h3 class='text-3xl text-yellow-400 mt-4'>📖 Story</h3>", unsafe_allow_html=True)
        st.info(f"**{story}**")

        st.markdown("<h3 class='text-3xl text-red-400 mt-4'>💥 Encounter</h3>", unsafe_allow_html=True)
        st.warning(f"**{encounter}**")

        st.markdown("<h3 class='text-3xl text-green-400 mt-4'>✨ Reward</h3>", unsafe_allow_html=True)
        st.success(f"**{reward}**")
