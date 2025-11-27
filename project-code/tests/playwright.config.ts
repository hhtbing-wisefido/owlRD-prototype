// Playwright配置示例 - 在tests/目录直接运行
// 使用方法：
// 1. 重命名: playwright.config.example.ts -> playwright.config.ts
// 2. 在tests/目录安装: npm install -D @playwright/test && npx playwright install
// 3. 运行: npx playwright test 或 python full_system_test.py --playwright

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './playwright_examples',
  
  // 测试超时时间
  timeout: 30 * 1000,
  
  // 每个测试的重试次数
  retries: process.env.CI ? 2 : 0,
  
  // 并行运行的worker数量
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter配置
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  
  use: {
    // 基础URL
    baseURL: 'http://localhost:3000',
    
    // 截图设置
    screenshot: 'only-on-failure',
    
    // 视频录制
    video: 'retain-on-failure',
    
    // 跟踪记录
    trace: 'on-first-retry',
  },

  // 配置不同的浏览器项目
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Web服务器配置（手动启动前端）
  // 注意：需要先手动运行前端服务器
  // cd frontend && npm run dev
  // 或者取消注释下面的webServer配置来自动启动
  /*
  webServer: {
    command: 'cd ../frontend && npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
  */
})
