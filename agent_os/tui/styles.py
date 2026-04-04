from __future__ import annotations

from agent_os.tui.nav import _TREE_WIDTH

CSS = f"""
Screen {{ background: #0d1117; }}

NavTree {{
    width: {_TREE_WIDTH};
    min-width: {_TREE_WIDTH};
    border-right: heavy #30363d;
    background: #0d1117;
    overflow-x: hidden;
    scrollbar-size: 0 0;
}}
NavTree .tree--highlight {{
    background: transparent;
}}
NavTree .tree--highlight-line {{
    background: transparent;
}}

#detail {{
    width: 1fr;
    padding: 1 3;
    background: #0d1117;
    scrollbar-size: 0 0;
}}

DetailTextArea {{
    border: tall #30363d;
    background: #161b22;
    color: #c9d1d9;
    height: 1fr;
    min-height: 8;
    scrollbar-size: 0 0;
}}
DetailTextArea:focus {{ border: tall #58a6ff; }}
"""
