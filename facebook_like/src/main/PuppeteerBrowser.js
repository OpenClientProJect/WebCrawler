// Puppeteer 浏览器管理
import puppeteer from 'puppeteer-core'
import { edgePaths } from './browserPath'

let puppeteerBrowser = null

// 创建 Puppeteer 浏览器实例
export async function createPuppeteerBrowser() {
  if (puppeteerBrowser) {
    return puppeteerBrowser
  }

  for (const browserPath of edgePaths) {
    try {
      console.log(`尝试使用 Chrome 路径: ${browserPath}`)

      puppeteerBrowser = await puppeteer.launch({
        headless: false, // 显示浏览器窗口
        executablePath: browserPath,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-web-security',
          '--disable-features=VizDisplayCompositor',
          '--user-data-dir=./chrome-user-data',
          '--window-size=800,1200', // 设置窗口大小
          '--window-position=0,0' // 设置窗口位置（左上角）
        ]
      })

      // 监听浏览器断开连接事件
      puppeteerBrowser.on('disconnected', () => {
        console.log('Puppeteer 浏览器已断开连接，清理资源...')
        puppeteerBrowser = null
      })

      // 设置窗口位置和大小

      console.log('Puppeteer 浏览器启动成功')
      return puppeteerBrowser
    } catch (error) {
      console.error(`使用路径 ${browserPath} 启动失败:`, error.message)
    }
  }

  throw new Error('所有 Chrome 路径都启动失败')
}

// 关闭浏览器
export async function closePuppeteerBrowser() {
  if (puppeteerBrowser) {
    try {
      await puppeteerBrowser.close()
      puppeteerBrowser = null
      console.log('浏览器已关闭')
      return true
    } catch (error) {
      console.error('关闭浏览器失败:', error)
      return false
    }
  }
  return true
}

// 获取浏览器实例
export function getPuppeteerBrowser() {
  return puppeteerBrowser
}

// 检查浏览器是否运行
export function isBrowserRunning() {
  return puppeteerBrowser !== null && puppeteerBrowser.isConnected()
}
