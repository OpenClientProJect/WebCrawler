// 使用XPath查找包含特定文本的元素
import {getSettings} from "./settings";
import {batchInsertUsers} from "./database";

async function findElementByXPath(page, xpath) {
  return await page.evaluate((xpathSelector) => {
    const result = document.evaluate(xpathSelector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    const element = result.singleNodeValue;

    if (element) {
      return {
        text: element.textContent,
        tagName: element.tagName,
        className: element.className,
        found: true
      };
    }
    return {found: false};
  }, xpath);
}

// 点击通过XPath找到的元素
async function clickElementByXPath(page, xpath) {
  return await page.evaluate((xpathSelector) => {
    const result = document.evaluate(xpathSelector, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    const element = result.singleNodeValue;

    if (element) {
      element.click();
      return true;
    }
    return false;
  }, xpath);
}

//切割用户id
function splitUserId(href) {
  //判断href中是否包含user
  if (href.includes('user')) {
    return href.split('user')[1].split('/')[0];
  }
  if (!href.includes('user')) {
    return href.split('https://www.facebook.com/')[1].split('?')[0];
  }
  return href;
}

//截取帖子id
function splitPostId(href) {
  if (href.includes('profile.php?id=')) {
    return href.split('profile.php?id=')[1].split('&')[0];
  } else if (href.includes('https://www.facebook.com/')) {
    return href.split('https://www.facebook.com/')[1].split('?')[0];
  }
  return href;
}

export async function crawler(page) {
  console.log('开始爬取')
  const currentSettings = getSettings()
  if (currentSettings.urlList.length >= 1) {
    await crawlerPost(currentSettings, page)
  } else
    await infiniteScroll(currentSettings, page)
}

//指定帖子爬取
async function crawlerPost(currentSettings, page) {
  for (const url of currentSettings.urlList) {
    //打开网页
    await page.goto(url)
    await new Promise((resolve) => setTimeout(resolve, 1000))
    //打开点赞列表
    const like = 'div[role="dialog"] span[role="toolbar"] + *'
    const likeButton = await page.$(like)
    likeButton.click()
    await new Promise((resolve) => setTimeout(resolve, 1000))

    //获取用户数
    const userMap = new Map()
    //获取用户数
    const userList = 'div[role="dialog"] div[aria-hidden=false] >div >div:nth-child(2)>div:nth-child(2)>div>div>div>div >div >div >div:nth-child(2) >div  span >div a'

    let userCount = 0
    const maxAttempts = currentSettings.collectCount
    let attempts = 0
    let end = 0
    let f = 0

    while (userCount < maxAttempts) {
      const users = await page.$$(userList)
      console.log(`找到${users.length}个用户`)
      // 处理新发现的用户
      for (const user of users) {
        try {
          // 检查是否已经收集了足够的用户
          if (userCount >= maxAttempts) {
            break
          }
          // await user.evaluate((user) => {
          //   user.scrollIntoView({behavior: "smooth", block: "center"})
          // })


          // 获取用户信息
          const textValue = await user.evaluate(el => el.textContent)
          const href = await user.getProperty('href')
          const hrefValue = await href.jsonValue()
          const userId = splitUserId(hrefValue)

          // 只有当用户尚未被添加时才添加
          if (!userMap.has(userId)) {
            userMap.set(userId, {
              userId: userId,
              userName: textValue,
              Supportid: url, // 使用帖子URL作为Supportid
            })
            userCount++
            console.log(`已收集${userCount}个用户`)
          }

          // 添加延迟以确保页面响应
          await new Promise((resolve) => setTimeout(resolve, 200))
        } catch (error) {
          console.log('获取用户数失败', error)
        }
      }
      const lastUser = users[users.length - 1]
      if (users.length > 0) {
        await lastUser.evaluate((lastUser) => {
          lastUser.scrollIntoView({behavior: "smooth", block: "center"})
        })
      }

      if (userCount >= maxAttempts) {
        break
      }
      attempts = userMap.size

      if (attempts === end) {
        f++
        if (f >= 3) {
          break
        }
      }
      end = attempts
    }

    // 关闭对话框
    await page.keyboard.press('Escape')
    console.log('用户数据', userMap)
  }
}

//无限爬取
async function infiniteScroll(currentSettings, page) {
  try {
    const home = await page.$(`div[role = banner] ul > li:first-child > span`)
    await home.click()
  } catch (error) {
    console.log('没有找到首页按钮，不做任何操作')
  }
  await new Promise((resolve) => setTimeout(resolve, 1000))
  let i = 1
  while (true) {
    try {
      await page.evaluate(() => {
        window.scrollBy(0, 600)
      })

      try {
        const posts = `div[role = main] div[aria-posinset="${i}"]`
        const post = await page.waitForSelector(posts)
        //滚动到post位置
        await post.evaluate((post) => {
          post.scrollIntoView()
        })

        // 等待滚动完成
        await new Promise((resolve) => setTimeout(resolve, 500))

        // 在当前post中查找包含"助"文本的元素
        try {
          // 构建XPath选择器，查找包含"助"文本的span元素
          const xpath = `//div[@aria-posinset="${i}"]//span[contains(text(), "助")]`;
          const sponsorElement = await findElementByXPath(page, xpath);

          if (sponsorElement.found) {
            console.log(`在第${i}个帖子中找到赞助元素:`, sponsorElement.text);
            console.log(`元素标签: ${sponsorElement.tagName}, 类名: ${sponsorElement.className}`);

            //帖子标题
            const postTitle = `${posts}  b > span`
            const titleText = await page.$(postTitle).then(async (titleElement) => {
              return await titleElement.evaluate(el => el.textContent);
            });

            //帖子id
            const postSelector = `${posts} span > a`
            const postIdElements = await page.$$(postSelector)
            const postIdValue = await postIdElements[0]
            const postId = await postIdValue.getProperty('href').then(async (href) => {
              const postIdHref = await href.jsonValue();
              return splitPostId(postIdHref);
            });

            const like = `${posts} span[role="toolbar"]`
            const likeButton = await page.waitForSelector(like)
            likeButton.click()
            await new Promise((resolve) => setTimeout(resolve, 3000))

            const window = "div[role='dialog'] div[aria-hidden=false] >div >div:nth-child(2)>div:nth-child(2)>div>div>div>div >div >div >div:nth-child(2) >div  span >div a"

            let userCount = 0

            const userMap = new Map()
            for (let j = 0; j < currentSettings.collectCount; j++) {
              const users = await page.$$(window, {delay: 5000})
              console.log(`找到${users.length}个用户`)
              if (users.length > 5) {
                for (const user of users) {
                  try {

                    await user.evaluate((user) => {
                      user.scrollIntoView()
                    })
                    //获取a标签的内容
                    const textValue = await user.evaluate(el => el.textContent);

                    const href = await user.getProperty('href');
                    const hrefValue = await href.jsonValue();
                    const userId = splitUserId(hrefValue)

                    userMap.set(userId, {
                      userId: userId,
                      userName: textValue,
                      Supportid: postId,
                    })
                    userCount++
                    if (userCount >= currentSettings.collectCount) {
                      console.log('结束', userCount)
                      break
                    }
                    if (userMap.size < currentSettings.constructor + 1) {

                    }
                    await new Promise((resolve) => setTimeout(resolve, 2000))
                  } catch (error) {
                    console.log('用户采集跳过')
                  }
                }
              }
              if (userCount >= currentSettings.collectCount) {
                console.log('结束', userCount)
                break
              }
            }

            await page.keyboard.press('Escape')
            console.log('用户数据', userMap)
            if (userMap.size > 0) {
              const SupportInf = {
                Supportid: postId,
                title: titleText,
                SupportCount: userMap.size,
              }
              await batchInsertUsers(userMap, SupportInf)
            }
            userMap.clear()
          } else {
            console.log(`第${i}个帖子中未找到包含"助"的元素`);
          }
        } catch (sponsorError) {
          console.log('查找赞助元素时出错:', sponsorError);
        }

        console.log(`处理完第${i}个帖子`);
      } catch (error) {
        console.log(error)
      } finally {
        i++
      }
      await new Promise((resolve) => setTimeout(resolve, 1000))
    } catch (error) {
      //向下滚动
      await page.evaluate(() => {
        window.scrollBy(0, 1000)
      })
    }
  }
}
