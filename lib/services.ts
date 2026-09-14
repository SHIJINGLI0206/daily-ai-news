import { hotModels, hotPapers, media, risingRepos, topics, trends } from "./seed-data";
import type { ModelItem, PaperItem, RepoItem, TrendCategory, TrendItem } from "./types";

export interface TrendFilters {
  category?: TrendCategory | "All";
  query?: string;
}

export interface TrendService {
  listTrends(filters?: TrendFilters): Promise<TrendItem[]>;
  listModels(): Promise<ModelItem[]>;
  listPapers(): Promise<PaperItem[]>;
  listRepos(): Promise<RepoItem[]>;
  listTopics(): Promise<string[]>;
}

export const mockTrendService: TrendService = {
  async listTrends(filters = {}) {
    const query = filters.query?.trim().toLowerCase();
    return trends.filter((trend) => {
      const matchesCategory = !filters.category || filters.category === "All" || trend.category === filters.category;
      const matchesQuery = !query || `${trend.title} ${trend.summary} ${trend.tags.join(" ")}`.toLowerCase().includes(query);
      return matchesCategory && matchesQuery;
    });
  },
  async listModels() { return hotModels; },
  async listPapers() { return hotPapers; },
  async listRepos() { return risingRepos; },
  async listTopics() { return topics; },
};

export const contentSources = { trends, models: hotModels, papers: hotPapers, repos: risingRepos, media };
