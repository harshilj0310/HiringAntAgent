<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Resume-JD Matching API</title>
</head>
<body>
  <h1>Resume-JD Matching API</h1>

  <h2>Overview</h2>
  <p>API to parse resumes and job descriptions, match them by skills and experience, and optionally send email notifications based on a configurable threshold.</p>

  <h2>Setup</h2>
  <ol>
    <li>Clone repo and create virtual environment:
      <pre><code>git clone &lt;repo-url&gt;
cd project-root
python3 -m venv venv
source venv/bin/activate  &lt;!-- Windows: venv\Scripts\activate --&gt;
</code></pre>
    </li>
    <li>Install dependencies:
      <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li>Create <code>.env</code> file with:
      <pre><code>EMAIL_PASSWORD=your_email_password</code></pre>
    </li>
    <li>Run the app:
      <pre><code>python3 run.py</code></pre>
    </li>
  </ol>

  <h2>API Endpoints</h2>

  <h3>1. POST /match</h3>
  <p>Match resumes against job descriptions and calculate a similarity score. This API does <strong>not send emails</strong> by itself but can optionally trigger email sending if configured.</p>

  <p><strong>Form Data:</strong></p>
  <ul>
    <li><code>resumes</code>: One or more resume files (PDF)</li>
    <li><code>jds</code>: One or more job description files (TXT)</li>
    <li><code>from_email</code>: Sender’s email address</li>
  </ul>

  <p><strong>Returns:</strong> JSON list of match results including:</p>
  <ul>
    <li><code>email</code>: Candidate’s email</li>
    <li><code>score</code>: Matching percentage</li>
    <li><code>job</code>: Job file name</li>
    <li><code>resume</code>: Resume file name</li>
    <li><code>explanation</code>: Explanation of match</li>
  </ul>

  <p><strong>Example curl:</strong></p>
  <pre><code>curl -X POST http://127.0.0.1:5000/match \
  -F "resumes=@resume.pdf" -F "jds=@job.txt" -F "from_email=you@example.com"</code></pre>

  <h3>2. POST /send-mails</h3>
  <p>This endpoint sends emails based on match results (e.g., from the <code>/match</code> endpoint). Emails are sent only if <code>proceed: true</code> is included.</p>

  <p><strong>Request JSON:</strong></p>
  <ul>
    <li><code>matches</code>: List of match result objects (with keys: email, job, resume, score, explanation)</li>
    <li><code>from_email</code>: Sender’s email address</li>
    <li><code>proceed</code>: Boolean to confirm sending emails</li>
  </ul>

  <p><strong>Logic:</strong></p>
  <ul>
    <li>If <code>score >= threshold</code>: Sends <strong>shortlisting email</strong></li>
    <li>If <code>score &lt; threshold</code>: Sends <strong>rejection email</strong></li>
  </ul>

  <p><strong>Example curl:</strong></p>
  <pre><code>curl -X POST http://127.0.0.1:5000/send-mails \
  -H "Content-Type: application/json" \
  -d '{
    "matches": [
      {
        "email": "candidate@example.com",
        "explanation": "Good Python and ML experience",
        "job": "Data_Scientist.txt",
        "resume": "resume.pdf",
        "score": 85
      }
    ],
    "from_email": "you@example.com",
    "proceed": true
  }'</code></pre>

  <h2>Config & Logs</h2>
  <p>Settings like score threshold and email templates are stored in <code>config.yaml</code>.</p>
  <p>Application logs are saved to <code>logs/app.log</code>.</p>

  <h2>Notes</h2>
  <ul>
    <li>Uses Gmail SMTP server by default (smtp.gmail.com:587)</li>
    <li>Emails are only sent if <code>EMAIL_PASSWORD</code> is set in the <code>.env</code> file</li>
    <li>For production, use a production-grade WSGI server instead of Flask’s built-in dev server</li>
  </ul>
</body>
</html>
