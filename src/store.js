import { create } from "zustand";

const load = (k, fallback) => {
  try { return JSON.parse(localStorage.getItem(k)) ?? fallback; } catch { return fallback; }
};
const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));

const useAppStore = create((set, get) => ({
  users: load("users", []),
  notifications: load("notifications", []),
  history: load("history", []),
  user: load("session", null),

  register: (email, password) => {
    const users = get().users;
    if (users.some(u => u.email === email)) throw new Error("User already exists");
    const newUser = { email, password, profile: null };
    const next = [...users, newUser];
    save("users", next);
    set({ users: next, user: newUser });
    save("session", newUser);
  },
  login: (email, password) => {
    const u = get().users.find(x => x.email === email && x.password === password);
    if (!u) throw new Error("Invalid credentials");
    set({ user: u });
    save("session", u);
  },

  logout: () => { set({ user: null }); save("session", null); },

  saveProfile: (profile) => {
    const { user, users } = get();
    const nextUsers = users.map(u => u.email === user.email ? { ...u, profile } : u);
    const nextUser = { ...user, profile };
    save("users", nextUsers); 
    set({ users: nextUsers, user: nextUser });
  },

  addNotification: (msg) => {
    const item = { id: crypto.randomUUID(), msg, ts: Date.now() };
    const next = [item, ...get().notifications];
    save("notifications", next); set({ notifications: next });
  },

  addHistory: (event) => {
    const { user } = get();
    const entry = { ...event, volunteerEmail: user?.email, ts: Date.now() };
    const next = [entry, ...get().history];
    save("history", next); set({ history: next });
  }
}));

export const useAuth = () => useAppStore(state => ({
  user: state.user, login: state.login, logout: state.logout, register: state.register
}));
export const useData = () => useAppStore(state => ({
  user: state.user,
  notifications: state.notifications,
  history: state.history,
  saveProfile: state.saveProfile,
  addNotification: state.addNotification,
  addHistory: state.addHistory,
}));

