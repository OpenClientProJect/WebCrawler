package com.ligg.modes.http_request;

import com.ligg.modes.automation.OpenBrowser;
import com.ligg.modes.pojo.Data;
import com.ligg.modes.pojo.ProfilePage;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.google.gson.Gson;

/**
 * @Author Ligg
 * @Time 2025/7/10
 **/
public class HttpRequest {

    private static final Logger log = LoggerFactory.getLogger(OpenBrowser.class);

    private static final String API_URL = "http://aj.ry188.vip";
    private static final String IG_API_URL = "https://ig.ry188.vip";

    /**
     * 发送登录请求
     */
    public String login(String Account, String PassWord) {
        OkHttpClient client = new OkHttpClient();

        String url = String.format(API_URL + "/api/Login.aspx?Account=%s&PassWord=%s", Account, PassWord);
        Request request = new Request.Builder()
                .url(url)
                .build();
        try (Response response = client.newCall(request).execute()) {
            if (response.body() != null) {
                return response.body().string();
            }
        } catch (Exception e) {
            log.error("发送登录请求失败");
        }
        return null;
    }

    /**
     * getData
     */
    public Data getData(String Account) {
        OkHttpClient client = new OkHttpClient();
        String url = String.format(IG_API_URL + "/API/GetData.aspx?Account=%s", Account);
        Request request = new Request.Builder()
                .url(url)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (response.body() != null) {
                String responseBody = response.body().string();
                Gson gson = new Gson();
                return gson.fromJson(responseBody, Data.class);
            }
        } catch (Exception e) {
            log.error("获取数据失败", e);
        }
        return null;
    }

    /**
     * getProfilePage
     */
    public ProfilePage getProfilePage(Integer Count, Integer id) {
        OkHttpClient client = new OkHttpClient();
        String url = String.format(IG_API_URL + "/API/GetUserList.aspx?Count=%s&id=%s", Count, id);
        Request request = new Request.Builder()
                .url(url)
                .build();
        try (Response response = client.newCall(request).execute()) {
            if (response.body() != null) {
                String responseBody = response.body().string();

                // 检查响应是否为空或错误消息
                if (responseBody.trim().isEmpty()) {
                    log.error("API返回空响应");
                    return null;
                }

                Gson gson = new Gson();
                return gson.fromJson(responseBody, ProfilePage.class);
            }
        } catch (Exception e) {
            log.error("获取用户列表失败", e);
        }
        return null;
    }
}
