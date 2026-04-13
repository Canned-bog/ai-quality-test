@echo off
chcp 65001 >nul
set JMETER_HOME=C:\Users\Li\Downloads\apache-jmeter-5.6.3\apache-jmeter-5.6.3

echo ========================================
echo JMeter 性能测试
echo ========================================

REM 清理旧文件
if exist reports\perf_report (
    echo 删除旧报告目录: reports\perf_report
    rmdir /s /q reports\perf_report
)

if exist reports\result.jtl (
    echo 删除旧结果文件: reports\result.jtl
    del reports\result.jtl
)

REM 确保 reports 目录存在
if not exist reports mkdir reports

echo.
echo 开始运行性能测试...
echo 脚本: performance/ai_benchmark.jmx
echo 结果: reports/result.jtl
echo 报告: reports/perf_report/index.html
echo.

%JMETER_HOME%\bin\jmeter -n -t performance\ai_benchmark.jmx -l reports\result.jtl -e -o reports\perf_report

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 性能测试成功完成！
    echo 报告位置: reports\perf_report\index.html
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ❌ 性能测试失败，错误码: %errorlevel%
    echo ========================================
)

pause