/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Backend runs on localhost:8000 in dev mode. See src/backend/main.py.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
