import { loadEnv } from "vite";
import { defineConfig, type ViteUserConfig } from "vitest/config";
import react from "@vitejs/plugin-react-swc";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiHost = env.API_HOST || "localhost";

  return {
    plugins: [react()],
    test: {
      globals: true,
      environment: "jsdom",
      setupFiles: "./src/setupTests.ts",
    },
    server: {
      proxy: {
        "/api": {
          target: `http://${apiHost}:5001`,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  } satisfies ViteUserConfig;
});
