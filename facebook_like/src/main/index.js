import {app, shell, BrowserWindow, ipcMain} from 'electron'
import {join} from 'path'
import {electronApp, optimizer, is} from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import {createPuppeteerBrowser, closePuppeteerBrowser} from './PuppeteerBrowser.js'
import {getSettings, updateSettings, validateSettings} from './settings.js'
import {crawler} from "./crawler";

// 保存窗口实例用于发送日志
let mainWindow = null;

// 拦截所有console.log并转发到渲染进程
const originalConsoleLog = console.log;
console.log = function(...args) {
  originalConsoleLog.apply(console, args);

  // 将日志发送到渲染进程
  if (mainWindow && !mainWindow.isDestroyed()) {
    try {
      const message = args.map(arg => {
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg);
          } catch (e) {
            return String(arg);
          }
        }
        return String(arg);
      }).join(' ');

      mainWindow.webContents.send('log-message', {
        type: 'log',
        message: message,
        timestamp: new Date().toLocaleTimeString()
      });
    } catch (error) {
      // 避免发送日志时出错导致程序崩溃
    }
  }
};

const originalConsoleError = console.error;
console.error = function(...args) {
  originalConsoleError.apply(console, args);

  if (mainWindow && !mainWindow.isDestroyed()) {
    try {
      const message = args.map(arg => String(arg)).join(' ');
      mainWindow.webContents.send('log-message', {
        type: 'error',
        message: message,
        timestamp: new Date().toLocaleTimeString()
      });
    } catch (error) {
      // 避免发送日志时出错导致程序崩溃
    }
  }
};

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 350,
    height:680,
    show: false,
    autoHideMenuBar: true,
    frame: false,
    transparent: true,
    resizable: false,
    ...(process.platform === 'linux' ? {icon} : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return {action: 'deny'}
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(viewportSize => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // 设置管理 IPC 处理
  ipcMain.handle('save-settings', (event, settings) => {
    // 验证设置
    const validation = validateSettings(settings)
    if (!validation.valid) {
      console.error('设置验证失败:', validation.errors)
      return {success: false, errors: validation.errors}
    }

    // 保存设置
    const success = updateSettings(settings)
    return {success, errors: []}
  })

  ipcMain.handle('get-settings', () => {
    return getSettings()
  })

  // 窗口控制IPC处理
  ipcMain.handle('minimize-window', () => {
    const windows = BrowserWindow.getAllWindows()
    if (windows.length > 0) {
      windows[0].minimize()
    }
  })

  ipcMain.handle('close-window', () => {
    const windows = BrowserWindow.getAllWindows()
    if (windows.length > 0) {
      windows[0].close()
    }
  })

  // Puppeteer 浏览器控制
  ipcMain.handle('open-puppeteer-browser', async (event, credentials) => {
    //隐藏窗口
    const windows = BrowserWindow.getAllWindows()
    if (windows.length > 0) {
      windows[0].hide()
    }
    try {
      console.log('主进程接收到数据', credentials)
      //创建浏览器实例
      const browser = await createPuppeteerBrowser()

      //新建页面实例
      const page = await browser.newPage()
      //设置用户代理
      await page.setUserAgent({
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
      })

      //打开 Facebook 登录页
      await page.goto('https://www.facebook.com')

      //等待待登录表单加载
      try {
        const loginForm = await page.waitForSelector('#email', {timeout: 5000})
        if (loginForm) {
          //关闭浏览器
          await closePuppeteerBrowser()
          // 重新显示窗口
          if (windows.length > 0) {
            windows[0].show()
            windows[0].webContents.send('switch-to-login')
          }
        }
      } catch (error) {
        //打开渲染进程运行页面
        if (windows.length > 0) {
          // 先发送登录成功事件，让渲染进程切换到Running页面
          windows[0].webContents.send('login-success')
          // 保持窗口显示，让用户看到运行状态
          windows[0].show()
          // 设置窗口在最前，但可以移动到旁边
          windows[0].setAlwaysOnTop(false)
        }
        await crawler(page)
      }
      return true
    } catch (error) {
      if (windows.length > 0) {
        // 先发送登录成功事件，让渲染进程切换到Running页面
        windows[0].webContents.send('login-success')
        // 保持窗口显示，让用户看到运行状态
        windows[0].show()
        // 设置窗口在最前，但可以移动到旁边
        windows[0].setAlwaysOnTop(false)
      }
      console.error(error)
      return false
    }
  })

  //登录
  ipcMain.handle('login', async (event, credentials) => {
    try {
      console.log('登录参数:', credentials)
      const currentSettings = getSettings()

      const browser = await createPuppeteerBrowser()
      //新建页面实例
      const page = await browser.newPage()

      //设置用户代理
      await page.setUserAgent({
        userAgent:
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
      })

      //打开 Facebook 登录页
      await page.goto('https://www.facebook.com')

      // 清空并输入邮箱输入框
      await page.evaluate(() => {
        const emailInput = document.querySelector('#email')
        if (emailInput) {
          emailInput.value = ''
        }
      })
      await page.type('#email', credentials.username, {delay: 500})

      // 清空并输入密码
      await page.evaluate(() => {
        const passInput = document.querySelector('#pass')
        if (passInput) {
          passInput.value = ''
          passInput.focus()
        }
      })
      await page.type('#pass', credentials.password, {delay: 500})

      // 等待1秒
      await new Promise((resolve) => setTimeout(resolve, 1000))
      //点击登录
      await page.click('form button')

      // 使用持久化的设置参数进行后续操作
      console.log('使用设备号:', currentSettings.deviceId)
      console.log('使用刷新数:', currentSettings.refreshCount)
      console.log('使用采集数:', currentSettings.collectCount)

      console.log('登录中...', credentials)

      //发送事件切换渲染进程页面
      const windows = BrowserWindow.getAllWindows()
      if (windows.length > 0) {
        // 先发送登录成功事件，让渲染进程切换到Running页面
        windows[0].webContents.send('login-success')
        // 保持窗口显示，让用户看到运行状态
        windows[0].show()
        // 设置窗口在最前，但可以移动到旁边
        windows[0].setAlwaysOnTop(false)
      }

      // 开始爬虫
      await crawler(page)
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  })

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 清理 Puppeteer 浏览器
app.on('before-quit', async () => {
  await closePuppeteerBrowser()
})

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.
