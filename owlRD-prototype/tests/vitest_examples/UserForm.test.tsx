// UserForm组件测试 - 根据实际组件编写
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UserForm from '@components/forms/UserForm'

describe('UserForm组件', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
    mockOnCancel.mockClear()
  })

  it('应该渲染所有表单字段', () => {
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    // 使用name查找input（因为FormInput封装了label）
    expect(screen.getByRole('textbox', { name: /用户名/ })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /邮箱/ })).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /手机号/ })).toBeInTheDocument()
    expect(screen.getByRole('combobox', { name: /角色/ })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '创建' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '取消' })).toBeInTheDocument()
  })

  it('应该验证必填字段-阻止空用户名提交', async () => {
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    // 只填写邮箱，不填用户名（用户名默认为空）
    const emailInput = screen.getByRole('textbox', { name: /邮箱/ })
    await userEvent.type(emailInput, 'test@example.com')
    
    // 提交表单
    const submitButton = screen.getByRole('button', { name: '创建' })
    await userEvent.click(submitButton)
    
    // 等待一小段时间，确保如果要调用也已经调用了
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 关键验证：onSubmit不应该被调用（因为验证失败）
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('应该验证邮箱格式-阻止无效邮箱提交', async () => {
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    // 填写有效用户名和无效邮箱
    const usernameInput = screen.getByRole('textbox', { name: /用户名/ })
    const emailInput = screen.getByRole('textbox', { name: /邮箱/ })
    
    await userEvent.type(usernameInput, 'testuser')
    await userEvent.type(emailInput, 'invalid-email')
    
    // 提交表单
    const submitButton = screen.getByRole('button', { name: '创建' })
    await userEvent.click(submitButton)
    
    // 等待一小段时间，确保如果要调用也已经调用了
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 关键验证：onSubmit不应该被调用（因为验证失败）
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('成功提交时应该调用onSubmit回调', async () => {
    mockOnSubmit.mockResolvedValue(undefined)
    
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    // 填写表单
    await userEvent.type(screen.getByRole('textbox', { name: /用户名/ }), 'testuser')
    await userEvent.type(screen.getByRole('textbox', { name: /邮箱/ }), 'test@example.com')
    await userEvent.type(screen.getByRole('textbox', { name: /手机号/ }), '13800138000')
    await userEvent.selectOptions(screen.getByRole('combobox', { name: /角色/ }), 'Nurse')
    
    // 提交
    fireEvent.click(screen.getByRole('button', { name: '创建' }))
    
    // 验证回调被调用
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          username: 'testuser',
          email: 'test@example.com',
          phone: '13800138000',
          role: 'Nurse'
        })
      )
    })
  })

  it('应该在编辑模式下显示初始值', () => {
    const initialData = {
      username: 'existinguser',
      email: 'existing@example.com',
      phone: '13900139000',
      role: 'Doctor',
      alert_levels: ['L1'],
      alert_channels: ['WEB']
    }
    
    render(
      <UserForm 
        initialData={initialData} 
        onSubmit={mockOnSubmit} 
        onCancel={mockOnCancel} 
        isEdit={true}
      />
    )
    
    // 验证字段值
    expect(screen.getByRole('textbox', { name: /用户名/ })).toHaveValue('existinguser')
    expect(screen.getByRole('textbox', { name: /邮箱/ })).toHaveValue('existing@example.com')
    expect(screen.getByRole('textbox', { name: /手机号/ })).toHaveValue('13900139000')
    expect(screen.getByRole('combobox', { name: /角色/ })).toHaveValue('Doctor')
    
    // 编辑模式下按钮文本应该是"更新"
    expect(screen.getByRole('button', { name: '更新' })).toBeInTheDocument()
  })

  it('点击取消按钮应该调用onCancel', () => {
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    fireEvent.click(screen.getByRole('button', { name: '取消' }))
    
    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('应该验证用户名最小长度', async () => {
    render(<UserForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)
    
    const usernameInput = screen.getByRole('textbox', { name: /用户名/ })
    
    // 输入少于3个字符的用户名
    await userEvent.type(usernameInput, 'ab')
    await userEvent.type(screen.getByRole('textbox', { name: /邮箱/ }), 'test@example.com')
    
    // 提交
    fireEvent.click(screen.getByRole('button', { name: '创建' }))
    
    // 应该显示用户名长度错误
    await waitFor(() => {
      expect(screen.getByText('用户名至少3个字符')).toBeInTheDocument()
    })
  })
})
