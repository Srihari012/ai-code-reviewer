import os
from google import genai
from github import Github

# 1. Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("GOOGLE_API_KEY")  # Using the variable that worked for you
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

# 2. Configure Gemini (New Syntax)
client = genai.Client(api_key=API_KEY)

def analyze_code(diff_text):
    """Constructs prompt and sends diff to Gemini 2.5."""
    
    system_prompt = """
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
        # Using the new google-genai syntax
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nGIT DIFF:\n{diff_text}"
        )
        return response.text
    except Exception as e:
        return f"Error analyzing code with AI: {str(e)}"

def main():
    # 3. Connect to GitHub
    if not GITHUB_TOKEN or not API_KEY:
        print("Error: Missing Environment Variables")
        return

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(int(PR_NUMBER))

    # 4. Extract Diffs
    print(f"Fetching diff for PR #{PR_NUMBER}...")
    diff_content = ""
    
    # Get the specific files changed in this PR
    for file in pr.get_files():
        if file.status == "removed":
            continue
        # Check for code files
        if not file.filename.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.html', '.css')):
            continue
            
        diff_content += f"\n\n--- File: {file.filename} ---\n{file.patch}"

    if not diff_content:
        print("No applicable code changes found.")
        return

    # 5. Analyze and Post Comment
    print("Sending diff to Gemini...")
    review = analyze_code(diff_content)
    
    print("Posting comment to GitHub...")
    pr.create_issue_comment(f"## 🤖 AI Code Review Agent\n\n{review}")
    print("Done.")

if __name__ == "__main__":
    main()