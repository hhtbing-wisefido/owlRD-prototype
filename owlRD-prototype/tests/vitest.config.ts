// Vitest配置示例 - 在tests/目录直接运行
// 使用方法：
// 1. 重命名: vitest.config.example.ts -> vitest.config.ts
// 2. 在tests/目录安装依赖: npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
// 3. 运行: npm test 或 python full_system_test.py --vitest

import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest_examples/setup.ts',
    include: ['./vitest_examples/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './test_reports/coverage',
    },
  },
  resolve: {
    alias: {
      // 指向frontend/src目录
      '@': path.resolve(__dirname, '../frontend/src'),
      '@components': path.resolve(__dirname, '../frontend/src/components'),
      '@pages': path.resolve(__dirname, '../frontend/src/pages'),
      '@services': path.resolve(__dirname, '../frontend/src/services'),
      // 强制使用tests/下的React，避免重复实例
      'react': path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
    },
    dedupe: ['react', 'react-dom'],
  },
})
