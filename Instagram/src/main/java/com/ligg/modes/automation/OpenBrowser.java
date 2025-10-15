package com.ligg.modes.automation;

import com.ligg.modes.http_request.HttpRequest;
import com.ligg.modes.pojo.Data;
import com.ligg.modes.pojo.ProfilePage;
import com.ligg.modes.service.CookieService;
import com.ligg.modes.service.PrivateMessage;
import com.ligg.modes.service.impl.CookieServiceImpl;
import com.ligg.modes.service.impl.PrivateMessageImpl;
import javafx.application.Platform;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ButtonType;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.List;
import java.util.Objects;
import java.util.Random;


/**
 * @Author Ligg
 * @Time 2025/7/2
 **/
public class OpenBrowser {

    private static final Logger log = LoggerFactory.getLogger(OpenBrowser.class);
    private WebDriver driver;
    private static final PrivateMessage privateMessage = new PrivateMessageImpl();
    private static final HttpRequest httpRequest = new HttpRequest();
    private static final CookieService cookieService = new CookieServiceImpl();
    private String adminUsername;
    private Data data = null;

    //打开浏览器
    public void Login(String username, String password, Button loginButton, String adminUsername) {
        this.adminUsername = adminUsername;
        //创建一个线程用于打开浏览器，避免GUI阻塞主线程
        new Thread(() -> {
            try {
                //默认启动Edge浏览器
                log.info("尝试启动Edge浏览器...");
                driver = new EdgeDriver();
            } catch (Exception e) {
                log.info("Edge启动失败，尝试启动Chrome浏览器...");
                driver = new ChromeDriver();
            }


            driver.get("https://www.instagram.com/");

            try {
                Thread.sleep(2000);
                log.info("开始添加 Instagram cookies...");

                // 首先尝试从 JSON 文件加载 cookies
                cookieService.loadCookiesFromJson(driver);

                cookieService.getCookieValue(driver, "sessionid");

                driver.navigate().refresh(); // 刷新页面使 cookies 生效
                //TODO 如果无法进入首页说明Cookie过期，需要删除 instagram_cookies.json文件 重新获取
                Thread.sleep(3000);
            } catch (Exception e) {
                log.warn("添加 cookies 失败: {}", e.getMessage());
            }

            // 检查登录状态并处理登录逻辑
            try {
                Thread.sleep(5000);

                // 检查是否已经登录（通过检测登录表单是否存在）
                boolean needLogin = false;
                try {
                    // 尝试查找登录表单，如果找到说明需要登录
                    WebElement loginForm = driver.findElement(By.xpath("//*[@id=\"loginForm\"]"));
                    log.info("检测到登录表单，需要手动登录");
                    needLogin = true;
                    cookieService.deleteAllCookies(driver);
                    //选中账号、密码输入框
                    WebElement usernameInput = driver.findElement(By.xpath("//*[@id=\"loginForm\"]/div[1]/div[1]/div/label/input"));
                    WebElement passwordInput = driver.findElement(By.xpath("//*[@id=\"loginForm\"]/div[1]/div[2]/div/label/input"));
                    if (usernameInput.isDisplayed()) {
                        log.info("已找到用户名输入框，开始填入登录信息");
                        usernameInput.sendKeys(username);
                        passwordInput.sendKeys(password);
                        //点击登录按钮
                        WebElement webLoginButton = driver.findElement(By.xpath("//*[@id=\"loginForm\"]/div[1]/div[3]/button"));
                        webLoginButton.click();
                        Thread.sleep(5000);

                        // 手动登录成功后，获取并保存 sessionid cookie
                        log.info("手动登录成功，开始获取 sessionid cookie...");
                        String sessionId = cookieService.getCookieValue(driver, "sessionid");
                        if (sessionId != null) {
                            log.info("成功获取 sessionid: {}", sessionId);
                            // 保存所有 cookies 到 JSON 文件
                            cookieService.saveCookiesToJson(driver);
                        } else {
                            log.warn("未能获取到 sessionid cookie");
                        }
                    }
                } catch (org.openqa.selenium.NoSuchElementException e) {
                    // 找不到登录表单，说明已经通过 cookie 登录
                    log.info("未检测到登录表单，已通过 cookie 完成登录");
                    needLogin = false;
                }

                // 根据登录状态决定后续操作
                if (needLogin) {
                    // 如果进行了手动登录，需要等待并导航到主页
                    Thread.sleep(5000);
                    String currentUrl = driver.getCurrentUrl();
                    log.info("登录后当前 URL: {}", currentUrl);

                    // 如果不在主页，尝试点击主页按钮
                    if (!currentUrl.equals("https://www.instagram.com/?next=%2F")) {
                        try {
                            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
                            var homeButton = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("body > div:nth-of-type(1) > div > div > div:nth-of-type(2) > div > div > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(2) > div > div > div > div > div > div:nth-of-type(1) > div > span > div > a > div")));
                            homeButton.click();
                            Thread.sleep(3000);
                        } catch (Exception e) {
                            log.warn("无法找到主页按钮，直接导航到主页");
                            driver.get("https://www.instagram.com/");
                            Thread.sleep(3000);
                        }
                    }
                } else {
                    // 如果通过 cookie 登录，直接等待页面稳定
                    Thread.sleep(3000);
                    log.info("Cookie 登录成功，页面已准备就绪");
                }

                //开始自动化操作
                log.info("开始执行自动化操作");
                like(driver, loginButton);

            } catch (InterruptedException e) {
                log.error("网页加载超时: {}", e.getMessage());
            } catch (Exception e) {
                log.error("登录过程中发生异常: {}", e.getMessage());
            }
        }).start();
    }

    /**
     * 点赞方法 - 自动滚动页面并对多个帖子点赞
     */
    public void like(WebDriver driver, Button loginButton) {
        Data data = httpRequest.getData(adminUsername);
        this.data = data;
        log.info("开始自动点赞...");
        Platform.runLater(() -> loginButton.setText("点赞中..."));
        new WebDriverWait(driver, Duration.ofSeconds(10));
        JavascriptExecutor js = (JavascriptExecutor) driver;

        Data.ConfigDatas configDatas = data.getSendData().getConfigDatas();
        String Home_IsEnableLike = configDatas.getHome_IsEnableLike();
        int likedCount = 0; // 已点赞的帖子数
        int maxLikes = Integer.parseInt(configDatas.getHome_HomeBrowseCount()); // 最多点赞10个帖子
//        int maxLikes = 0; // 最多点赞10个帖子
        int scrollAttempts = 0; // 滚动次数
        int maxScrollAttempts = 10; // 最多滚动次

        //点赞
        if (Objects.equals(Home_IsEnableLike, "true")) {
            try {
                while (likedCount < maxLikes && scrollAttempts < maxScrollAttempts) {
                    // 查找所有未点赞的按钮（通过aria-label="赞"识别）
                    List<WebElement> likeButtons = driver.findElements(By.cssSelector("svg[aria-label='赞']"));

                    if (!likeButtons.isEmpty()) {
                        for (WebElement svgElement : likeButtons) {
                            // 检查元素是否可见且可点击
                            if (svgElement.isDisplayed()) {
                                // 滚动到元素位置
                                js.executeScript("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", svgElement);
                                Thread.sleep(1000); // 等待滚动完成

                                // 查找可点击的父元素（通常是button）
                                WebElement clickableParent = findClickableParent(svgElement, js);

                                if (clickableParent != null) {
                                    // 使用JavaScript点击，避免元素被遮挡的问题
                                    js.executeScript("arguments[0].click();", clickableParent);
                                    likedCount++;
                                    log.info("成功点赞第{}个帖子", likedCount);
                                    Thread.sleep(2000); // 点赞后等待2秒
                                    break;
                                }
                            }
                        }
                    }

                    // 如果还没达到目标数量，继续滚动页面
                    if (likedCount < maxLikes) {
                        log.info("滚动页面加载更多帖子...");
                        js.executeScript("window.scrollBy(0, 800);"); // 向下滚动800像素
                        Thread.sleep(3000); // 等待页面加载
                        scrollAttempts++;
                    }
                }

                log.info("点赞完成，共点赞{}个帖子", likedCount);

            } catch (InterruptedException e) {
                log.error("点赞过程中发生异常：{}", e.getMessage());
            }
        }

        //评论
        if (Objects.equals(configDatas.getHome_IsEnableLeave(), "true")) {
            comment(driver, loginButton);
        }

        //私信
        if (Objects.equals(configDatas.getHuDong_IsEnableMsg(), "true")) {
            goToProfilePage(driver, js);
        }

        if (Objects.equals(configDatas.getKey_IsEnableKey(), "true")) {
            search(driver);
        }

        //结束后弹窗通知是否关闭浏览器
        Platform.runLater(() -> {
            Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
            alert.setTitle("操作完成");
            alert.setHeaderText("自动化操作已完成");
            alert.setContentText("是否需要关闭浏览器?");

            ButtonType closeBrowser = new ButtonType("关闭浏览器");
            ButtonType keepBrowser = new ButtonType("保持打开");

            alert.getButtonTypes().setAll(closeBrowser, keepBrowser);

            alert.showAndWait().ifPresent(buttonType -> {
                if (buttonType == closeBrowser) {
                    if (driver != null) {
                        driver.quit();
                    }
                } else {
                    updateButtonState(loginButton, "已完成");
                }
            });
        });
    }

    /**
     * 查找SVG元素的可点击父元素
     */
    private WebElement findClickableParent(WebElement svgElement, JavascriptExecutor js) {
        String script = "var element = arguments[0];" +
                "while (element.parentNode) {" +
                "  element = element.parentNode;" +
                "  if (element.tagName.toLowerCase() === 'button' || element.hasAttribute('onclick') || element.getAttribute('role') === 'button') {" +
                "    return element;" +
                "  }" +
                "}" +
                "return null;";

        return (WebElement) js.executeScript(script, svgElement);
    }

    /**
     * 评论方法 - 自动滚动页面并对多个帖子进行评论
     */
    public void comment(WebDriver driver, Button loginButton) {
        log.info("开始自动评论...");
        Platform.runLater(() -> loginButton.setText("评论中..."));

        JavascriptExecutor js = (JavascriptExecutor) driver;
        int commentedCount = 0; // 已评论的帖子数
        int maxComments = Integer.parseInt(data.getSendData().getConfigDatas().getHome_HomeBrowseCount());
//        int maxComments = 0; // 最多点赞x个帖子
        int scrollAttempts = 0; // 滚动次数
        int maxScrollAttempts = 15; // 最多滚动15次

        try {
            while (commentedCount < maxComments && scrollAttempts < maxScrollAttempts) {
                List<WebElement> commentButtons = driver.findElements(By.cssSelector("svg[aria-label='评论']"));

                for (WebElement svgElement : commentButtons) {
                    if (commentOnPost(svgElement, driver, js, commentedCount)) {
                        commentedCount++;
                        if (commentedCount >= maxComments) {
                            break;
                        }
                    }
                }

                if (commentedCount < maxComments) {
                    log.info("滚动页面加载更多帖子...");
                    js.executeScript("window.scrollBy(0, 800);");
                    Thread.sleep(3000);
                    scrollAttempts++;
                }
            }

            log.info("评论完成，共评论{}个帖子", commentedCount);
            updateButtonState(loginButton, "完成");

        } catch (InterruptedException e) {
            log.error("评论过程中发生异常：{}", e.getMessage());
            updateButtonState(loginButton, "评论失败");
        }
    }

    /**
     * 评论单个帖子
     */
    private boolean commentOnPost(WebElement svgElement, WebDriver driver, JavascriptExecutor js, int commentedCount) {
        try {
            if (!svgElement.isDisplayed()) {
                return false;
            }

            js.executeScript("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", svgElement);
            Thread.sleep(1000);

            WebElement clickableParent = findClickableParent(svgElement, js);
            if (clickableParent == null) {
                return false;
            }

            js.executeScript("arguments[0].click();", clickableParent);
            Thread.sleep(2000); // 等待弹窗加载

            // 点击弹窗中的评论按钮
            try {
                WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
                // 等待弹窗出现
                WebElement commentModal = wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("div[role='dialog']")));
                // 在弹窗中查找评论图标
                WebElement commentIconInPopup = commentModal.findElement(By.cssSelector("svg[aria-label='评论']"));
                WebElement clickableCommentButton = findClickableParent(commentIconInPopup, js);
                if (clickableCommentButton != null) {
                    js.executeScript("arguments[0].click();", clickableCommentButton);
                    Thread.sleep(1000); // 等待输入框出现
                }
            } catch (Exception e) {
                log.warn("在弹窗中未找到或无法点击评论图标，将直接尝试输入评论。");
                // 即使找不到图标，也继续尝试，因为UI可能已经允许直接输入
            }
            boolean success = submitComment(driver, js, commentedCount);
            closeCommentBox(js);

            return success;
        } catch (Exception e) {
            log.warn("评论单个帖子时出现异常: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 提交评论
     */
    private boolean submitComment(WebDriver driver, JavascriptExecutor js, int commentedCount) {
        String[] comments = this.data.getSendData().getLeaveText().split("\\n\\n\\n");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        try {
            String commentInputSelector = "body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div.xb88tzc.xw2csxc.x1odjw0f.x5fp0pe.x1qjc9v5.xjbqb8w.xjwep3j.x1t39747.x1wcsgtt.x1pczhz8.xr1yuqi.x11t971q.x4ii5y1.xvc5jky.x15h9jz8.x47corl.xh8yej3.xir0mxb.x1juhsu6 > div > article > div > div.x1qjc9v5.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x5wqa0o.xln7xf2.xk390pu.xdj266r.x14z9mp.xat24cr.x1lziwak.x65f84u.x1vq45kp.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1n2onr6.x11njtxf > div > div > div.x78zum5.xdt5ytf.x1q2y9iw.x1n2onr6.xh8yej3.x9f619.x1iyjqo2.x13lttk3.x1t7ytsu.xpilrb4.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1b5io7h > section.x5ur3kl.x13fuv20.x178xt8z.x1roi4f4.x2lah0s.xvs91rp.xl56j7k.x17ydfre.x1n2onr6.x10b6aqq.x1yrsyyn.x1hrcb2b.xv54qhq > div > form > div > textarea";
            WebElement commentInput = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(commentInputSelector)));
            //随机选择一个评论内容
            String commentText = comments[new Random().nextInt(comments.length)];
            commentInput.sendKeys(commentText);
            Thread.sleep(1000);

            //发送评论
            String postSelector = "body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div.xb88tzc.xw2csxc.x1odjw0f.x5fp0pe.x1qjc9v5.xjbqb8w.xjwep3j.x1t39747.x1wcsgtt.x1pczhz8.xr1yuqi.x11t971q.x4ii5y1.xvc5jky.x15h9jz8.x47corl.xh8yej3.xir0mxb.x1juhsu6 > div > article > div > div.x1qjc9v5.x972fbf.x10w94by.x1qhh985.x14e42zd.x9f619.x78zum5.xdt5ytf.x1iyjqo2.x5wqa0o.xln7xf2.xk390pu.xdj266r.x14z9mp.xat24cr.x1lziwak.x65f84u.x1vq45kp.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1n2onr6.x11njtxf > div > div > div.x78zum5.xdt5ytf.x1q2y9iw.x1n2onr6.xh8yej3.x9f619.x1iyjqo2.x13lttk3.x1t7ytsu.xpilrb4.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1b5io7h > section.x5ur3kl.x13fuv20.x178xt8z.x1roi4f4.x2lah0s.xvs91rp.xl56j7k.x17ydfre.x1n2onr6.x10b6aqq.x1yrsyyn.x1hrcb2b.xv54qhq > div > form > div > div.x13fj5qh > div";
            js.executeScript("document.querySelector('" + postSelector + "').click();");
            log.info("成功评论第{}个帖子: {}", commentedCount + 1, commentText);
            Thread.sleep(3000);
            return true;

        } catch (Exception e) {
            log.warn("评论输入框操作失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 进入个人首页
     */
    private void goToProfilePage(WebDriver driver, JavascriptExecutor js) {
        List<Data.UserInFIdList> userInFIdList = data.getUserInFIdList();

        Data.UserInFIdList userInFI = userInFIdList.get(0);
        Integer id = Integer.parseInt(userInFI.getId());
        Integer count = Integer.parseInt(userInFI.getCount());
        ProfilePage profilePage = httpRequest.getProfilePage(0, id);

        if (profilePage != null) {
            String[] MsgText = this.data.getSendData().getMsgText().split("\\n\\n\\n");
            for (ProfilePage.User user : profilePage.getUserList()) {
                try {
                    String userId = user.getUser_id();
                    String userName = user.getUser_name();
                    String userFullName = user.getUser_fullname();
                    String instagramId = user.getInstagram_id();
                    String instagraminfId = user.getInstagraminf_id();
                    String createdAt = user.getCreated_at();
                    int types = user.getTypes();
                    String instagramURL = "https://www.instagram.com/";
                    String msgText = MsgText[new Random().nextInt(MsgText.length)];//从MsgText数组中随机获取一条消息

                    //发送私信
                    privateMessage.sendPrivateMessage(driver, instagramURL, userName, msgText);
                    Thread.sleep(2000); //等待发送完成
                } catch (Exception e) {
                    log.warn("进入用户主页失败: {}", e.getMessage());
                }
            }
        }
    }

    /**
     * 关键字搜索
     */
    private void search(WebDriver driver) {

        String instagram = "https://www.instagram.com";
        driver.get(instagram + "/?next=%2F");
        String[] MsgText = this.data.getSendData().getMsgText().split("\\n\\n\\n");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        try {

            //点击搜索按钮
            WebElement searchSvg = wait.until(ExpectedConditions.presenceOfElementLocated(
                    By.cssSelector("svg[aria-label='搜索']")
            ));
            searchSvg.click();

            Thread.sleep(2000);

            //搜索框中输入关键字
            WebElement searchInput = wait.until(ExpectedConditions.presenceOfElementLocated(
                    By.cssSelector("input[aria-label='搜索输入']")
            ));
            searchInput.sendKeys(this.data.getSendData().getConfigDatas().getKeys());
            log.info("已输入搜索关键字: {}", this.data.getSendData().getConfigDatas().getKeys());
            Thread.sleep(2000);

            //获取搜索条目集合
            List<WebElement> searchItems = wait.until(ExpectedConditions.presenceOfAllElementsLocatedBy(
                    By.cssSelector("div > div > div.x9f619.x1ja2u2z.x78zum5.x1n2onr6.x1iyjqo2.xs83m0k.xeuugli.x1qughib.x6s0dn4.x1a02dak.x1q0g3np.xdl72j9 > div > div > div > span")
            ));
            //创建一个String数组，用于存储搜索条目
            String[] searchItemTexts = new String[searchItems.size()];
            //遍历搜索条目集合，将每个条目的文本存储到String数组中
            for (int i = 0; i < searchItems.size(); i++) {
                searchItemTexts[i] = searchItems.get(i).getText();
            }

            //遍历搜索条目，打开每个条目的页面
            for (String searchItemText : searchItemTexts) {
                driver.get(instagram + "/" + searchItemText);
                Thread.sleep(2000);
                String msgText = MsgText[new Random().nextInt(MsgText.length)];
                // 发送私信
                privateMessage.sendPrivateMessage(driver, instagram, searchItemText, msgText);
                Thread.sleep(2000);
            }

        } catch (Exception e) {
            log.warn("关键词操作失败: {}", e.getMessage());
        }
    }


    /**
     * 关闭评论弹窗
     */
    private void closeCommentBox(JavascriptExecutor js) {
        //关闭弹窗
        String closeButtonSelector = "body > div.x1n2onr6.xzkaem6 > div.x9f619.x1n2onr6.x1ja2u2z > div > div.xo2ifbc.x10l6tqk.x1eu8d0j.x1vjfegm > div > div";
        js.executeScript("document.querySelector('" + closeButtonSelector + "').click();");
        log.info("关闭评论弹窗");
    }

    /**
     * 更新按钮状态
     */
    private void updateButtonState(Button button, String text) {
        Platform.runLater(() -> {
            button.setText(text);
            button.setDisable(false);
        });
    }
}
