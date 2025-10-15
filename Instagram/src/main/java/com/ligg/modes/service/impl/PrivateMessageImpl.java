package com.ligg.modes.service.impl;

import com.ligg.modes.automation.OpenBrowser;
import com.ligg.modes.service.PrivateMessage;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;


/**
 * @Author Ligg
 * @Time 2025/7/25
 * <p>
 * 私信实现类
 **/
public class PrivateMessageImpl implements PrivateMessage {

    private static final Logger log = LoggerFactory.getLogger(OpenBrowser.class);

    /**
     * 发送私信
     */
    @Override
    public void sendPrivateMessage(
            WebDriver driver, String url, String username, String msgText
    ) throws InterruptedException {
        //打开弹窗点击私信按钮
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));

        //先判断是否有发送信息按钮可以直接点击
        try {
            WebElement sendButton = wait.until(ExpectedConditions.elementToBeClickable(
                    By.cssSelector("  div.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x9f619.xjbqb8w.x78zum5.x15mokao.x1ga7v0g.x16uus16.xbiv7yw.x1n2onr6.x6ikm8r.x10wlt62.x1iyjqo2.x2lwn1j.xeuugli.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > div")
            ));
            if (sendButton.isDisplayed()) {
                sendButton.click();
                Thread.sleep(3000);
                //放大窗口
                WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(".x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x9f619.xjbqb8w.x78zum5.x15mokao.x1ga7v0g.x16uus16.xbiv7yw.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1qjc9v5.x1oa3qoh.x1nhvcw1 > div > div.html-div.xdj266r.x14z9mp.xat24cr.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x9f619.xjbqb8w.x78zum5.x15mokao.x1ga7v0g.x16uus16.xbiv7yw.x1diwwjn.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.x1q0g3np.xqjyukv.x1qjc9v5.x1oa3qoh.x13a6bvl > div:nth-child(1)")
                ));
                Thread.sleep(4000);
                element.click();
            }
        } catch (Exception e) {
            // 更多按钮
            String moreSelector = "svg[aria-label='选项']";
            WebElement more = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(moreSelector)));
            more.click();
            Thread.sleep(5000);
            String messageSelector = "body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div > button:nth-child(6)";
            WebElement message = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(messageSelector)));
            message.click();
        }

        //判断是否有通知弹窗
        try {
            WebElement textarea = wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//h2[text()='打开通知']")));
            if (textarea.isDisplayed()) {
                Thread.sleep(2000);
                wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[text()='以后再说']"))).click();
            }
        } catch (Exception e) {
            log.warn("没有通知弹窗");
        }

        //判断该用户是否允许发送私信
        try {
            WebElement element = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector(
                    ".x1lun4ml.xso031l.xpilrb4.x78zum5.x1gg8mnh > div > span"
            )));
            if (element.isDisplayed()) {
                return;
            }
        } catch (Exception e) {
            // 如果找不到该元素，说明可以发送私信，继续执行
            log.info("未找到限制发送私信的元素，可以继续发送私信");
        }
        //输入框框添加内容
        WebElement messageInput = wait.until(ExpectedConditions.presenceOfElementLocated(
                By.cssSelector("div.xzsf02u.x1a2a7pz.x1n2onr6.x14wi4xw.x1iyjqo2.x1gh3ibb.xisnujt.xeuugli.x1odjw0f.notranslate > p")));
        Thread.sleep(2000);
        messageInput.click();
        messageInput.sendKeys(msgText);
        log.info("已输入私信内容: {}", msgText);

        //点击发送按钮
        WebElement sendButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//div[text()='Send']")));
        Thread.sleep(2000);
        sendButton.click();
        log.info("已发送私信给用户: {}", username);
    }
}
