package com.ligg.modes.pojo;

import java.util.List;

/**
 * @Author Ligg
 * @Time 2025/7/15
 **/
public class ProfilePage {

    private List<User> UserList;

    public List<User> getUserList() {
        return UserList;
    }

    public void setUserList(List<User> userList) {
        UserList = userList;
    }

    public static class User {

        private int id;
        private String user_id;
        private String user_name;
        private String user_fullname;
        private String instagram_id;
        private String instagraminf_id;
        private String created_at;
        private int Types;

        public int getId() {
            return id;
        }

        public void setId(int id) {
            this.id = id;
        }

        public String getUser_id() {
            return user_id;
        }

        public void setUser_id(String user_id) {
            this.user_id = user_id;
        }

        public String getUser_name() {
            return user_name;
        }

        public void setUser_name(String user_name) {
            this.user_name = user_name;
        }

        public String getUser_fullname() {
            return user_fullname;
        }

        public void setUser_fullname(String user_fullname) {
            this.user_fullname = user_fullname;
        }

        public String getInstagram_id() {
            return instagram_id;
        }

        public void setInstagram_id(String instagram_id) {
            this.instagram_id = instagram_id;
        }

        public String getInstagraminf_id() {
            return instagraminf_id;
        }

        public void setInstagraminf_id(String instagraminf_id) {
            this.instagraminf_id = instagraminf_id;
        }

        public String getCreated_at() {
            return created_at;
        }

        public void setCreated_at(String created_at) {
            this.created_at = created_at;
        }

        public int getTypes() {
            return Types;
        }

        public void setTypes(int types) {
            Types = types;
        }
    }

}
