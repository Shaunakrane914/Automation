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
  Eye,
  FlaskConical,
  FolderOpen,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Trash2,
  Search
} from 'lucide-react';

interface PracticeTodo {
  id: string;
  task: string;
  category: string;
}

interface Labwork {
  id: number;
  subject_id: number;
  subject_name: string;
  lab_number: string;
  title: string;
  file_path: string;
  code_type: string;
  concepts: string[];
  problem_statement: string;
  code_summary: string;
  practice_todos: PracticeTodo[];
  starter_code: string;
  status: 'ready' | 'in_progress' | 'completed';
  completed_tasks: string[];
  tasks_count: number;
  completed_count: number;
  progress_pct: number;
}

interface LabSubjectGroup {
  subject_name: string;
  subject_id: number;
  labworks: Labwork[];
  total_labs: number;
  completed_labs: number;
}

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
  { label: '👋 Say Hi to Copilot', query: "hi" },
  { label: '📚 Query Course RAG: Time Series ARIMA', query: "Explain ARIMA models and stationarity from my Time Series coursework" },
  { label: '📚 Query Course RAG: AJP Question Bank', query: "Show me questions from my AJP midterm question bank" },
  { label: '🤖 ReAct Agent: Multi-Step Execution', query: "check if any subject has attendance below 75 percent and list its name" },
  { label: '💼 Show 7 Verified Applied Jobs', query: "show applied jobs" },
  { label: '🖥️ Workstation Hardware & GPU Specs', query: "system specs" },
  { label: '🤖 Daemon: Check Background Status', query: "daemon status" },
  { label: '⚡ Auto Apply to All Open Opportunities', query: "auto apply to all opportunities" },
  { label: '🔬 Review Deep Learning Lab Code & Practice', query: "Show me my Deep Learning labworks, code breakdown, and practice to-do list." },
  { label: '🔬 Review NLP Text Preprocessing & BoW', query: "Show me my NLP lab practicals and what code I need to practice." },
  { label: '📊 Check My Attendance & Risk', query: "Check my attendance" },
  { label: '⏳ What Assignments are Pending?', query: "What assignments are pending?" },
  { label: '📂 Open Deep Learning Folder', query: "Open Deep Learning folder" },
  { label: '💻 Run: git status', query: "run git status" },
  { label: '💻 Run: nvidia-smi', query: "run nvidia-smi" },
  { label: '🔄 Rerun DigiCampus Sync', query: "Rerun full digicampus audit and sync" },
  { label: '⚡ Escalate to Antigravity (Explicit Directive)', query: "escalate to antigravity build full neural network architecture" },
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
  const [activeTab, setActiveTab] = useState<'copilot' | 'academic' | 'labs' | 'resources' | 'career'>('copilot');
  const [wsConnected, setWsConnected] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncStatusMsg, setSyncStatusMsg] = useState<string>('');
  const [syncProgress, setSyncProgress] = useState<{ current: number; total: number; subject: string } | null>(null);
  const [lastSyncTime, setLastSyncTime] = useState<string>('Live Synced (Sept 2026)');

  // Labworks states
  const [labworks, setLabworks] = useState<Labwork[]>([]);
  const [labSubjects, setLabSubjects] = useState<LabSubjectGroup[]>([]);
  const [labStats, setLabStats] = useState<{
    total_labs: number;
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    overall_readiness_pct: number;
  }>({ total_labs: 0, total_tasks: 0, completed_tasks: 0, pending_tasks: 0, overall_readiness_pct: 0 });
  const [selectedLabSubject, setSelectedLabSubject] = useState<string>('ALL');
  const [rescanLabsLoading, setRescanLabsLoading] = useState<boolean>(false);
  const [expandedCodeIds, setExpandedCodeIds] = useState<Record<number, boolean>>({});
  const [copiedCodeId, setCopiedCodeId] = useState<number | null>(null);

  // Chat Copilot states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: "⚡ **Student OS Autonomous Copilot & Ultimate Workstation Controller**\n\nI am your live workstation AI powered by **Ollama (local RTX 3050 GPU) + Gemini (cloud)** with direct PC control, terminal execution, DigiCampus auditing, and verified Career Radar tracking.\n\n- 🧠 **Dual-Brain AI:** Local GPU generation via Ollama (`qwen2.5:0.5b`) & Gemini cloud for zero-latency, private reasoning.\n- 💻 **PC & Shell Execution:** Run terminal commands (`run git status`, `run dir`, `run nvidia-smi`), inspect hardware (`system specs`).\n- 🚀 **App Launcher:** Open VS Code, Terminal, Chrome, or any of your 12 academic folders (`open deep learning`, `open time series`).\n- 📊 **Academic & Career:** Real-time attendance breakdown, DigiCampus sync, and 7 verified applications on LinkedIn, Internshala, and Indeed.\n- ⚡ **Antigravity Protocol:** ONLY when you explicitly command Antigravity delegation (`escalate to antigravity`), I formulate a high-leverage directive and launch Antigravity IDE.\n\nType `hi`, `system specs`, or `show applied jobs` to test live execution!",
      tool_used: 'workstation_greeting'
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

  // Assignment Manager states
  const [assignmentFilter, setAssignmentFilter] = useState<'ongoing' | 'all' | 'submitted' | 'closed'>('ongoing');
  const [assignmentSearch, setAssignmentSearch] = useState('');
  const [showAddAssignmentModal, setShowAddAssignmentModal] = useState(false);
  const [newAssignmentTitle, setNewAssignmentTitle] = useState('');
  const [newAssignmentSubject, setNewAssignmentSubject] = useState('');
  const [newAssignmentDeadline, setNewAssignmentDeadline] = useState('');
  const [newAssignmentIsLab, setNewAssignmentIsLab] = useState(false);
  const [submittingAssignment, setSubmittingAssignment] = useState(false);

  // Dynamic Assignment Metrics & Filter
  const ongoingAssignments = assignments.filter((a) => ['pending', 'open'].includes((a.status || '').toLowerCase()));
  const submittedAssignments = assignments.filter((a) => ['submitted', 'completed'].includes((a.status || '').toLowerCase()));
  const closedAssignments = assignments.filter((a) => ['closed', 'not submitted'].includes((a.status || '').toLowerCase()));

  const filteredAssignments = assignments.filter((a) => {
    const st = (a.status || '').toLowerCase();
    const isOngoing = ['pending', 'open'].includes(st);
    const isSubmitted = ['submitted', 'completed'].includes(st);
    const isClosed = ['closed', 'not submitted'].includes(st);

    if (assignmentFilter === 'ongoing' && !isOngoing) return false;
    if (assignmentFilter === 'submitted' && !isSubmitted) return false;
    if (assignmentFilter === 'closed' && !isClosed) return false;

    if (assignmentSearch.trim()) {
      const q = assignmentSearch.toLowerCase();
      return (
        (a.title || '').toLowerCase().includes(q) ||
        (a.subject_name || '').toLowerCase().includes(q) ||
        (a.deadline || '').toLowerCase().includes(q) ||
        (a.status || '').toLowerCase().includes(q)
      );
    }
    return true;
  });

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
          } else if (data.type === 'LAB_TASK_TOGGLED' || data.type === 'LABS_RESCANNED') {
            fetchLabworks();
            fetchAcademicData();
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
          } else if (data.type === 'ASSIGNMENT_CREATED' || data.type === 'ASSIGNMENT_UPDATED' || data.type === 'ASSIGNMENT_DELETED') {
            fetchAcademicData();
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
    fetchLabworks();
    fetchCareerData();
    fetchTodos();
    fetchLogs();
    fetchAutoApplyStatus();
  }, []);

  const fetchLabworks = async () => {
    try {
      const res = await axios.get('/api/labs');
      if (res.data) {
        setLabworks(res.data.labworks || []);
        setLabSubjects(res.data.subjects || []);
        if (res.data.stats) {
          setLabStats(res.data.stats);
        }
      }
    } catch (e) {
      console.error('Error fetching labworks:', e);
    }
  };

  const handleToggleLabTask = async (labworkId: number, taskId: string) => {
    // Optimistically update local state
    setLabworks(prev => prev.map(lw => {
      if (lw.id === labworkId) {
        const isCompleted = lw.completed_tasks.includes(taskId);
        const newCompleted = isCompleted
          ? lw.completed_tasks.filter(t => t !== taskId)
          : [...lw.completed_tasks, taskId];
        const newPct = Math.round((newCompleted.length / (lw.practice_todos.length || 1)) * 100);
        const newStatus: 'ready' | 'in_progress' | 'completed' =
          newCompleted.length === lw.practice_todos.length && lw.practice_todos.length > 0
            ? 'completed'
            : (newCompleted.length > 0 ? 'in_progress' : 'ready');
        return {
          ...lw,
          completed_tasks: newCompleted,
          completed_count: newCompleted.length,
          progress_pct: newPct,
          status: newStatus
        };
      }
      return lw;
    }));

    try {
      await axios.post('/api/labs/todo/toggle', { labwork_id: labworkId, task_id: taskId });
      fetchLabworks();
    } catch (e) {
      console.error('Error toggling lab task:', e);
      fetchLabworks();
    }
  };

  const handleRescanLabs = async () => {
    setRescanLabsLoading(true);
    try {
      await axios.post('/api/labs/rescan');
      await fetchLabworks();
      await fetchAcademicData();
    } catch (e) {
      console.error('Error rescanning labworks:', e);
    } finally {
      setRescanLabsLoading(false);
    }
  };

  const handleOpenLabFile = async (filePath: string) => {
    try {
      await axios.post('/api/labs/open', { path: filePath });
    } catch (e) {
      console.error('Error opening lab file:', e);
    }
  };

  const toggleCodeExpand = (labId: number) => {
    setExpandedCodeIds(prev => ({ ...prev, [labId]: !prev[labId] }));
  };

  const copyCodeSnippet = (code: string, labId: number) => {
    navigator.clipboard.writeText(code);
    setCopiedCodeId(labId);
    setTimeout(() => setCopiedCodeId(null), 2500);
  };

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

  const toggleAssignmentStatus = async (id: number) => {
    try {
      const res = await axios.patch(`/api/assignments/${id}/toggle`);
      setAssignments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: res.data.status } : a))
      );
      fetchLogs();
    } catch (err) {
      console.error('Failed to toggle assignment:', err);
    }
  };

  const deleteAssignment = async (id: number) => {
    if (!window.confirm('Are you sure you want to remove this assignment record?')) return;
    try {
      await axios.delete(`/api/assignments/${id}`);
      setAssignments((prev) => prev.filter((a) => a.id !== id));
      fetchLogs();
    } catch (err) {
      console.error('Failed to delete assignment:', err);
    }
  };

  const handleAddAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAssignmentTitle.trim()) return;
    setSubmittingAssignment(true);
    try {
      const targetSubject = newAssignmentSubject || (subjects[0] ? subjects[0].name : 'General Coursework');
      const subjObj = subjects.find((s) => s.name === targetSubject);
      const res = await axios.post('/api/assignments', {
        title: newAssignmentTitle.trim(),
        subject_id: subjObj ? subjObj.id : (subjects[0]?.id || 1),
        subject_name: targetSubject,
        deadline: newAssignmentDeadline.trim() || new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
        is_lab: newAssignmentIsLab ? 1 : 0,
        status: 'pending'
      });
      const newAsg: Assignment = {
        id: res.data.id,
        subject_id: subjObj ? subjObj.id : (subjects[0]?.id || 1),
        subject_name: targetSubject,
        title: newAssignmentTitle.trim(),
        deadline: newAssignmentDeadline.trim() || new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
        is_lab: newAssignmentIsLab ? 1 : 0,
        status: 'pending'
      };
      setAssignments((prev) => [newAsg, ...prev]);
      setNewAssignmentTitle('');
      setNewAssignmentDeadline('');
      setShowAddAssignmentModal(false);
      fetchLogs();
    } catch (err) {
      console.error('Failed to create assignment:', err);
    } finally {
      setSubmittingAssignment(false);
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
            { id: 'labs', label: 'Labworks & Code Practice', icon: FlaskConical, badge: labworks.length },
            { id: 'resources', label: 'Course Materials & Files', icon: FolderCheck },
            { id: 'career', label: 'Career & Opportunities', icon: Briefcase },
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
                {tab.badge !== undefined && tab.badge > 0 && (
                  <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-blue-900/60 text-blue-300 border border-blue-700/60 font-semibold">
                    {tab.badge}
                  </span>
                )}
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
                            : msg.tool_used === 'academic_rag_llm'
                            ? 'bg-indigo-950/90 text-indigo-300 border border-indigo-700/80 font-semibold'
                            : msg.tool_used === 'react_agent_loop'
                            ? 'bg-emerald-950/90 text-emerald-300 border border-emerald-700/80 font-semibold'
                            : msg.tool_used === 'daemon_control'
                            ? 'bg-rose-950/80 text-rose-300 border border-rose-800/80 font-semibold'
                            : msg.tool_used === 'ollama_gpu_llm'
                            ? 'bg-purple-950/80 text-purple-300 border border-purple-800/80 font-semibold'
                            : msg.tool_used === 'gemini_cloud_llm'
                            ? 'bg-sky-950/80 text-sky-300 border border-sky-800/80 font-semibold'
                            : msg.tool_used === 'workstation_greeting'
                            ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 font-semibold'
                            : msg.tool_used === 'system_telemetry'
                            ? 'bg-teal-950/80 text-teal-300 border border-teal-800/80 font-semibold'
                            : msg.tool_used === 'applied_applications'
                            ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/80 font-semibold'
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
                  <span>ONGOING ASSIGNMENTS</span>
                  {ongoingAssignments.length > 0 ? (
                    <Clock className="h-4 w-4 text-amber-400" />
                  ) : (
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  )}
                </div>
                <div className={`text-2xl font-bold ${ongoingAssignments.length > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {ongoingAssignments.length} Ongoing
                </div>
                <p className="text-xs text-zinc-500 mt-1">
                  {ongoingAssignments.length > 0
                    ? `${ongoingAssignments.length} active assignment(s) require submission`
                    : `All active caught up • ${submittedAssignments.length} submitted • ${closedAssignments.length} closed`}
                </p>
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
                    className="px-2.5 py-1 rounded text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 transition flex items-center space-x-1.5 border border-zinc-700 disabled:opacity-50"
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
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                  <h3 className="text-sm font-semibold text-zinc-200 flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-zinc-400" />
                    <span>Classroom Submissions & Assignment Manager</span>
                  </h3>
                  <div className="flex items-center space-x-2">
                    {ongoingAssignments.length > 0 ? (
                      <span className="text-[11px] font-mono text-amber-400 px-2.5 py-1 rounded bg-amber-950/60 border border-amber-800/80 flex items-center space-x-1 font-semibold">
                        <AlertCircle className="h-3.5 w-3.5 text-amber-400" />
                        <span>{ongoingAssignments.length} ONGOING SUBMISSION</span>
                      </span>
                    ) : (
                      <span className="text-[11px] font-mono text-emerald-400 px-2.5 py-1 rounded bg-emerald-950/40 border border-emerald-800/60 flex items-center space-x-1 font-semibold">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                        <span>STATUS: ALL CAUGHT UP</span>
                      </span>
                    )}
                    <button
                      onClick={() => setShowAddAssignmentModal(true)}
                      className="px-2.5 py-1 rounded text-[11px] font-medium text-emerald-300 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/80 flex items-center space-x-1 transition shadow-sm"
                    >
                      <Plus className="h-3.5 w-3.5" />
                      <span>Add Assignment</span>
                    </button>
                  </div>
                </div>

                {ongoingAssignments.length > 0 ? (
                  <div className="p-3 rounded-lg bg-amber-950/40 border border-amber-800/60 flex items-start space-x-3 mb-3">
                    <AlertCircle className="h-4 w-4 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-semibold text-xs text-amber-200">
                        {ongoingAssignments.length} Active Assignment(s) Pending Submission
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-0.5">
                        Track deadlines below. Click the checkmark to mark an assignment complete, or click trash to remove.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/50 flex items-start space-x-3 mb-3">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <div className="font-semibold text-xs text-emerald-300">
                        Zero Ongoing Submissions Required
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-0.5">
                        All active coursework submissions are caught up. Java Lab is submitted, and past closed assignments are archived.
                      </p>
                    </div>
                  </div>
                )}

                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center space-x-1 bg-zinc-950 p-0.5 rounded border border-zinc-800 text-[11px]">
                    <button
                      onClick={() => setAssignmentFilter('ongoing')}
                      className={`px-2.5 py-1 rounded font-medium transition ${
                        assignmentFilter === 'ongoing'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold'
                          : 'text-zinc-400 hover:text-zinc-200'
                      }`}
                    >
                      Ongoing ({ongoingAssignments.length})
                    </button>
                    <button
                      onClick={() => setAssignmentFilter('submitted')}
                      className={`px-2.5 py-1 rounded font-medium transition ${
                        assignmentFilter === 'submitted'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                          : 'text-zinc-400 hover:text-zinc-200'
                      }`}
                    >
                      Submitted ({submittedAssignments.length})
                    </button>
                    <button
                      onClick={() => setAssignmentFilter('closed')}
                      className={`px-2.5 py-1 rounded font-medium transition ${
                        assignmentFilter === 'closed'
                          ? 'bg-zinc-800 text-zinc-200 border border-zinc-700 font-semibold'
                          : 'text-zinc-400 hover:text-zinc-200'
                      }`}
                    >
                      Closed ({closedAssignments.length})
                    </button>
                    <button
                      onClick={() => setAssignmentFilter('all')}
                      className={`px-2.5 py-1 rounded font-medium transition ${
                        assignmentFilter === 'all' ? 'bg-zinc-800 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
                      }`}
                    >
                      All ({assignments.length})
                    </button>
                  </div>

                  <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
                    <input
                      type="text"
                      value={assignmentSearch}
                      onChange={(e) => setAssignmentSearch(e.target.value)}
                      placeholder="Search title, subject, status..."
                      className="w-full pl-8 pr-3 py-1 bg-zinc-950 border border-zinc-800 rounded text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-zinc-600"
                    />
                  </div>
                </div>

                <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                  {filteredAssignments.map((asg) => {
                    const st = (asg.status || '').toLowerCase();
                    const isOngoing = ['pending', 'open'].includes(st);
                    const isSubmitted = ['submitted', 'completed'].includes(st);
                    const isClosed = ['closed', 'not submitted'].includes(st);

                    return (
                      <div
                        key={asg.id}
                        className={`p-3 rounded-lg border transition flex items-start justify-between gap-3 text-xs ${
                          isOngoing
                            ? 'bg-zinc-950/70 border-zinc-800/90 hover:border-zinc-700'
                            : isSubmitted
                            ? 'bg-emerald-950/10 border-emerald-950/40'
                            : 'bg-zinc-950/30 border-zinc-900 opacity-60'
                        }`}
                      >
                        <div className="flex items-start space-x-3 flex-1 min-w-0">
                          <button
                            onClick={() => toggleAssignmentStatus(asg.id)}
                            title={isOngoing ? 'Mark as completed' : 'Toggle status'}
                            className={`mt-0.5 flex-shrink-0 w-4 h-4 rounded-full border flex items-center justify-center transition ${
                              isOngoing
                                ? 'border-zinc-600 hover:border-emerald-400 hover:text-emerald-400 text-transparent'
                                : isSubmitted
                                ? 'bg-emerald-500 border-emerald-500 text-zinc-950'
                                : 'bg-zinc-800 border-zinc-700 text-zinc-400'
                            }`}
                          >
                            <Check className="h-3 w-3 stroke-[3]" />
                          </button>

                          <div className="min-w-0 flex-1">
                            <div className={`font-medium truncate ${isOngoing ? 'text-zinc-200' : isSubmitted ? 'text-zinc-300' : 'text-zinc-500'}`}>
                              {asg.title}
                            </div>
                            <div className="flex flex-wrap items-center gap-2 text-[11px] text-zinc-500 mt-1">
                              <span className="font-mono text-zinc-400">{asg.subject_name}</span>
                              <span>•</span>
                              <span className="flex items-center space-x-1 text-zinc-400 font-mono">
                                <Clock className="h-3 w-3 text-zinc-500" />
                                <span>{isClosed ? `Deadline: ${asg.deadline || 'Past Due'}` : `Due: ${asg.deadline || 'No deadline'}`}</span>
                              </span>
                              {asg.is_lab === 1 && (
                                <span className="px-1.5 py-0.2 rounded bg-blue-950/60 text-blue-400 border border-blue-900/60 text-[10px] font-mono">
                                  LAB
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 flex-shrink-0">
                          <span
                            className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                              isOngoing
                                ? 'bg-amber-950/50 text-amber-300 border-amber-800/60'
                                : isSubmitted
                                ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800/50'
                                : 'bg-zinc-900 text-zinc-400 border-zinc-800'
                            }`}
                          >
                            {asg.status}
                          </span>
                          <button
                            onClick={() => deleteAssignment(asg.id)}
                            title="Remove assignment"
                            className="p-1 rounded text-zinc-500 hover:text-rose-400 hover:bg-zinc-900 transition"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    );
                  })}

                  {filteredAssignments.length === 0 && (
                    <div className="p-8 text-center text-xs text-zinc-500 bg-zinc-950/40 rounded-lg border border-dashed border-zinc-800">
                      {assignmentFilter === 'ongoing'
                        ? 'No active ongoing assignments currently require submission.'
                        : 'No assignments match the selected filter.'}
                    </div>
                  )}
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

        {/* TAB: LABWORKS & CODE PRACTICE ROADMAPS */}
        {activeTab === 'labs' && (
          <div className="space-y-6">
            {/* Header Banner */}
            <div className="p-5 rounded-xl border border-zinc-800 bg-gradient-to-r from-zinc-900 via-zinc-900/90 to-blue-950/30 backdrop-blur shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-start space-x-3.5">
                <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 mt-0.5">
                  <FlaskConical className="h-6 w-6" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-base font-bold text-white tracking-tight">
                      Autonomous Labworks Scraper & Code Practice Roadmaps
                    </h2>
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      Live Indexed
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-1 max-w-3xl">
                    Autonomous engine that scrapes assignments, drive resources, and Jupyter/code files from{' '}
                    <code className="text-zinc-200 font-mono bg-zinc-800 px-1 py-0.5 rounded">Desktop\3rd Year</code>,
                    understands neural network architectures, pipelines, and algorithms, and generates step-by-step
                    practice to-do checklists for hands-on learning.
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-stretch md:self-auto flex-shrink-0">
                <button
                  onClick={handleRescanLabs}
                  disabled={rescanLabsLoading}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition flex items-center space-x-2 shadow-sm disabled:opacity-50"
                  title="Rescan 3rd Year directory and update code practice checklists"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${rescanLabsLoading ? 'animate-spin' : ''}`} />
                  <span>{rescanLabsLoading ? 'Rescanning Code...' : 'Rescan Labs & Code'}</span>
                </button>
              </div>
            </div>

            {/* Metrics Overview */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <div className="text-[11px] font-mono text-zinc-400 uppercase">Total Labworks</div>
                <div className="text-xl font-bold text-white mt-1">{labStats.total_labs} Experiments</div>
                <p className="text-[11px] text-zinc-500 mt-0.5">Across 6 Academic Lab Subjects</p>
              </div>

              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <div className="text-[11px] font-mono text-zinc-400 uppercase">Practice Tasks Mastered</div>
                <div className="text-xl font-bold text-emerald-400 mt-1">
                  {labStats.completed_tasks} / {labStats.total_tasks}
                </div>
                <p className="text-[11px] text-zinc-500 mt-0.5">{labStats.pending_tasks} Tasks Pending Practice</p>
              </div>

              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <div className="text-[11px] font-mono text-zinc-400 uppercase">Practical Readiness</div>
                <div className="text-xl font-bold text-blue-400 mt-1">{labStats.overall_readiness_pct}%</div>
                <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden mt-1.5">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-emerald-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${labStats.overall_readiness_pct}%` }}
                  />
                </div>
              </div>

              <div className="p-3.5 rounded-lg bg-zinc-900/60 border border-zinc-800">
                <div className="text-[11px] font-mono text-zinc-400 uppercase">Code Repositories</div>
                <div className="text-xl font-bold text-purple-400 mt-1">6 Active</div>
                <p className="text-[11px] text-zinc-500 mt-0.5">Jupyter, Python, Java, TypeScript</p>
              </div>
            </div>

            {/* Subject Selector Filter Tabs */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
              <span className="text-zinc-500 font-medium whitespace-nowrap mr-1">Subject Filter:</span>
              <button
                onClick={() => setSelectedLabSubject('ALL')}
                className={`px-3 py-1.5 rounded-lg font-medium transition whitespace-nowrap flex items-center space-x-1.5 ${
                  selectedLabSubject === 'ALL'
                    ? 'bg-blue-600 text-white font-semibold shadow-sm'
                    : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800 hover:border-zinc-700'
                }`}
              >
                <span>All Subjects</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-950/60 font-mono">
                  {labworks.length}
                </span>
              </button>

              {labSubjects.map((sub) => {
                const isSelected = selectedLabSubject === sub.subject_name;
                return (
                  <button
                    key={sub.subject_name}
                    onClick={() => setSelectedLabSubject(sub.subject_name)}
                    className={`px-3 py-1.5 rounded-lg font-medium transition whitespace-nowrap flex items-center space-x-1.5 ${
                      isSelected
                        ? 'bg-blue-600 text-white font-semibold shadow-sm'
                        : 'bg-zinc-900 text-zinc-400 hover:text-zinc-200 border border-zinc-800 hover:border-zinc-700'
                    }`}
                  >
                    <span>{sub.subject_name.replace(' (Neural Network)', '').replace(' Modelling & Forecasting', '')}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-zinc-950/60 font-mono">
                      {sub.total_labs}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Labworks List */}
            <div className="space-y-4">
              {labworks
                .filter((lw) => selectedLabSubject === 'ALL' || lw.subject_name === selectedLabSubject)
                .map((lw) => {
                  const isExpanded = !!expandedCodeIds[lw.id];
                  const isCopied = copiedCodeId === lw.id;

                  // Dynamic subject badge colors
                  const sName = lw.subject_name.toLowerCase();
                  const badgeStyle = sName.includes('deep learning')
                    ? 'bg-purple-950/70 text-purple-300 border-purple-800/60'
                    : sName.includes('natural language') || sName.includes('nlp')
                    ? 'bg-cyan-950/70 text-cyan-300 border-cyan-800/60'
                    : sName.includes('time series')
                    ? 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60'
                    : sName.includes('big data')
                    ? 'bg-amber-950/70 text-amber-300 border-amber-800/60'
                    : sName.includes('java')
                    ? 'bg-orange-950/70 text-orange-300 border-orange-800/60'
                    : 'bg-blue-950/70 text-blue-300 border-blue-800/60';

                  return (
                    <div
                      key={lw.id}
                      className="rounded-xl border border-zinc-800 bg-zinc-900/60 backdrop-blur overflow-hidden hover:border-zinc-700 transition"
                    >
                      {/* Top Card Bar */}
                      <div className="p-4 sm:p-5 border-b border-zinc-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3">
                        <div className="space-y-1.5">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-semibold border ${badgeStyle}`}>
                              {lw.subject_name}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-300 border border-zinc-700">
                              {lw.lab_number}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-zinc-900 text-zinc-400 border border-zinc-800">
                              {lw.code_type}
                            </span>
                          </div>
                          <h3 className="text-sm sm:text-base font-bold text-white tracking-tight">
                            {lw.title}
                          </h3>
                          <div className="flex items-center space-x-2 text-xs text-zinc-400 font-mono">
                            <FolderOpen className="h-3 w-3 text-zinc-500" />
                            <span className="truncate max-w-md">{lw.file_path}</span>
                          </div>
                        </div>

                        {/* Status and Progress Info */}
                        <div className="flex flex-col sm:flex-row sm:items-center gap-3 flex-shrink-0">
                          <div className="text-right sm:text-right">
                            <div className="flex items-center justify-end space-x-2">
                              {lw.status === 'completed' ? (
                                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-800 flex items-center space-x-1">
                                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                                  <span>Mastered</span>
                                </span>
                              ) : lw.status === 'in_progress' ? (
                                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-950/80 text-amber-300 border border-amber-800 flex items-center space-x-1">
                                  <Clock className="h-3.5 w-3.5 text-amber-400" />
                                  <span>In Progress</span>
                                </span>
                              ) : (
                                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-zinc-800 text-zinc-400 border border-zinc-700 flex items-center space-x-1">
                                  <Circle className="h-3 w-3 text-zinc-500" />
                                  <span>Ready to Practice</span>
                                </span>
                              )}
                            </div>
                            <div className="text-[11px] font-mono text-zinc-400 mt-1">
                              {lw.completed_count} of {lw.tasks_count} Tasks ({lw.progress_pct}%)
                            </div>
                            <div className="w-32 bg-zinc-800 h-1.5 rounded-full overflow-hidden mt-1 ml-auto">
                              <div
                                className={`h-full transition-all duration-300 rounded-full ${
                                  lw.status === 'completed'
                                    ? 'bg-emerald-500'
                                    : lw.status === 'in_progress'
                                    ? 'bg-amber-500'
                                    : 'bg-zinc-600'
                                }`}
                                style={{ width: `${lw.progress_pct}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Card Content */}
                      <div className="p-4 sm:p-5 space-y-4 text-xs">
                        {/* Problem Statement */}
                        <div className="p-3 rounded-lg bg-zinc-950/70 border border-zinc-800 text-zinc-300 leading-relaxed">
                          <span className="font-semibold text-zinc-100 mr-1.5">Objective & Problem:</span>
                          <span>{lw.problem_statement}</span>
                        </div>

                        {/* Concept Badges */}
                        <div>
                          <div className="text-[11px] font-mono text-zinc-400 uppercase mb-1.5">Core Architecture & Concepts:</div>
                          <div className="flex flex-wrap gap-1.5">
                            {lw.concepts.map((concept, cIdx) => (
                              <span
                                key={cIdx}
                                className="px-2.5 py-1 rounded text-[11px] bg-zinc-800/70 text-zinc-200 border border-zinc-700/80 font-mono"
                              >
                                {concept}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Interactive Practice To-Do Checklist */}
                        <div className="pt-2 border-t border-zinc-800/80">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-zinc-200 flex items-center space-x-1.5 text-xs">
                              <CheckSquare className="h-3.5 w-3.5 text-blue-400" />
                              <span>Shaunak's Hands-on Practice To-Do Checklist:</span>
                            </span>
                            <span className="text-[11px] font-mono text-zinc-500">
                              Click task checkbox to track mastering code
                            </span>
                          </div>

                          <div className="space-y-1.5">
                            {lw.practice_todos.map((todo) => {
                              const isDone = lw.completed_tasks.includes(todo.id);
                              return (
                                <div
                                  key={todo.id}
                                  onClick={() => handleToggleLabTask(lw.id, todo.id)}
                                  className={`p-2.5 rounded-lg border transition flex items-start space-x-3 cursor-pointer select-none ${
                                    isDone
                                      ? 'bg-emerald-950/20 border-emerald-900/50 hover:bg-emerald-950/30'
                                      : 'bg-zinc-950/50 border-zinc-800/80 hover:bg-zinc-800/40 hover:border-zinc-700'
                                  }`}
                                >
                                  <button
                                    type="button"
                                    className="mt-0.5 flex-shrink-0 text-zinc-400 hover:text-white transition"
                                  >
                                    {isDone ? (
                                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                                    ) : (
                                      <Circle className="h-4 w-4 text-zinc-600 hover:text-zinc-400" />
                                    )}
                                  </button>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center space-x-2">
                                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-semibold ${
                                        isDone
                                          ? 'bg-emerald-900/40 text-emerald-300'
                                          : 'bg-zinc-800 text-zinc-400'
                                      }`}>
                                        {todo.category}
                                      </span>
                                      <span
                                        className={`leading-snug text-xs ${
                                          isDone ? 'line-through text-zinc-400' : 'text-zinc-200'
                                        }`}
                                      >
                                        {todo.task}
                                      </span>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        {/* Code Toggle & Launcher Bar */}
                        <div className="pt-2 border-t border-zinc-800/80 flex flex-wrap items-center justify-between gap-2">
                          <button
                            onClick={() => toggleCodeExpand(lw.id)}
                            className="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 transition flex items-center space-x-1.5 border border-zinc-700"
                          >
                            <Code2 className="h-3.5 w-3.5 text-blue-400" />
                            <span>{isExpanded ? 'Hide Starter Code' : 'Inspect Code & Starter Implementation'}</span>
                            {isExpanded ? (
                              <ChevronUp className="h-3 w-3 text-zinc-400" />
                            ) : (
                              <ChevronDown className="h-3 w-3 text-zinc-400" />
                            )}
                          </button>

                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleOpenLabFile(lw.file_path)}
                              className="px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-900 hover:bg-zinc-800 transition flex items-center space-x-1.5 border border-zinc-800 hover:border-zinc-700"
                              title="Reveal file in File Explorer"
                            >
                              <FolderOpen className="h-3.5 w-3.5 text-zinc-400" />
                              <span>Reveal in Explorer</span>
                            </button>

                            <button
                              onClick={() => launchApp('code', lw.file_path)}
                              className="px-3 py-1.5 rounded-lg text-xs font-medium text-blue-300 bg-blue-950/60 hover:bg-blue-900/70 transition flex items-center space-x-1.5 border border-blue-800/60"
                              title="Launch directly in VS Code"
                            >
                              <ExternalLink className="h-3.5 w-3.5 text-blue-400" />
                              <span>Open in VS Code</span>
                            </button>
                          </div>
                        </div>

                        {/* Expanded Code Box */}
                        {isExpanded && (
                          <div className="rounded-lg border border-zinc-800 bg-zinc-950 overflow-hidden mt-3">
                            <div className="px-3 py-2 bg-zinc-900/90 border-b border-zinc-800 flex items-center justify-between text-xs">
                              <span className="font-mono text-[11px] text-zinc-400">
                                {lw.file_path.split('\\').pop() || 'implementation'}
                              </span>
                              <button
                                onClick={() => copyCodeSnippet(lw.starter_code, lw.id)}
                                className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition flex items-center space-x-1 font-mono text-[11px]"
                              >
                                {isCopied ? (
                                  <>
                                    <Check className="h-3 w-3 text-emerald-400" />
                                    <span className="text-emerald-400">Copied!</span>
                                  </>
                                ) : (
                                  <>
                                    <Copy className="h-3 w-3 text-zinc-400" />
                                    <span>Copy Code</span>
                                  </>
                                )}
                              </button>
                            </div>
                            <div className="p-4 overflow-x-auto max-h-96 font-mono text-[11px] text-zinc-300 leading-relaxed">
                              <pre className="whitespace-pre">{lw.starter_code}</pre>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
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
                      <span className={`font-mono text-[9px] px-1.5 py-0.5 rounded uppercase ${
                        msg.tool_used === 'delegate_to_antigravity' ? 'bg-amber-950/80 text-amber-300 border border-amber-800/80 font-semibold'
                        : msg.tool_used === 'academic_rag_llm' ? 'bg-indigo-950/90 text-indigo-300 border border-indigo-700/80 font-semibold'
                        : msg.tool_used === 'react_agent_loop' ? 'bg-emerald-950/90 text-emerald-300 border border-emerald-700/80 font-semibold'
                        : msg.tool_used === 'ollama_gpu_llm' ? 'bg-purple-950/80 text-purple-300 border border-purple-800/80 font-semibold'
                        : msg.tool_used === 'workstation_greeting' ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/80'
                        : msg.tool_used === 'applied_applications' ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/80'
                        : msg.tool_used === 'system_telemetry' ? 'bg-teal-950/80 text-teal-300 border border-teal-800/80'
                        : 'bg-zinc-800 text-zinc-300'
                      }`}>
                        [{msg.tool_used}]
                      </span>
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
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-4xl w-full min-h-[500px] max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
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

      {/* Log New Assignment Modal */}
      {showAddAssignmentModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-lg w-full overflow-hidden shadow-2xl">
            <div className="px-5 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/90">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-emerald-400" />
                <span className="text-sm font-semibold text-zinc-100">Log Pending Coursework Assignment</span>
              </div>
              <button
                onClick={() => setShowAddAssignmentModal(false)}
                className="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-white transition"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <form onSubmit={handleAddAssignment} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-zinc-300 mb-1">
                  Assignment Title / Problem Statement *
                </label>
                <input
                  type="text"
                  required
                  value={newAssignmentTitle}
                  onChange={(e) => setNewAssignmentTitle(e.target.value)}
                  placeholder="e.g. Lab 4: Recurrent Neural Network on Sequence Data"
                  className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-zinc-300 mb-1">
                    Enrolled Subject
                  </label>
                  <select
                    value={newAssignmentSubject}
                    onChange={(e) => setNewAssignmentSubject(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-emerald-500"
                  >
                    {subjects.map((s) => (
                      <option key={s.id} value={s.name}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-300 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    value={newAssignmentDeadline}
                    onChange={(e) => setNewAssignmentDeadline(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="asgIsLab"
                  checked={newAssignmentIsLab}
                  onChange={(e) => setNewAssignmentIsLab(e.target.checked)}
                  className="rounded border-zinc-700 text-emerald-500 focus:ring-0 bg-zinc-950"
                />
                <label htmlFor="asgIsLab" className="text-xs text-zinc-300 cursor-pointer">
                  This is a practical / lab experiment (scaffoldable in Labworks)
                </label>
              </div>

              <div className="pt-3 border-t border-zinc-800 flex items-center justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAddAssignmentModal(false)}
                  className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingAssignment || !newAssignmentTitle.trim()}
                  className="px-4 py-1.5 rounded-lg text-xs font-medium text-white bg-emerald-600 hover:bg-emerald-500 transition disabled:opacity-50 flex items-center space-x-1.5 shadow"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>{submittingAssignment ? 'Saving...' : 'Add to Assignments'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
