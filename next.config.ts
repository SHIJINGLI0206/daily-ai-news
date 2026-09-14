import type { NextConfig } from "next";

const projectRoot = process.cwd();
const isGitHubPages = process.env.GITHUB_ACTIONS === "true";
const githubBasePath = "/daily-ai-news";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: projectRoot,
  turbopack: { root: projectRoot },
  output: "export",
  trailingSlash: true,
  basePath: isGitHubPages ? githubBasePath : undefined,
  assetPrefix: isGitHubPages ? `${githubBasePath}/` : undefined,
};

export default nextConfig;
