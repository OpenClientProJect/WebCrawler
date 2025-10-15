module instagram.automation {
    requires javafx.controls;
    requires javafx.fxml;
    requires org.seleniumhq.selenium.api;
    requires org.seleniumhq.selenium.edge_driver;
    requires org.seleniumhq.selenium.chrome_driver;
    requires org.slf4j;
    requires dev.failsafe.core;
    requires org.junit.jupiter.api;
    requires org.seleniumhq.selenium.support;
    requires com.google.common;
    requires okhttp3;
    requires com.google.gson;

    exports com.ligg.modes.ui;
    exports com.ligg.modes.pojo to com.google.gson;
    opens com.ligg.modes.pojo to com.google.gson;
}
