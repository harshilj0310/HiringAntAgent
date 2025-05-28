<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Resume-JD Matching API</title>
</head>
<body>
  <h1>Resume-JD Matching API</h1>
  <h2>Overview</h2>
  <p>API to parse resumes and job descriptions, match them by skills and experience, and optionally send email notifications.</p>

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
      <pre><code>flask run</code></pre>
    </li>
  </ol>

  <h2>API Endpoints</h2>

  <h3>POST /match</h3>
  <p>Upload resumes and job descriptions, with optional from_email.</p>
  <p><strong>Form Data:</strong> <code>resumes</code> (files), <code>jds</code> (files), <code>from_email</code> (string)</p>
  <p>Returns JSON list of match results with scores and explanations.</p>
  <p><strong>Example curl:</strong></p>
  <pre><code>curl -X POST http://127.0.0.1:5000/match \
  -F "resumes=@resume.pdf" -F "jds=@job.txt" -F "from_email=you@example.com"</code></pre>

  <h3>POST /send_email_permission</h3>
  <p>Sends emails based on match results and threshold if permission granted.</p>
  <p><strong>JSON Body:</strong> <code>{ "matches": [...], "from_email": "...", "send_email": true/false }</code></p>
  <p>Returns status of email sending.</p>
  <p><strong>Example curl:</strong></p>
  <pre><code>curl -X POST http://127.0.0.1:5000/send_email_permission \
  -H "Content-Type: application/json" \
  -d '{"matches": [...], "from_email": "you@example.com", "send_email": true}'</code></pre>

  <h2>Config & Logs</h2>
  <p>Settings stored in <code>config.yaml</code>. Logs saved in <code>logs/app.log</code>.</p>

  <h2>Notes</h2>
  <ul>
    <li>Uses Gmail SMTP server by default.</li>
    <li>For production, use a production-grade WSGI server instead of Flask dev server.</li>
  </ul>
</body>
</html>
