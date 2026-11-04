import asyncio,os,socket
from pathlib import Path
from unittest.mock import patch
from unittest.mock import AsyncMock
from fulcrum.config import FulcrumConfig
from fulcrum.cost import CostTracker
from fulcrum.tui.app import FulcrumApp
from fulcrum.tui.transcript import Transcript
from fulcrum.tui.input import PromptInput
# Run with the Fulcrum Code checkout's Python environment. No model calls are made.
out=Path(__file__).resolve().parent.parent/'assets/screenshots'
class DemoAgent:
    def __init__(self,config,tui,**kwargs):
        self.config=config;self.tui=tui;self.history=[];self.cost_tracker=CostTracker();self.primary_mode='plan';self.reset=AsyncMock();self.run_query=AsyncMock()
async def main():
    demo=Path('/tmp/fulcrum-demo-project');demo.mkdir(exist_ok=True);os.chdir(demo)
    cfg=FulcrumConfig(base_url='https://api.example.test/v1',api_key='',model='demo-model',user_email='demo@example.test',lsp_warmup=False,primary_mode='plan')
    with patch('fulcrum.tui.app.load_config',return_value=cfg),patch('fulcrum.tui.app.Agent',DemoAgent),patch('pathlib.Path.home',return_value=demo),patch('socket.create_connection',side_effect=RuntimeError('Network disabled for screenshot')):
        app=FulcrumApp(skip_bootstrap=True)
        async with app.run_test(size=(120,42)) as pilot:
            await pilot.pause()
            transcript=app.query_one(Transcript)
            transcript.append_user('Inspect this demo project and propose a validation change. Wait before editing.')
            transcript.append_assistant_delta('I will inspect the form and its existing checks, then propose a small change. Plan mode is active; no files have been changed.')
            transcript.close_assistant_block()
            app.query_one(PromptInput).text='/help'
            await pilot.pause()
            import re
            svg=app.export_screenshot(title='Fulcrum Code — demonstration session')
            svg=re.sub(r'\s*@font-face\s*\{[^}]+\}', '', svg)
            (out/'code-plan.svg').write_text(svg)
asyncio.run(main())
