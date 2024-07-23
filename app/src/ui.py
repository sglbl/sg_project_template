"""Css settings and Js functions for the UI"""

# Set footer unvisible and add css for the table
css = """
    #chatbot table {
        border: 1px solid;
        border-collapse: collapse;
        text-align: center;
        vertical-align: middle;
    }

    #chatbot table th {
        border: 1px solid;
        padding: 4px;
    }

    #chatbot table td {
        border: 1px solid;
        padding: 4px;
    }
    footer {visibility: hidden}
"""

# js_refresh: Refresh the page with explicit dark theme if the theme is not set
js_refresh = """
    function refresh() {
        const url = new URL(window.location);
        if (url.searchParams.get('__theme') !== 'dark' && url.searchParams.get('__theme') !== 'light') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        } 
    }
"""

# If button is clicked, change the theme
js_change_color_theme = """
    function change_color_theme() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        } 
        else if (url.searchParams.get('__theme') !== 'light') {
            url.searchParams.set('__theme', 'light');
            window.location.href = url.href;
        }
        else {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
"""

logo_without_title = """
    <img src="/file=data/images/logo.png" width="300" style='display:block; margin-left: auto; 
    margin-right: auto; padding-top: 1ch; align-items: center; justify-content: center;'>
"""

logo_with_title = """<h1 style="text-align:center; font-family:'system-ui'; display:block;">SG PROJECT</h1>
    <img src="/file=data/images/logo.png" width="300" style='display:block; margin-left: auto; 
    margin-right: auto; padding-top: 1ch; align-items: center; justify-content: center;'>"""

import base64
with open("data/images/logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()
    logo_base64_with_title = f""" <h1 style="text-align:center; font-family:'system-ui'; display:block;">IDBOX GPT</h1>
                            <img src="data:image/jpeg;base64,{logo_base64}" width="300" style='display:block; margin-left: auto; 
                            margin-right: auto; padding-top: 1ch; align-items: center; justify-content: center;'>"""

# If dislike button is clicked, automatically click into the hidden button to trigger the function
js_hidden_results = """
    () => {
        if (document.activeElement.getAttribute('aria-label') === 'clicked dislike') {
            document.getElementById('hidden_other_results').click();
        } else {
            // Do nothing
        }
    }
"""
