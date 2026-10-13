import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

out_dir = r"c:\Users\thanh\Desktop\klcn\report_demo_screenshots"
os.makedirs(out_dir, exist_ok=True)
html_file = os.path.join(out_dir, "terminal_log.html")

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0b0e14;
    font-family: 'Consolas', 'Courier New', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 24px;
  }
  .terminal {
    width: 100%;
    max-width: 1200px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 10px;
    box-shadow: 0 16px 48px rgba(0,0,0,0.7);
    overflow: hidden;
  }
  .header {
    background: #161b22;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #30363d;
  }
  .dots {
    display: flex;
    gap: 8px;
    margin-right: 16px;
  }
  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .dot-red { background: #ff5f56; }
  .dot-yellow { background: #ffbd2e; }
  .dot-green { background: #27c93f; }
  .title {
    color: #8b949e;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    flex: 1;
    text-align: center;
  }
  .content {
    padding: 20px 24px;
    color: #c9d1d9;
    font-size: 13px;
    line-height: 1.6;
    overflow-x: auto;
  }
  .step-banner {
    color: #58a6ff;
    font-weight: bold;
    margin-top: 14px;
    margin-bottom: 4px;
    border-bottom: 1px dashed #30363d;
    padding-bottom: 2px;
  }
  .step-banner:first-child { margin-top: 0; }
  .time { color: #6e7681; }
  .info { color: #3fb950; font-weight: bold; }
  .root { color: #d29922; font-weight: bold; }
  .hiring { color: #38bdf8; font-weight: bold; }
  .mcp-client { color: #bc8cff; font-weight: bold; }
  .mcp-server { color: #f0883e; font-weight: bold; }
  .service { color: #79c0ff; }
  .data { color: #a5d6ff; }
  .json-key { color: #7ee787; }
  .json-val { color: #a5d6ff; }
  .prompt { color: #f0883e; }
</style>
</head>
<body>
<div class="terminal">
  <div class="header">
    <div class="dots">
      <div class="dot dot-red"></div>
      <div class="dot dot-yellow"></div>
      <div class="dot dot-green"></div>
    </div>
    <div class="title">bash - ai-agent-platform : Trace luồng thực thi Root Agent &rarr; Hiring Agent &rarr; MCP Client &rarr; MCP Server</div>
  </div>
  <div class="content">
    <div class="step-banner">&gt;&gt;&gt; [BƯỚC 1: KHỞI TẠO MCP SERVERS QUA STDIO RPC PROTOCOL]</div>
    <div><span class="time">2026-10-01 21:24:22</span> [<span class="info">INFO</span>] <span class="mcp-server">mcp.hiring</span>: Khởi động Hiring MCP Server với giao thức stdio (JSON-RPC 2.0)...</div>
    <div><span class="time">2026-10-01 21:24:22</span> [<span class="info">INFO</span>] <span class="mcp-client">MCP Client</span>: Kết nối thành công tới MCP server 'hiring' qua stdio pipe. Sẵn sàng gọi 4 tools.</div>
    <div><span class="time">2026-10-01 21:24:27</span> [<span class="info">INFO</span>] <span class="mcp-server">mcp.employee</span>: Khởi động Employee MCP Server với giao thức stdio (JSON-RPC 2.0)...</div>
    <div><span class="time">2026-10-01 21:24:27</span> [<span class="info">INFO</span>] <span class="mcp-client">MCP Client</span>: Kết nối thành công tới MCP server 'employee' qua stdio pipe. Sẵn sàng gọi 5 tools.</div>

    <div class="step-banner">&gt;&gt;&gt; [BƯỚC 2: USER REQUEST &rarr; ROOT AGENT INTENT ROUTING]</div>
    <div><span class="time">2026-10-01 22:01:14</span> [<span class="info">INFO</span>] <span class="service">fme.chat_service</span>: [ChatService] Bắt đầu xử lý tin nhắn: <span class="prompt">'Có bao nhiêu ứng viên đang chờ phỏng vấn?'</span></div>
    <div><span class="time">2026-10-01 22:01:14</span> [<span class="info">INFO</span>] <span class="root">fme.agent.root</span>: [RootAgent] Phân loại intent câu hỏi người dùng bằng LLM (Zero-shot Routing)...</div>
    <div><span class="time">2026-10-01 22:01:14</span> [<span class="info">INFO</span>] <span class="root">fme.agent.root</span>: [RootAgent] Kết quả: intent='hiring', điều phối request sang DomainAgent <span class="hiring">'hiring'</span></div>

    <div class="step-banner">&gt;&gt;&gt; [BƯỚC 3: HIRING AGENT TOOL SELECTION &amp; PARAMETER EXTRACTION]</div>
    <div><span class="time">2026-10-01 22:01:14</span> [<span class="info">INFO</span>] <span class="hiring">fme.agent.hiring</span>: [DomainAgent:Hiring] LLM trích xuất công cụ phù hợp với schema MCP...</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="hiring">fme.agent.hiring</span>: [DomainAgent:Hiring] Trích xuất thành công: tool=<span class="mcp-server">'search_candidates'</span>, params={<span class="json-key">'status'</span>: <span class="json-val">'pending_interview'</span>}</div>

    <div class="step-banner">&gt;&gt;&gt; [BƯỚC 4: AGENT &rarr; MCP CLIENT &rarr; MCP SERVER &rarr; TOOL EXECUTION]</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="mcp-client">fme.agent.hiring</span>: [DomainAgent:Hiring] Gửi lệnh gọi tool qua MCP Client tới server 'hiring'...</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="mcp-server">mcp.hiring.server</span>: [MCP Server] Nhận RPC method 'tools/call' | Tool: 'search_candidates'</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="mcp-server">mcp.hiring.validators</span>: [Validator] Tham số status='pending_interview' hợp lệ theo enum CandidatesStatus.</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="mcp-server">mcp.hiring.tools</span>: [HiringTools] Tìm thấy 3 ứng viên thỏa điều kiện (UV001, UV003, UV005).</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="mcp-client">fme.agent.hiring</span>: [DomainAgent:Hiring] Nhận kết quả từ MCP Tool: success=True, total_found=3</div>

    <div class="step-banner">&gt;&gt;&gt; [BƯỚC 5: RESPONSE SYNTHESIS &amp; CHATBOT UI PRESENTATION]</div>
    <div><span class="time">2026-10-01 22:01:18</span> [<span class="info">INFO</span>] <span class="hiring">fme.agent.hiring</span>: [DomainAgent:Hiring] Tổng hợp kết quả thành văn bản Markdown chuyên nghiệp bằng LLM...</div>
    <div><span class="time">2026-10-01 22:01:25</span> [<span class="info">INFO</span>] <span class="hiring">fme.agent.hiring</span>: [DomainAgent:Hiring] Hoàn thành tổng hợp câu trả lời (Bảng 7 cột danh sách ứng viên).</div>
    <div><span class="time">2026-10-01 22:01:25</span> [<span class="info">INFO</span>] <span class="service">fme.chat_service</span>: [ChatService] Hoàn thành xử lý tin nhắn (success=True, reply_length=934, metadata.routed_by='root_agent').</div>
  </div>
</div>
</body>
</html>
"""

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Written {html_file}")

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,820')

service = Service(r"C:\Users\thanh\.cache\selenium\chromedriver\win64\154.0.8037.92\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(f"file:///{html_file.replace(os.sep, '/')}")
    time.sleep(2)
    p9_path = os.path.join(out_dir, "09_mcp_flow_terminal_log.png")
    driver.save_screenshot(p9_path)
    print(f">>> Successfully generated {p9_path}")
finally:
    driver.quit()
