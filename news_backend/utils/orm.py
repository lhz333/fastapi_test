from sqlalchemy import inspect

def to_dict(obj):
    """将 SQLAlchemy 模型实例转换为字典，自动排除内部状态"""
    if obj is None:
        return None
    # inspect 会安全获取所有映射的列属性，不会包含 _sa_instance_state
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}