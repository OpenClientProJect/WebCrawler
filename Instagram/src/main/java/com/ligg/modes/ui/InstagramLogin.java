package com.ligg.modes.ui;

import com.ligg.modes.http_request.HttpRequest;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.stage.Stage;

import java.util.Objects;


/**
 * @Author Ligg
 * @Time 2025/7/2
 **/
public class InstagramLogin extends Application {

    private static final HttpRequest httpRequest = new HttpRequest();

    @Override
    public void start(Stage stage) {
        //设置窗口标题
        stage.setTitle("后台登录验证");
        //设置icon
        stage.getIcons().add(new Image(Objects.requireNonNull(getClass().getResourceAsStream("/image/instagram_logo.jpg"))));
        //创建一个垂直盒子布局作为根容器
        VBox root = new VBox(20);
        root.setAlignment(Pos.CENTER);
        root.setPadding(new Insets(20, 20, 20, 20));

        //添加Logo
        Image logoImage = new Image(Objects.requireNonNull(getClass().getResourceAsStream("/image/instagram_logo.jpg")));
        ImageView logo = new ImageView(logoImage);
        logo.setFitHeight(80);
        logo.setFitWidth(80);
        logo.setPreserveRatio(true);

        //创建输入框
        TextField usernameField = new TextField();
        usernameField.setPromptText("请输入后台用户名");
        usernameField.setPrefWidth(200);

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("请输入后台密码");
        passwordField.setPrefWidth(200);

        //创建登录按钮
        Button loginButton = new Button("后台登录");
        loginButton.setStyle("-fx-background-color: #3897f0; -fx-text-fill: white;");
        loginButton.setPrefWidth(300);
        loginButton.setFont(Font.font(16));

        //添加登录按钮点击事件
        loginButton.setOnAction(event -> {
            String username = usernameField.getText();
            String password = passwordField.getText();

            if (username.isEmpty() || password.isEmpty()) {
                Platform.runLater(() -> {
                    Alert alert = new Alert(Alert.AlertType.WARNING);
                    alert.setTitle("提示");
                    alert.setHeaderText("请输入用户名和密码");
                    alert.showAndWait();
                });
                return;
            }

            loginButton.setText("验证中...");
            loginButton.setDisable(true);

            String response = httpRequest.login(username, password);
            if (response == null || response.contains("ok") || response.contains("no")) {
                Platform.runLater(() -> {
                    Alert alert = new Alert(Alert.AlertType.WARNING);
                    alert.setTitle("提示");
                    alert.setHeaderText(response);
                    alert.showAndWait();
                });
                loginButton.setText("后台登录");
                loginButton.setDisable(false);
                return;
            }

            // 登录成功，关闭当前窗口并打开Instagram登录界面
            stage.close();

            // 创建新的Stage用于Instagram登录界面
            Platform.runLater(() -> {
                Stage instagramStage = new Stage();
                LoginUi.createInstagramLoginUI(instagramStage,username);
            });
        });

        //将所有元素添加到根容器
        root.getChildren().addAll(logo, usernameField, passwordField, loginButton);

        //创建容器设置样式
        Scene scene = new Scene(root, 400, 500);
        scene.setFill(Color.web("#fafafa"));

        //设置场景并显示
        stage.setScene(scene);
        stage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
