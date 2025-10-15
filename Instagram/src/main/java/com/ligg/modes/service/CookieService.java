package com.ligg.modes.service;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;

import java.util.Set;

/**
 * @Author Ligg
 * @Time 2025/7/28
 **/
public interface CookieService {

    /**
     * 添加单个 cookie
     * @param driver WebDriver实例
     * @param name cookie名称
     * @param value cookie值
     * @param domain cookie域名
     * @param path cookie路径
     */
    void addCookie(WebDriver driver, String name, String value, String domain, String path);

    /**
     * 添加多个 cookies
     * @param driver WebDriver实例
     * @param cookies cookie集合
     */
    void addCookies(WebDriver driver, Set<Cookie> cookies);

    /**
     * 获取所有 cookies
     * @param driver WebDriver实例
     * @return cookie集合
     */
    Set<Cookie> getAllCookies(WebDriver driver);

    /**
     * 删除所有 cookies
     * @param driver WebDriver实例
     */
    void deleteAllCookies(WebDriver driver);

    /**
     * 添加 Instagram 常用 cookies
     * @param driver WebDriver实例
     */
    void addInstagramCookies(WebDriver driver);

    /**
     * 添加 Instagram 自定义 cookies
     * @param driver WebDriver实例
     * @param sessionId 会话ID
     * @param csrfToken CSRF令牌
     * @param mid 机器ID
     * @param igDid Instagram设备ID
     */
    void addInstagramCookies(WebDriver driver, String sessionId, String csrfToken, String mid, String igDid);

    /**
     * 获取特定的 cookie 值
     * @param driver WebDriver实例
     * @param cookieName cookie名称
     * @return cookie值，如果不存在返回null
     */
    String getCookieValue(WebDriver driver, String cookieName);

    /**
     * 保存 cookies 到 JSON 文件
     * @param driver WebDriver实例
     */
    void saveCookiesToJson(WebDriver driver);

    /**
     * 从 JSON 文件加载 cookies
     * @param driver WebDriver实例
     */
    void loadCookiesFromJson(WebDriver driver);
}
