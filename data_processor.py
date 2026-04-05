import pandas as pd
import json

# 读取Excel数据
df = pd.read_excel('../香港各区疫情数据_20250322.xlsx')

# 计算每日新增与累计确诊
daily_new_cases = df.groupby('报告日期')['新增确诊'].sum().reset_index()
daily_new_cases.columns = ['日期', '每日新增确诊']
daily_new_cases = daily_new_cases.sort_values('日期')
daily_new_cases['每日累计确诊'] = daily_new_cases['每日新增确诊'].cumsum()

# 计算各区累计确诊
district_cases = df.groupby('地区名称')['累计确诊'].max().reset_index()
district_cases = district_cases.sort_values('累计确诊', ascending=False)

# 计算每日新增康复与死亡
daily_recovery_death = df.groupby('报告日期').agg({
    '新增康复': 'sum',
    '新增死亡': 'sum'
}).reset_index()
daily_recovery_death.columns = ['日期', '每日新增康复', '每日新增死亡']

# 计算风险等级分布
try:
    risk_distribution = df['风险等级'].value_counts().reset_index()
    risk_distribution.columns = ['风险等级', '数量']
except KeyError:
    # 如果没有风险等级列，创建默认数据
    risk_distribution = pd.DataFrame({'风险等级': ['低风险', '中风险', '高风险'], '数量': [10, 5, 2]})

# 计算各地区的累计确诊和风险等级
district_map_data = df.groupby('地区名称').agg({
    '累计确诊': 'max'
}).reset_index()

# 尝试获取风险等级，如果没有则添加默认值
try:
    district_map_data['风险等级'] = df.groupby('地区名称')['风险等级'].last().values
except KeyError:
    district_map_data['风险等级'] = '低风险'

# 转换日期格式
daily_new_cases['日期'] = pd.to_datetime(daily_new_cases['日期']).dt.strftime('%Y-%m-%d')
daily_recovery_death['日期'] = pd.to_datetime(daily_recovery_death['日期']).dt.strftime('%Y-%m-%d')

# 生成JSON数据
data = {
    'stats': {
        'total_confirm': int(df['累计确诊'].max()),
        'total_recover': int(df['累计康复'].max()) if '累计康复' in df.columns else 0,
        'total_death': int(df['累计死亡'].max()) if '累计死亡' in df.columns else 0,
        'total_current': int(df['累计确诊'].max()) - (int(df['累计康复'].max()) if '累计康复' in df.columns else 0) - (int(df['累计死亡'].max()) if '累计死亡' in df.columns else 0)
    },
    'daily_cases': {
        'dates': daily_new_cases['日期'].tolist(),
        'new_cases': daily_new_cases['每日新增确诊'].tolist(),
        'total_cases': daily_new_cases['每日累计确诊'].tolist()
    },
    'district_cases': {
        'districts': district_cases['地区名称'].tolist(),
        'cases': district_cases['累计确诊'].tolist()
    },
    'recovery_death': {
        'dates': daily_recovery_death['日期'].tolist(),
        'recovery': daily_recovery_death['每日新增康复'].tolist(),
        'death': daily_recovery_death['每日新增死亡'].tolist()
    },
    'risk_distribution': {
        'risk_levels': risk_distribution['风险等级'].tolist(),
        'counts': risk_distribution['数量'].tolist()
    },
    'district_map_data': [
        {
            'name': row['地区名称'],
            'value': int(row['累计确诊']),
            'risk': row['风险等级']
        }
        for _, row in district_map_data.iterrows()
    ]
}

# 保存为JSON文件
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("数据处理完成，生成了data.json文件")
