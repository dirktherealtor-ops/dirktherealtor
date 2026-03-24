import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
from PIL import Image

BASE_DIR = Path('/mnt/data')
LOGO_PATH = BASE_DIR / 'Realty Mark New Logo Transparent.png'
EMOJI_PATH = BASE_DIR / 'Dirk Full Emoji.jpg'


@dataclass
class Scenario:
    seller_name: str
    neighborhood: str
    home_type: str
    bedrooms: int
    bathrooms: float
    motivation: str
    concern: str
    objection: str
    personality: str
    urgency: str
    price_hint: str
    condition: str
    competing_agent: bool
    hidden_need: str
    must_hit_keywords: List[str] = field(default_factory=list)

    def intro(self) -> str:
        competing = (
            'I am also speaking with another agent. '
            if self.competing_agent
            else 'I have not committed to any agent yet. '
        )
        return (
            f"Hi, I'm {self.seller_name}. I own a {self.bedrooms}-bedroom, {self.bathrooms}-bath "
            f"{self.home_type} in {self.neighborhood}. The home is in {self.condition} condition. "
            f"I'm thinking about selling because {self.motivation}. My biggest concern is {self.concern}. "
            f"{competing}I'm feeling {self.urgency} about the timeline."
        )


def make_scenarios() -> List[Scenario]:
    return [
        Scenario(
            seller_name='Monica',
            neighborhood='Mount Airy',
            home_type='rowhome',
            bedrooms=3,
            bathrooms=1.5,
            motivation='I may need more space for my growing family',
            concern='pricing it right without leaving money on the table',
            objection='Why should I hire you instead of a more experienced agent?',
            personality='warm but cautious',
            urgency='somewhat urgent',
            price_hint='similar homes nearby sold between $305,000 and $340,000',
            condition='good',
            competing_agent=True,
            hidden_need='She wants a step-by-step plan because uncertainty stresses her out.',
            must_hit_keywords=['market', 'plan', 'communication', 'timeline'],
        ),
        Scenario(
            seller_name='Mr. Jackson',
            neighborhood='West Oak Lane',
            home_type='single-family home',
            bedrooms=4,
            bathrooms=2.5,
            motivation='I inherited the property and do not want to hold it much longer',
            concern='getting the house sold quickly without too many repairs',
            objection='I do not want to spend money fixing this place up first.',
            personality='direct and skeptical',
            urgency='very urgent',
            price_hint='cash investors have hinted at offers below market value',
            condition='fair',
            competing_agent=False,
            hidden_need='He wants convenience and clarity more than the absolute top price.',
            must_hit_keywords=['options', 'as-is', 'strategy', 'net'],
        ),
        Scenario(
            seller_name='Alicia',
            neighborhood='Newtown Square',
            home_type='colonial',
            bedrooms=5,
            bathrooms=3.5,
            motivation='we are relocating for work in about 60 days',
            concern='coordinating the sale with our move',
            objection='What exactly would you do to market a home like mine?',
            personality='organized and detail-oriented',
            urgency='moderately urgent',
            price_hint="the neighbor's home sold in the mid $1.4M range",
            condition='excellent',
            competing_agent=True,
            hidden_need='She wants confidence that the agent has a premium marketing process.',
            must_hit_keywords=['marketing', 'photos', 'showings', 'coordination'],
        ),
        Scenario(
            seller_name='Devon',
            neighborhood='Harrisburg',
            home_type='duplex',
            bedrooms=6,
            bathrooms=2.0,
            motivation='I am tired of being a landlord',
            concern='whether now is a smart time to sell an investment property',
            objection="Wouldn't it make more sense to keep renting it out?",
            personality='analytical',
            urgency='not urgent',
            price_hint='current rents are okay but maintenance has increased',
            condition='average',
            competing_agent=False,
            hidden_need='He wants data and a comparison of sell-versus-hold.',
            must_hit_keywords=['numbers', 'equity', 'market', 'analysis'],
        ),
        Scenario(
            seller_name='Tanya',
            neighborhood='Roxborough',
            home_type='townhome',
            bedrooms=3,
            bathrooms=2.5,
            motivation='I want to downsize and free up cash',
            concern='strangers walking through my house and judging it',
            objection='I hate the idea of constant showings.',
            personality='friendly but anxious',
            urgency='flexible',
            price_hint='she wants strong proceeds but peace of mind matters too',
            condition='very good',
            competing_agent=False,
            hidden_need='She needs empathy and control over the process.',
            must_hit_keywords=['comfort', 'schedule', 'prep', 'communication'],
        ),
    ]


class Simulator:
    def __init__(self):
        self.scenarios = make_scenarios()
        self.reset()

    def reset(self):
        self.scenario = random.choice(self.scenarios)
        self.turn = 0
        self.max_turns = 5
        self.history: List[Tuple[str, str]] = [('client', self.scenario.intro())]
        self.score_breakdown: Dict[str, int] = {
            'rapport': 0,
            'discovery': 0,
            'value': 0,
            'objection': 0,
            'close': 0,
        }
        self.asked_questions = 0
        self.used_keywords = set()
        self.closed = False
        self.finished = False

    def keyword_check(self, text: str):
        lower = text.lower()
        for kw in self.scenario.must_hit_keywords:
            if kw.lower() in lower:
                self.used_keywords.add(kw.lower())

    def evaluate(self, text: str) -> Dict[str, int]:
        lower = text.lower()
        delta = {k: 0 for k in self.score_breakdown}

        if any(word in lower for word in ['understand', 'appreciate', 'hear', 'important', 'stressful', 'comfortable', 'glad']):
            delta['rapport'] += 2

        if '?' in text:
            qmarks = text.count('?')
            delta['discovery'] += min(3, qmarks)
            self.asked_questions += qmarks

        if any(word in lower for word in ['market', 'strategy', 'plan', 'marketing', 'timeline', 'communication', 'analysis', 'pricing']):
            delta['value'] += 2

        if any(word in lower for word in ['because', 'so that', 'options', 'as-is', 'net', 'showings', 'photos', 'prep', 'process']):
            delta['objection'] += 2

        if any(phrase in lower for phrase in [
            'would you be open',
            'can we schedule',
            "let's set",
            'next step',
            'meet with you',
            'listing appointment',
            'preview your home',
        ]):
            delta['close'] += 4
            self.closed = True

        self.keyword_check(text)
        for key, value in delta.items():
            self.score_breakdown[key] += value
        return delta

    def client_reply(self, text: str) -> str:
        lower = text.lower()
        s = self.scenario

        if self.turn == 0:
            if '?' not in text:
                return f"Before I say much more, what would you want to know about my situation in {s.neighborhood}?"
            if any(w in lower for w in ['why', 'moving', 'timeline', 'when']):
                return f"I'm selling because {s.motivation}, and I would ideally like a plan that fits a {s.urgency} timeline."
            if any(w in lower for w in ['concern', 'worry', 'important']):
                return f"Honestly, my biggest concern is {s.concern}."
            return f"I'm open to talking, but I want to know how you would handle a seller like me who is {s.personality}."

        if any(w in lower for w in ['market', 'price', 'pricing', 'analysis', 'comps']):
            return f"What do you think this home could realistically sell for? For context, {s.price_hint}."

        if any(w in lower for w in ['marketing', 'photos', 'video', 'advertising', 'exposure']):
            return 'That sounds good, but lots of agents promise marketing. What makes your plan different in practice?'

        if any(w in lower for w in ['as-is', 'repairs', 'prep', 'staging', 'showings']):
            return f"I like the sound of options, but I still worry about {s.concern}."

        if any(w in lower for w in ['appointment', 'meet', 'next step', 'schedule']):
            return 'Maybe. Before I agree, tell me why I should trust you with one of my biggest financial decisions.'

        if self.turn >= self.max_turns - 1:
            return s.objection

        generic_replies = [
            'That makes sense. How would you guide me step by step?',
            'Okay, but how would you communicate with me during the process?',
            'I hear you. What would be the smartest first step for my home?',
            'Interesting. How would you help me avoid leaving money on the table?',
        ]
        return random.choice(generic_replies)

    def final_assessment(self) -> Tuple[str, str, int]:
        total = sum(self.score_breakdown.values()) + len(self.used_keywords)
        bonus = 0
        if self.asked_questions >= 3:
            bonus += 3
        if len(self.used_keywords) >= 2:
            bonus += 3
        if self.closed:
            bonus += 5
        total += bonus

        if total >= 20:
            verdict = 'Listing Appointment Won'
            feedback = (
                'Strong job. You built rapport, asked enough questions, gave a strategy, and moved toward an appointment. '
                'Your biggest strength was sounding consultative instead of pushy.'
            )
        elif total >= 13:
            verdict = 'Warm Lead - Needs Follow-Up'
            feedback = (
                "You created interest, but you left some value on the table. Ask more discovery questions, tie your plan to the seller's main concern, "
                'and finish with a clearer next step.'
            )
        else:
            verdict = 'Lead Lost'
            feedback = (
                'The seller did not hear enough tailored value yet. Slow down, ask better questions, reflect their concerns, and confidently ask for an appointment.'
            )
        return verdict, feedback, total


def coach_note(delta: Dict[str, int], sim: Simulator) -> str:
    notes = []
    if delta['discovery'] == 0:
        notes.append('Ask at least one question before pitching.')
    if delta['value'] == 0:
        notes.append('Add more value: pricing, strategy, communication, marketing, or timeline.')
    if delta['close'] == 0 and sim.turn >= 3:
        notes.append('Move toward a next step or listing appointment.')
    if delta['rapport'] == 0:
        notes.append('Reflect the seller’s emotions so you sound consultative.')
    return ' '.join(notes) if notes else 'Good balance. Keep building trust and asking for the next step.'


def ensure_state():
    if 'simulator' not in st.session_state:
        st.session_state.simulator = Simulator()
    if 'last_feedback' not in st.session_state:
        st.session_state.last_feedback = 'Start with rapport and discovery. Ask questions before pitching.'
    if 'draft_text' not in st.session_state:
        st.session_state.draft_text = ''
    if 'agent_name' not in st.session_state:
        st.session_state.agent_name = ''


def reset_simulator():
    st.session_state.simulator = Simulator()
    st.session_state.last_feedback = 'New seller loaded. Start by asking thoughtful discovery questions.'
    st.session_state.draft_text = ''


def submit_response(user_text: str):
    sim: Simulator = st.session_state.simulator
    if sim.finished:
        st.session_state.last_feedback = 'This round is complete. Start a new scenario to keep practicing.'
        return

    text = user_text.strip()
    if not text:
        st.session_state.last_feedback = 'Type a response before sending.'
        return

    sim.history.append(('mentee', text))
    delta = sim.evaluate(text)
    sim.turn += 1

    if sim.turn >= sim.max_turns:
        final_reply = sim.scenario.objection
        sim.history.append(('client', final_reply))
        verdict, feedback, total = sim.final_assessment()
        sim.history.append(('coach', f'Result: {verdict} | Score: {total}'))
        st.session_state.last_feedback = feedback
        sim.finished = True
        return

    reply = sim.client_reply(text)
    sim.history.append(('client', reply))
    st.session_state.last_feedback = coach_note(delta, sim)


def sample_response(sim: Simulator) -> str:
    return (
        f"Thanks for sharing that, {sim.scenario.seller_name}. It sounds like your biggest concern is {sim.scenario.concern}. "
        'Could I ask a couple quick questions about your timeline, what outcome matters most, and anything you want to avoid in the process? '
        'Then I can outline a simple pricing and marketing plan and suggest the best next step.'
    )


def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #09131f 0%, #102742 100%);
            color: #eef3f8;
        }
        .block-container {
            max-width: 760px;
            padding-top: 0.7rem;
            padding-bottom: 2rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }
        .brand-shell {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(217, 177, 93, 0.22);
            border-radius: 20px;
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        }
        .hero-title {
            color: #d9b15d;
            font-size: 1.6rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0 0 0.2rem 0;
        }
        .hero-sub {
            color: #eef3f8;
            font-size: 0.96rem;
            margin: 0;
        }
        .badge-row {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
        }
        .badge {
            background: rgba(217,177,93,0.15);
            border: 1px solid rgba(217,177,93,0.35);
            color: #fff7df;
            border-radius: 999px;
            padding: 0.24rem 0.6rem;
            font-size: 0.78rem;
        }
        .panel {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 0.9rem;
            margin-top: 0.8rem;
        }
        .coach-box {
            background: rgba(217, 177, 93, 0.12);
            border: 1px solid rgba(217, 177, 93, 0.4);
            border-radius: 16px;
            padding: 0.85rem;
            margin-top: 0.7rem;
            color: #f7f2e6;
        }
        .tiny-muted {
            color: #c5d4e3;
            font-size: 0.82rem;
        }
        .stChatMessage {
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
        }
        .stTextArea textarea {
            font-size: 16px !important;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.045);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 0.55rem;
            border-radius: 14px;
        }
        @media (max-width: 640px) {
            .hero-title { font-size: 1.35rem; }
            .hero-sub { font-size: 0.92rem; }
            .block-container { padding-left: 0.55rem; padding-right: 0.55rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(sim: Simulator):
    left, center, right = st.columns([1.05, 2.4, 0.95])
    with left:
        if LOGO_PATH.exists():
            st.image(Image.open(LOGO_PATH), use_container_width=True)
    with center:
        st.markdown("<div class='hero-title'>Realty Mark First Client Closer</div>", unsafe_allow_html=True)
        st.markdown("<p class='hero-sub'>Mobile-friendly seller conversation trainer for mentees. Practice discovery, value, objections, and the close.</p>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='badge-row'><span class='badge'>Turns {sim.turn}/{sim.max_turns}</span><span class='badge'>Scenario: {sim.scenario.neighborhood}</span><span class='badge'>Goal: Win the appointment</span></div>",
            unsafe_allow_html=True,
        )
    with right:
        if EMOJI_PATH.exists():
            st.image(Image.open(EMOJI_PATH), use_container_width=True)


def render_quick_stats(sim: Simulator):
    verdict, _, total = sim.final_assessment()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Score', total)
    with c2:
        st.metric('Questions', sim.asked_questions)
    with c3:
        st.metric('Status', 'Won' if 'Won' in verdict else ('Warm' if 'Warm' in verdict else 'At Risk'))


def render_scenario_card(sim: Simulator):
    s = sim.scenario
    with st.expander('Seller scenario + hidden coaching notes', expanded=False):
        st.write(f"**Seller:** {s.seller_name}")
        st.write(f"**Property:** {s.bedrooms} BR / {s.bathrooms} BA {s.home_type} in {s.neighborhood}")
        st.write(f"**Condition:** {s.condition}")
        st.write(f"**Personality:** {s.personality}")
        st.write(f"**Urgency:** {s.urgency}")
        st.write(f"**Concern:** {s.concern}")
        st.write(f"**Hidden need:** {s.hidden_need}")
        st.write(f"**Likely objection:** {s.objection}")
        st.write(f"**Target themes:** {', '.join(s.must_hit_keywords)}")


def render_scoreboard(sim: Simulator):
    st.markdown('### Coach scoreboard')
    sb = sim.score_breakdown
    r1, r2 = st.columns(2)
    with r1:
        st.metric('Rapport', sb['rapport'])
        st.metric('Value', sb['value'])
        st.metric('Closing', sb['close'])
    with r2:
        st.metric('Discovery', sb['discovery'])
        st.metric('Objection', sb['objection'])
        st.metric('Themes Hit', len(sim.used_keywords))


def main():
    st.set_page_config(page_title='Realty Mark First Client Closer', page_icon='🏠', layout='centered')
    inject_css()
    ensure_state()
    sim: Simulator = st.session_state.simulator

    st.markdown("<div class='brand-shell'>", unsafe_allow_html=True)
    render_header(sim)
    st.markdown("</div>", unsafe_allow_html=True)

    name_col, action_col = st.columns([1.55, 1])
    with name_col:
        st.text_input('Mentee name', key='agent_name', placeholder='Type your name')
    with action_col:
        if st.button('🎲 New scenario', use_container_width=True):
            reset_simulator()
            st.rerun()

    render_quick_stats(sim)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown('### Conversation arena')
    st.caption('Tip: On phone, scroll the chat, type your reply, then tap Send.')
    for speaker, message in sim.history:
        avatar = '🏠' if speaker == 'client' else ('🧑🏾‍💼' if speaker == 'mentee' else '🎯')
        role = 'assistant' if speaker == 'client' else 'user'
        with st.chat_message(role, avatar=avatar):
            st.write(message)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.text_area(
            'Your response',
            key='draft_text',
            height=150,
            placeholder='Type how you would respond to win trust, ask smart questions, and move toward the listing appointment...',
        )
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button('Send', type='primary', use_container_width=True):
                submit_response(st.session_state.draft_text)
                st.session_state.draft_text = ''
                st.rerun()
        with b2:
            if st.button('Sample', use_container_width=True):
                st.session_state.draft_text = sample_response(sim)
                st.rerun()
        with b3:
            if st.button('Score now', use_container_width=True):
                verdict, feedback, total = sim.final_assessment()
                st.session_state.last_feedback = f'{verdict} | Score: {total}. {feedback}'
                st.rerun()

    st.markdown(f"<div class='coach-box'><strong>Coach note</strong><br>{st.session_state.last_feedback}</div>", unsafe_allow_html=True)

    if sim.finished:
        verdict, feedback, total = sim.final_assessment()
        st.success(f'{verdict} | Final Score: {total}')
        st.info(feedback)

    render_scenario_card(sim)
    render_scoreboard(sim)

    with st.expander('How to win this conversation'):
        st.write('1. Start with empathy and rapport.')
        st.write('2. Ask questions before pitching.')
        st.write('3. Tie your plan to the seller’s concern.')
        st.write('4. Handle the objection directly and calmly.')
        st.write('5. Ask for the listing appointment or next meeting.')

    with st.expander('Suggested closing lines'):
        st.write('• Would you be open to a quick listing appointment this week?')
        st.write('• Can we schedule a time for me to preview the home and outline a strategy?')
        st.write('• The next best step is for me to meet with you, review the home, and build a pricing plan.')


if __name__ == '__main__':
    main()
