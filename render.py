import json
from flask import Flask, request, render_template_string
import markdown
import re
import ast
import json5 as json

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def render_markdown():
    if request.method == "POST":
        try:
            # Get the JSON input with markdown content
            data = request.json
            astr = json.loads(data["text"])
            
            # Extract only the .content field from the input
            assistant_content = astr.get("content", "")
            
            if not assistant_content:
                return {"error": "'content' field is required in the request JSON"}, 400

            # Convert the .content field into Markdown
            html_content = markdown.markdown(assistant_content, extensions=["fenced_code", "tables"])
            
            # Return the rendered markdown as plain HTML
            return html_content
        except Exception as e:
            return {"error": str(e)}, 400
    
    # HTML for the main page with a form
    return '''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <title>Markdown Renderer</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
                pre, code { background: #f4f4f4; margin: 10px; border-radius: 5px; }
                pre { overflow: auto; }
                h1, h2, h3 { border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                #renderedContent { margin-top: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <form id="markdownForm">
                <textarea id="assistantText" rows="10" cols="80" placeholder="Paste your 'content' field text here"></textarea><br>
                <button type="submit">Render Markdown</button>
            </form>
            <div id="renderedContent">
                <!-- Rendered markdown will appear here -->
            </div>
            <script>
                document.getElementById('markdownForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const text = document.getElementById('assistantText').value;
                    const response = await fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ text }) // Send only the 'content' field
                    });
                    const renderedContent = await response.text();
                    document.getElementById('renderedContent').innerHTML = renderedContent;
                });
            </script>
        </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
