# simple ui to run the docker container
from flask import Flask, render_template_string, request
import subprocess
import os
from datetime import date
import markdown
from dotenv import load_dotenv
load_dotenv()

UIPORT = int(os.environ.get("UIPORT", 5000))

app = Flask(__name__)

# very basic html template directly in the file so we don't need a templates folder
HTML_TEMPLATE = """
<html>
<head>
    <title>Financial Researcher</title>
    <style>
        body { font-family: -apple-system, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px 40px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; }
        h1 { color: #2c3e50; font-size: 28px; margin-bottom: 10px; }
        p.subtitle { color: #7f8c8d; font-size: 16px; margin-bottom: 30px; }
        button { background-color: #007aff; color: white; border: none; padding: 12px 24px; cursor: pointer; font-size: 16px; border-radius: 6px; font-weight: bold; }
        button:hover { background-color: #005bb5; }
        #loading { display: none; margin-top: 20px; color: #555; font-style: italic; }
        .output-section { text-align: left; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        pre { background: #f8f9fa; padding: 20px; border: 1px solid #ddd; white-space: pre-wrap; font-size: 14px; border-radius: 6px; line-height: 1.5; font-family: -apple-system, sans-serif; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Financial Researcher UI</h1>
        <p class="subtitle">Click the button below to start the pipeline and generate today's briefing.</p>
        
        <!-- form hides button on click and shows loading -->
        <form action="/run" method="post" onsubmit="document.getElementById('loading').style.display='block'; document.getElementById('run-btn').style.display='none';">
            <button id="run-btn" type="submit">Start Research</button>
        </form>
        
        <div id="loading">Generating the report... Please wait a minute while the AI gathers live context!</div>
        
        {% if error %}
            <div class="output-section">
                <h3>Error Occurred</h3>
                <pre style="color: red; font-family: monospace;">{{ error }}</pre>
            </div>
        {% endif %}
        
        {% if briefing %}
            <div class="output-section">
                <h3>Latest Briefing Result:</h3>
                <div style="line-height: 1.6; font-size: 15px;">
                    {{ briefing | safe }}
                </div>
            </div>
        {% endif %}
        
        {% if logs %}
            <div class="output-section" style="margin-top: 50px;">
                <details>
                    <summary style="cursor: pointer; color: #007aff; font-weight: bold; padding: 10px; background: #f4f7f6; border-radius: 4px; display: inline-block;">Show Raw Container Logs</summary>
                    <pre style="margin-top: 15px; background: #2d2d2d; color: #f8f8f2; font-family: monospace; font-size: 12px; overflow-x: auto;">{{ logs }}</pre>
                </details>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    # just show the home page
    return render_template_string(HTML_TEMPLATE)

@app.route("/run", methods=["POST"])
def run_researcher():
    
    logs = ""
    current_dir = os.getcwd()
    
    # helper to find the docker executable manually if it's missing from python's system PATH
    # some of us have a mac so we need to do this
    import shutil
    docker_cmd = shutil.which("docker")
    if not docker_cmd:
        for path in ["/usr/local/bin/docker", "/opt/homebrew/bin/docker", "/Applications/Docker.app/Contents/Resources/bin/docker"]:
            if os.path.exists(path):
                docker_cmd = path
                break
                
    error_msg = ""
    logs = ""
    
    try:
        if not docker_cmd:
            raise FileNotFoundError()
            
        # run the docker build command with exact path
        build_result = subprocess.run(
            [docker_cmd, "build", "-t", "financial-researcher", "."], 
            capture_output=True, text=True, encoding="utf-8"
        )
        logs += build_result.stdout + "\n" + build_result.stderr
        
        # command to run the container using exact path
        run_cmd = [docker_cmd, "run", "--rm", "--env-file", ".env", "-v", f"{current_dir}/data:/app/data", "financial-researcher"]
        
        # execute the docker container
        run_result = subprocess.run(run_cmd, capture_output=True, text=True, encoding="utf-8")
        logs += "\n\n" + run_result.stdout + "\n" + run_result.stderr
        
    except FileNotFoundError:
        error_msg = "could not find docker. is docker desktop installed and running?"
    except Exception as e:
        error_msg = f"an unexpected error occurred: {str(e)}"
    
    # check if the briefing was created and read it
    file_date = date.today().strftime("%d%m%y")
    briefing_text = ""
    briefing_path = f"data/output/briefing_{file_date}.md"
    
    if os.path.exists(briefing_path):
        with open(briefing_path, "r", encoding="utf-8") as f:
            raw_markdown = f.read()
            briefing_text = markdown.markdown(raw_markdown)
            
    return render_template_string(HTML_TEMPLATE, error=error_msg, briefing=briefing_text, logs=logs)

if __name__ == "__main__":
    # run the app locally
    app.run(port=UIPORT)
