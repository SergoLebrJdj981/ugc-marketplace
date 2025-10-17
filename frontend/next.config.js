const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true'
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compress: true,
  output: 'standalone',
  images: {
    formats: ['image/avif', 'image/webp'],
    domains: ['localhost', '127.0.0.1']
  },
  experimental: {
    optimizeCss: true,
    scrollRestoration: true
  }
};

module.exports = withBundleAnalyzer(nextConfig);
