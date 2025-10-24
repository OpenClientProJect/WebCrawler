export async function crawler(page) {
  console.log('开始爬取')
  try {
    const home = await page.waitForSelector(`div[role = banner] ul > li:first-child > span`)
    await home.click()
  } catch (error) {
    console.log('没有找到首页按钮，不做任何操作')
  }
  await new Promise((resolve) => setTimeout(resolve, 1000))
  while (true) {
    try {
      await page.evaluate(() => {
        window.scrollBy(0, 600)
      })
      const title == await page.$$("div[role = main] > div > div > div > div:nth-child(2) >  div > div:nth-child(4) >div >div:nth-child(3)> div:nth-child(8) span >a")
      const likes = await page.$$("div[role = main] > div > div > div > div:nth-child(2) >  div > div:nth-child(4) span[role='toolbar']")
      console.log(`找到${likes.length}个点赞按钮`)
      for (const like of likes) {
        try {
          await like.click()
          await new Promise((resolve) => setTimeout(resolve, 1000))

          try {
            const u = "div[role='dialog' ] div[aria-hidden=false] >div >div:nth-child(2)>div:nth-child(2)>div>div>div>div >div >div >div:nth-child(2) >div  span >div a"
            const users = await page.$$(u)
            console.log(`找到${users.length}个用户`)
            if (users.length > 5) {
              for (const user of users) {
                try {
                  const href = await user.getProperty('href');
                  const hrefValue = await href.jsonValue();
                  console.log('用户链接:', hrefValue);
                  await new Promise((resolve) => setTimeout(resolve, 1000))
                } catch (error) {
                  console.log('用户采集跳过')
                }
              }
            }
            //输入esc键
            await page.keyboard.press('Escape')
          } catch (error) {
            console.log('跳过')
          }
        } catch (error) {
          console.log('点击点赞按钮时出错:', error)
        }
      }
      //等待
      await new Promise((resolve) => setTimeout(resolve, 1000))
    } catch (error) {
      //向下滚动
      await page.evaluate(() => {
        window.scrollBy(0, 1000)
      })
    }
  }
}
