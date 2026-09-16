import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  GraduationCap,
  Briefcase,
  Terminal,
  CheckSquare,
  AlertTriangle,
  Clock,
  ExternalLink,
  Play,
  RefreshCw,
  Bell,
  Folder,
  FolderCheck,
  Code2,
  BookOpen,
  Activity,
  Plus,
  CheckCircle2,
  Circle,
  FileText,
  Layers,
  ShieldCheck,
  Server,
  Bot,
  Sparkles,
  Zap,
  Send,
  Copy,
  Check,
  X,
  Maximize2,
  RotateCcw,
  Eye
} from 'lucide-react';

interface Subject {
  id: number;
  name: string;
  code?: string;
  attendance_percentage: number;
  last_synced?: string;
  folder_name?: string;
  local_path?: string;
}

interface FolderInventoryItem {
  name: string;
  path: string;
  files_count: number;
  online_resources_count: number;
  missing_resources_count: number;
  description: string;
  sample_files: string[];
}

interface Assignment {
  id: number;
  subject_id: number;
  subject_name: string;
  title: string;
  deadline: string;
  is_lab: number;
  status: string;
  local_lab_dir?: string;
}

interface DocumentItem {
  id: number;
  subject_id: number;
  subject_name: string;
  file_name: string;
  local_path: string;
  upload_date?: string;
  summary_path?: string;
}

interface CareerItem {
  id: number;
  category: string;
  name: string;
  deadline: string;
  benefits_credits: string;
  status: string;
  url: string;
  eligibility: string;
  applied_at?: string;
  proof_screenshot?: string;
}

interface TodoItem {
  id: number;
  title: string;
  category: string;
  due_date: string;
  completed: number;
}

interface AgentLog {
  id: number;
  timestamp: string;
  level: string;
  message: string;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  text: string;
  tool_used?: string;
  details?: any;
}

const QUICK_PROMPTS = [
  { label: '⚡ Auto Apply to All Open Opportunities', query: "auto apply to all opportunities" },
  { label: '⚡ Ask Antigravity: Create NLP README', query: "Open Antigravity and ask it to create the README for today's NLP class." },
  { label: '⚡ Delegate: Train PyTorch Neural Net', query: "Train a PyTorch neural network for transformer attention mechanism" },
  { label: '📊 Check My Attendance & Risk', query: "Check my attendance" },
  { label: '⏳ What Assignments are Pending?', query: "What assignments are pending?" },
  { label: '📂 Open Deep Learning Folder', query: "Open Deep Learning folder" },
  { label: '💻 Run: git status', query: "run git status" },
  { label: '🔄 Rerun DigiCampus Sync', query: "Rerun full digicampus audit and sync" },
  { label: '🏆 Active Competitions & Hackathons', query: "What new opportunities or hackathons appeared today?" },
  { label: '📌 What Should I Work on Today?', query: "What do I need to do today?" },
  { label: '💻 Run: python --version', query: "run python --version" },
];

function renderFormattedMarkdown(content: string) {
  const parts = content.split(/(```[\s\S]*?```)/g);
  return parts.map((part, index) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const lines = part.slice(3, -3).trim().split('\n');
      const lang = lines[0].trim();
      const codeText = lang && !lines[0].includes(' ') ? lines.slice(1).join('\n') : lines.join('\n');
      return (
        <div key={index} className="my-2 rounded-md bg-zinc-950 p-3 font-mono text-[11px] text-zinc-300 border border-zinc-800 overflow-x-auto">
          <pre className="whitespace-pre">{codeText}</pre>
        </div>
      );
    }
    return (
      <span key={index}>
        {part.split('\n').map((line, lIdx) => {
          let lineContent = line;
          const isQuote = line.startsWith('> ');
          if (isQuote) lineContent = line.slice(2);
          const isBullet = line.startsWith('- ') || line.startsWith('* ');
          if (isBullet) lineContent = line.slice(2);

          return (
            <div
              key={lIdx}
              className={`${isQuote ? 'border-l-2 border-amber-500/80 pl-2.5 my-1 text-zinc-300 italic' : ''} ${
                isBullet ? 'flex items-start space-x-1.5 ml-2' : ''
              }`}
            >
              {isBullet && <span className="text-zinc-500 font-bold">•</span>}
              <span dangerouslySetInnerHTML={{
                __html: lineContent
                  .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>')
                  .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded bg-zinc-800 text-zinc-200 font-mono text-[10px]">$1</code>')
              }} />
            </div>
          );
        })}
      </span>
    );
  });
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'copilot' | 'academic' | 'resources' | 'career' | 'desktop' | 'todos' | 'logs'>('copilot');
  const [wsConnected, setWsConnected] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatusMsg, setSyncStatusMsg] = useState<string>('');
  const [syncProgress, setSyncProgress] = useState<{ current: number; total: number; subject: string } | null>(null);
  const [lastSyncTime, setLastSyncTime] = useState<string>('Live Synced (Sept 2026)');

  // Chat Copilot states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: "⚡ **Student OS Autonomous Copilot & Universal Workstation Controller**\n\nI am your centralized workstation AI with direct PC control, DigiCampus academic auditing, and autonomous self-empowerment via Google Antigravity.\n\n- 💻 **PC Control:** Run commands (`run git status`, `run python ...`), launch apps (`open vs code`, `open deep learning`).\n- 📊 **Academic Engine:** Live attendance breakdown, assignment deadlines, local course folders.\n- ⚡ **Antigravity Power Protocol:** If you ask me to perform a complex task, build new code, train models, or if I cannot do it with local tools, I will write a custom directive in your style (`USER_PROFILE.md`), copy it to clipboard, and open Google Antigravity (`Antigravity.exe`) to empower the workstation and perform the task!",
      tool_used: 'identity_overview'
    }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [copilotDrawerOpen, setCopilotDrawerOpen] = useState(false);
  const [copiedPromptId, setCopiedPromptId] = useState<string | null>(null);
  const chatContainerRef = React.useRef<HTMLDivElement>(null);
  const chatDrawerContainerRef = React.useRef<HTMLDivElement>(null);

  // Data states
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [folders, setFolders] = useState<FolderInventoryItem[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [careerItems, setCareerItems] = useState<CareerItem[]>([]);
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [logs, setLogs] = useState<AgentLog[]>([]);

  // Auto-Apply states
  const [autoApplyRunning, setAutoApplyRunning] = useState(false);
  const [autoApplyStatusMsg, setAutoApplyStatusMsg] = useState<string>('');
  const [autoApplyProgress, setAutoApplyProgress] = useState<{ current: number; total: number; opportunity: string } | null>(null);
  const [autoApplyInfo, setAutoApplyInfo] = useState<any>(null);
  const [activeScreenshotModal, setActiveScreenshotModal] = useState<string | null>(null);

  // Desktop command states
  const [cmdInput, setCmdInput] = useState('python --version');
  const [cmdOutput, setCmdOutput] = useState('');
  const [cmdRunning, setCmdRunning] = useState(false);

  // New todo input
  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoCategory, setNewTodoCategory] = useState('Academic');

  // Lab modal
  const [selectedSubjectForLab, setSelectedSubjectForLab] = useState('');
  const [labNumber, setLabNumber] = useState('1');
  const [labProblem, setLabProblem] = useState('Data Pipeline & Model Evaluation');
  const [labScaffolding, setLabScaffolding] = useState(false);

  // Subject filter
  const [selectedSubjectFilter, setSelectedSubjectFilter] = useState<string>('ALL');

  // WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    let socket: WebSocket | null = null;

    try {
      socket = new WebSocket(wsUrl);
      socket.onopen = () => {
        setWsConnected(true);
        socket?.send(JSON.stringify({ type: 'PING' }));
      };
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'SYNC_STARTED') {
            setSyncing(true);
            setSyncStatusMsg(data.message || 'Connecting to DigiCampus session...');
            setSyncProgress(null);
          } else if (data.type === 'SYNC_PROGRESS') {
            setSyncing(true);
            setSyncStatusMsg(data.message || `Auditing ${data.subject}...`);
            if (data.current && data.total) {
              setSyncProgress({ current: data.current, total: data.total, subject: data.subject || '' });
            }
          } else if (data.type === 'SYNC_COMPLETED') {
            setSyncing(false);
            setSyncStatusMsg(data.message || 'Complete audit finished.');
            if (data.timestamp) setLastSyncTime(data.timestamp);
            setSyncProgress(null);
            fetchAcademicData();
            fetchLogs();
          } else if (data.type === 'LAB_SCAFFOLDED') {
            fetchAcademicData();
            fetchLogs();
          } else if (data.type === 'AUTO_APPLY_PROGRESS') {
            setAutoApplyRunning(true);
            setAutoApplyStatusMsg(`Applying to ${data.opportunity} (${data.current}/${data.total})...`);
            setAutoApplyProgress({ current: data.current, total: data.total, opportunity: data.opportunity });
          } else if (data.type === 'AUTO_APPLY_COMPLETED' || data.type === 'CAREER_OPPORTUNITIES_UPDATED') {
            setAutoApplyRunning(false);
            setAutoApplyStatusMsg('Auto-apply pipeline run completed!');
            setAutoApplyProgress(null);
            fetchCareerData();
            fetchAutoApplyStatus();
            fetchLogs();
          }
        } catch (e) {
          console.error(e);
        }
      };
      socket.onclose = () => setWsConnected(false);
      socket.onerror = () => setWsConnected(false);
    } catch (e) {
      console.warn('WebSocket connection not established:', e);
    }

    return () => {
      if (socket) socket.close();
    };
  }, []);

  // Fetch initial data
  useEffect(() => {
    fetchAcademicData();
    fetchCareerData();
    fetchTodos();
    fetchLogs();
    fetchAutoApplyStatus();
  }, []);

  const fetchAcademicData = async () => {
    try {
      const res = await axios.get('/api/academic/overview');
      setSubjects(res.data.subjects || []);
      setAssignments(res.data.assignments || []);
      setDocuments(res.data.documents || []);
      setFolders(res.data.folders || []);
      if (res.data.subjects && res.data.subjects.length > 0 && !selectedSubjectForLab) {
        setSelectedSubjectForLab(res.data.subjects[0].name);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchCareerData = async () => {
    try {
      const res = await axios.get('/api/career/radar');
      setCareerItems(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchTodos = async () => {
    try {
      const res = await axios.get('/api/todos');
      setTodos(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get('/api/logs');
      setLogs(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAutoApplyStatus = async () => {
    try {
      const res = await axios.get('/api/auto-apply/status');
      setAutoApplyInfo(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const triggerAutoApplyAll = async () => {
    try {
      setAutoApplyRunning(true);
      setAutoApplyStatusMsg('Initiating autonomous auto-apply with latest resume...');
      await axios.post('/api/auto-apply/run', { run_all: true });
    } catch (err) {
      console.error(err);
      setAutoApplyRunning(false);
    }
  };

  const triggerAutoApplySingle = async (oppId: number) => {
    try {
      setAutoApplyRunning(true);
      setAutoApplyStatusMsg(`Applying autonomously to opportunity #${oppId}...`);
      await axios.post(`/api/auto-apply/opportunity/${oppId}`);
      await fetchCareerData();
      await fetchAutoApplyStatus();
    } catch (err) {
      console.error(err);
    } finally {
      setAutoApplyRunning(false);
    }
  };

  const triggerSync = async () => {
    setSyncing(true);
    setSyncStatusMsg('Connecting to DigiCampus session and auditing all subjects...');
    setSyncProgress(null);
    try {
      await axios.post('/api/academic/sync');
    } catch (err: any) {
      setSyncing(false);
      setSyncStatusMsg(`Sync error: ${err.message}`);
    }
  };

  const toggleTodo = async (id: number) => {
    try {
      await axios.patch(`/api/todos/${id}/toggle`);
      fetchTodos();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodoTitle.trim()) return;
    try {
      await axios.post('/api/todos', {
        title: newTodoTitle,
        category: newTodoCategory,
        due_date: new Date().toISOString().split('T')[0],
        completed: 0
      });
      setNewTodoTitle('');
      fetchTodos();
    } catch (err) {
      console.error(err);
    }
  };

  const runCommand = async () => {
    setCmdRunning(true);
    try {
      const res = await axios.post('/api/desktop/execute', { command: cmdInput });
      setCmdOutput(res.data.output || (res.data.success ? 'Command executed with code 0.' : res.data.error));
      fetchLogs();
    } catch (err: any) {
      setCmdOutput(`Execution Error: ${err.message}`);
    } finally {
      setCmdRunning(false);
    }
  };

  const launchApp = async (appName: string, path: string = '') => {
    try {
      await axios.post('/api/desktop/launch', { app: appName, path });
      fetchLogs();
    } catch (err) {
      console.error(err);
    }
  };

  const scaffoldLab = async () => {
    setLabScaffolding(true);
    try {
      await axios.post('/api/academic/scaffold-lab', {
        subject_name: selectedSubjectForLab,
        lab_number: labNumber,
        problem_title: labProblem,
        language: 'python'
      });
      fetchAcademicData();
      fetchLogs();
    } catch (err) {
      console.error(err);
    } finally {
      setLabScaffolding(false);
    }
  };

  const sendTestAlert = async () => {
    try {
      await axios.post('/api/notifications/test');
      alert('Alert ping dispatched via ntfy.sh!');
      fetchLogs();
    } catch (err) {
      alert('Failed to send push alert.');
    }
  };

  const sendChatMessage = async (customQuery?: string, forceAntigravity: boolean = false) => {
    const q = (customQuery !== undefined ? customQuery : chatInput).trim();
    if (!q || chatLoading) return;

    const finalQuery = forceAntigravity && !q.toLowerCase().includes('antigravity')
      ? `Ask Antigravity to: ${q}`
      : q;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: finalQuery
    };

    setChatMessages((prev) => [...prev, userMsg]);
    if (!customQuery) setChatInput('');
    setChatLoading(true);

    try {
      const res = await axios.post('/api/chat', { query: finalQuery });
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: res.data.response || 'Action processed.',
        tool_used: res.data.tool_used,
        details: res.data.details
      };
      setChatMessages((prev) => [...prev, assistantMsg]);
      fetchLogs();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `⚠️ **Execution Error:** ${err.response?.data?.detail || err.message}`,
        tool_used: 'error'
      };
      setChatMessages((prev) => [...prev, errorMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPromptId(id);
    setTimeout(() => setCopiedPromptId(null), 2500);
  };

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
    if (chatDrawerContainerRef.current) {
      chatDrawerContainerRef.current.scrollTop = chatDrawerContainerRef.current.scrollHeight;
    }
  }, [chatMessages, chatLoading]);

  const filteredDocuments = selectedSubjectFilter === 'ALL'
    ? documents
    : documents.filter(d => d.subject_name === selectedSubjectFilter);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-100">
              <Layers className="h-5 w-5 text-zinc-200" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-base tracking-tight text-white">
                  Student OS
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 font-medium">
                  v2.4 Workstation
                </span>
              </div>
              <p className="text-xs text-zinc-400">Universal AI University • B.Tech CS (AI & ML)</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Live Feed Status */}
            <div className="hidden sm:flex items-center space-x-2 text-xs font-mono px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800">
              <span className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
              <span className={wsConnected ? 'text-emerald-400' : 'text-zinc-400'}>
                {wsConnected ? 'LIVE FEED' : 'STANDBY'}
              </span>
            </div>

            {/* Test Alert Button */}
            <button
              onClick={sendTestAlert}
              className="px-2.5 py-1.5 rounded text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 transition flex items-center space-x-1.5 border border-zinc-700"
              title="Send notification ping"
            >
              <Bell className="h-3.5 w-3.5 text-zinc-400" />
              <span>Ping Alert</span>
            </button>

            {/* Main Full Sync & Update Button */}
            <button
              onClick={triggerSync}
              disabled={syncing}
              className="px-3.5 py-1.5 rounded text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition flex items-center space-x-1.5 border border-blue-500 shadow-sm disabled:opacity-50"
              title="Rerun complete DigiCampus crawler and file audit"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${syncing ? 'animate-spin' : ''}`} />
              <span>
                {syncing
                  ? (syncProgress ? `Auditing (${syncProgress.current}/${syncProgress.total})...` : 'Syncing...')
                  : 'Rerun Full Update'}
              </span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 overflow-x-auto border-t border-zinc-800">
          {[
            { id: 'copilot', label: 'AI Copilot & Antigravity', icon: Bot, isSpecial: true },
            { id: 'academic', label: 'Classroom & Academics', icon: GraduationCap },
            { id: 'resources', label: 'Course Materials & Files', icon: FolderCheck },
            { id: 'career', label: 'Career & Opportunities', icon: Briefcase },
            { id: 'desktop', label: 'Desktop Terminal', icon: Terminal },
            { id: 'todos', label: 'Action Items', icon: CheckSquare },
            { id: 'logs', label: 'System Audit Logs', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-2.5 px-3.5 text-xs font-medium border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-blue-500 text-blue-400 bg-zinc-800/40 font-semibold'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${tab.isSpecial ? 'text-amber-400 animate-pulse' : ''}`} />
                <span>{tab.label}</span>
                {tab.isSpecial && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-amber-950 text-amber-300 border border-amber-800">
                    ⚡ ULTIMATE
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </header>

      {/* Live Sync Progress Banner */}
      {syncing && (
        <div className="bg-zinc-900 border-b border-blue-900/60 px-4 py-2.5 sm:px-6">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
            <div className="flex items-center space-x-2 text-blue-400 font-mono">
              <RefreshCw className="h-3.5 w-3.5 animate-spin flex-shrink-0" />
              <span className="truncate">{syncStatusMsg}</span>
            </div>
            {syncProgress && (
              <div className="flex items-center space-x-3 flex-shrink-0">
                <span className="text-zinc-400 font-mono text-[11px]">
                  Course {syncProgress.current} of {syncProgress.total} ({Math.round((syncProgress.current / syncProgress.total) * 100)}%)
                </span>
                <div className="w-28 bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-blue-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${(syncProgress.current / syncProgress.total) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full">
        {/* TAB 0: AUTONOMOUS COPILOT & ANTIGRAVITY */}
        {activeTab === 'copilot' && (
          <div className="space-y-6">
            {/* Top Copilot Capability Banner */}
            <div className="p-5 rounded-xl bg-gradient-to-r from-zinc-900 via-zinc-900 to-blue-950/40 border border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center space-x-2.5">
                  <div className="h-8 w-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-white tracking-tight flex items-center space-x-2">
                      <span>Student OS Ultimate Autonomous Copilot</span>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                        PC Control & Antigravity Bridge
                      </span>
                    </h2>
                    <p className="text-xs text-zinc-400">
                      Orchestrating desktop CLI, local subject files, DigiCampus sync, and autonomous Google Antigravity delegation.
                    </p>
                  </div>
                </div>
              </div>

              {/* Status pills */}
              <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
                <span className="px-2.5 py-1 rounded bg-zinc-800/80 text-zinc-300 border border-zinc-700 flex items-center space-x-1.5">
                  <Terminal className="h-3 w-3 text-emerald-400" />
                  <span>CLI Shell: Active</span>
                </span>
                <span className="px-2.5 py-1 rounded bg-zinc-800/80 text-zinc-300 border border-zinc-700 flex items-center space-x-1.5">
                  <Zap className="h-3 w-3 text-amber-400" />
                  <span>Antigravity Bridge: Online</span>
                </span>
                <button
                  onClick={() => setChatMessages([chatMessages[0]])}
                  className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 border border-zinc-700 transition flex items-center space-x-1"
                  title="Clear chat history"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Reset</span>
                </button>
              </div>
            </div>

            {/* Quick Action Suggestion Pills */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
                <span className="flex items-center space-x-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-blue-400" />
                  <span>Quick Workstation Directives & Queries:</span>
                </span>
                <span className="text-[11px] font-mono text-zinc-500">1-click execution</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {QUICK_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => sendChatMessage(p.query)}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white transition flex items-center space-x-1.5"
                  >
                    <span>{p.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Main Chat Stream Box */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 backdrop-blur flex flex-col h-[580px]">
              {/* Messages Container */}
              <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 font-sans text-xs">
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    {/* Message Header */}
                    <div className="flex items-center space-x-2 mb-1 text-[11px] text-zinc-500 font-mono">
                      <span>{msg.sender === 'user' ? 'User Workstation' : 'Autonomous Copilot'}</span>
                      <span>•</span>
                      <span>{msg.timestamp}</span>
                      {msg.tool_used && (
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono ${
                          msg.tool_used === 'delegate_to_antigravity'
                            ? 'bg-amber-950/80 text-amber-300 border border-amber-800/80 font-semibold'
                            : msg.tool_used === 'execute_command'
                            ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/80'
                            : msg.tool_used === 'open_application'
                            ? 'bg-blue-950/80 text-blue-300 border border-blue-800/80'
                            : 'bg-zinc-800 text-zinc-300 border border-zinc-700'
                        }`}>
                          [TOOL: {msg.tool_used}]
                        </span>
                      )}
                    </div>

                    {/* Message Body */}
                    <div
                      className={`max-w-[85%] rounded-xl p-4 leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-blue-600 text-white shadow-md'
                          : 'bg-zinc-900 border border-zinc-800 text-zinc-200'
                      }`}
                    >
                      {/* Markdown formatted text */}
                      <div className="whitespace-pre-wrap font-sans text-xs space-y-1">
                        {renderFormattedMarkdown(msg.text)}
                      </div>

                      {/* Antigravity Delegation Card */}
                      {msg.tool_used === 'delegate_to_antigravity' && msg.details && (
                        <div className="mt-3.5 p-3.5 rounded-lg bg-amber-950/30 border border-amber-500/40 space-y-2.5">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2 text-amber-300 font-semibold text-xs">
                              <Zap className="h-4 w-4 animate-pulse text-amber-400" />
                              <span>Google Antigravity Directive Bridge</span>
                            </div>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-900/60 text-amber-200 border border-amber-700/60">
                              {msg.details.launched ? 'Launched in IDE' : 'Ready'}
                            </span>
                          </div>

                          <div className="text-[11px] font-mono text-zinc-300 space-y-1 bg-zinc-950/70 p-2.5 rounded border border-zinc-800">
                            <div><span className="text-zinc-500">File:</span> {msg.details.prompt_file}</div>
                            <div><span className="text-zinc-500">Status:</span> {msg.details.message}</div>
                            <div><span className="text-zinc-500">Clipboard:</span> {msg.details.clipboard_copied ? 'Copied to clipboard' : 'Available for manual copy'}</div>
                          </div>

                          <div className="flex flex-wrap items-center gap-2 pt-1">
                            <button
                              onClick={() => copyToClipboard(msg.details?.prompt_preview || '', msg.id)}
                              className="px-2.5 py-1.5 rounded text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 transition flex items-center space-x-1.5"
                            >
                              {copiedPromptId === msg.id ? (
                                <>
                                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                                  <span className="text-emerald-300">Prompt Copied!</span>
                                </>
                              ) : (
                                <>
                                  <Copy className="h-3.5 w-3.5 text-zinc-400" />
                                  <span>Copy Directive</span>
                                </>
                              )}
                            </button>

                            <button
                              onClick={() => launchApp('antigravity', msg.details?.prompt_file)}
                              className="px-2.5 py-1.5 rounded text-xs font-medium bg-amber-600 hover:bg-amber-500 text-white transition flex items-center space-x-1.5 shadow-sm"
                            >
                              <Play className="h-3.5 w-3.5" />
                              <span>Re-Open in Antigravity</span>
                            </button>

                            <button
                              onClick={() => launchApp('explorer', 'Student_OS/backend/data/antigravity_prompts')}
                              className="px-2.5 py-1.5 rounded text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 transition flex items-center space-x-1.5"
                            >
                              <Folder className="h-3.5 w-3.5 text-zinc-400" />
                              <span>Open Prompts Folder</span>
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Desktop Command Execution Details */}
                      {msg.tool_used === 'execute_command' && msg.details && (
                        <div className="mt-2.5 flex items-center justify-between text-[11px] font-mono text-zinc-400 bg-zinc-950/60 px-3 py-1.5 rounded border border-zinc-800">
                          <span>Exit Code: {msg.details.success ? '0 (Success)' : 'Non-zero'}</span>
                          <button
                            onClick={() => copyToClipboard(msg.details?.result || '', msg.id)}
                            className="hover:text-white flex items-center space-x-1 text-zinc-400"
                          >
                            <Copy className="h-3 w-3" />
                            <span>Copy Output</span>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Loading indicator */}
                {chatLoading && (
                  <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 bg-zinc-900/90 border border-zinc-800 rounded-lg p-3 max-w-md animate-pulse">
                    <RefreshCw className="h-4 w-4 animate-spin flex-shrink-0" />
                    <span>Autonomous Copilot is orchestrating system tools & executing...</span>
                  </div>
                )}
              </div>

              {/* Chat Input Bar */}
              <div className="p-3 sm:p-4 border-t border-zinc-800 bg-zinc-900/90 rounded-b-xl">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    sendChatMessage();
                  }}
                  className="flex flex-col sm:flex-row gap-2"
                >
                  <div className="relative flex-1">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask anything, control PC (e.g., 'run git status', 'check attendance', or 'train a neural net')..."
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition font-sans pr-10"
                    />
                    {chatInput && (
                      <button
                        type="button"
                        onClick={() => setChatInput('')}
                        className="absolute right-3 top-2.5 text-zinc-500 hover:text-zinc-300"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      type="submit"
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-4 py-2.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition flex items-center space-x-1.5 border border-blue-500 shadow-sm disabled:opacity-50"
                    >
                      <Send className="h-3.5 w-3.5" />
                      <span>Execute</span>
                    </button>

                    <button
                      type="button"
                      disabled={chatLoading || !chatInput.trim()}
                      onClick={() => sendChatMessage(undefined, true)}
                      className="px-3.5 py-2.5 rounded-lg text-xs font-semibold text-amber-200 bg-amber-950/70 hover:bg-amber-900/80 transition flex items-center space-x-1.5 border border-amber-700/80 shadow-sm disabled:opacity-50"
                      title="Force generation of an Antigravity directive and launch Antigravity IDE"
                    >
                      <Zap className="h-3.5 w-3.5 text-amber-400" />
                      <span>Escalate to Antigravity</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: ACADEMIC & CLASSROOM */}
        {activeTab === 'academic' && (
          <div className="space-y-6">
            {/* Status Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800">
                <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-1">
                  <span>ENROLLED COURSES</span>
                  <BookOpen className="h-4 w-4 text-blue-400" />
                </div>
                <div className="text-2xl font-bold text-white">{subjects.length} Subjects</div>
                <p className="text-xs text-zinc-500 mt-1">3rd Year Semester 5 Curriculum</p>
              </div>

              <div className="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800">
                <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-1">
                  <span>PENDING ASSIGNMENTS</span>
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-bold text-emerald-400">0 Ongoing</div>
                <p className="text-xs text-zinc-500 mt-1">All classroom assignments caught up</p>
              </div>

              <div className="p-4 rounded-lg bg-zinc-900/70 border border-zinc-800">
                <div className="flex items-center justify-between text-zinc-400 text-xs font-medium mb-1">
                  <span>LOCAL WORKSPACE DIRECTORY</span>
                  <FolderCheck className="h-4 w-4 text-zinc-300" />
                </div>
                <div className="text-sm font-mono text-zinc-200 truncate">Desktop\3rd Year</div>
                <p className="text-xs text-zinc-400 mt-1">
                  {folders.length} Subject Folders • {folders.reduce((acc, f) => acc + f.files_count, 0)} Academic Files
                </p>
              </div>
            </div>

            {/* Subject Overview Header with Rerun Button */}
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 flex items-center space-x-2">
                  <GraduationCap className="h-4 w-4 text-zinc-300" />
                  <span>Enrolled Subjects & Attendance Monitor</span>
                </h2>
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono text-zinc-500">Threshold: 75.0% Required</span>
                  <button
                    onClick={triggerSync}
                    disabled={syncing}
                    className="px-2.5 py-1 rounded text-[11px] font-medium text-zinc-300 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 flex items-center space-x-1 transition disabled:opacity-50"
                  >
                    <RefreshCw className={`h-3 w-3 ${syncing ? 'animate-spin' : ''}`} />
                    <span>Rerun Update</span>
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {subjects.map((subj) => {
                  const isSafe = subj.attendance_percentage >= 75.0;
                  return (
                    <div
                      key={subj.id}
                      className={`p-4 rounded-lg border bg-zinc-900/60 transition flex flex-col justify-between ${
                        isSafe ? 'border-zinc-800 hover:border-zinc-700' : 'border-rose-900/60 bg-rose-950/20'
                      }`}
                    >
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-semibold text-zinc-200 text-sm leading-snug pr-2">
                            {subj.name}
                          </span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded font-mono font-bold ${
                              isSafe
                                ? 'bg-zinc-800 text-zinc-200 border border-zinc-700'
                                : 'bg-rose-900/50 text-rose-300 border border-rose-700'
                            }`}
                          >
                            {subj.attendance_percentage.toFixed(1)}%
                          </span>
                        </div>

                        {subj.code && (
                          <span className="text-[11px] font-mono text-zinc-500 block mb-3">
                            [{subj.code}]
                          </span>
                        )}

                        <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden mb-3">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${
                              isSafe ? 'bg-zinc-300' : 'bg-rose-500'
                            }`}
                            style={{ width: `${Math.min(subj.attendance_percentage, 100)}%` }}
                          />
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80 text-xs">
                        <span className="text-zinc-500 font-mono text-[11px]">
                          {subj.last_synced ? `Synced ${subj.last_synced.split('T')[0]}` : 'Active'}
                        </span>
                        <button
                          onClick={() => launchApp('explorer', subj.local_path || `c:\\Users\\Shaunak Rane\\Desktop\\3rd Year`)}
                          className="text-zinc-400 hover:text-white flex items-center space-x-1"
                        >
                          <Folder className="h-3 w-3" />
                          <span>Open Folder</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Submissions & Lab Workspace */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-zinc-200 flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-zinc-400" />
                    <span>Classroom Submissions & Verification</span>
                  </h3>
                  <span className="text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-800/60">
                    STATUS: ALL CAUGHT UP
                  </span>
                </div>

                <div className="space-y-2.5">
                  <div className="p-3 rounded bg-zinc-950/80 border border-zinc-800/80 flex items-start space-x-3">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-medium text-xs text-zinc-200">
                        No ongoing assignments are pending on DigiCampus
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-0.5">
                        All modules across NLP, AWT, Time Series, SEPM, AJP, and Big Data Analytics have 0 open tasks.
                      </p>
                    </div>
                  </div>

                  {assignments.slice(0, 5).map((asg) => (
                    <div
                      key={asg.id}
                      className="p-3 rounded bg-zinc-950/50 border border-zinc-800/60 flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-medium text-zinc-200">{asg.title}</div>
                        <div className="text-[11px] text-zinc-500 mt-0.5">
                          {asg.subject_name} • Due: {asg.deadline || 'Completed'}
                        </div>
                      </div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {asg.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Lab Scaffolding Utility */}
              <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-5">
                <h3 className="text-sm font-semibold text-zinc-200 mb-2 flex items-center space-x-2">
                  <Code2 className="h-4 w-4 text-blue-400" />
                  <span>Lab Environment Workspace Generator</span>
                </h3>
                <p className="text-xs text-zinc-400 mb-4">
                  Scaffolds starter code, docstrings, and tests inside <code className="font-mono text-zinc-300">Desktop\3rd Year\&lt;Subject&gt;\labs\</code>.
                </p>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="block font-medium text-zinc-400 mb-1">Target Subject</label>
                    <select
                      value={selectedSubjectForLab}
                      onChange={(e) => setSelectedSubjectForLab(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600"
                    >
                      {subjects.map((s) => (
                        <option key={s.id} value={s.name}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-medium text-zinc-400 mb-1">Lab Index</label>
                      <input
                        type="text"
                        value={labNumber}
                        onChange={(e) => setLabNumber(e.target.value)}
                        className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600"
                      />
                    </div>
                    <div>
                      <label className="block font-medium text-zinc-400 mb-1">Language</label>
                      <select className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600">
                        <option value="python">Python</option>
                        <option value="c">C / C++</option>
                        <option value="java">Java</option>
                        <option value="ts">TypeScript</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block font-medium text-zinc-400 mb-1">Problem / Experiment Title</label>
                    <input
                      type="text"
                      value={labProblem}
                      onChange={(e) => setLabProblem(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600"
                    />
                  </div>

                  <button
                    onClick={scaffoldLab}
                    disabled={labScaffolding}
                    className="w-full mt-2 py-2 rounded text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition flex items-center justify-center space-x-2"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    <span>{labScaffolding ? 'Generating...' : 'Scaffold Lab Directory'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: COURSE MATERIALS & FILES */}
        {activeTab === 'resources' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 flex items-center space-x-2">
                  <FolderCheck className="h-4 w-4 text-zinc-300" />
                  <span>Academic Materials & Local Folder Inventory</span>
                </h2>
                <p className="text-xs text-zinc-400">
                  DigiCampus resources cross-referenced with <code className="font-mono text-zinc-300">Desktop\3rd Year</code>
                </p>
              </div>

              <div className="flex items-center space-x-3 text-xs">
                <button
                  onClick={triggerSync}
                  disabled={syncing}
                  className="px-3 py-1.5 rounded text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition flex items-center space-x-1.5 border border-blue-500 shadow-sm disabled:opacity-50"
                  title="Rerun complete DigiCampus crawler and file audit"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${syncing ? 'animate-spin' : ''}`} />
                  <span>
                    {syncing
                      ? (syncProgress ? `Auditing (${syncProgress.current}/${syncProgress.total})...` : 'Syncing...')
                      : 'Rerun Full Update'}
                  </span>
                </button>

                <div className="flex items-center space-x-1.5">
                  <span className="text-zinc-500 font-medium">Filter:</span>
                  <select
                    value={selectedSubjectFilter}
                    onChange={(e) => setSelectedSubjectFilter(e.target.value)}
                    className="bg-zinc-900 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 focus:outline-none focus:border-zinc-700"
                  >
                    <option value="ALL">All Subjects ({documents.length} files)</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.name}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {folders.map((f) => (
                <div key={f.name} className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-semibold text-sm text-zinc-200">{f.name}</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">
                        {f.online_resources_count} online
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400 mb-2 line-clamp-2">{f.description}</p>
                    {f.missing_resources_count > 0 && (
                      <span className="text-[10px] font-mono text-amber-400 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-800/50 mb-2 inline-block">
                        {f.missing_resources_count} pending sync
                      </span>
                    )}
                  </div>
                  <div className="pt-2 border-t border-zinc-800/60 flex items-center justify-between text-xs mt-2">
                    <span className="text-zinc-400 font-mono text-[11px]">{f.files_count} local files</span>
                    <button
                      onClick={() => launchApp('explorer', f.path)}
                      className="text-blue-400 hover:text-blue-300 font-medium text-[11px] flex items-center space-x-1"
                    >
                      <Folder className="h-3 w-3" />
                      <span>Browse</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-zinc-800 flex justify-between items-center text-xs">
                <span className="font-medium text-zinc-300">Showing {filteredDocuments.length} files</span>
                <button
                  onClick={() => launchApp('explorer', `c:\\Users\\Shaunak Rane\\Desktop\\3rd Year`)}
                  className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 flex items-center space-x-1"
                >
                  <Folder className="h-3 w-3" />
                  <span>Open 3rd Year Directory</span>
                </button>
              </div>

              <div className="max-h-[500px] overflow-y-auto divide-y divide-zinc-800/60 text-xs">
                {filteredDocuments.map((doc) => (
                  <div key={doc.id} className="px-4 py-2.5 flex items-center justify-between hover:bg-zinc-800/30">
                    <div className="flex items-center space-x-2.5 min-w-0 pr-4">
                      <FileText className="h-4 w-4 text-zinc-400 flex-shrink-0" />
                      <div className="truncate">
                        <span className="font-medium text-zinc-200 block truncate">{doc.file_name}</span>
                        <span className="text-[11px] text-zinc-500 font-mono">{doc.subject_name}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 flex-shrink-0 text-zinc-500 font-mono text-[11px]">
                      <span>{doc.upload_date || 'Indexed'}</span>
                      <button
                        onClick={() => launchApp('code', doc.local_path)}
                        className="px-2 py-0.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition"
                      >
                        Inspect
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: CAREER & OPPORTUNITIES */}
        {activeTab === 'career' && (
          <div className="space-y-6">
            {/* Mission Control Auto-Apply Banner */}
            <div className="p-4 rounded-xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-zinc-900 to-indigo-950/40 backdrop-blur shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-start space-x-3.5">
                <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 mt-0.5">
                  <Zap className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-zinc-100 uppercase tracking-wider">
                      Autonomous Auto-Apply Engine & Career Radar
                    </h3>
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      CDP Active
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    Iterates over opportunities, attaches verified candidate resume, fills portal forms, and captures visual proofs.
                  </p>
                  <div className="flex flex-wrap items-center gap-3 mt-2 text-[11px] font-mono text-zinc-300">
                    <span className="px-2 py-0.5 rounded bg-zinc-800/80 border border-zinc-700 text-blue-300 flex items-center space-x-1.5">
                      <FileText className="h-3 w-3" />
                      <span>Resume: <strong>{autoApplyInfo?.resume?.name || 'resume (2).pdf'}</strong></span>
                    </span>
                    <span className="text-zinc-500">•</span>
                    <span className="text-emerald-400 font-semibold">
                      {careerItems.filter(c => c.status === 'applied').length} Applied
                    </span>
                    <span className="text-zinc-600">/</span>
                    <span className="text-zinc-300 font-medium">
                      {careerItems.length} Total Opportunities
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-stretch md:self-auto">
                <button
                  onClick={triggerAutoApplyAll}
                  disabled={autoApplyRunning}
                  className={`flex-1 md:flex-none px-4 py-2.5 rounded-lg text-xs font-bold text-white transition flex items-center justify-center space-x-2 shadow-md ${
                    autoApplyRunning
                      ? 'bg-blue-700 opacity-80 cursor-wait'
                      : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 border border-blue-400/30'
                  }`}
                >
                  <RefreshCw className={`h-4 w-4 ${autoApplyRunning ? 'animate-spin' : ''}`} />
                  <span>
                    {autoApplyRunning
                      ? (autoApplyProgress ? `Applying (${autoApplyProgress.current}/${autoApplyProgress.total})...` : 'Applying...')
                      : '⚡ Auto Apply All Opportunities'}
                  </span>
                </button>
              </div>
            </div>

            {/* Live Progress Bar when Running */}
            {autoApplyRunning && (
              <div className="p-3 rounded-lg bg-blue-950/40 border border-blue-800/60 text-blue-200 text-xs flex items-center justify-between animate-pulse">
                <div className="flex items-center space-x-2">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin text-blue-400" />
                  <span>{autoApplyStatusMsg}</span>
                </div>
                {autoApplyProgress && (
                  <span className="font-mono text-[11px] text-blue-300">
                    {Math.round((autoApplyProgress.current / autoApplyProgress.total) * 100)}%
                  </span>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {careerItems.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/60 flex flex-col justify-between text-xs"
                >
                  <div>
                    <div className="flex justify-between items-start mb-1.5">
                      <span className="font-semibold text-sm text-zinc-100">{item.name}</span>
                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
                        {item.category}
                      </span>
                    </div>
                    <p className="text-emerald-400 font-medium mb-2 text-[11px]">
                      {item.benefits_credits}
                    </p>
                    <div className="space-y-1 text-zinc-400">
                      <p><span className="text-zinc-500 font-medium">Deadline:</span> {item.deadline}</p>
                      <p><span className="text-zinc-500 font-medium">Eligibility:</span> {item.eligibility}</p>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-zinc-800/80 flex flex-wrap justify-between items-center gap-2">
                    <div className="flex items-center space-x-2">
                      {item.status === 'applied' ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 text-[11px] font-semibold">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                          <span>APPLIED</span>
                        </span>
                      ) : item.status === 'open' ? (
                        <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-blue-950/50 text-blue-400 border border-blue-800/50 text-[10px] font-mono">
                          OPEN
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1.5 px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 text-[10px] font-mono">
                          {item.status.toUpperCase()}
                        </span>
                      )}

                      {item.applied_at && (
                        <span className="text-[10px] text-zinc-500 font-mono">
                          {item.applied_at.split(' ')[0]}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      {item.proof_screenshot && (
                        <button
                          onClick={() => {
                            const filename = item.proof_screenshot?.split(/[/\\]/).pop();
                            setActiveScreenshotModal(`/api/screenshots/${filename}`);
                          }}
                          className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition text-[11px] font-medium flex items-center space-x-1"
                          title="View visual proof screenshot captured during application"
                        >
                          <Eye className="h-3 w-3 text-zinc-400" />
                          <span>Proof</span>
                        </button>
                      )}

                      {item.status !== 'applied' && (
                        <button
                          onClick={() => triggerAutoApplySingle(item.id)}
                          disabled={autoApplyRunning}
                          className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-semibold transition text-[11px] flex items-center space-x-1 disabled:opacity-50"
                        >
                          <Zap className="h-3 w-3" />
                          <span>Auto Apply</span>
                        </button>
                      )}

                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-blue-400 transition flex items-center space-x-1 text-[11px]"
                        >
                          <span>Portal</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: DESKTOP TERMINAL */}
        {activeTab === 'desktop' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 flex items-center space-x-2">
                <Terminal className="h-4 w-4 text-zinc-300" />
                <span>Desktop Workspace & Tool Runner</span>
              </h2>
              <p className="text-xs text-zinc-400">
                Execute approved local tooling, file operations, and project launchers.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              {[
                { name: 'VS Code', app: 'code', icon: Code2, desc: 'Open Workspace' },
                { name: 'Terminal', app: 'terminal', icon: Terminal, desc: 'PowerShell Console' },
                { name: 'Academic Dir', app: 'explorer', icon: Folder, desc: 'Desktop\\3rd Year' },
                { name: 'Antigravity', app: 'antigravity', icon: Server, desc: 'IDE Environment' }
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.name}
                    onClick={() => launchApp(item.app)}
                    className="p-3.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800/80 transition text-left"
                  >
                    <Icon className="h-4 w-4 text-zinc-300 mb-2" />
                    <span className="font-semibold text-zinc-200 block">{item.name}</span>
                    <span className="text-[11px] text-zinc-500">{item.desc}</span>
                  </button>
                );
              })}
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-5 font-mono text-xs">
              <div className="flex items-center space-x-2 mb-3">
                <div className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
                <div className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
                <div className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
                <span className="text-zinc-500 text-[11px] ml-2">student-os@workstation:~$</span>
              </div>

              <div className="flex items-center space-x-2 mb-3">
                <span className="text-zinc-400">$</span>
                <input
                  type="text"
                  value={cmdInput}
                  onChange={(e) => setCmdInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && runCommand()}
                  className="flex-1 bg-zinc-950 border border-zinc-800 rounded px-3 py-1.5 text-zinc-200 focus:outline-none focus:border-zinc-600"
                  placeholder="e.g. python --version, git status, pytest"
                />
                <button
                  onClick={runCommand}
                  disabled={cmdRunning}
                  className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500 font-semibold text-white transition flex items-center space-x-1"
                >
                  <Play className="h-3 w-3" />
                  <span>{cmdRunning ? 'Running...' : 'Execute'}</span>
                </button>
              </div>

              {cmdOutput && (
                <div className="bg-zinc-950 p-3 rounded border border-zinc-800/80 text-zinc-300 max-h-56 overflow-y-auto whitespace-pre-wrap">
                  {cmdOutput}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 5: ACTION ITEMS */}
        {activeTab === 'todos' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 flex items-center space-x-2">
                <CheckSquare className="h-4 w-4 text-zinc-300" />
                <span>Academic & Career Action Items</span>
              </h2>
              <p className="text-xs text-zinc-400">Prioritized checklist of tasks, submissions, and goals</p>
            </div>

            <form onSubmit={handleAddTodo} className="flex gap-2 text-xs">
              <input
                type="text"
                value={newTodoTitle}
                onChange={(e) => setNewTodoTitle(e.target.value)}
                placeholder="Add new task or study objective..."
                className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600"
              />
              <select
                value={newTodoCategory}
                onChange={(e) => setNewTodoCategory(e.target.value)}
                className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none focus:border-zinc-600"
              >
                <option value="Academic">Academic</option>
                <option value="Career">Career</option>
                <option value="Coding">Coding</option>
              </select>
              <button
                type="submit"
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 font-semibold text-white transition flex items-center space-x-1"
              >
                <Plus className="h-3.5 w-3.5" />
                <span>Add Item</span>
              </button>
            </form>

            <div className="space-y-2 text-xs">
              {todos.map((todo) => (
                <div
                  key={todo.id}
                  onClick={() => toggleTodo(todo.id)}
                  className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between ${
                    todo.completed
                      ? 'bg-zinc-900/30 border-zinc-800/40 text-zinc-500 line-through'
                      : 'bg-zinc-900/60 border-zinc-800 text-zinc-200 hover:border-zinc-700'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    {todo.completed ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                    ) : (
                      <Circle className="h-4 w-4 text-zinc-600 flex-shrink-0" />
                    )}
                    <span className="font-medium">{todo.title}</span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
                    {todo.category}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 6: SYSTEM AUDIT LOGS */}
        {activeTab === 'logs' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-400 flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-zinc-300" />
                  <span>System Audit & Execution Logs</span>
                </h2>
                <p className="text-xs text-zinc-400">Live operational log of background synchronization and tasks</p>
              </div>
              <button
                onClick={fetchLogs}
                className="px-2.5 py-1.5 rounded text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 transition flex items-center space-x-1 border border-zinc-700"
              >
                <RefreshCw className="h-3 w-3" />
                <span>Refresh</span>
              </button>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 font-mono text-xs max-h-[550px] overflow-y-auto space-y-1.5">
              {logs.map((log) => (
                <div key={log.id} className="flex space-x-2.5 border-b border-zinc-800/50 pb-1.5">
                  <span className="text-zinc-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  <span
                    className={`font-semibold uppercase text-[11px] ${
                      log.level === 'ERROR'
                        ? 'text-rose-400'
                        : log.level === 'WARNING'
                        ? 'text-amber-400'
                        : 'text-zinc-300'
                    }`}
                  >
                    [{log.level}]
                  </span>
                  <span className="text-zinc-300 flex-1">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 py-3 text-center text-xs text-zinc-500 font-mono">
        Student OS • Universal AI University Workstation Environment
      </footer>

      {/* Floating Copilot Trigger Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setCopilotDrawerOpen(true)}
          className="flex items-center space-x-2.5 px-4 py-2.5 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs shadow-xl shadow-blue-950/60 border border-blue-400/40 transition transform hover:scale-105 active:scale-95 cursor-pointer"
          title="Open Autonomous Copilot Drawer"
        >
          <Bot className="h-4 w-4" />
          <span className="font-semibold">AI Copilot</span>
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        </button>
      </div>

      {/* Slide-over Copilot Drawer */}
      {copilotDrawerOpen && (
        <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-zinc-900 border-l border-zinc-800 flex flex-col h-full shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Drawer Header */}
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/90">
              <div className="flex items-center space-x-2.5">
                <div className="h-8 w-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <Bot className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Student OS Copilot</h3>
                  <p className="text-[11px] text-zinc-400">PC Control & Antigravity Bridge</p>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => {
                    setActiveTab('copilot');
                    setCopilotDrawerOpen(false);
                  }}
                  className="p-1.5 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                  title="Expand to Full Tab"
                >
                  <Maximize2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setCopilotDrawerOpen(false)}
                  className="p-1.5 rounded hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                  title="Close Drawer"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Quick Chips inside Drawer */}
            <div className="px-4 py-2 border-b border-zinc-800/80 bg-zinc-950/40 flex overflow-x-auto space-x-1.5 text-[11px]">
              {QUICK_PROMPTS.slice(0, 5).map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => sendChatMessage(p.query)}
                  className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 whitespace-nowrap text-[10px] transition"
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Drawer Messages Stream */}
            <div ref={chatDrawerContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3 font-sans text-xs">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div className="flex items-center space-x-1.5 mb-1 text-[10px] text-zinc-500 font-mono">
                    <span>{msg.sender === 'user' ? 'User' : 'Copilot'}</span>
                    <span>•</span>
                    <span>{msg.timestamp}</span>
                    {msg.tool_used && (
                      <span className="text-blue-400 font-mono text-[9px]">[{msg.tool_used}]</span>
                    )}
                  </div>
                  <div
                    className={`max-w-[90%] rounded-xl p-3 text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-zinc-950 border border-zinc-800 text-zinc-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{renderFormattedMarkdown(msg.text)}</div>
                    {msg.tool_used === 'delegate_to_antigravity' && msg.details && (
                      <div className="mt-2 p-2 rounded bg-amber-950/30 border border-amber-600/40 text-[11px] space-y-1.5">
                        <div className="flex items-center space-x-1 text-amber-300 font-semibold">
                          <Zap className="h-3.5 w-3.5" />
                          <span>Antigravity Directive Generated</span>
                        </div>
                        <div className="flex gap-1.5 pt-1">
                          <button
                            onClick={() => copyToClipboard(msg.details?.prompt_preview || '', msg.id)}
                            className="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-[10px] flex items-center space-x-1"
                          >
                            <Copy className="h-3 w-3" />
                            <span>Copy</span>
                          </button>
                          <button
                            onClick={() => launchApp('antigravity', msg.details?.prompt_file)}
                            className="px-2 py-1 rounded bg-amber-600 hover:bg-amber-500 text-white text-[10px] flex items-center space-x-1"
                          >
                            <Play className="h-3 w-3" />
                            <span>Launch</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 bg-zinc-950 border border-zinc-800 rounded p-2.5 animate-pulse">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                  <span>Processing workstation command...</span>
                </div>
              )}
            </div>

            {/* Drawer Input */}
            <div className="p-3 border-t border-zinc-800 bg-zinc-900">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  sendChatMessage();
                }}
                className="flex flex-col gap-2"
              >
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Command PC or ask Antigravity..."
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-blue-500 font-sans"
                />
                <div className="flex items-center justify-between">
                  <button
                    type="button"
                    onClick={() => sendChatMessage(undefined, true)}
                    disabled={chatLoading || !chatInput.trim()}
                    className="px-2.5 py-1.5 rounded text-[11px] font-medium text-amber-300 bg-amber-950/60 hover:bg-amber-900 border border-amber-800 flex items-center space-x-1 disabled:opacity-50"
                  >
                    <Zap className="h-3 w-3" />
                    <span>Antigravity</span>
                  </button>
                  <button
                    type="submit"
                    disabled={chatLoading || !chatInput.trim()}
                    className="px-3 py-1.5 rounded text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 flex items-center space-x-1 disabled:opacity-50"
                  >
                    <Send className="h-3 w-3" />
                    <span>Send</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Visual Proof Screenshot Modal */}
      {activeScreenshotModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between bg-zinc-900">
              <div className="flex items-center space-x-2">
                <Eye className="h-4 w-4 text-emerald-400" />
                <span className="text-sm font-semibold text-zinc-200">Application Proof Verification</span>
              </div>
              <button
                onClick={() => setActiveScreenshotModal(null)}
                className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-white transition"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-4 overflow-auto flex-1 bg-zinc-950 flex items-center justify-center">
              <img
                src={activeScreenshotModal}
                alt="Application Proof"
                className="rounded border border-zinc-800 max-w-full h-auto object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
