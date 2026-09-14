export type TrendCategory = "Agents" | "Models" | "Infrastructure" | "Research" | "Creative";

export type SourceKind = "Research" | "Product" | "GitHub" | "Hugging Face" | "Video";

export interface TrendItem {
  id: string;
  rank: number;
  title: string;
  summary: string;
  signal: string;
  category: TrendCategory;
  source: string;
  sourceKind: SourceKind;
  score: number;
  published: string;
  tags: string[];
  href: string;
}

export interface ModelItem {
  name: string;
  org: string;
  detail: string;
  momentum: string;
  accent: "violet" | "orange" | "cyan" | "lime";
}

export interface PaperItem {
  title: string;
  authors: string;
  metric: string;
  note: string;
  href: string;
}

export interface RepoItem {
  name: string;
  description: string;
  stars: string;
  language: string;
  href: string;
}

export interface MediaItem {
  title: string;
  type: "Video" | "Podcast";
  duration: string;
  meta: string;
  href: string;
}
