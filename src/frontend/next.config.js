/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  reactStrictMode: true,
  // Static export for standalone Windows exe distribution.
  // In dev, rewrites() proxies /api/* to the FastAPI backend on :8000.
  // In production (static export), both are served from the same FastAPI process.
  ...(isProd
    ? { output: 'export', trailingSlash: true }
    : {
        async rewrites() {
          return [
            {
              source: '/api/:path*',
              destination: 'http://localhost:8000/api/:path*',
            },
          ];
        },
      }),
};

module.exports = nextConfig;
