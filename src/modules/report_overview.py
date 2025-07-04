from typing import Dict, Any
from datetime import datetime
from ..data_loader import ESDataLoader
from ..i18n import I18n


class ReportOverviewGenerator:
    """Report overview generator / 报告概述生成器"""
    
    def __init__(self, data_loader: ESDataLoader, language: str = "zh"):
        self.data_loader = data_loader
        self.language = language
        self.i18n = I18n(language)
    
    def generate(self) -> str:
        """Generate report overview content / 生成报告概述内容"""
        licenses = self.data_loader.get_licenses()
        cluster_health = self.data_loader.get_cluster_health()
        manifest = self.data_loader.get_manifest()
        
        # Get customer name / 获取客户名称
        customer_name = "N/A"
        if licenses and 'license' in licenses:
            customer_name = licenses['license'].get('issued_to', 'N/A')
        
        # Get cluster name / 获取集群名称
        cluster_name = "N/A"
        if cluster_health:
            cluster_name = cluster_health.get('cluster_name', 'N/A')
        
        # Get inspection date / 获取巡检日期
        collection_date = "N/A"
        if manifest:
            collection_date_str = manifest.get('collectionDate', 'N/A')
            if collection_date_str != "N/A":
                try:
                    # Parse ISO format time / 解析ISO格式时间
                    dt = datetime.fromisoformat(collection_date_str.replace('Z', '+00:00'))
                    collection_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    collection_date = collection_date_str
        
        # Get ES version / 获取ES版本
        es_version = "N/A"
        if manifest and 'Product Version' in manifest:
            version_info = manifest['Product Version']
            if isinstance(version_info, dict):
                es_version = version_info.get('value', 'N/A')
            else:
                es_version = str(version_info)
        
        # Get license information / 获取许可证信息
        license_type = "N/A"
        license_status = "N/A"
        license_expiry = "N/A"
        max_nodes = "N/A"
        
        if licenses and 'license' in licenses:
            license_info = licenses['license']
            license_type = license_info.get('type', 'N/A')
            license_status = license_info.get('status', 'N/A')
            
            # Format expiry time / 格式化过期时间
            expiry_date_str = license_info.get('expiry_date', 'N/A')
            if expiry_date_str != "N/A":
                try:
                    dt = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
                    license_expiry = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    license_expiry = expiry_date_str
            
            max_nodes = license_info.get('max_nodes', 'N/A')
        
        # Get diagnostic tool version / 获取诊断工具版本
        diag_version = "N/A"
        if manifest:
            diag_version = manifest.get('diagVersion', 'N/A')
        
        # Generate table content based on language / 根据语言生成表格内容
        if self.language == 'en':
            overview_content = f"""| Item | Content |
|------|---------|
| **Customer Name** | {customer_name} |
| **Cluster Name** | {cluster_name} |
| **Inspection Date** | {collection_date} |
| **ES Version** | {es_version} |
| **Software License** | {license_type} ({license_status}) |
| **License Owner** | {customer_name} |
| **Expiry Date** | {license_expiry} |
| **License Node Limit** | {max_nodes} |
| **Diagnostic Tool Version** | {diag_version} |

| Item | Content |
|------|---------|
| **Inspector** | [To be filled] |
| **Contact** | [To be filled] |"""
        else:
            overview_content = f"""| 项目 | 内容 |
|------|------|
| **客户名称** | {customer_name} |
| **集群名称** | {cluster_name} |
| **巡检日期** | {collection_date} |
| **ES版本** | {es_version} |
| **软件许可** | {license_type} ({license_status}) |
| **许可所属** | {customer_name} |
| **到期时间** | {license_expiry} |
| **许可节点上限** | {max_nodes} |
| **巡检工具版本** | {diag_version} |

| 项目 | 内容 |
|------|------|
| **执行人员** | [待填写] |
| **联系方式** | [待填写] |"""

        return overview_content
    
    def get_case_data(self) -> Dict[str, Any]:
        """Get raw data for inspection / 获取用于检查的原始数据"""
        return {
            "licenses": self.data_loader.get_licenses(),
            "cluster_health": self.data_loader.get_cluster_health(),
            "manifest": self.data_loader.get_manifest()
        } 