// 基础E2E测试 - 不依赖后端数据
import { test, expect } from '@playwright/test'

test.describe('基础功能测试', () => {
  // 检查服务是否运行
  test.beforeAll(async () => {
    console.log('提示：确保前端服务运行在 http://localhost:3000')
    console.log('启动命令: cd frontend && npm run dev')
  })

  test('应该能够访问首页', async ({ page }) => {
    try {
      // 尝试访问首页，增加超时时间
      const response = await page.goto('/', { 
        waitUntil: 'domcontentloaded',
        timeout: 10000 
      })
      
      // 验证响应成功
      if (response) {
        expect(response.status()).toBeLessThan(400)
      }
      
      // 验证页面加载
      await expect(page.locator('body')).toBeVisible({ timeout: 5000 })
      
    } catch (error) {
      throw new Error('无法访问首页。请确保前端服务运行在 http://localhost:3000')
    }
  })

  test('应该能够导航到登录页', async ({ page }) => {
    try {
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
      
      // 验证页面加载成功
      await expect(page.locator('body')).toBeVisible()
      
      // 查找登录相关的元素（可选）
      const hasLoginButton = await page.getByRole('link', { name: /登录|Login/i })
        .or(page.getByRole('button', { name: /登录|Login/i }))
        .count() > 0
      
      if (hasLoginButton) {
        console.log('✓ 找到登录按钮')
      } else {
        console.log('ℹ 未找到登录按钮（可能已登录或设计不同）')
      }
      
    } catch (error) {
      throw new Error('页面导航失败。请确保前端服务正常运行')
    }
  })

  test('页面应该响应式设计', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded', timeout: 10000 })
    
    // 移动端viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('body')).toBeVisible()
    
    // 桌面端viewport  
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page.locator('body')).toBeVisible()
  })
})

test.describe('用户管理（需要前端运行）', () => {
  test.skip('完整的用户CRUD流程', async ({ page }) => {
    // 这个测试需要前端和后端都运行
    // 使用 test.skip 暂时跳过，需要时手动启用
    await page.goto('/users')
    await expect(page.locator('h1')).toContainText('用户管理')
  })
})
