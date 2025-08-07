#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import engine
from sqlalchemy import inspect, text
import json

def check_database_structure():
    """데이터베이스 구조를 확인하고 models.py와 비교"""
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("=== 실제 데이터베이스 테이블 목록 ===")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    print("\n=== 각 테이블의 상세 구조 ===")
    
    db_structure = {}
    
    for table_name in tables:
        print(f"\n--- {table_name} 테이블 ---")
        
        # 컬럼 정보 가져오기
        columns = inspector.get_columns(table_name)
        print("컬럼:")
        
        table_info = {
            'columns': [],
            'primary_keys': [],
            'foreign_keys': [],
            'indexes': []
        }
        
        for column in columns:
            col_info = {
                'name': column['name'],
                'type': str(column['type']),
                'nullable': column.get('nullable', True),
                'default': column.get('default', None),
                'primary_key': column.get('primary_key', False)
            }
            table_info['columns'].append(col_info)
            
            pk_marker = " (PK)" if column.get('primary_key', False) else ""
            nullable_marker = "NULL" if column.get('nullable', True) else "NOT NULL"
            
            print(f"  - {column['name']}: {column['type']} ({nullable_marker}){pk_marker}")
        
        # 외래키 정보 가져오기
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print("외래키:")
            for fk in foreign_keys:
                table_info['foreign_keys'].append(fk)
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # 인덱스 정보 가져오기
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print("인덱스:")
            for idx in indexes:
                table_info['indexes'].append(idx)
                unique_marker = "unique" if idx.get('unique', False) else "non-unique"
                print(f"  - {idx['name']}: {idx['column_names']} ({unique_marker})")
        
        db_structure[table_name] = table_info
    
    # JSON 파일로 저장
    with open('database_structure.json', 'w', encoding='utf-8') as f:
        json.dump(db_structure, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n=== 구조 정보가 'database_structure.json' 파일로 저장되었습니다 ===")
    
    return db_structure

if __name__ == "__main__":
    try:
        structure = check_database_structure()
        print("\n✅ 데이터베이스 구조 확인 완료!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc() 