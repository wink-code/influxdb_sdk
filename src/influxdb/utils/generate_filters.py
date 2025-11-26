from typing import Dict, List

def generate_filters(
            filters:Dict[str,str|List[str]], 
            )->str:
    # 如果筛选条件为空，则返回全部
    if not filters:
        return "fn: (r)=> true"
    filter_conditions = []
    def _handle_list(key):
        if isinstance(filters[key],list):
            # 单独处理
            # values = filters.pop(key)
            return f" filter(fn: (r)=> {' or '.join(f'r.{key} == "{ele}"' for ele in filters[key])})"
    for key, value in filters.items():
        # 处理字符串（需加引号）和数值（直接放进去）
        if isinstance(value, str):
            filter_conditions.append(f'filter(fn: (r)=> r.{key} == "{value}")')
        elif isinstance(value,list):
            filter_conditions.append(_handle_list(key))
        else:
            filter_conditions.append(f'r.{key} == {value}')
    
    return '\n|>'.join(filter_conditions)