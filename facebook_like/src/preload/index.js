import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {}

contextBridge.exposeInMainWorld('electronAPI', {
  // 窗口控制
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  closeWindow: () => ipcRenderer.invoke('close-window'),

  // 设置管理
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  getSettings: () => ipcRenderer.invoke('get-settings'),

  // Puppeteer 浏览器控制
  openPuppeteerBrowser: (credentials) => ipcRenderer.invoke('open-puppeteer-browser', credentials),

  //登录
  login: (credentials) => ipcRenderer.invoke('login', credentials),

  // 监听主进程消息
  onSwitchToLogin: (callback) => ipcRenderer.on('switch-to-login', callback),
  removeSwitchToLoginListener: (callback) => ipcRenderer.removeListener('switch-to-login', callback)
})

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  window.electron = electronAPI
  window.api = api
}
