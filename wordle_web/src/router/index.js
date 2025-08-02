import { createRouter, createWebHistory } from "vue-router";
import WordlePage from "../components/wordle.vue"; // Import your new page

const routes = [
  {
    path: "/",
    name: "WordlePage",
    component: WordlePage,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
