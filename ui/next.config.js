/** @type {import('next').NextConfig} */

const nextConfig = {
  experimental: {
    largePageDataBytes: 256 * 100000,
  },
};

module.exports = nextConfig;
