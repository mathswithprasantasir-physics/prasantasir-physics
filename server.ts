import express, { Request, Response, NextFunction } from 'express';
import session from 'express-session';
import cookieParser from 'cookie-parser';
import nunjucks from 'nunjucks';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename_polyfill = typeof __filename !== 'undefined'
  ? __filename
  : (typeof import.meta !== 'undefined' && import.meta.url ? fileURLToPath(import.meta.url) : path.join(process.cwd(), 'server.ts'));

const __dirname_polyfill = typeof __dirname !== 'undefined'
  ? __dirname
  : path.dirname(__filename_polyfill);

const app = express();
const PORT = 3000;
const ADMIN_PASSWORD = 'admin123';

interface Question {
  id: number;
  chapter?: string;
  topic?: string;
  subtopic?: string;
  year?: string;
  exam_type?: string;
  difficulty?: string;
  question_text?: string;
  question_image?: string;
  option_a?: string;
  option_b?: string;
  option_c?: string;
  option_d?: string;
  option_a_image?: string;
  option_b_image?: string;
  option_c_image?: string;
  option_d_image?: string;
  correct_answer?: string;
  solution?: string;
  solution_image?: string;
  explanation?: string;
  marks?: number;
  negative_marks?: number;
  [key: string]: any;
}

function loadQuestions(): Question[] {
  const jsonPath = path.join(__dirname_polyfill, 'questions.json');
  try {
    if (!fs.existsSync(jsonPath)) {
      return [];
    }
    const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
    return data.questions || [];
  } catch (err) {
    console.error('Error loading questions:', err);
    return [];
  }
}

function saveQuestions(questions: Question[]): boolean {
  const jsonPath = path.join(__dirname_polyfill, 'questions.json');
  try {
    fs.writeFileSync(jsonPath, JSON.stringify({ questions }, null, 2), 'utf-8');
    return true;
  } catch (err) {
    console.error('Error saving questions:', err);
    return false;
  }
}

function getTopics(): string[] {
  const questions = loadQuestions();
  const topics = Array.from(new Set(questions.map(q => q.topic || 'Unknown')));
  return topics.sort();
}

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());
app.use(session({
  secret: 'your-super-secret-key-change-in-production',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false }
}));

app.use('/static', express.static(path.join(__dirname_polyfill, 'static')));

app.use((req: Request, res: Response, next: NextFunction) => {
  res.locals.req = req;
  const sessionData = req.session as any;
  if (!sessionData.flashMessages) {
    sessionData.flashMessages = [];
  }
  if (!Array.isArray(sessionData.bookmarks)) {
    sessionData.bookmarks = [];
  }
  res.locals.bookmarks = sessionData.bookmarks;
  res.locals.flash = (message: string, category: string = 'info') => {
    sessionData.flashMessages.push([category, message]);
  };
  next();
});

const nunjucksEnv = nunjucks.configure('templates', {
  autoescape: true,
  express: app,
  noCache: true
});

nunjucksEnv.addFilter('is_bookmarked', (id: number, bookmarksArray: any) => {
  return Array.isArray(bookmarksArray) && bookmarksArray.includes(Number(id));
});

nunjucksEnv.addFilter('tojson', (val: any) => {
  return JSON.stringify(val);
});

nunjucksEnv.addGlobal('url_for', (name: string, ...args: any[]) => {
  let kwargs: any = {};
  if (args.length > 0) {
    if (typeof args[0] === 'object' && args[0] !== null) {
      kwargs = args[0];
    } else if (typeof args[0] !== 'undefined') {
      kwargs = { id: args[0], filename: args[0] };
    }
  }

  if (name === 'static') {
    const filename = kwargs.filename || (typeof args[0] === 'string' ? args[0] : '');
    return `/static/${filename}`;
  }

  let pathStr = '#';
  const id = kwargs.id ?? kwargs.question_id ?? (typeof args[0] === 'number' || typeof args[0] === 'string' ? args[0] : '');

  if (name === 'student_home' || name === 'index' || name === 'home' || name === 'student.index') {
    pathStr = '/';
  } else if (name === 'student_practice' || name === 'practice' || name === 'student.practice') {
    pathStr = '/practice';
  } else if (name === 'student_bookmarks' || name === 'bookmarks' || name === 'student.bookmarks') {
    pathStr = '/bookmarks';
  } else if (name === 'student_question_detail' || name === 'question_detail' || name === 'student.question_detail' || name === 'question') {
    pathStr = id ? `/question/${id}` : '/practice';
  } else if (name === 'admin_dashboard' || name === 'admin' || name === 'admin.dashboard' || name === 'admin_index') {
    pathStr = '/admin';
  } else if (name === 'admin_login' || name === 'login' || name === 'admin.login') {
    pathStr = '/admin/login';
  } else if (name === 'admin_logout' || name === 'logout' || name === 'admin.logout') {
    pathStr = '/admin/logout';
  } else if (name === 'admin_questions' || name === 'questions' || name === 'admin.questions') {
    pathStr = '/admin/questions';
  } else if (name === 'admin_add_question' || name === 'add_question' || name === 'admin.add_question') {
    pathStr = '/admin/add-question';
  } else if (name === 'admin_edit_question' || name === 'edit_question' || name === 'admin.edit_question') {
    pathStr = id ? `/admin/edit-question/${id}` : '/admin/questions';
  } else if (name === 'admin_delete_question' || name === 'delete_question' || name === 'admin.delete_question') {
    pathStr = id ? `/admin/delete-question/${id}` : '/admin/questions';
  }

  if (kwargs && typeof kwargs === 'object') {
    const params = new URLSearchParams();
    for (const k of Object.keys(kwargs)) {
      if (k !== '__keywords' && k !== 'filename' && k !== 'id' && k !== 'question_id' && kwargs[k] !== undefined && kwargs[k] !== null && kwargs[k] !== '') {
        params.append(k, kwargs[k]);
      }
    }
    const q = params.toString();
    if (q) {
      pathStr += (pathStr.includes('?') ? '&' : '?') + q;
    }
  }
  return pathStr;
});

nunjucksEnv.addGlobal('get_flashed_messages', function(this: any, options?: any) {
  const req = this.ctx ? this.ctx.req : null;
  if (req && req.session && req.session.flashMessages) {
    const messages = req.session.flashMessages;
    req.session.flashMessages = [];
    if (options && options.with_categories) {
      return messages;
    }
    return messages.map((m: any) => Array.isArray(m) ? m[1] : m);
  }
  return [];
});

nunjucksEnv.addGlobal('range', (start: number, stop?: number, step: number = 1) => {
  if (stop === undefined) {
    stop = start;
    start = 0;
  }
  const result: number[] = [];
  for (let i = start; step > 0 ? i < stop : i > stop; i += step) {
    result.push(i);
  }
  return result;
});

nunjucksEnv.addFilter('min', (val: any) => Array.isArray(val) ? Math.min(...val) : val);
nunjucksEnv.addFilter('max', (val: any) => Array.isArray(val) ? Math.max(...val) : val);
nunjucksEnv.addFilter('lower', (val: any) => typeof val === 'string' ? val.toLowerCase() : val);
nunjucksEnv.addFilter('upper', (val: any) => typeof val === 'string' ? val.toUpperCase() : val);
nunjucksEnv.addFilter('tojson', (val: any) => JSON.stringify(val));

nunjucksEnv.addFilter('round', (val: number, precision: number = 0) => {
  if (typeof val !== 'number' || isNaN(val)) return 0;
  const factor = Math.pow(10, precision);
  return Math.round(val * factor) / factor;
});

// Admin routes
app.get('/admin/login', (req: Request, res: Response) => {
  res.render('admin/login.html');
});

app.post('/admin/login', (req: Request, res: Response) => {
  const password = req.body.password;
  if (password === ADMIN_PASSWORD) {
    (req.session as any).admin_logged_in = true;
    res.locals.flash('✅ Welcome Admin!', 'success');
    return res.redirect('/admin');
  } else {
    res.locals.flash('❌ Incorrect password!', 'error');
    return res.render('admin/login.html');
  }
});

app.get('/admin/logout', (req: Request, res: Response) => {
  delete (req.session as any).admin_logged_in;
  res.locals.flash('✅ Logged out successfully!', 'success');
  return res.redirect('/admin/login');
});

app.get('/admin', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }

  const questions = loadQuestions();
  const total_questions = questions.length;

  const chapterStats: Record<string, number> = {};
  for (const q of questions) {
    const chapter = q.chapter || 'Uncategorized';
    chapterStats[chapter] = (chapterStats[chapter] || 0) + 1;
  }
  const chapter_list = Object.entries(chapterStats).map(([k, v]) => ({
    name: k,
    count: v,
    weightage: total_questions > 0 ? Number((v / total_questions * 100).toFixed(2)) : 0
  }));

  const topicStats: Record<string, number> = {};
  for (const q of questions) {
    const topic = q.topic || 'Unknown';
    topicStats[topic] = (topicStats[topic] || 0) + 1;
  }
  const topic_list = Object.entries(topicStats).map(([k, v]) => ({
    name: k,
    count: v,
    weightage: total_questions > 0 ? Number((v / total_questions * 100).toFixed(2)) : 0
  }));

  const easy = questions.filter(q => q.difficulty === 'Easy').length;
  const medium = questions.filter(q => q.difficulty === 'Medium').length;
  const hard = questions.filter(q => q.difficulty === 'Hard').length;

  res.render('admin/dashboard.html', {
    total_questions,
    chapter_stats: chapter_list,
    topic_stats: topic_list,
    recent_questions: questions.slice(0, 10),
    easy,
    medium,
    hard
  });
});

app.get('/admin/questions', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }

  const questions = loadQuestions();
  const topics = getTopics();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  const chapter_filter = (req.query.chapter as string) || '';
  const topic_filter = (req.query.topic as string) || '';
  const difficulty_filter = (req.query.difficulty as string) || '';

  let filtered = questions;
  if (chapter_filter) {
    filtered = filtered.filter(q => q.chapter === chapter_filter);
  }
  if (topic_filter) {
    filtered = filtered.filter(q => q.topic === topic_filter);
  }
  if (difficulty_filter) {
    filtered = filtered.filter(q => q.difficulty === difficulty_filter);
  }

  res.render('admin/questions_list.html', {
    questions: filtered,
    topics,
    chapters,
    current_chapter: chapter_filter,
    current_topic: topic_filter,
    current_difficulty: difficulty_filter
  });
});

app.get('/admin/add-question', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }
  const topics = getTopics();
  const questions = loadQuestions();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  res.render('admin/add_question.html', { topics, chapters });
});

app.post('/admin/add-question', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }
  try {
    const questions = loadQuestions();
    const new_id = questions.length > 0 ? Math.max(...questions.map(q => q.id || 0)) + 1 : 1;

    const new_question: Question = {
      id: new_id,
      chapter: req.body.chapter || 'Uncategorized',
      topic: req.body.topic || '',
      subtopic: req.body.subtopic || '',
      year: req.body.year || '2026',
      question_text: req.body.question_text || '',
      question_image: req.body.question_image || '',
      option_a: req.body.option_a || '',
      option_b: req.body.option_b || '',
      option_c: req.body.option_c || '',
      option_d: req.body.option_d || '',
      option_a_image: req.body.option_a_image || '',
      option_b_image: req.body.option_b_image || '',
      option_c_image: req.body.option_c_image || '',
      option_d_image: req.body.option_d_image || '',
      correct_answer: req.body.correct_answer || '',
      solution_image: req.body.solution_image || '',
      solution: req.body.solution || '',
      explanation: req.body.explanation || '',
      marks: parseInt(req.body.marks || '4', 10),
      negative_marks: parseInt(req.body.negative_marks || '1', 10),
      exam_type: req.body.exam_type || 'NEET',
      difficulty: req.body.difficulty || 'Medium'
    };

    questions.push(new_question);
    saveQuestions(questions);

    res.locals.flash('✅ Question added successfully!', 'success');
    return res.redirect('/admin/questions');
  } catch (e: any) {
    res.locals.flash(`❌ Error: ${e.message}`, 'error');
    return res.redirect('/admin/add-question');
  }
});

app.get('/admin/edit-question/:id', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }
  const id = parseInt(req.params.id, 10);
  const questions = loadQuestions();
  const question = questions.find(q => q.id === id);

  if (!question) {
    res.locals.flash('❌ Question not found!', 'error');
    return res.redirect('/admin/questions');
  }

  const topics = getTopics();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  res.render('admin/edit_question.html', { question, topics, chapters });
});

app.post('/admin/edit-question/:id', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }
  const id = parseInt(req.params.id, 10);
  const questions = loadQuestions();
  const question = questions.find(q => q.id === id);

  if (!question) {
    res.locals.flash('❌ Question not found!', 'error');
    return res.redirect('/admin/questions');
  }

  try {
    question.chapter = req.body.chapter || 'Uncategorized';
    question.topic = req.body.topic || '';
    question.subtopic = req.body.subtopic || '';
    question.year = req.body.year || '2026';
    question.question_text = req.body.question_text || '';
    question.question_image = req.body.question_image || '';
    question.option_a = req.body.option_a || '';
    question.option_b = req.body.option_b || '';
    question.option_c = req.body.option_c || '';
    question.option_d = req.body.option_d || '';
    question.option_a_image = req.body.option_a_image || '';
    question.option_b_image = req.body.option_b_image || '';
    question.option_c_image = req.body.option_c_image || '';
    question.option_d_image = req.body.option_d_image || '';
    question.correct_answer = req.body.correct_answer || '';
    question.solution = req.body.solution || '';
    question.solution_image = req.body.solution_image || '';
    question.explanation = req.body.explanation || '';
    question.marks = parseInt(req.body.marks || '4', 10);
    question.negative_marks = parseInt(req.body.negative_marks || '1', 10);
    question.exam_type = req.body.exam_type || 'NEET';
    question.difficulty = req.body.difficulty || 'Medium';

    saveQuestions(questions);
    res.locals.flash('✅ Question updated successfully!', 'success');
    return res.redirect('/admin/questions');
  } catch (e: any) {
    res.locals.flash(`❌ Error: ${e.message}`, 'error');
    return res.redirect(`/admin/edit-question/${id}`);
  }
});

app.get('/admin/delete-question/:id', (req: Request, res: Response) => {
  if (!(req.session as any).admin_logged_in) {
    return res.redirect('/admin/login');
  }
  const id = parseInt(req.params.id, 10);
  let questions = loadQuestions();
  questions = questions.filter(q => q.id !== id);
  saveQuestions(questions);

  res.locals.flash('✅ Question deleted successfully!', 'success');
  return res.redirect('/admin/questions');
});

// Student routes
app.get('/', (req: Request, res: Response) => {
  const questions = loadQuestions();
  const total_questions = questions.length;
  const topics = getTopics();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  const searchQuery = (req.query.q as string || req.query.search as string || '').trim();

  const chapterStats: Record<string, number> = {};
  const chapterTopics: Record<string, Set<string>> = {};

  for (const q of questions) {
    const chapter = q.chapter || 'Uncategorized';
    const topic = q.topic || 'Unknown';

    chapterStats[chapter] = (chapterStats[chapter] || 0) + 1;

    if (!chapterTopics[chapter]) {
      chapterTopics[chapter] = new Set();
    }
    if (topic && topic !== 'Unknown') {
      chapterTopics[chapter].add(topic);
    }
  }

  const chapter_list = Object.entries(chapterStats).map(([chapter, count]) => ({
    name: chapter,
    count,
    topic_count: chapterTopics[chapter] ? chapterTopics[chapter].size : 0,
    percentage: total_questions > 0 ? Number(((count / total_questions) * 100).toFixed(1)) : 0
  }));

  const topicStats: Record<string, number> = {};
  for (const q of questions) {
    const topic = q.topic || 'Unknown';
    topicStats[topic] = (topicStats[topic] || 0) + 1;
  }
  const topic_list = Object.entries(topicStats).map(([k, v]) => ({ name: k, count: v }));

  let search_results: Question[] = [];
  if (searchQuery) {
    const qLower = searchQuery.toLowerCase();
    search_results = questions.filter(q => {
      const matchText = (q.question_text || '').toLowerCase().includes(qLower);
      const matchTopic = (q.topic || '').toLowerCase().includes(qLower);
      const matchChapter = (q.chapter || '').toLowerCase().includes(qLower);
      const matchSubtopic = (q.subtopic || '').toLowerCase().includes(qLower);
      const matchYear = (q.year || '').toString().toLowerCase().includes(qLower);
      const matchExam = (q.exam_type || '').toLowerCase().includes(qLower);
      return matchText || matchTopic || matchChapter || matchSubtopic || matchYear || matchExam;
    });
  }

  const shuffled = [...questions].sort(() => 0.5 - Math.random());
  const random_questions = shuffled.slice(0, 5);

  res.render('student/index.html', {
    total_questions,
    chapter_stats: chapter_list,
    topic_stats: topic_list,
    random_questions,
    topics,
    chapters,
    search_query: searchQuery,
    search_results,
    search_count: search_results.length
  });
});

app.get('/practice', (req: Request, res: Response) => {
  const questions = loadQuestions();
  const topics = getTopics();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  const yearsSet = new Set<string>();
  for (const q of questions) {
    if (q.year) yearsSet.add(String(q.year));
  }
  const years = Array.from(yearsSet).sort().reverse();

  const searchQuery = (req.query.q as string || req.query.search as string || '').trim();
  const chapter_filter = (req.query.chapter as string) || '';
  const topic_filter = (req.query.topic as string) || '';
  const difficulty_filter = (req.query.difficulty as string) || '';
  const year_filter = (req.query.year as string) || '';

  let page = parseInt(req.query.page as string, 10);
  if (isNaN(page) || page < 1) page = 1;
  const per_page = 10;

  let filtered = questions;
  if (searchQuery) {
    const qLower = searchQuery.toLowerCase();
    filtered = filtered.filter(q => {
      const matchText = (q.question_text || '').toLowerCase().includes(qLower);
      const matchTopic = (q.topic || '').toLowerCase().includes(qLower);
      const matchChapter = (q.chapter || '').toLowerCase().includes(qLower);
      const matchSubtopic = (q.subtopic || '').toLowerCase().includes(qLower);
      const matchYear = (q.year || '').toString().toLowerCase().includes(qLower);
      const matchExam = (q.exam_type || '').toLowerCase().includes(qLower);
      return matchText || matchTopic || matchChapter || matchSubtopic || matchYear || matchExam;
    });
  }
  if (chapter_filter) {
    filtered = filtered.filter(q => q.chapter === chapter_filter);
  }
  if (topic_filter) {
    filtered = filtered.filter(q => q.topic === topic_filter);
  }
  if (difficulty_filter) {
    filtered = filtered.filter(q => q.difficulty === difficulty_filter);
  }
  if (year_filter) {
    filtered = filtered.filter(q => String(q.year) === year_filter);
  }

  const total_questions_count = filtered.length;
  const total_pages = Math.max(1, Math.ceil(total_questions_count / per_page));

  if (page > total_pages) page = total_pages;

  const start = (page - 1) * per_page;
  const end = start + per_page;
  const paginated_questions = filtered.slice(start, end);

  const chapter_topics: Record<string, string[]> = {};
  for (const q of questions) {
    const chapter = q.chapter || 'Uncategorized';
    const topic = q.topic || 'Unknown';
    if (!chapter_topics[chapter]) chapter_topics[chapter] = [];
    if (!chapter_topics[chapter].includes(topic)) {
      chapter_topics[chapter].push(topic);
    }
  }
  for (const ch in chapter_topics) {
    chapter_topics[ch].sort();
  }

  res.render('student/practice.html', {
    questions: paginated_questions,
    chapters,
    topics,
    years,
    chapter_topics,
    search_query: searchQuery,
    current_chapter: chapter_filter,
    current_topic: topic_filter,
    current_difficulty: difficulty_filter,
    current_year: year_filter,
    page,
    total_pages,
    total_questions: total_questions_count,
    per_page
  });
});

app.get('/question/:id', (req: Request, res: Response) => {
  const id = parseInt(req.params.id, 10);
  const questions = loadQuestions();
  const question = questions.find(q => q.id === id);

  if (!question) {
    return res.status(404).render('404.html');
  }

  res.render('student/question_detail.html', { question });
});

app.get('/bookmarks', (req: Request, res: Response) => {
  const sessionData = req.session as any;
  const bookmarkIds: number[] = Array.isArray(sessionData.bookmarks) ? sessionData.bookmarks : [];
  const questions = loadQuestions();
  const bookmarkedQuestions = questions.filter(q => bookmarkIds.includes(q.id));

  const topics = getTopics();
  const chapters = Array.from(new Set(questions.map(q => q.chapter || 'Uncategorized'))).sort();

  res.render('student/bookmarks.html', {
    questions: bookmarkedQuestions,
    bookmark_count: bookmarkedQuestions.length,
    topics,
    chapters
  });
});

app.post('/api/bookmark/:id', (req: Request, res: Response) => {
  const id = parseInt(req.params.id, 10);
  if (isNaN(id)) {
    return res.status(400).json({ success: false, error: 'Invalid question ID' });
  }

  const sessionData = req.session as any;
  if (!Array.isArray(sessionData.bookmarks)) {
    sessionData.bookmarks = [];
  }

  const index = sessionData.bookmarks.indexOf(id);
  let isBookmarked = false;

  if (index >= 0) {
    sessionData.bookmarks.splice(index, 1);
    isBookmarked = false;
  } else {
    sessionData.bookmarks.push(id);
    isBookmarked = true;
  }

  if (req.xhr || req.headers.accept?.includes('application/json') || req.body?.ajax) {
    return res.json({
      success: true,
      isBookmarked,
      questionId: id,
      bookmarks: sessionData.bookmarks,
      count: sessionData.bookmarks.length
    });
  }

  res.locals.flash(isBookmarked ? 'Question bookmarked!' : 'Bookmark removed.', 'info');
  return res.redirect(req.get('referer') || '/');
});

app.get('/api/random-questions', (req: Request, res: Response) => {
  const questions = loadQuestions();
  const sessionData = req.session as any;
  const bookmarkIds: number[] = Array.isArray(sessionData.bookmarks) ? sessionData.bookmarks : [];

  const count = parseInt(req.query.count as string, 10) || 5;
  const shuffled = [...questions].sort(() => 0.5 - Math.random());
  const randomQuestions = shuffled.slice(0, count);

  res.json({
    success: true,
    questions: randomQuestions,
    bookmarks: bookmarkIds
  });
});

app.get('/api/questions', (req: Request, res: Response) => {
  res.json(loadQuestions());
});

app.use((req: Request, res: Response) => {
  res.status(404).render('404.html');
});

app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(500).render('500.html');
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});
