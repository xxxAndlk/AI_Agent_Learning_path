package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"sync"

	"github.com/philippgille/chromem-go"
)

const pageHTML = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>AI 技术栈答疑机器人</title>
<style>
 body{font-family:system-ui,"Microsoft YaHei",sans-serif;max-width:820px;margin:0 auto;padding:16px}
 #log{display:flex;flex-direction:column;gap:12px;margin-bottom:16px}
 .u{align-self:flex-end;background:#dbeafe;padding:8px 12px;border-radius:12px;max-width:80%;white-space:pre-wrap}
 .a{background:#f3f4f6;padding:8px 12px;border-radius:12px;max-width:80%;white-space:pre-wrap}
 .src{font-size:12px;color:#555;margin-top:8px;border-top:1px solid #ddd;padding-top:6px}
 form{display:flex;gap:8px;position:sticky;bottom:0;background:#fff;padding:8px 0}
 input{flex:1;padding:10px;font-size:15px}
 button{padding:10px 18px}
</style>
</head>
<body>
<h3>AI 应用开发技术栈 · 文档答疑机器人</h3>
<div id="log"></div>
<form id="f"><input id="q" placeholder="问点什么，比如：5.1 讲了哪几种切分策略？" autocomplete="off"><button>发送</button></form>
<script>
const sid = Math.random().toString(36).slice(2);
const log = document.getElementById('log');
const f = document.getElementById('f'), input = document.getElementById('q');
function bubble(cls){const d=document.createElement('div');d.className=cls;log.appendChild(d);return d;}
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  input.value = '';
  bubble('u').textContent = question;
  const answerEl = bubble('a');
  answerEl.textContent = '检索并生成中…';
  const res = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({session_id: sid, question})});
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '', first = true;
  while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    buf += decoder.decode(value, {stream:true});
    const events = buf.split('\n\n');
    buf = events.pop();
    for (const ev of events) {
      if (!ev.startsWith('data: ')) continue;
      const msg = JSON.parse(ev.slice(6));
      if (msg.type === 'delta') {
        if (first) { answerEl.textContent = ''; first = false; }
        answerEl.textContent += msg.text;
      } else if (msg.type === 'sources') {
        const div = document.createElement('div');
        div.className = 'src';
        div.textContent = '引用来源：' + msg.sources.map((s,i)=>'['+(i+1)+'] '+s).join('   ');
        answerEl.appendChild(div);
      } else if (msg.type === 'error') {
        answerEl.textContent = '出错了：' + msg.message;
      }
    }
  }
});
</script>
</body>
</html>`

var pageTmpl = template.Must(template.New("page").Parse(pageHTML))

type server struct {
	col      *chromem.Collection
	mu       sync.Mutex
	sessions map[string]*ChatSession
}

func (s *server) sessionFor(id string) *ChatSession {
	s.mu.Lock()
	defer s.mu.Unlock()
	sess, ok := s.sessions[id]
	if !ok {
		sess = newChatSession(s.col) // 每个浏览器会话一份历史
		s.sessions[id] = sess
	}
	return sess
}

func (s *server) handlePage(w http.ResponseWriter, r *http.Request) {
	if err := pageTmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func (s *server) handleAsk(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SessionID string `json:"session_id"`
		Question  string `json:"question"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Question == "" {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming unsupported", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")

	send := func(v any) {
		b, _ := json.Marshal(v)
		fmt.Fprintf(w, "data: %s\n\n", b)
		flusher.Flush()
	}

	sess := s.sessionFor(req.SessionID)
	_, hits, _, err := sess.Ask(r.Context(), req.Question, func(delta string) {
		send(map[string]any{"type": "delta", "text": delta})
	})
	if err != nil {
		send(map[string]any{"type": "error", "message": err.Error()})
		return
	}

	sources := make([]string, 0, len(hits))
	seen := map[string]bool{}
	for _, h := range hits {
		label := h.Source
		if h.Title != "" {
			label += " › " + h.Title
		}
		if !seen[label] {
			seen[label] = true
			sources = append(sources, label)
		}
	}
	send(map[string]any{"type": "sources", "sources": sources})
	send(map[string]any{"type": "done"})
}

func serve(addr string) error {
	col, err := openCollection()
	if err != nil {
		return err
	}
	if col.Count() == 0 {
		return fmt.Errorf("索引是空的，先运行 build 建索引")
	}

	s := &server{col: col, sessions: map[string]*ChatSession{}}
	mux := http.NewServeMux()
	mux.HandleFunc("/", s.handlePage)
	mux.HandleFunc("/api/ask", s.handleAsk)

	srv := &http.Server{Addr: addr, Handler: mux}
	log.Printf("打开 http://localhost%s", addr)
	return srv.ListenAndServe()
}
