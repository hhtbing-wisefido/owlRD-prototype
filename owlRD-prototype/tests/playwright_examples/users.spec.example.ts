// 用户管理E2E测试示例
// 使用方法：复制到 e2e/users.spec.ts

import { test, expect } from '@playwright/test'

test.describe('用户管理', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前导航到用户管理页面
    await page.goto('/users')
  })

  test('应该显示用户列表', async ({ page }) => {
    // 验证页面标题
    await expect(page.locator('h1')).toContainText('用户管理')
    
    // 验证表格存在
    await expect(page.locator('table')).toBeVisible()
    
    // 验证新建按钮存在
    await expect(page.getByRole('button', { name: '新建用户' })).toBeVisible()
  })

  test('完整的用户CRUD流程', async ({ page }) => {
    // 1. 点击新建用户按钮
    await page.click('button:has-text("新建用户")')
    
    // 2. 验证模态框打开
    await expect(page.locator('[role="dialog"]')).toBeVisible()
    await expect(page.locator('[role="dialog"]')).toContainText('新建用户')
    
    // 3. 填写表单
    const timestamp = Date.now()
    const username = `testuser_${timestamp}`
    const email = `test_${timestamp}@example.com`
    
    await page.fill('input[name="username"]', username)
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="phone"]', '13800138000')
    await page.fill('input[name="full_name"]', '测试用户')
    await page.selectOption('select[name="role"]', 'Nurse')
    await page.fill('input[name="password"]', 'Test123456')
    
    // 4. 提交表单
    await page.click('button[type="submit"]:has-text("提交")')
    
    // 5. 验证成功提示
    await expect(page.locator('.success-message, .toast-success')).toBeVisible()
    
    // 6. 验证用户出现在列表中
    await expect(page.locator('table')).toContainText(username)
    await expect(page.locator('table')).toContainText(email)
    
    // 7. 编辑用户
    const row = page.locator(`tr:has-text("${username}")`)
    await row.locator('button[aria-label="编辑"]').click()
    
    // 8. 验证编辑模态框打开并显示数据
    await expect(page.locator('[role="dialog"]')).toBeVisible()
    await expect(page.locator('input[name="username"]')).toHaveValue(username)
    
    // 9. 修改数据
    const newEmail = `updated_${timestamp}@example.com`
    await page.fill('input[name="email"]', newEmail)
    await page.click('button[type="submit"]:has-text("保存")')
    
    // 10. 验证修改成功
    await expect(page.locator('table')).toContainText(newEmail)
    
    // 11. 删除用户
    await row.locator('button[aria-label="删除"]').click()
    
    // 12. 确认删除
    await page.click('button:has-text("确认")')
    
    // 13. 验证用户已删除
    await expect(page.locator('table')).not.toContainText(username)
  })

  test('应该验证表单必填字段', async ({ page }) => {
    // 打开新建用户对话框
    await page.click('button:has-text("新建用户")')
    
    // 不填写任何字段直接提交
    await page.click('button[type="submit"]:has-text("提交")')
    
    // 验证错误信息
    await expect(page.locator('text=用户名不能为空')).toBeVisible()
    await expect(page.locator('text=邮箱不能为空')).toBeVisible()
  })

  test('应该验证邮箱格式', async ({ page }) => {
    await page.click('button:has-text("新建用户")')
    
    // 输入无效邮箱
    await page.fill('input[name="email"]', 'invalid-email')
    await page.click('button[type="submit"]')
    
    // 验证错误信息
    await expect(page.locator('text=请输入有效的邮箱地址')).toBeVisible()
  })

  test('应该能够搜索用户', async ({ page }) => {
    // 输入搜索关键词
    await page.fill('input[placeholder="搜索用户"]', 'admin')
    
    // 等待搜索结果
    await page.waitForTimeout(500)
    
    // 验证搜索结果
    const rows = page.locator('table tbody tr')
    await expect(rows).not.toHaveCount(0)
    
    // 所有结果应该包含搜索关键词
    const firstRow = rows.first()
    await expect(firstRow).toContainText('admin', { ignoreCase: true })
  })

  test('应该能够按角色筛选', async ({ page }) => {
    // 选择角色筛选
    await page.selectOption('select[name="roleFilter"]', 'Nurse')
    
    // 等待筛选结果
    await page.waitForTimeout(500)
    
    // 验证筛选结果
    const rows = page.locator('table tbody tr')
    const count = await rows.count()
    
    // 所有结果的角色应该是Nurse
    for (let i = 0; i < count; i++) {
      const row = rows.nth(i)
      await expect(row).toContainText('Nurse')
    }
  })

  test('应该能够分页浏览', async ({ page }) => {
    // 验证分页控件存在
    await expect(page.locator('.pagination')).toBeVisible()
    
    // 记录第一页的第一个用户
    const firstUserOnPage1 = await page.locator('table tbody tr').first().textContent()
    
    // 点击下一页
    await page.click('button:has-text("下一页")')
    
    // 等待数据加载
    await page.waitForTimeout(500)
    
    // 验证内容已改变
    const firstUserOnPage2 = await page.locator('table tbody tr').first().textContent()
    expect(firstUserOnPage1).not.toBe(firstUserOnPage2)
  })
})
