import axios from "axios";

const API = "http://127.0.0.1:8000/posts";

export const getPosts = async () => {
  const res = await axios.get(API);
  return res.data;
};

export const createPost = async (post) => {
  const res = await axios.post(API, post);
  return res.data;
};