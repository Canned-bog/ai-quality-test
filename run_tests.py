import pytest
import sys
import os


def main():
    """运行所有测试并生成报告"""
    # 确保报告目录存在
    os.makedirs("reports", exist_ok=True)

    # 运行测试
    args = [
        "test_cases/",
        "-v",
        "--html=reports/ai_quality_report.html",
        "--self-contained-html",
        "--maxfail=5",  # 最多失败5个后停止
        "-m", "not slow"  # 默认跳过慢速测试
    ]

    # 如果命令行有参数，使用命令行参数
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    exit_code = pytest.main(args)

    print("\n" + "=" * 50)
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请查看报告")
    print(f"📊 报告已生成: reports/ai_quality_report.html")
    print("=" * 50)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())