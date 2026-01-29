import os

from functools import lru_cache

__all__ = ['httpfpt_path']


class HttpFptPathConfig:
    @property
    def project_dir(self) -> str:
        _base_dir = os.path.dirname(os.path.dirname(__file__))
        return _base_dir

    @property
    def log_dir(self) -> str:
        """日志路径"""
        return os.path.join(self.project_dir, 'log')

    @property
    def data_dir(self) -> str:
        """数据路径"""
        return os.path.join(self.project_dir, 'data')

    @property
    def case_data_dir(self) -> str:
        """用例数据路径"""
        return os.path.join(self.project_dir, 'data', 'test_data')

    @property
    def _report_dir(self) -> str:
        """测试报告路径"""
        return os.path.join(self.project_dir, 'report')

    @property
    def allure_report_dir(self) -> str:
        """allure测试报告路径"""
        return os.path.join(self._report_dir, 'allure_report')

    @property
    def allure_report_env_file(self) -> str:
        """allure报告环境文件，用作copy，避免allure开启清理缓存导致环境文件丢失"""
        return os.path.join(self._report_dir, 'allure_report', 'environment.properties')

    @property
    def allure_html_report_dir(self) -> str:
        """allure html测试报告路径"""
        return os.path.join(self._report_dir, 'allure_report', 'html')

    @property
    def html_report_dir(self) -> str:
        """HTML测试报告路径"""
        return os.path.join(self._report_dir, 'html_report')

    @property
    def html_email_report_dir(self) -> str:
        """html邮箱报告路径"""
        return os.path.join(self.project_dir, 'templates')

    @property
    def yaml_report_dir(self) -> str:
        """YAML测试报告路径"""
        return os.path.join(self._report_dir, 'yaml_report')

    @property
    def core_dir(self) -> str:
        """核心配置文件路径"""
        return os.path.join(self.project_dir, 'core')

    @property
    def auth_conf_dir(self) -> str:
        """AUTH配置文件路径"""
        return self.core_dir

    @property
    def global_var_dir(self) -> str:
        """全局变量文件路径"""
        return self.core_dir

    @property
    def hook_dir(self) -> str:
        """钩子函数文件路径"""
        return self.core_dir

    @property
    def allure_env_file(self) -> str:
        """allure环境文件"""
        return os.path.join(self.core_dir, 'allure_env', 'environment.properties')

    @property
    def run_env_dir(self) -> str:
        """运行环境文件路径"""
        return os.path.join(self.core_dir, 'run_env')

    @property
    def testcase_dir(self) -> str:
        """测试用例路径"""
        return os.path.join(self.project_dir, 'testcases')


@lru_cache(maxsize=None)
def cache_httpfpt_path() -> HttpFptPathConfig:
    return HttpFptPathConfig()


httpfpt_path = cache_httpfpt_path()
