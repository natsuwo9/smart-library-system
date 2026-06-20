import axios from "axios";

const api = axios.create({ baseURL: "/api" });

// Books
export const getBooks = (params) => api.get("/books", { params }).then((r) => r.data);
export const getGenres = () => api.get("/books/genres").then((r) => r.data);
export const createBook = (payload) => api.post("/books", payload).then((r) => r.data);
export const updateBook = (id, payload) => api.put(`/books/${id}`, payload).then((r) => r.data);
export const deleteBook = (id) => api.delete(`/books/${id}`).then((r) => r.data);
export const getSimilarBooks = (id, limit = 6) =>
  api.get(`/recommendations/book/${id}/similar`, { params: { limit } }).then((r) => r.data);

// Members
export const getMembers = () => api.get("/members").then((r) => r.data);
export const createMember = (payload) => api.post("/members", payload).then((r) => r.data);
export const deleteMember = (id) => api.delete(`/members/${id}`).then((r) => r.data);

// Loans
export const getLoans = (params) => api.get("/loans", { params }).then((r) => r.data);
export const createLoan = (payload) => api.post("/loans", payload).then((r) => r.data);
export const returnLoan = (id) => api.post(`/loans/${id}/return`).then((r) => r.data);

// Analytics
export const getSummary = () => api.get("/analytics/summary").then((r) => r.data);
export const getPopularBooks = (limit = 10) =>
  api.get("/analytics/popular-books", { params: { limit } }).then((r) => r.data);
export const getGenreDistribution = () =>
  api.get("/analytics/genre-distribution").then((r) => r.data);
export const getLoanTrends = (weeks = 12) =>
  api.get("/analytics/loan-trends", { params: { weeks } }).then((r) => r.data);
export const getTopMembers = (limit = 5) =>
  api.get("/analytics/top-members", { params: { limit } }).then((r) => r.data);

// Recommendations
export const getMemberRecommendations = (memberId, limit = 8) =>
  api.get(`/recommendations/member/${memberId}`, { params: { limit } }).then((r) => r.data);

export default api;
