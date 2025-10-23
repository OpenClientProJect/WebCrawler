import fs from 'fs'
import { join } from 'path'
import { app } from 'electron'

// 设置文件路径
const settingsPath = join(app.getPath('userData'), 'settings.json')

// 当前设置
let appSettings = {
  deviceId: '',
  refreshCount: null,
  collectCount: null
}

/**
 * 加载设置从文件
 * @returns {Object} 设置对象
 */
const loadSettings = () => {
  try {
    if (fs.existsSync(settingsPath)) {
      const data = fs.readFileSync(settingsPath, 'utf8')
      const fileSettings = JSON.parse(data)
      appSettings = { ...appSettings, ...fileSettings }
      console.log('设置已从文件加载:', appSettings)
    } else {
      console.log('设置文件不存在，等待用户设置')
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
  return appSettings
}

/**
 * 保存设置到文件
 * @param {Object} settings - 要保存的设置对象
 * @returns {boolean} 保存是否成功
 */
const saveSettings = (settings = null) => {
  try {
    if (settings) {
      appSettings = { ...appSettings, ...settings }
    }

    // 确保目录存在
    const dir = join(app.getPath('userData'))
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }

    // 保存到文件
    fs.writeFileSync(settingsPath, JSON.stringify(appSettings, null, 2))
    console.log('设置已保存到文件:', appSettings)
    return true
  } catch (error) {
    console.error('保存设置失败:', error)
    return false
  }
}

/**
 * 获取当前设置
 * @returns {Object} 当前设置对象
 */
const getSettings = () => {
  return { ...appSettings }
}

/**
 * 更新设置
 * @param {Object} newSettings - 新的设置对象
 * @returns {boolean} 更新是否成功
 */
const updateSettings = (newSettings) => {
  try {
    appSettings = { ...appSettings, ...newSettings }
    return saveSettings()
  } catch (error) {
    console.error('更新设置失败:', error)
    return false
  }
}

/**
 * 验证设置参数
 * @param {Object} settings - 要验证的设置对象
 * @returns {Object} 验证结果 {valid: boolean, errors: string[]}
 */
const validateSettings = (settings) => {
  const errors = []

  if (!settings.deviceId || settings.deviceId.trim() === '') {
    errors.push('设备号不能为空')
  }

  if (
    typeof settings.refreshCount !== 'number' ||
    settings.refreshCount < 1 ||
    settings.refreshCount > 1000
  ) {
    errors.push('刷新数必须在1-1000之间')
  }

  if (
    typeof settings.collectCount !== 'number' ||
    settings.collectCount < 1 ||
    settings.collectCount > 10000
  ) {
    errors.push('采集数必须在1-10000之间')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

// 导出所有函数
export { loadSettings, saveSettings, getSettings, updateSettings, validateSettings }
