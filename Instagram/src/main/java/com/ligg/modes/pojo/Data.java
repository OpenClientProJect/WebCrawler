package com.ligg.modes.pojo;

import java.util.List;

/**
 * @Author Ligg
 * @Time 2025/7/12
 **/
public class Data {
    private String Status;
    private String Msg;
    private SendData SendData;
    private List<UserInFIdList> UserInFIdList;

    public static class SendData {
        private int Id;
        private String LeaveText;
        private String MsgText;
        private Object ConfigData;
        private int UserId;
        private ConfigDatas ConfigDatas;

        // Getters and Setters
        public int getId() { return Id; }
        public void setId(int id) { Id = id; }

        public String getLeaveText() { return LeaveText; }
        public void setLeaveText(String leaveText) { LeaveText = leaveText; }

        public String getMsgText() { return MsgText; }
        public void setMsgText(String msgText) { MsgText = msgText; }

        public Object getConfigData() { return ConfigData; }
        public void setConfigData(Object configData) { ConfigData = configData; }

        public int getUserId() { return UserId; }
        public void setUserId(int userId) { UserId = userId; }

        public ConfigDatas getConfigDatas() { return ConfigDatas; }
        public void setConfigDatas(ConfigDatas configDatas) { ConfigDatas = configDatas; }
    }

    public static class ConfigDatas {
        private String Key_IsEnableKey;
        private String Keys;
        private String Key_TrackingUserCount;
        private String Key_SearchCount;
        private String Key_IsEnableTracking;
        private String Key_IsEnableLike;
        private String Key_IsEnableLeave;
        private String Key_IntervalTime;
        private String Home_IsEnableBrowse;
        private String Home_IsEnableLike;
        private String Home_IsEnableLeave;
        private String Home_HomeBrowseCount;
        private String HuDong_IsHuDong;
        private String HuDong_IsEnableTracking;
        private String HuDong_IsEnableLike;
        private String HuDong_IsEnableLeave;
        private String HuDong_IsEnableMsg;
        private String HuDong_TrackingUserCount;
        private String HuDong_SendUserCount;
        private String HuDong_GetUserCount;
        private String HuDong_IsResetProgress;

        // Getters and Setters
        public String getKey_IsEnableKey() { return Key_IsEnableKey; }
        public void setKey_IsEnableKey(String key_IsEnableKey) { Key_IsEnableKey = key_IsEnableKey; }

        public String getKeys() { return Keys; }
        public void setKeys(String keys) { Keys = keys; }

        public String getKey_TrackingUserCount() { return Key_TrackingUserCount; }
        public void setKey_TrackingUserCount(String key_TrackingUserCount) { Key_TrackingUserCount = key_TrackingUserCount; }

        public String getKey_SearchCount() { return Key_SearchCount; }
        public void setKey_SearchCount(String key_SearchCount) { Key_SearchCount = key_SearchCount; }

        public String getKey_IsEnableTracking() { return Key_IsEnableTracking; }
        public void setKey_IsEnableTracking(String key_IsEnableTracking) { Key_IsEnableTracking = key_IsEnableTracking; }

        public String getKey_IsEnableLike() { return Key_IsEnableLike; }
        public void setKey_IsEnableLike(String key_IsEnableLike) { Key_IsEnableLike = key_IsEnableLike; }

        public String getKey_IsEnableLeave() { return Key_IsEnableLeave; }
        public void setKey_IsEnableLeave(String key_IsEnableLeave) { Key_IsEnableLeave = key_IsEnableLeave; }

        public String getKey_IntervalTime() { return Key_IntervalTime; }
        public void setKey_IntervalTime(String key_IntervalTime) { Key_IntervalTime = key_IntervalTime; }

        public String getHome_IsEnableBrowse() { return Home_IsEnableBrowse; }
        public void setHome_IsEnableBrowse(String home_IsEnableBrowse) { Home_IsEnableBrowse = home_IsEnableBrowse; }

        public String getHome_IsEnableLike() { return Home_IsEnableLike; }
        public void setHome_IsEnableLike(String home_IsEnableLike) { Home_IsEnableLike = home_IsEnableLike; }

        public String getHome_IsEnableLeave() { return Home_IsEnableLeave; }
        public void setHome_IsEnableLeave(String home_IsEnableLeave) { Home_IsEnableLeave = home_IsEnableLeave; }

        public String getHome_HomeBrowseCount() { return Home_HomeBrowseCount; }
        public void setHome_HomeBrowseCount(String home_HomeBrowseCount) { Home_HomeBrowseCount = home_HomeBrowseCount; }

        public String getHuDong_IsHuDong() { return HuDong_IsHuDong; }
        public void setHuDong_IsHuDong(String huDong_IsHuDong) { HuDong_IsHuDong = huDong_IsHuDong; }

        public String getHuDong_IsEnableTracking() { return HuDong_IsEnableTracking; }
        public void setHuDong_IsEnableTracking(String huDong_IsEnableTracking) { HuDong_IsEnableTracking = huDong_IsEnableTracking; }

        public String getHuDong_IsEnableLike() { return HuDong_IsEnableLike; }
        public void setHuDong_IsEnableLike(String huDong_IsEnableLike) { HuDong_IsEnableLike = huDong_IsEnableLike; }

        public String getHuDong_IsEnableLeave() { return HuDong_IsEnableLeave; }
        public void setHuDong_IsEnableLeave(String huDong_IsEnableLeave) { HuDong_IsEnableLeave = huDong_IsEnableLeave; }

        public String getHuDong_IsEnableMsg() { return HuDong_IsEnableMsg; }
        public void setHuDong_IsEnableMsg(String huDong_IsEnableMsg) { HuDong_IsEnableMsg = huDong_IsEnableMsg; }

        public String getHuDong_TrackingUserCount() { return HuDong_TrackingUserCount; }
        public void setHuDong_TrackingUserCount(String huDong_TrackingUserCount) { HuDong_TrackingUserCount = huDong_TrackingUserCount; }

        public String getHuDong_SendUserCount() { return HuDong_SendUserCount; }
        public void setHuDong_SendUserCount(String huDong_SendUserCount) { HuDong_SendUserCount = huDong_SendUserCount; }

        public String getHuDong_GetUserCount() { return HuDong_GetUserCount; }
        public void setHuDong_GetUserCount(String huDong_GetUserCount) { HuDong_GetUserCount = huDong_GetUserCount; }

        public String getHuDong_IsResetProgress() { return HuDong_IsResetProgress; }
        public void setHuDong_IsResetProgress(String huDong_IsResetProgress) { HuDong_IsResetProgress = huDong_IsResetProgress; }
    }

    public static class UserInFIdList {
        private String Id;
        private String Count;

        // Getters and Setters
        public String getId() { return Id; }
        public void setId(String id) { Id = id; }

        public String getCount() { return Count; }
        public void setCount(String count) { Count = count; }
    }

    // Getters and Setters for outer class
    public String getStatus() { return Status; }
    public void setStatus(String status) { Status = status; }

    public String getMsg() { return Msg; }
    public void setMsg(String msg) { Msg = msg; }

    public SendData getSendData() { return SendData; }
    public void setSendData(SendData sendData) { SendData = sendData; }

    public List<UserInFIdList> getUserInFIdList() { return UserInFIdList; }
    public void setUserInFIdList(List<UserInFIdList> userInFIdList) { UserInFIdList = userInFIdList; }
}
