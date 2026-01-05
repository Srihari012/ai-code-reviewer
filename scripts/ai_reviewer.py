import os
import requests
import google.generativeai as genai
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_NAME = os.getenv("REPO_NAME")
PR_NUMBER = os.getenv("PR_NUMBER")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)

def get_diff():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
    }
    return requests.get(pr.url, headers=headers).text

def analyze_diff(diff):
    prompt = """
    You are a Senior Software Engineer reviewing a Pull Request.
    Your goal is to analyze the following code DIFF and identify:
    1. CRITICAL BUGS (Logic errors, potential crashes)
    2. SECURITY VULNERABILITIES (SQL injection, XSS, exposed secrets)
    3. PERFORMANCE IMPROVEMENTS (inefficient loops, memory leaks)
    
    INPUT CONTEXT:
    The input provided is a GIT DIFF. Lines starting with '+' are additions.
    
    OUTPUT RULES:
    - Be concise.
    - If the code looks good, strictly reply with "LGTM" (Looks Good To Me).
    - If there are issues, format your response in Markdown.
    - Provide specific code snippets for fixes.
    """
    try:
        response = model.generate_content(
            [prompt, f"DIFF:\n{diff}"]
        )
        return response.text.strip()
    except Exception as e:
        return f"Error during analysis: {str(e)}"
    
if __name__ == "__main__":
    print(f"Analyzing PR #{PR_NUMBER}...")
    diff = get_diff()
    if diff:
        review = analyze_diff(diff)
        pr.create_issue_comment(f"## 🤖 AI Review\n{review}")