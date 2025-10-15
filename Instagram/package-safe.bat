@echo off
chcp 65001 > nul
echo ========================================
echo Instagram自动化工具 - 安全打包脚本
echo ========================================
echo.

echo [1/3] 清理之前的构建文件...
if exist target rmdir /s /q target
if exist installer rmdir /s /q installer
if exist dependency-reduced-pom.xml del dependency-reduced-pom.xml

echo [2/3] 编译并创建Fat JAR...
call mvn clean package -DskipTests
if %errorlevel% neq 0 (
    echo Maven打包失败！
    pause
    exit /b 1
)

echo [3/3] 使用jpackage创建独立应用程序...
echo 正在创建应用程序包，请稍候...

jpackage --type app-image ^
         --input target ^
         --dest installer ^
         --name Instagram ^
         --main-jar Instagram-1.0.0.jar ^
         --main-class com.ligg.App ^
         --app-version 1.0.0 ^
         --vendor "Ligg" ^
         --description "Instagram自动化工具" ^
         --copyright "Copyright (c) 2025 Ligg" ^
         --java-options "-Dfile.encoding=UTF-8" ^
         --java-options "-Djava.awt.headless=false"

if %errorlevel% neq 0 (
    echo.
    echo jpackage创建应用程序包失败！
    echo 可能的原因：
    echo 1. 请确保使用JDK 17或更高版本（不是JRE）
    echo 2. 检查JAVA_HOME环境变量是否正确设置
    echo 3. 确保jpackage命令可用
    echo.
    echo 调试信息：
    java -version
    echo.
    jpackage --version 2>nul || echo jpackage命令不可用
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo 应用程序包位置: installer\Instagram\
echo 主程序: installer\Instagram\Instagram.exe
echo.
echo 测试运行：
echo cd installer\Instagram
echo Instagram.exe
echo.
echo 分发说明：
echo 将整个 installer\Instagram 文件夹复制到目标机器
echo 无需安装JDK，直接运行Instagram.exe即可
echo.
echo 文件夹大小约为200-300MB（包含完整Java运行时）
echo.
pause