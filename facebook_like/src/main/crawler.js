// 使用XPath查找包含特定文本的元素
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
    return { found: false };
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

export async function crawler(page) {
  console.log('开始爬取')
  try {
    const home = await page.waitForSe1lector(`div[role = banner] ul > li:first-child > span`)
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
      // const title = await page.$$("div[role = main] > div > div > div > div:nth-child(2) >  div > div:nth-child(4) >div >div:nth-child(3)> div:nth-child(8) span >a")
      // const likes = await page.$$("div[role = main] > div > div > div > div:nth-child(2) >  div > div:nth-child(4) span[role='toolbar']")
      // console.log(`找到${likes.length}个点赞按钮`)

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

            const like = `${posts} span[role="toolbar"]`
            const likeButton = await page.waitForSelector(like)
            likeButton.click()
            await new Promise((resolve) => setTimeout(resolve, 1000))

            const window = "div[role='dialog' ] div[aria-hidden=false] >div >div:nth-child(2)>div:nth-child(2)>div>div>div>div >div >div >div:nth-child(2) >div  span >div a"
            const users = await page.$$(window)
            console.log(`找到${users.length}个用户`)
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
            await page.keyboard.press('Escape')
          } else {
            console.log(`第${i}个帖子中未找到包含"助"的元素`);
          }
        } catch (sponsorError) {
          console.log('查找赞助元素时出错:', sponsorError);
        }

        console.log(`处理完第${i}个帖子`);
      }catch ( error) {
        console.log(error)
      } finally {
        i++
      }


      // for (const like of likes) {
      //   try {
      //
      //     await like.click()
      //     await new Promise((resolve) => setTimeout(resolve, 1000))
      //
      //     try {
      //       const u = "div[role='dialog' ] div[aria-hidden=false] >div >div:nth-child(2)>div:nth-child(2)>div>div>div>div >div >div >div:nth-child(2) >div  span >div a"
      //       const users = await page.$$(u)
      //       console.log(`找到${users.length}个用户`)
      //       if (users.length > 5) {
      //         for (const user of users) {
      //           try {
      //             const href = await user.getProperty('href');
      //             const hrefValue = await href.jsonValue();
      //             console.log('用户链接:', hrefValue);
      //             await new Promise((resolve) => setTimeout(resolve, 1000))
      //           } catch (error) {
      //             console.log('用户采集跳过')
      //           }
      //         }
      //       }
      //       //输入esc键
      //       await page.keyboard.press('Escape')
      //     } catch (error) {
      //       console.log('跳过')
      //     }
      //   } catch (error) {
      //     console.log('点击点赞按钮时出错:', error)
      //   }
      // }
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
