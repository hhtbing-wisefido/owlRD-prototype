#!/usr/bin/env node
/**
 * 前端端口检查和交互式清理脚本
 * 检查3000端口占用情况，提供交互式清理选项
 */

import { exec, spawn } from 'child_process';
import readline from 'readline';

const PORT = 3000;
const APP_NAME = 'owlRD Frontend';

console.log('========================================');
console.log(`  ${APP_NAME} 端口检查`);
console.log(`  目标端口: ${PORT}`);
console.log('========================================');
console.log('');

/**
 * 获取占用指定端口的进程信息
 */
function getPortProcesses(port) {
    return new Promise((resolve) => {
        exec(`netstat -ano | findstr ":${port}"`, (error, stdout) => {
            if (error || !stdout.trim()) {
                resolve([]);
                return;
            }

            const processes = [];
            const lines = stdout.trim().split('\n');
            
            lines.forEach(line => {
                if (line.includes('LISTENING')) {
                    const match = line.match(/\s+(\d+)\s*$/);
                    if (match) {
                        const pid = match[1];
                        // 获取进程名称
                        exec(`tasklist /FI "PID eq ${pid}" /FO CSV /NH`, (err, procStdout) => {
                            if (!err && procStdout.trim()) {
                                const procName = procStdout.trim().split(',')[0].replace(/"/g, '');
                                processes.push({ pid, name: procName });
                            } else {
                                processes.push({ pid, name: 'Unknown' });
                            }
                        });
                    }
                }
            });

            // 等待所有进程信息获取完成
            setTimeout(() => resolve(processes), 500);
        });
    });
}

/**
 * 终止指定进程
 */
function killProcesses(pids) {
    return new Promise((resolve) => {
        let completed = 0;
        let success = true;

        if (pids.length === 0) {
            resolve(true);
            return;
        }

        pids.forEach(pid => {
            exec(`taskkill /PID ${pid} /F`, (error) => {
                if (error) {
                    console.log(`❌ 无法终止进程 PID: ${pid}`);
                    success = false;
                } else {
                    console.log(`✅ 成功终止进程 PID: ${pid}`);
                }
                
                completed++;
                if (completed === pids.length) {
                    resolve(success);
                }
            });
        });
    });
}

/**
 * 交互式询问用户
 */
function askUser(question) {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer.trim().toUpperCase());
        });
    });
}

/**
 * 启动Vite开发服务器
 */
function startVite() {
    console.log('');
    console.log(`正在启动 ${APP_NAME}...`);
    console.log(`访问地址: http://localhost:${PORT}`);
    console.log('');
    console.log('按 Ctrl+C 停止服务');
    console.log('========================================');
    console.log('');

    // 启动npm run dev
    const vite = spawn('npm', ['run', 'dev'], {
        stdio: 'inherit',
        shell: true
    });

    vite.on('close', (code) => {
        console.log(`\n${APP_NAME} 已停止 (退出码: ${code})`);
    });
}

/**
 * 主函数
 */
async function main() {
    try {
        console.log(`检查端口 ${PORT} 占用情况...`);
        
        const processes = await getPortProcesses(PORT);
        
        if (processes.length === 0) {
            console.log(`✅ 端口 ${PORT} 可用`);
            startVite();
            return;
        }

        console.log(`⚠️  端口 ${PORT} 被以下进程占用:`);
        processes.forEach(proc => {
            console.log(`  - PID: ${proc.pid} | 进程: ${proc.name}`);
        });
        console.log('');

        while (true) {
            const response = await askUser('是否终止这些进程以启动新的服务? (Y/N): ');
            
            if (['Y', 'YES'].includes(response)) {
                const pids = processes.map(proc => proc.pid);
                const success = await killProcesses(pids);
                
                if (success) {
                    console.log('✅ 所有占用进程已清理');
                    console.log('');
                    startVite();
                    return;
                } else {
                    console.log('❌ 部分进程清理失败，无法启动服务');
                    process.exit(1);
                }
            } else if (['N', 'NO'].includes(response)) {
                console.log('❌ 用户选择不清理进程，服务无法启动');
                process.exit(1);
            } else {
                console.log('请输入 Y 或 N');
            }
        }
    } catch (error) {
        console.error('❌ 端口检查失败:', error.message);
        process.exit(1);
    }
}

// 运行主函数
main();
